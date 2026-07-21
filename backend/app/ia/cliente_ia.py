from __future__ import annotations

import json

from openai import (
    APIConnectionError,
    APIError,
    APIStatusError,
    OpenAI,
    RateLimitError,
)
from pydantic import ValidationError

from app.core.config import settings
from app.ia.excepciones import (
    FormatoInesperado,
    LimiteTokensError,
    ProveedorIAError,
    RespuestaInvalidaIA,
)
from app.schemas.evaluacion import EvaluacionIA, ResultadoMotorIA

# Tope de tokens de salida. Un EvaluacionIA completo ronda ~1-1.5k; 4096 da margen.
MAX_TOKENS: int = 4096


def generar_evaluacion(system_prompt: str, datos_idea: str) -> ResultadoMotorIA:
    """Envía el prompt al proveedor y devuelve el resultado completo y trazable.

    Usa la API de DeepSeek (compatible con la de OpenAI) en modo JSON. El prompt
    se manda en dos mensajes: `system` (plantilla estática, la sirve la caché de
    contexto de DeepSeek) y `user` (datos variables de la idea). Mapea los fallos
    del proveedor y del parseo a las excepciones tipadas de la sección 6, que el
    backend traduce al Error del contrato 4.6.
    """
    client = OpenAI(api_key=settings.IA_API_KEY, base_url=settings.IA_BASE_URL)

    try:
        respuesta = client.chat.completions.create(
            model=settings.IA_MODELO,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": datos_idea},
            ],
            response_format={"type": "json_object"},
            max_tokens=MAX_TOKENS,
        )
    except RateLimitError as e:
        raise LimiteTokensError("Se alcanzó el límite del proveedor (429).") from e
    except APIStatusError as e:
        if e.status_code == 429:
            raise LimiteTokensError("Se alcanzó el límite del proveedor (429).") from e
        raise ProveedorIAError(
            f"Error del proveedor ({e.status_code}): {e.message}"
        ) from e
    except APIConnectionError as e:
        raise ProveedorIAError(f"No se pudo conectar con el proveedor de IA: {e}") from e
    except APIError as e:
        raise ProveedorIAError(f"Error de la API de IA: {e}") from e

    eleccion = respuesta.choices[0] if respuesta.choices else None
    cruda = (eleccion.message.content if eleccion and eleccion.message else None) or ""

    if eleccion and eleccion.finish_reason == "length":
        raise LimiteTokensError("La respuesta se truncó por límite de tokens.")

    if not cruda.strip():
        raise FormatoInesperado("La IA devolvió una respuesta vacía.")

    try:
        datos = json.loads(cruda)
    except json.JSONDecodeError as e:
        raise FormatoInesperado("La IA no devolvió JSON parseable.") from e

    try:
        evaluacion = EvaluacionIA.model_validate(datos)
    except ValidationError as e:
        raise RespuestaInvalidaIA(f"El JSON no cumple el contrato 4.2: {e}") from e

    uso = respuesta.usage
    return ResultadoMotorIA(
        evaluacion=evaluacion,
        prompt=f"{system_prompt}\n\n{datos_idea}",
        respuesta_cruda=cruda,
        modelo_ia=settings.IA_MODELO,
        tokens_prompt=getattr(uso, "prompt_tokens", 0) or 0,
        tokens_completion=getattr(uso, "completion_tokens", 0) or 0,
        # Campo propio de DeepSeek: tokens de entrada servidos desde caché.
        tokens_cache_hit=getattr(uso, "prompt_cache_hit_tokens", 0) or 0,
    )
