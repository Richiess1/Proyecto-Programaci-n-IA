from __future__ import annotations

from app.ia.excepciones import EntradaIncompletaError

# Mínimo de caracteres (contenido real, ya .strip()) que exigimos por campo
# obligatorio antes de gastar tokens con el proveedor. Umbral "suave": lo justo
# para que la IA tenga algo concreto que analizar y no rellene con suposiciones
# (RNF-03). El nombre se exime del mínimo largo porque por naturaleza es corto.
UMBRALES_MINIMOS: dict[str, tuple[str, int]] = {
    "nombre": ("Nombre", 3),
    "descripcion": ("Descripción", 25),
    "problema": ("Problema que resuelve", 25),
    "publico_objetivo": ("Público objetivo", 15),
    "propuesta_valor": ("Propuesta de valor", 20),
}


def revisar_completitud(idea: dict) -> list[str]:
    """Devuelve la lista de campos obligatorios que no alcanzan el mínimo.

    Lista vacía = la idea está lo bastante completa para evaluar.
    """
    faltantes: list[str] = []
    for clave, (etiqueta, minimo) in UMBRALES_MINIMOS.items():
        valor = str(idea.get(clave, "") or "").strip()
        if len(valor) < minimo:
            faltantes.append(f"{etiqueta} (mínimo {minimo} caracteres)")
    return faltantes


def asegurar_completitud(idea: dict) -> None:
    """Corta el flujo ANTES de llamar al proveedor si la idea está incompleta.

    Así una entrada pobre no consume tokens: se rechaza localmente y el usuario
    recibe exactamente qué campos completar.
    """
    faltantes = revisar_completitud(idea)
    if faltantes:
        raise EntradaIncompletaError(
            "La idea no tiene información suficiente para evaluarse. "
            "Completá o ampliá: " + "; ".join(faltantes) + ".",
            campos=faltantes,
        )
