from __future__ import annotations

import json

from app.ia.motor_ia import evaluar_idea
from app.ia.excepciones import MotorIAError
from app.ia.prompts import PROMPT_VERSION
from app.core.config import settings

# Idea de ejemplo (contrato 4.1). Parte de los campos van vacíos a propósito,
# para ver que el modelo los manda a preguntas_aclaracion y no los inventa.
idea = {
    "nombre": "TutorLocal",
    "descripcion": "Plataforma que conecta estudiantes de secundaria con tutores universitarios para clases de refuerzo.",
    "problema": "A los estudiantes les cuesta encontrar tutores confiables y accesibles.",
    "publico_objetivo": "Padres de estudiantes de secundaria de clase media en San Salvador.",
    "propuesta_valor": "Tutores verificados, agenda flexible y precio accesible por hora.",
    "sector": "EdTech",
    "pais_mercado": "El Salvador",
}

print(f"DEBUG - Llave en uso: {settings.IA_API_KEY[:5]}...{settings.IA_API_KEY[-4:]}")

try:
    res = evaluar_idea(idea)
    print(f"OK  |  prompt: {PROMPT_VERSION}  |  modelo: {res.modelo_ia}")
    print(f"semaforo: {res.evaluacion.semaforo.value}")
    print(f"preguntas_aclaracion: {len(res.evaluacion.preguntas_aclaracion)}")
    print("\n--- EvaluacionIA validada (contrato 4.2) ---")
    print(json.dumps(res.evaluacion.model_dump(), ensure_ascii=False, indent=2))
    print("\n--- respuesta cruda (primeros 300 chars, para el PromptLog 4.4) ---")
    print(res.respuesta_cruda[:300])
except MotorIAError as e:
    # Fallo controlado: el mapeo funcionó. Esto también es un resultado válido de prueba.
    print(f"FALLO CONTROLADO  |  codigo: {e.codigo}  |  {e.mensaje}")
except Exception as e:  # noqa: BLE001
    # Fallo NO controlado: algo se escapó del mapeo. Anotalo, es un bug a corregir.
    print(f"FALLO NO CONTROLADO ({type(e).__name__}): {e}")