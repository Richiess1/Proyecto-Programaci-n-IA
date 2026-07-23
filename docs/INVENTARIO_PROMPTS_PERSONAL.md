# Inventario de Prompts — Evidencia Individual

**Autor(a):** Marjorie Monson

**Qué es este documento.** El inventario de **los prompts que diseñé y usé
con el asistente de IA (Claude Code) para producir mi propia parte del
proyecto**: la suite de pruebas automatizadas y su documentación, la
documentación técnica, y el manual de usuario — la evidencia que pide la
rúbrica en "Evidencia individual" (*"prompts [...] realizados"*) y que
sostiene mi participación en "Calidad del prompting".

Cada prompt sigue la metodología **C-O-S-T-A-R** (Contexto, Objetivo,
Estilo, Tono, Audiencia, Respuesta), para dejar explícito antes de ejecutar
cada tarea qué necesitaba, con qué restricciones, para quién y en qué
formato de salida.

---

## Prompt 1 — Diagnóstico de entorno y elección de herramientas de testing

| Campo | Detalle |
|---|---|
| **Objetivo** | Decidir con qué framework y estrategia de aislamiento construir la suite, verificando de verdad qué herramientas están disponibles en el entorno real (no asumirlo), y resolver cualquier cambio mínimo de producción necesario para que el backend sea testeable. |
| **Versión** | v1.0 |
| **Entrada esperada** | Estado real del backend (sin ninguna suite automatizada, solo `tests/smoke_test_ia.py` manual) y del entorno de desarrollo (disponibilidad real de red/PyPI, sin asumirla). |
| **Salida esperada** | Una decisión de herramientas justificada (framework de test, cliente HTTP, aislamiento de base de datos) y, si hacía falta, un cambio mínimo y retrocompatible en el código de producción para habilitarlo. |
| **Controles aplicados** | Exigir verificación empírica de la disponibilidad de cada herramienta antes de asumirla; exigir que cualquier cambio de código de producción para habilitar tests sea backward-compatible (el comportamiento por defecto no cambia). |

### Prompt (metodología C-O-S-T-A-R)

```
# Contexto (C)
El backend de Evaluador de Ideas no tiene ninguna suite de pruebas
automatizada, solo `tests/smoke_test_ia.py`, que llama a DeepSeek real y
gasta tokens. Antes de escribir un solo test necesito saber con qué
herramientas cuento de verdad en este entorno, no asumirlo de entrada.

# Objetivo (O)
Diagnosticá qué herramientas de testing están realmente disponibles —
probá la instalación en vez de asumir que va a funcionar— y definí la
estrategia de aislamiento: cómo evitar llamadas reales a DeepSeek durante
los tests y cómo evitar tocar `backend/evaluador.db` (la base de
desarrollo). Si hace falta un cambio mínimo en el código de producción para
que esto sea posible, hacelo, pero que sea retrocompatible: el
comportamiento por defecto del sistema no puede cambiar.

# Estilo (S)
Decisión documentada con su justificación, no un simple "usé X". Si la
herramienta ideal no está disponible, explicá la alternativa elegida y por
qué es equivalente en garantías.

# Tono (T)
Pragmático — priorizá que la suite funcione y sea confiable en este entorno
real, no la opción "de manual" si no es viable acá.

# Audiencia (A)
Yo mismo/a más adelante (mantenimiento de la suite) y cualquier evaluador
que solo va a correr un comando y necesita que simplemente funcione, sin
configuración adicional de su parte.

# Respuesta (R)
Un módulo de infraestructura común (`tests/testing_setup.py`) que fije las
variables de entorno necesarias ANTES de importar la aplicación, el cambio
de producción documentado y justificado (`app/db/session.py`), y una
justificación corta y explícita de la elección de herramientas.
```

---

## Prompt 2 — Pruebas unitarias del motor de IA y piezas puras

