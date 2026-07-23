# Manual de usuario — Evaluador de Ideas

**Autor(a):** Marjorie Monson

Escribí este manual probando la aplicación de punta a punta —cada flujo,
pantalla, límite de campo y mensaje de error que describo abajo lo verifiqué
usando la app real, no lo asumí a partir del código. La intención es que
cualquier persona pueda entender qué hace el sistema y cómo usarlo sin haber
visto una línea de código.

## 1. Descripción del problema

Una persona con una idea de negocio en etapa temprana normalmente no tiene
forma rápida ni objetiva de saber si esa idea "se sostiene": si el problema es
real, si el cliente está bien definido, si hay diferenciación frente a lo que
ya existe, o qué le falta validar antes de invertir tiempo o dinero. Pedir esa
retroalimentación a un mentor o consultor toma tiempo y no siempre está
disponible.

**Evaluador de Ideas** resuelve esto dándole a la persona un diagnóstico
inmediato y estructurado (tipo consultoría) generado por inteligencia
artificial: qué tan viable es la idea (semáforo verde/amarillo/rojo), un
análisis FODA, los riesgos y supuestos más críticos, preguntas puntuales sobre
lo que falta definir, y un plan concreto de cómo validarla en la práctica.
También permite comparar varias ideas entre sí para decidir en cuál enfocarse.

## 2. Usuarios

- **Persona emprendedora / estudiante**, con o sin formación en negocios, que
  quiere validar una idea antes de desarrollarla. Es el usuario principal: usa
  el formulario de registro y lee el diagnóstico.
- **Equipo o mentor** que gestiona varias ideas (propias o de terceros) y
  necesita compararlas para priorizar en cuáles invertir esfuerzo — usa la
  pantalla de comparación y el cambio de estado (pendiente/aceptado/descartado)
  como seguimiento simple.

No hay roles ni permisos diferenciados: el sistema no tiene login, así que
cualquier persona con acceso a la app ve y gestiona todas las ideas cargadas.

## 3. Funcionalidades

| # | Funcionalidad | Dónde |
|---|---|---|
| 1 | Registrar una idea de negocio | Pantalla "Registro" (`/registro`) |
| 2 | Evaluar una idea con IA | Botón "Guardar y evaluar" (Registro) o desde el Detalle |
| 3 | Ver el listado de todas las ideas registradas | Pantalla "Ideas" (`/`) |
| 4 | Buscar ideas por nombre, sector o descripción | Buscador en el Listado |
| 5 | Marcar una idea como favorita | Ícono ★ en el Listado (solo en tu navegador) |
| 6 | Ocultar una idea del listado | Ícono ✕ en el Listado (solo en tu navegador, no la borra del servidor) |
| 7 | Ver el diagnóstico completo de una idea evaluada | Pantalla "Detalle" (`/ideas/:id`) |
| 8 | Cambiar el estado de una evaluación | Selector en el Detalle (pendiente / aceptado / descartado) |
| 9 | Comparar varias ideas evaluadas entre sí | Pantalla "Comparación" (`/comparar`) |

## 4. Pasos de uso

### 4.1 Registrar y evaluar una idea

1. Desde cualquier pantalla, hacé clic en **"+ Nueva idea"** (barra lateral o
   botón del Listado). Se abre el formulario de Registro.
2. Completá los **5 campos obligatorios** (columna izquierda, marcados
   "OBLIGATORIO"):
   - Nombre
   - Descripción
   - Problema (qué problema resuelve)
   - Público objetivo (quién es el cliente)
   - Propuesta de valor (por qué te elegirían)
3. Opcionalmente, completá los **campos complementarios** (columna derecha):
   contexto inicial, sector, país/mercado, tipo de cliente, canales, recursos
   disponibles, restricciones, competencia conocida. Cuantos más completes, más
   preciso será el diagnóstico — los campos vacíos se marcan como "sin
   información" y el sistema te preguntará por ellos en vez de inventarlos.
