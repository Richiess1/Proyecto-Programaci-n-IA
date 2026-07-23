from __future__ import annotations


class MotorIAError(Exception):
    """Base de los errores propios del Motor IA. `codigo` mapea al Error 4.6."""
    codigo: str = "FORMATO_INESPERADO"

    def __init__(self, mensaje: str) -> None:
        super().__init__(mensaje)
        self.mensaje = mensaje


class RespuestaInvalidaIA(MotorIAError):
    """La IA respondió pero el JSON no cumple el contrato 4.2."""
    codigo = "IA_RESPUESTA_INVALIDA"


class ProveedorIAError(MotorIAError):
    """Falló la llamada al proveedor de IA (red, auth, 5xx)."""
    codigo = "IA_PROVEEDOR"


class LimiteTokensError(MotorIAError):
    """Se excedió el límite de tokens del proveedor."""
    codigo = "IA_LIMITE_TOKENS"


class FormatoInesperado(MotorIAError):
    """La respuesta no llega en el formato esperado (p. ej. no es JSON parseable)."""
    codigo = "FORMATO_INESPERADO"


class EntradaIncompletaError(MotorIAError):
    """La Idea no trae información suficiente para evaluar.

    Se detecta ANTES de llamar al proveedor, así que no consume tokens. `campos`
    lista qué campos quedaron por debajo del mínimo, para devolvérselos al usuario.
    """
    codigo = "ENTRADA_INCOMPLETA"

    def __init__(self, mensaje: str, campos: list[str] | None = None) -> None:
        super().__init__(mensaje)
        self.campos = campos or []