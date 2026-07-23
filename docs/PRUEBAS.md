# Pruebas automatizadas — Evaluador de Ideas (backend)

En este documento describo la suite de pruebas que escribí para el backend:
qué probé, por qué, con qué herramientas, cómo correrla, y qué dejé fuera de
alcance. Complementa a [`DOCUMENTACION_TECNICA.md`](DOCUMENTACION_TECNICA.md)
(arquitectura) y [`MANUAL_USUARIO.md`](MANUAL_USUARIO.md) (funcional), que
también escribí yo.

Al momento de entregar esto, la suite queda en: **90 tests, 100% verdes**,
corridos contra el código real del backend después del merge del frontend
del equipo (commit `9ae0314`).

```
$ cd backend && source .venv/bin/activate
$ python -m unittest discover -s tests -p "test_*.py"
..........................................................................................
----------------------------------------------------------------------
Ran 90 tests in 0.529s

OK
```

---

## 1. Alcance y objetivo

Cuando empecé, el proyecto no tenía suite automatizada: solo
`tests/smoke_test_ia.py`, un script manual que llama a DeepSeek de verdad
(gasta tokens, no es determinista, no corre en CI). La suite que escribí
cubre lo que ese script no puede: **backend completo, sin red, determinista,
rápido (< 1 segundo)**, apta para correr en cada commit.

Prioricé los objetivos de mayor a menor riesgo de negocio:

1. **Que la IA nunca se llame de más** (deduplicación, guardia de completitud)
   — es la garantía de costo del sistema.
2. **Que el contrato de error 4.6 no se rompa en silencio** — el frontend
   decide su UI según `error.codigo`; un código mal mapeado rompe la UX sin
   que ningún tipo estático lo detecte.
3. **Que el CRUD de ideas y el flujo de evaluación se comporten según el
   contrato 4.1-4.5** documentado en `backend/README-FRONTEND.md`.
4. **Piezas puras** (hash de dedup, construcción del prompt, migraciones)
   probadas de forma aislada por ser fáciles de romper sin darse cuenta.

Dejé el frontend **fuera de alcance de esta suite** — no hay tooling de test
configurado en `frontend/package.json` (ni Vitest ni Jest ni Testing
Library). Lo anoto como deuda pendiente en §7.

---

## 2. Herramientas

| Elegí | En vez de | Por qué |
|---|---|---|
| `unittest` (stdlib) | `pytest` | No tuve acceso a PyPI al momento de escribir la suite (`pip install pytest` falló por resolución DNS a `files.pythonhosted.org`, mientras que otros hosts como GitHub y el registro de npm sí respondían). `unittest` viene con Python, no depende de red. |
| `unittest.mock` | `pytest-mock` / librerías de mocking de terceros | Mismo motivo — es stdlib. |
| `fastapi.testclient.TestClient` | — | Ya es una dependencia transitiva de FastAPI (usa `httpx`, que ya estaba instalado); me permite probar los endpoints HTTP reales sin levantar un servidor. |
| SQLite temporal vía `DATABASE_URL` env var | Mock del ORM | Probar contra SQLAlchemy + SQLite real (no una base en memoria simulada a mano) detecta bugs de la capa de persistencia real que un mock no vería. |

**Nota de portabilidad:** elegí escribir las clases de test como
`unittest.TestCase` estándar. Si en el futuro hay acceso a PyPI, `pip
install -r backend/tests/requirements.txt && pytest backend/tests` las
descubre y corre tal cual — pytest soporta `TestCase` de forma nativa. No
hace falta reescribir nada para "migrar" a pytest; es un cambio de un
comando, no de código.

### Cambio de producción que tuve que hacer para poder testear

`backend/app/db/session.py` tenía la URL de la base de datos **hardcodeada**
(`sqlite:///./evaluador.db`), así que importar `app.main` para usar
`TestClient` habría creado/tocado la base de datos real de desarrollo en
cada corrida de tests. Lo cambié a:

```python
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./evaluador.db")
```

Backward-compatible (el default es idéntico al valor anterior); en
`tests/testing_setup.py` fijo `DATABASE_URL` a un archivo temporal único
(`tempfile.gettempdir()/evaluador_test_<uuid>.db`) **antes** de importar
cualquier módulo de `app`, así la suite nunca toca `backend/evaluador.db`.

---

## 3. Estrategia

### 3.1 Aislar la IA (nunca red real en tests automatizados)

Todo lo que en producción termina llamando a DeepSeek lo corté con un doble:

- **A nivel de proveedor** (`test_cliente_ia.py`): reemplazo
  `app.ia.cliente_ia.OpenAI` por `FakeOpenAIClient`, un doble mínimo que
  imita `.chat.completions.create(...)`. Con esto simulo tanto respuestas
  válidas como cada excepción que el SDK de OpenAI puede lanzar
  (`RateLimitError`, `APIStatusError`, `APIConnectionError`, `APIError`),
  usando las clases reales de excepción del SDK (no dobles de la excepción)
  para que el `except` de producción las capture de verdad.
