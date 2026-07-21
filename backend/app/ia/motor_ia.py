from __future__ import annotations

from app.ia.cliente_ia import generar_evaluacion
from app.ia.excepciones import (
    FormatoInesperado,
    LimiteTokensError,
    MotorIAError,
    ProveedorIAError,
    RespuestaInvalidaIA,
)
from app.ia.prompts import SYSTEM_PROMPT, construir_datos_idea
from app.schemas.evaluacion import ResultadoMotorIA

# Re-exportadas para que el backend (main.py) las importe desde el motor.
__all__ = [
    "evaluar_idea",
    "FormatoInesperado",
    "LimiteTokensError",
    "MotorIAError",
    "ProveedorIAError",
    "RespuestaInvalidaIA",
]


def evaluar_idea(idea: dict) -> ResultadoMotorIA:
    """Evalúa una Idea (4.1) y devuelve el resultado completo (sección 6, v1.2).

    Arma el prompt (system estático + datos variables), llama al proveedor de IA
    vía el cliente, y devuelve la evaluación validada junto con la traza (prompt,
    respuesta cruda, modelo, consumo de tokens). Las excepciones tipadas del
    cliente suben tal cual; el backend las mapea al Error del contrato 4.6.
    """
    datos_idea = construir_datos_idea(idea)
    return generar_evaluacion(SYSTEM_PROMPT, datos_idea)