4. Elegí una de las dos acciones:
   - **"Guardar sin evaluar"** → la idea queda registrada en el Listado, sin
     diagnóstico. Podés evaluarla más tarde desde el Detalle.
   - **"Guardar y evaluar"** → guarda la idea y de inmediato la manda a
     evaluar con IA. Aparece un loader ("Evaluando con IA... esto puede tomar
     de 10 a 20 segundos") y al terminar te lleva directo al Detalle con el
     resultado.

### 4.2 Ver el listado de ideas

- La pantalla principal (`/`) muestra todas las ideas registradas, cada una
  con: nombre, sector, descripción breve, semáforo (si ya fue evaluada),
  versión y fecha de la última evaluación, y estado (pendiente / aceptado /
  descartado).
- Usá el buscador para filtrar por nombre, sector o texto de la descripción.
- Hacé clic en una idea para ir a su Detalle.
- El ícono ★ marca/desmarca una idea como favorita; el ícono ✕ la oculta de tu
  listado. **Ambas acciones son solo locales a tu navegador** — no afectan lo
  que ven otras personas ni borran nada del servidor.

### 4.3 Leer el diagnóstico de una idea

Al entrar al Detalle de una idea evaluada, vas a ver, en este orden:

1. **Ficha de la idea**: los datos que cargaste (descripción, problema,
   público objetivo, propuesta de valor).
2. **Diagnóstico**: el semáforo, su justificación en 1-2 frases, y una lectura
   general de la idea.
3. **FODA**: fortalezas, debilidades, oportunidades y amenazas específicas de
   tu idea.
4. **Riesgos** y **Supuestos críticos**: qué podría hacer fracasar la idea si
   resulta falso o no se maneja bien.
5. **Propuesta de valor mejorada**: una reescritura más fuerte de tu propuesta
   original, sugerida por el modelo.
6. **Preguntas de aclaración** (si aplica): qué información falta para un
   diagnóstico más sólido. Si no aparece esta sección, es porque la idea traía
   suficiente información.
7. **Plan de validación**: pasos concretos (entrevistas, encuestas, MVP,
   análisis de competencia, etc.) con una métrica de éxito para cada uno.

Desde ahí también podés **cambiar el estado** de la evaluación (selector junto
a la fecha): `pendiente` → `aceptado` o `descartado`, según lo que decidas
hacer con la idea.

### 4.4 Comparar ideas

1. Andá a **"Comparar ideas"** en la barra lateral.
2. Hacé clic en **"+ Agregar idea"** y elegí, una por una, las ideas que
   querés comparar (solo aparecen las que ya tienen al menos una evaluación).
3. Cada idea agregada se muestra como una tarjeta con su semáforo y una
   valoración (Fuerte / Moderado / Débil) por cada uno de los 7 criterios:
   problema, mercado, cliente, diferenciación, riesgos, monetización y
   factibilidad.
4. Podés quitar una idea de la comparación con la ✕ en su chip.

## 5. Entradas y salidas

### 5.1 Entradas (lo que carga el usuario)

| Campo | Obligatorio | Límite | Descripción |
|---|---|---|---|
| Nombre | Sí | 120 caracteres | Nombre de la idea |
| Descripción | Sí | 3000 caracteres | Resumen de la idea |
| Problema | Sí | 3000 caracteres | Qué problema resuelve |
| Público objetivo | Sí | 1500 caracteres | Quién es el cliente/usuario |
| Propuesta de valor | Sí | 3000 caracteres | Por qué te elegirían |
| Contexto inicial | No | 3000 caracteres | Origen de la idea |
| Sector | No | 200 caracteres | Ej. EdTech, Fintech, Retail |
| País / mercado | No | 200 caracteres | Ej. El Salvador |
| Tipo de cliente | No | 500 caracteres | Ej. B2C, B2B, B2G |
| Canales | No | 1000 caracteres | Cómo se llega al cliente |
| Recursos disponibles | No | 2000 caracteres | Equipo, capital, activos |
| Restricciones | No | 2000 caracteres | Regulaciones, límites conocidos |
| Competencia conocida | No | 2000 caracteres | Alternativas existentes |

Además de ser obligatorios, los 5 primeros campos deben tener **contenido
real y de largo mínimo** para poder evaluarse (ver §6, restricciones) — no
basta con que no estén vacíos.

### 5.2 Salidas (lo que devuelve el diagnóstico)

| Salida | Descripción |
|---|---|
| Semáforo | Verde, amarillo o rojo, según la solidez del núcleo de la idea |
| Justificación del semáforo | 1-2 frases explicando el color asignado |
| Diagnóstico | Lectura general en prosa |
| FODA | Listas de fortalezas, debilidades, oportunidades y amenazas |
| Supuestos críticos | Lo que, si resulta falso, hunde la idea |
| Riesgos | Riesgos concretos identificados |
| Propuesta de valor mejorada | Reescritura sugerida, más fuerte que la original |
| Preguntas de aclaración | Qué falta definir (vacío si la idea ya trae suficiente) |
| Plan de validación | Pasos accionables, cada uno con tipo, descripción y métrica de éxito |
| Criterios evaluados | Una valoración por cada uno de los 7 criterios (problema, mercado, cliente, diferenciación, riesgos, monetización, factibilidad) |

## 6. Restricciones y comportamientos a tener en cuenta

- **La IA nunca inventa datos.** Si un campo queda vacío o es muy breve, el
  sistema lo refleja en "Preguntas de aclaración" en vez de asumir cifras,
  competidores o tamaños de mercado que no proporcionaste.
- **Mínimos de contenido para evaluar:** aunque un campo obligatorio no esté
  vacío, si es demasiado corto la evaluación se rechaza (error "entrada
  incompleta") y te dice exactamente qué campo ampliar. Esto evita gastar el
  análisis en una idea sin sustancia.
- **La evaluación tarda entre 10 y 20 segundos** la primera vez (llamada real
  al modelo de IA). Si volvés a evaluar exactamente el mismo contenido, la
  respuesta es instantánea (se reutiliza el resultado anterior, no se vuelve a
  gastar el análisis).
- **El semáforo no baja solo por falta de datos opcionales.** Una idea con
  núcleo sólido (problema real, cliente y mercado identificables,
  diferenciación plausible) puede salir "verde" aunque le falten datos — esos
  vacíos van a las preguntas de aclaración, no bajan el color por sí solos. El
  color baja cuando hay una debilidad de fondo real (amarillo) o una falla que
  hace inviable la idea tal como está (rojo).
- **Favoritos y ocultar ideas son solo de tu navegador.** No se sincronizan
  entre dispositivos ni afectan lo que ven otras personas que usan la misma
  app; tampoco borran la idea del sistema.
- **No hay usuarios ni permisos.** Cualquiera con acceso a la aplicación puede
  ver, evaluar y cambiar el estado de cualquier idea registrada.
- **Solo se pueden comparar ideas ya evaluadas.** Una idea sin evaluación no
  aparece como opción en la pantalla de Comparación.
- **Errores posibles al evaluar:**
  - *"La idea no tiene información suficiente..."* → completá o ampliá los
    campos que te indica el mensaje.
  - *"Servicio saturado, intentá en unos minutos"* → límite temporal del
    proveedor de IA; reintentá más tarde.
  - *"No disponible por ahora, reintentá"* → problema de conexión con el
    proveedor de IA; reintentá.
  - Error de formato / respuesta inválida → problema puntual del modelo;
    reintentar suele resolverlo; si persiste, es un caso para reportar a
    soporte técnico.