| Campo | Detalle |
|---|---|
| **Objetivo** | Cubrir con tests aislados (sin red) cada pieza pura del subsistema de IA: guardia de completitud, construcción del prompt, jerarquía de excepciones, hash de deduplicación, orquestación del motor, cliente HTTP hacia el proveedor, y migraciones de base de datos. |
| **Versión** | v1.0 |
| **Entrada esperada** | Los módulos `ia/completitud.py`, `ia/prompts.py`, `ia/excepciones.py`, `services/evaluacion_service._hash_idea`, `ia/motor_ia.py`, `ia/cliente_ia.py`, `db/migraciones.py`, con la infraestructura de aislamiento del Prompt 1 ya disponible. |
| **Salida esperada** | Un archivo de test por módulo, cada uno cubriendo casos límite reales (no solo el camino feliz): idea incompleta que jamás debe llamar a la IA, mapeo completo de errores del proveedor usando las excepciones reales del SDK, y bordes de formato (JSON vacío, truncado, inválido). |
| **Controles aplicados** | Exigir un test explícito que verifique con `assert_not_called()` que una idea incompleta nunca dispara una llamada a la IA (no alcanza con que no truene); exigir simular los errores del proveedor con las clases de excepción REALES del SDK de OpenAI, no con dobles simplificados, para confirmar que el `except` de producción realmente las atrapa; exigir cobertura explícita de cada borde de formato de respuesta. |

### Prompt (metodología C-O-S-T-A-R)

```
# Contexto (C)
Ya está definida la infraestructura de testing (Prompt 1). Ahora hay que
probar el subsistema de IA del backend: `ia/completitud.py` (guardia de
costo), `ia/prompts.py` (construcción del prompt), `ia/excepciones.py`
(códigos de error), `services/evaluacion_service._hash_idea`
(deduplicación), `ia/motor_ia.py` (orquestación) y `ia/cliente_ia.py`
(llamada real al proveedor), más `db/migraciones.py`.

# Objetivo (O)
Escribí tests unitarios que aíslen cada pieza sin llamar nunca a DeepSeek
de verdad. El caso más importante: probá explícitamente que una idea
incompleta NUNCA dispara una llamada al cliente de IA — verificalo con un
mock y `assert_not_called()`, no solo comprobando que no truene. Para
`cliente_ia.py`, simulá TODAS las excepciones reales que el SDK de OpenAI
puede lanzar (`RateLimitError`, `APIStatusError` en distintos status codes,
`APIConnectionError`, `APIError` genérico) usando las clases reales del
SDK, no excepciones inventadas, para confirmar que el `except` de
producción realmente las captura y las mapea bien.

# Estilo (S)
Un archivo de test por módulo, con nombres de test en español que digan
exactamente qué comportamiento verifican (nada de `test_1` o `test_ok`).
Casos límite explícitos y nombrados: respuesta vacía, `None`, no
parseable como JSON, truncada por límite de tokens, que no cumple el
contrato de salida.

# Tono (T)
Exhaustivo en los casos negativos — un motor de IA falla de más formas que
las que tiene éxito, y son esas fallas las que rompen la experiencia del
usuario si no están bien mapeadas.

# Audiencia (A)
Un futuro desarrollador que modifique `cliente_ia.py` o `motor_ia.py` y
necesite saber, con solo correr la suite, si rompió algún mapeo de error o
la guardia de costo.

# Respuesta (R)
`test_completitud.py`, `test_prompts.py`, `test_excepciones.py`,
`test_service_hash.py`, `test_motor_ia.py`, `test_cliente_ia.py` y
`test_migraciones.py` — cada uno corriendo en milisegundos, sin red ni base
de datos real.
```

---

## Prompt 3 — Pruebas de integración de los endpoints HTTP

| Campo | Detalle |
|---|---|
| **Objetivo** | Probar los 7 endpoints reales de la API end-to-end contra una base de datos SQLite temporal, con énfasis en el flujo completo de evaluación, su deduplicación, y el mapeo exacto de errores al contrato 4.6. |
| **Versión** | v1.0 |
| **Entrada esperada** | Los módulos `api/endpoints.py`, `services/evaluacion_service.py` y `schemas/evaluacion.py`, ya cubiertos a nivel unitario en el Prompt 2, más la infraestructura de aislamiento del Prompt 1. |
| **Salida esperada** | Tests de integración por endpoint (o grupo de endpoints relacionados), verificando deduplicación por conteo real de llamadas al mock del motor de IA, y el cuerpo completo de cada respuesta de error, no solo su status HTTP. |
| **Controles aplicados** | Exigir verificar el cuerpo completo de la respuesta de error (`{"error": {"codigo", "mensaje"}}`), no solo el status code; exigir un test que confirme que un error del proveedor de IA no deja una evaluación a medias persistida en la base de datos; exigir que la deduplicación se verifique contando llamadas al mock, no solo comparando resultados. |