- **A nivel de motor** (`test_motor_ia.py`): reemplazo
  `app.ia.motor_ia.generar_evaluacion` para probar la orquestación
  (completitud → prompt → cliente) sin bajar hasta HTTP.
- **A nivel de servicio/endpoint** (`test_endpoints_evaluar.py`,
  `test_endpoints_estado.py`, `test_endpoints_comparar.py`): reemplazo
  `app.services.evaluacion_service.evaluar_idea` (el nombre tal como lo
  importa ese módulo — clave para que `unittest.mock.patch` apunte al lugar
  correcto). Así puedo probar deduplicación, persistencia y mapeo de errores
  sin re-simular todo el stack de la IA en cada test.

Decidí probar cada capa por separado (en vez de solo la más externa) porque
cada una tiene lógica propia que puede romperse independientemente: el
mapeo de errores del proveedor no depende de la deduplicación, y viceversa.

### 3.2 Aislar la base de datos

En `ApiTestCase` (dentro de `testing_setup.py`) creo las tablas en la base
temporal antes de cada test y las borro después (`Base.metadata.create_all`
/ `drop_all`), y sobreescribo la dependencia `get_db` de FastAPI para que
cada test use su propia `Session`. Ningún test depende del orden de
ejecución ni de qué corrió antes.

### 3.3 Payloads y resultados de ejemplo centralizados

Centralicé `idea_valida()` y `fake_resultado_motor_ia()` en
`testing_setup.py` como única fuente de verdad para "cómo se ve una Idea
válida" / "cómo se ve un resultado de IA válido" dentro de los tests. Si el
contrato 4.1 o 4.2 cambia, lo actualizo en un solo lugar y la mayoría de los
tests siguen siendo válidos sin tocarlos.

---

## 4. Matriz de cobertura

| Archivo | Módulo bajo prueba | Tests | Qué cubre |
|---|---|---|---|
| `test_completitud.py` | `ia/completitud.py` | 11 | Umbrales mínimos por campo, strip de espacios, mensaje de error, que `asegurar_completitud` lance con `codigo=ENTRADA_INCOMPLETA` |
| `test_prompts.py` | `ia/prompts.py` | 7 | Marcado de campos vacíos como `(no proporcionado)`, armado de `system`+`user`, que campos no reconocidos no se filtren al prompt |
| `test_excepciones.py` | `ia/excepciones.py` | 5 | Que cada excepción tenga el `codigo` correcto del contrato 4.6, herencia común, preservación de `mensaje`/`campos` |
| `test_service_hash.py` | `services/evaluacion_service._hash_idea` | 7 | Determinismo del hash, sensibilidad a contenido/modelo/versión de prompt, insensibilidad a orden de claves y a `None` vs `""` |
| `test_motor_ia.py` | `ia/motor_ia.evaluar_idea` | 3 | **Que una idea incompleta NUNCA llegue a llamar al cliente de IA** (el test de costo más importante de la suite); que el prompt se arme antes de llamar; propagación de errores |
| `test_cliente_ia.py` | `ia/cliente_ia.generar_evaluacion` | 14 | Éxito con y sin `prompt_cache_hit_tokens`; mapeo completo de errores del proveedor (429 por `RateLimitError` y por `APIStatusError`, 5xx, 401, conexión, genérico); respuesta truncada, vacía, `None`, no-JSON, JSON que no cumple el contrato 4.2, enum inválido |
| `test_migraciones.py` | `db/migraciones.py` | 4 | Agrega columnas faltantes, idempotencia (correr dos veces no falla), tabla inexistente no rompe, no pisa datos de una columna ya migrada |
| `test_endpoints_ideas.py` | `POST/GET /ideas`, `GET /ideas/{id}` | 12 | Creación válida, defaults de opcionales, 422 por campo obligatorio faltante/vacío, 422 por `max_length` excedido, generación de UUID, 404 en idea inexistente |
| `test_endpoints_evaluar.py` | `POST /ideas/{id}/evaluar` | 14 | Éxito end-to-end con `PromptLog` persistido, 404 en idea inexistente, 422 `ENTRADA_INCOMPLETA` sin persistir nada, **los 4 códigos de error de IA con su status HTTP exacto**, y deduplicación (misma idea, dos ideas con contenido idéntico, invalidación al cambiar contenido) |
| `test_endpoints_estado.py` | `PATCH /evaluaciones/{id}/estado` | 5 | Cambio de estado, que sea texto libre (sin enum cerrado, tal como lo documenta el contrato), 404, 422 sin body, persistencia |
| `test_endpoints_comparar.py` | `POST /comparar` | 8 | Solo incluye ideas evaluadas, orden fijo de criterios, ids inexistentes se omiten, límites `min_length=1`/`max_length=20`, y un caso documentado como hallazgo (§5) |
| **Total** | | **90** | |

---

## 5. Hallazgos durante la escritura de la suite

Al escribir tests de un contrato me encontré con huecos que la lectura del
código no siempre deja ver. Los documenté como tests (para que no se
reintroduzcan) y los reporto acá para que el equipo decida si son
aceptables:

1. **`POST /ideas` acepta un `id` elegido por el cliente.**
   `endpoints.crear_idea` hace `idea.model_dump(exclude_none=True)`, que solo
   descarta el campo si es `None`. Si el cliente manda `"id": "lo-que-sea"`,
   se persiste tal cual — no hay UUID forzado ni validación de formato server
   side. Lo dejé documentado en `test_crear_idea_respeta_id_explicito_del_cliente`.
   No me parece explotable de forma grave (no hay auth ni datos sensibles por
   idea), pero permite colisiones de `id` si dos clientes eligen el mismo
   valor.

2. **`POST /comparar` no ordena las evaluaciones por fecha explícitamente.**
   `generar_comparacion` usa `idea.evaluaciones[-1]` (último elemento de la
   relación SQLAlchemy) para decidir cuál es "la más reciente", en vez de
   `order_by(Evaluacion.fecha.desc())`. En SQLite, sin `ORDER BY` explícito,
   una consulta simple normalmente devuelve las filas en orden de inserción
   — por eso funciona en la práctica — pero no es un contrato garantizado por
   SQL. Lo documenté en `test_comparar_usa_la_ultima_evaluacion_insertada`
   (describe el comportamiento actual, no lo prescribe). Mi recomendación:
   agregar `order_by="Evaluacion.fecha"` a la relación en `models.py` para
   que deje de depender de una casualidad del motor de base de datos.

Ninguno de los dos bloqueó la suite (los probé como comportamiento
observado, no como bug a ciegas), pero me parece que valen una decisión
consciente del equipo.

---

## 6. Cómo correr la suite

```bash
cd backend
source .venv/bin/activate          # o crear el venv si no existe (ver docs/DOCUMENTACION_TECNICA.md §7)
python -m unittest discover -s tests -p "test_*.py" -v
```

- **No requiere `IA_API_KEY` real** ni conexión a internet: en
  `tests/testing_setup.py` fijo una key falsa y aíslo la IA con mocks antes
  de que se importe `app`.
- **No toca `backend/evaluador.db`**: usa un archivo SQLite temporal por
  corrida, borrado por el sistema operativo (queda en `$TMPDIR`).
- Para correr un solo archivo: `python -m unittest discover -s tests -p "test_endpoints_evaluar.py" -v`
  (uso siempre `discover`, no `python -m unittest tests.test_x`, porque
  `testing_setup.py` se importa como módulo de nivel superior — dejé el
  comentario al respecto en el propio archivo).
- Si en el futuro hay acceso a PyPI: `pip install -r backend/tests/requirements.txt`
  habilita `pytest` (mismo resultado, mejor output) y `coverage`/`pytest-cov`
  para métricas de cobertura por línea — no pude generarlas en este entorno
  por la misma razón de red (ver §2).

El script manual `tests/smoke_test_ia.py` (preexistente, no forma parte de
la suite que escribí) sigue siendo la única forma de validar contra
DeepSeek real; ver `docs/DOCUMENTACION_TECNICA.md` §7 para cómo correrlo.

---

## 7. Deuda y próximos pasos

- **Frontend sin tests.** No hay Vitest/Jest/Testing Library configurado en
  `frontend/package.json`. Dada la cantidad de lógica ya presente en
  `Listado.tsx` (favoritos/ocultar en `localStorage`), `FormularioIdea.tsx`
  (validación antes de evaluar) y `apiClient.js` (normalización de los dos
  formatos de error), sería el siguiente candidato natural: `apiClient.js`
  en particular es lógica pura fácil de testear con Vitest sin necesitar DOM.
- **Sin CI configurado.** La suite corre en <1s; es una candidata inmediata
  para un workflow de GitHub Actions que la corra en cada PR. No lo agregué
  acá por estar fuera del alcance que me pidieron ("agregar pruebas y
  documentarlas"), pero es el paso obvio siguiente.
- **Sin métricas de cobertura por línea.** Ver §2/§6 — bloqueado por la
  misma limitación de red de este entorno, no por decisión de diseño mía. La
  matriz de §4 es una cobertura funcional (qué comportamiento está probado),
  no un porcentaje de líneas.
- **`main.py` (los `@app.exception_handler`) se prueba indirectamente.** Los
  tests de `test_endpoints_evaluar.py` verifican el status HTTP y el cuerpo
  JSON final, que es lo que le importa a un consumidor de la API — pero no
  escribí un test que importe y llame a los handlers de `main.py` de forma
  aislada. Lo consideré innecesario: probarlos vía HTTP es más representativo
  del contrato real y ya los ejercita a todos.
- **Migraciones probadas contra un esquema sintético, no contra el histórico
  real.** En `test_migraciones.py` armé a mano una tabla "vieja" mínima; no
  reproduce la secuencia exacta de esquemas por los que pasó `evaluador.db`
  en desarrollo. Me pareció una simplificación razonable dado que
  `aplicar_migraciones` es puramente aditiva y su lógica no depende de esa
  historia.
