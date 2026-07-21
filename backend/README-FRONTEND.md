# Guía de integración para el Front — Evaluador de Ideas API

Todo lo que necesita el equipo de front para conectarse al backend: cómo levantarlo,
los endpoints, los shapes de datos, los errores y el flujo de uso.

---

## 1. Cómo levantar el backend (para desarrollar en local)

Requisitos: Python 3.11+.

```bash
cd backend
python -m venv .venv                # si no existe todavía
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

- **Base URL:** `http://localhost:8000`
- **Docs interactivas (Swagger):** `http://localhost:8000/docs` — podés probar todos los endpoints desde ahí.
- **OpenAPI JSON:** `http://localhost:8000/openapi.json` — útil si querés autogenerar un cliente TypeScript.

> El backend necesita un archivo `backend/.env` con la API key de DeepSeek. Eso ya está
> configurado; el front no maneja claves ni habla con DeepSeek directamente, solo con este backend.

---

## 2. CORS

Ya está habilitado para los orígenes de desarrollo típicos:

- `http://localhost:5173` y `http://127.0.0.1:5173` (Vite)
- `http://localhost:3000` y `http://127.0.0.1:3000` (Create React App)

Si tu front corre en otro puerto/dominio, avisá para agregarlo en
`backend/app/core/config.py` (`CORS_ORIGINS`). No hace falta configurar nada del lado del front.

---

## 3. Endpoints

Todos reciben y devuelven **JSON** (`Content-Type: application/json`). No hay autenticación por ahora.

| Método | Ruta | Para qué sirve |
|--------|------|----------------|
| `POST` | `/ideas` | Crear una idea |
| `GET`  | `/ideas` | Listar todas las ideas |
| `GET`  | `/ideas/{idea_id}` | Obtener una idea por id |
| `POST` | `/ideas/{idea_id}/evaluar` | **Evaluar la idea con IA** (paso clave) |
| `GET`  | `/ideas/{idea_id}/evaluaciones` | Listar las evaluaciones de una idea |
| `PATCH`| `/evaluaciones/{evaluacion_id}/estado` | Cambiar el estado de una evaluación |
| `POST` | `/comparar` | Comparar varias ideas ya evaluadas |

---

### 3.1 `POST /ideas` — crear idea

**Body:**

```jsonc
{
  "nombre": "TutorLocal",                                  // obligatorio
  "descripcion": "Plataforma que conecta estudiantes...",  // obligatorio
  "problema": "A los estudiantes les cuesta encontrar...", // obligatorio
  "publico_objetivo": "Padres de secundaria en...",        // obligatorio
  "propuesta_valor": "Tutores verificados, agenda...",     // obligatorio

  // Opcionales (pueden ir vacíos o directamente omitirse):
  "contexto_inicial": "",
  "sector": "EdTech",
  "pais_mercado": "El Salvador",
  "tipo_cliente": "",
  "canales": "",
  "recursos_disponibles": "",
  "restricciones": "",
  "competencia_conocida": ""
}
```

**Respuesta `200`:** la idea creada, ahora **con su `id`** (UUID string). Guardá ese `id`: lo necesitás para evaluar.

```jsonc
{ "id": "40697a15-3e79-460f-b0a8-a02ed7ee0e5c", "nombre": "TutorLocal", ... }
```

> ⚠️ Los 5 campos obligatorios no pueden ir vacíos. Además, para que la **evaluación**
> no sea rechazada más adelante, conviene que tengan contenido real (ver §5, error
> `ENTRADA_INCOMPLETA`). Ideal validar longitudes mínimas también en el formulario.

---

### 3.2 `POST /ideas/{idea_id}/evaluar` — evaluar con IA (el importante)

Sin body. Toma la idea guardada, la manda a la IA y devuelve la evaluación.

- **Tarda ~10–20 segundos** la primera vez (llamada real al modelo). Mostrá un loader.
- Si ya se evaluó **exactamente el mismo contenido** antes, responde **al instante** y
  devuelve la evaluación existente (deduplicación, para no gastar tokens). Es transparente
  para el front: siempre recibís una `Evaluacion` válida.

**Respuesta `200` — objeto `Evaluacion` (contrato 4.3):**

```jsonc
{
  "id": "228424cd-...",          // id de la evaluación
  "idea_id": "40697a15-...",
  "version": 1,
  "fecha": "2026-07-21T18:30:00Z",
  "modelo_ia": "deepseek-chat",
  "estado": "pendiente",
  "resultado": { /* EvaluacionIA, ver §4 */ }
}
```

**Errores posibles:** `422` (idea incompleta), `404` (idea no existe), `429/500/502/503`
(problemas de la IA). Ver §5.

---

### 3.3 `GET /ideas` y `GET /ideas/{idea_id}`

- `GET /ideas` → array de `Idea`.
- `GET /ideas/{idea_id}` → una `Idea`, o `404` si no existe.

### 3.4 `GET /ideas/{idea_id}/evaluaciones`

Array de `Evaluacion` de esa idea (historial). Vacío `[]` si nunca se evaluó.

### 3.5 `PATCH /evaluaciones/{evaluacion_id}/estado`

Cambia el `estado` de una evaluación (ej. marcarla como revisada/archivada).

**Body:**
```json
{ "estado": "revisada" }
```
El `estado` es texto libre (no hay lista cerrada por ahora). Responde la `Evaluacion` actualizada, o `404`.

### 3.6 `POST /comparar` — comparar ideas

**Body:**
```json
{ "idea_ids": ["id-1", "id-2", "id-3"] }
```