### Prompt (metodología C-O-S-T-A-R)

```
# Contexto (C)
Con las piezas del subsistema de IA ya probadas por separado (Prompt 2),
ahora hay que probar los endpoints HTTP reales: `POST/GET /ideas`,
`POST /ideas/{id}/evaluar`, `GET /ideas/{id}/evaluaciones`,
`PATCH /evaluaciones/{id}/estado`, `POST /comparar`.

# Objetivo (O)
Usá el TestClient de FastAPI contra la base de datos SQLite temporal para
probar cada endpoint de punta a punta. En `/evaluar`, cubrí especialmente
la deduplicación: reevaluar la misma idea sin cambios NO debe volver a
llamar al motor de IA (comprobalo contando las llamadas al mock, no solo
comparando el resultado devuelto); dos ideas con contenido idéntico deben
compartir el resultado sin una segunda llamada; cambiar el contenido debe
invalidar la caché y forzar una llamada nueva. Para cada uno de los 4
errores posibles de IA, verificá el status HTTP exacto Y el cuerpo de error
completo, no solo el código de estado.

# Estilo (S)
Un archivo de test por endpoint o grupo de endpoints relacionados,
reutilizando un caso base común (`ApiTestCase`) para no repetir el setup de
la base de datos temporal en cada archivo.

# Tono (T)
Estricto con el contrato de error — el frontend decide su UI según
`error.codigo`, así que un test que solo mire el status HTTP y no el
código específico deja pasar bugs reales de integración.

# Audiencia (A)
El equipo de frontend, que confía en que `error.codigo` siempre llega en
el formato documentado en `backend/README-FRONTEND.md`.

# Respuesta (R)
`test_endpoints_ideas.py`, `test_endpoints_evaluar.py`,
`test_endpoints_estado.py` y `test_endpoints_comparar.py`, con la garantía
adicional de que un error del proveedor de IA nunca persiste una
evaluación a medias en la base de datos.
```

---

## Prompt 4 — Verificación de comportamiento y reporte de hallazgos

| Campo | Detalle |
|---|---|
| **Objetivo** | Detectar, durante la escritura de los tests de integración, cualquier comportamiento real del sistema que no coincidiera con lo documentado o lo esperado — y reportarlo con evidencia, sin corregirlo a ciegas. |
| **Versión** | v1.0 |
| **Entrada esperada** | Los tests de los Prompts 2 y 3 ya escritos y corridos contra el código real del backend. |
| **Salida esperada** | Hallazgos documentados con evidencia reproducible (archivo, línea, un test dedicado que lo demuestre), gravedad estimada, y una recomendación concreta — nunca un cambio de comportamiento aplicado sin aviso. |
| **Controles aplicados** | Prohibición explícita de "arreglar" un comportamiento inesperado del código de producción sin señalarlo primero; exigir que cada hallazgo cite el archivo y la línea responsable; exigir una recomendación concreta, no solo la queja. |

### Prompt (metodología C-O-S-T-A-R)

```
# Contexto (C)
Al escribir los tests de los Prompts 2 y 3 aparecieron comportamientos del
sistema que no estaban documentados en `DOCUMENTACION_TECNICA.md` ni eran
evidentes con una lectura superficial del código.

# Objetivo (O)
Si encontrás un comportamiento real que se aparte de lo esperado —por
ejemplo, una validación que falta, o un orden de datos que depende de una
casualidad del motor de base de datos en vez de una regla explícita— NO lo
corrijas sin avisarme antes. Escribí un test que documente el
comportamiento actual tal cual es, y reportalo como hallazgo: archivo y
línea exacta, por qué ocurre, qué tan grave es, y una recomendación.

# Estilo (S)
Directo, con evidencia de código citada (ruta y línea), sin exagerar la
gravedad ni minimizarla.

# Tono (T)
Honesto — si algo no es un bug bloqueante, decilo con esa misma
proporción, pero tampoco lo escondas de la documentación.

# Audiencia (A)
El equipo completo del proyecto, que tiene que decidir conscientemente si
ese comportamiento es aceptable o si hace falta un commit aparte para
corregirlo.

# Respuesta (R)
Una sección "Hallazgos" en la documentación de pruebas, con un test
dedicado por cada hallazgo que sirve como evidencia reproducible del
comportamiento observado.
```

---

## Prompt 5 — Documentación de pruebas a nivel senior

| Campo | Detalle |
|---|---|
| **Objetivo** | Documentar la suite completa (alcance, herramientas, estrategia, cobertura, hallazgos, cómo correrla, deuda pendiente) como un reporte técnico verificable, no como una lista plana de "qué se probó". |
| **Versión** | v1.0 |
| **Entrada esperada** | La suite completa ya escrita y corrida (Prompts 1 a 4), con su salida real de ejecución disponible. |
| **Salida esperada** | `docs/PRUEBAS.md`, con una matriz de cobertura módulo→archivo de test→qué cubre, resultados reales de la corrida pegados como evidencia (no proyectados), y una sección de deuda pendiente sin maquillar. |
| **Controles aplicados** | Exigir pegar la salida REAL de la corrida de la suite (número de tests, tiempo, resultado) como evidencia, nunca un número estimado; exigir declarar explícitamente qué no se pudo lograr (cobertura por línea, tests de frontend, CI) en vez de omitirlo. |

### Prompt (metodología C-O-S-T-A-R)

```
# Contexto (C)
La suite completa (Prompts 1 a 4) ya está escrita y corre en verde. Ahora
hace falta el entregable de documentación de pruebas que pide la rúbrica
del proyecto, a nivel senior.

# Objetivo (O)
Documentá la suite completa: alcance y objetivo priorizado por riesgo de
negocio, herramientas usadas y por qué (incluido el motivo real detrás de
cualquier decisión de herramientas), la estrategia de aislamiento
explicada con su razón de ser, una matriz de cobertura por archivo de test
con el número real de casos y qué cubre cada uno, los hallazgos de
comportamiento detectados, instrucciones paso a paso de cómo correr la
suite, y qué queda como deuda pendiente sin esconderlo.

# Estilo (S)
Formato de reporte técnico con tablas, no prosa suelta. La matriz de
cobertura tiene que ser exhaustiva: un renglón por archivo de test, con su
conteo real de casos.

# Tono (T)
Riguroso y verificable — cada número que aparezca en el documento (cantidad
de tests, tiempo de ejecución) tiene que salir de correr la suite de
verdad, nunca de una estimación.

# Audiencia (A)
Un evaluador académico calificando la calidad del código y las pruebas del
proyecto, y cualquier desarrollador que necesite confiar en la suite antes
de modificar el backend.

# Respuesta (R)
`docs/PRUEBAS.md`, con la salida real de la corrida final de la suite
pegada como evidencia desde el principio del documento.
```

---

## Prompt 6 — Documentación Técnica

| Campo | Detalle |
|---|---|
| **Objetivo** | Generar la documentación técnica completa del proyecto (arquitectura, componentes, servicios, integración con IA, configuración, dependencias, decisiones técnicas) a partir de la lectura real del código, no de suposiciones. |
| **Versión** | v1.0 |
| **Entrada esperada** | Acceso de lectura al repositorio completo (backend + frontend); ningún dato inventado — todo derivado de archivos reales. |
| **Salida esperada** | Un documento Markdown estructurado en secciones fijas, con tablas, ejemplos de código citados con ruta y número de línea, y una sección explícita de "decisiones técnicas" con su justificación. |
| **Controles aplicados** | Verificación de código fuente antes de documentar cada afirmación (no aceptar el primer resultado sin leer los archivos reales); prohibición implícita de inventar versiones de dependencias (se listaron las realmente instaladas vía `pip list`); estructura fija para que sea comparable con la Documentación Funcional. |

### Prompt (metodología C-O-S-T-A-R)