**Respuesta `200` — `Comparacion` (contrato 4.5):**
```jsonc
{
  "criterios": ["problema", "mercado", "cliente", "diferenciacion", "riesgos", "monetizacion", "factibilidad"],
  "ideas": [
    {
      "idea_id": "id-1",
      "nombre": "TutorLocal",
      "semaforo": "amarillo",
      "criterios_evaluados": { "problema": "...", "mercado": "...", ... }
    }
  ]
}
```
> Solo aparecen las ideas que **ya tienen al menos una evaluación**. Usa la evaluación más reciente de cada una.

---

## 4. El objeto `resultado` (EvaluacionIA — contrato 4.2)

Es el corazón de lo que mostrás en pantalla. Siempre viene completo y validado:

```jsonc
{
  "semaforo": "verde" | "amarillo" | "rojo",
  "justificacion_semaforo": "string (1-2 frases)",
  "diagnostico": "string (lectura general)",
  "foda": {
    "fortalezas":   ["string", ...],
    "debilidades":  ["string", ...],
    "oportunidades":["string", ...],
    "amenazas":     ["string", ...]
  },
  "supuestos_criticos": ["string", ...],
  "riesgos": ["string", ...],
  "propuesta_valor_mejorada": "string",
  "preguntas_aclaracion": ["string", ...],   // puede venir [] si no falta info
  "plan_validacion": [
    { "tipo": "string", "descripcion": "string", "metrica": "string" }
  ],
  "criterios_evaluados": {
    "problema": "string",
    "mercado": "string",
    "cliente": "string",
    "diferenciacion": "string",
    "riesgos": "string",
    "monetizacion": "string",
    "factibilidad": "string"
  }
}
```

Sugerencias de UI:
- **`semaforo`** → badge de color (verde/amarillo/rojo).
- **`preguntas_aclaracion`** → si trae items, destacarlas: son los datos que faltan para una evaluación más sólida.
- **`plan_validacion`** → lista/tabla de pasos accionables.
- **`criterios_evaluados`** → ideal para una vista comparativa (coincide con `/comparar`).

---

## 5. Manejo de errores

⚠️ **Hay DOS formatos de error distintos.** El front debe contemplar ambos:

### A) Errores de negocio / IA — formato del contrato 4.6

```json
{ "error": { "codigo": "ENTRADA_INCOMPLETA", "mensaje": "texto para mostrar" } }
```

| HTTP | `codigo` | Qué significa | Qué hacer en el front |
|------|----------|----------------|------------------------|
| `422` | `ENTRADA_INCOMPLETA` | La idea no tiene info suficiente; **no se gastó IA** | Mostrar `mensaje` (ya incluye qué campos completar) y volver al formulario |
| `429` | `IA_LIMITE_TOKENS` | Límite del proveedor de IA | "Servicio saturado, intentá en unos minutos" |
| `500` | `FORMATO_INESPERADO` | La IA respondió algo no parseable | Reintentar; si persiste, avisar soporte |
| `502` | `IA_RESPUESTA_INVALIDA` | La IA respondió pero no cumple el contrato | Reintentar |
| `503` | `IA_PROVEEDOR` | Falló la conexión con la IA | "No disponible por ahora, reintentá" |

### B) Errores estándar de FastAPI — formato `detail`

- **`404`** (idea/evaluación no encontrada): `{ "detail": "Idea no encontrada" }`
- **`422`** por validación de campos faltantes al **crear** la idea (`POST /ideas`):
  `{ "detail": [ { "loc": [...], "msg": "...", "type": "..." } ] }`

> Regla práctica: si la respuesta trae `error.codigo` → usá el mensaje de ahí.
> Si trae `detail` → es un 404 o una validación de formulario.

---

## 6. Flujo típico del front (paso a paso)

```
1. Usuario completa el formulario de idea
        │
        ▼
2. POST /ideas               → guardás el "id" que devuelve
        │
        ▼
3. POST /ideas/{id}/evaluar  → loader ~10-20s
        │
        ├── 200 → renderizás "resultado" (semáforo, FODA, plan, etc.)
        ├── 422 ENTRADA_INCOMPLETA → mostrás el mensaje y pedís completar campos
        └── 4xx/5xx IA_* → mensaje de error + botón reintentar
        │
        ▼
4. (opcional) PATCH /evaluaciones/{eval_id}/estado  → marcar como revisada
5. (opcional) POST /comparar  → vista comparativa de varias ideas
```

### Ejemplo mínimo con `fetch`

```js
const API = "http://localhost:8000";

// 1) crear
const idea = await fetch(`${API}/ideas`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(datosDelFormulario),
}).then(r => r.json());

// 2) evaluar
const res = await fetch(`${API}/ideas/${idea.id}/evaluar`, { method: "POST" });
const data = await res.json();

if (res.ok) {
  render(data.resultado);            // EvaluacionIA
} else if (data.error?.codigo === "ENTRADA_INCOMPLETA") {
  mostrarAviso(data.error.mensaje);  // qué campos completar
} else {
  mostrarError(data.error?.mensaje ?? data.detail ?? "Error inesperado");
}
```

---

## 7. Notas

- **Encoding:** todo es UTF-8. Si ves caracteres raros, es la consola, no la API.
- **IDs:** son UUID en formato string.
- **Fechas:** ISO 8601 (`fecha` en las evaluaciones).
- **Persistencia:** SQLite local (`backend/evaluador.db`) en desarrollo. Los datos sobreviven reinicios.
- **Tip:** para generar un cliente TypeScript tipado automáticamente, usá el `/openapi.json` con `openapi-typescript` u `openapi-generator`.

---

Dudas sobre la API → hablar con el equipo de backend. Los contratos (4.1 a 4.6) están en `backend/app/schemas/evaluacion.py`.