```
# Contexto (C)
Repositorio "Proyecto-Programación-IA" (Evaluador de Ideas): backend en
FastAPI + SQLAlchemy + SQLite, integración con DeepSeek vía SDK de OpenAI,
frontend en React + Vite + TypeScript + Tailwind.

# Objetivo (O)
Escribí la Documentación Técnica del proyecto para el entregable académico
de la rúbrica de "Introducción a la Programación con IA". Debe cubrir,
como mínimo: arquitectura, componentes, servicios, integración con IA,
configuración, dependencias y decisiones técnicas — basado ÚNICAMENTE en
código leído de verdad, nunca en suposiciones genéricas de "cómo suele ser"
un proyecto FastAPI+React.

# Estilo (S)
Técnico, denso en información, con tablas para specs (endpoints, variables
de entorno, dependencias) y diagramas simples en texto para el flujo de
datos. Cada decisión técnica debe llevar su "por qué", no solo el "qué".

# Tono (T)
Profesional, directo, sin relleno de marketing ni frases genéricas tipo
"este proyecto sigue las mejores prácticas". Si algo es una limitación o
una decisión discutible, decilo explícitamente.

# Audiencia (A)
Un evaluador académico que va a leer esto para calificar la rúbrica de
"Arquitectura, diseño técnico y calidad del código" (12%) y "Documentación"
(5%), y un futuro desarrollador que necesite entender el sistema sin haber
hablado con el equipo.

# Respuesta (R)
Un archivo Markdown (`docs/DOCUMENTACION_TECNICA.md`) con estas secciones
fijas: (1) descripción general y diagrama de alto nivel, (2) arquitectura
backend y frontend, (3) componentes principales, (4) integración con IA
—diseño del prompt, contrato de salida, deduplicación, trazabilidad, manejo
de errores—, (5) configuración (variables de entorno de ambos lados), (6)
dependencias con versiones reales instaladas, (7) cómo correr todo
localmente, (8) decisiones técnicas con su justificación.
```

---

## Prompt 7 — Documentación Funcional / Manual de Usuario

| Campo | Detalle |
|---|---|
| **Objetivo** | Producir el manual de usuario / documentación funcional: qué problema resuelve el sistema, quién lo usa, qué puede hacer, cómo se usa paso a paso, y qué entra/sale de cada funcionalidad. |
| **Versión** | v1.0 |
| **Entrada esperada** | Las mismas fuentes que el Prompt 6 (código real), pero leídas desde la perspectiva del usuario final, no del desarrollador: pantallas del frontend, mensajes de error mostrados al usuario, límites de los campos del formulario. |
| **Salida esperada** | Documento Markdown en lenguaje no técnico, organizado por flujo de uso (no por módulo de código), con tablas de entradas/salidas y una sección de restricciones que el usuario debería conocer antes de usar el sistema. |
| **Controles aplicados** | Separación estricta de audiencia respecto al Prompt 6 (nada de jerga de FastAPI/SQLAlchemy acá); cada límite de campo (`max_length`, mínimos de caracteres) se tradujo a lenguaje de usuario, no se copió el nombre de la validación técnica. |

### Prompt (metodología C-O-S-T-A-R)

```
# Contexto (C)
Mismo proyecto que el Prompt 6 (Evaluador de Ideas), pero ahora necesito
el entregable "Documentación funcional o manual de usuario" de la rúbrica,
que es un documento distinto y para una audiencia distinta: no técnica.

# Objetivo (O)
Documentá: la descripción del problema que resuelve el sistema, los
usuarios (perfiles, no roles de código), las funcionalidades disponibles,
los pasos de uso de cada flujo (registrar idea, evaluar, comparar, cambiar
estado), y las entradas/salidas/restricciones de cada una — todo verificado
contra el comportamiento real de la UI y de la API, no inventado.

# Estilo (S)
Narrativo y por pasos numerados donde aplique, con tablas solo para datos
tabulares de verdad (campos de entrada, límites de caracteres). Nada de
nombres de funciones, clases o archivos de código.

# Tono (T)
Claro y directo, como si le explicaras el sistema a alguien que lo va a
usar mañana sin haber visto una línea de código. Nada de tecnicismos
innecesarios.

# Audiencia (A)
Dos lectores: (1) un evaluador académico calificando "Solución efectiva
del sistema" (10%) y "Calidad funcional y experiencia de usuario" (6%), y
(2) un usuario real (persona emprendedora) que quiera entender qué puede
hacer la herramienta antes de usarla.

# Respuesta (R)
Un archivo Markdown (`docs/MANUAL_USUARIO.md`) con: (1) descripción del
problema, (2) perfiles de usuario, (3) tabla de funcionalidades, (4) pasos
de uso por flujo, (5) tabla de entradas con límites, (6) tabla de salidas
del diagnóstico de IA, (7) restricciones y comportamientos a tener en
cuenta (qué hace el sistema si faltan datos, qué errores puede mostrar y
qué significan).
```
