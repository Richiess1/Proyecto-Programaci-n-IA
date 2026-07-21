from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

# Columnas nuevas por tabla. create_all() crea tablas que faltan pero NO altera
# las existentes, así que agregamos columnas nuevas a mano sobre la BD ya creada.
# SQLite soporta ADD COLUMN con un valor por defecto simple.
_COLUMNAS_NUEVAS: dict[str, dict[str, str]] = {
    "evaluaciones": {
        "idea_hash": "VARCHAR",
    },
    "prompt_logs": {
        "tokens_prompt": "INTEGER",
        "tokens_completion": "INTEGER",
        "tokens_cache_hit": "INTEGER",
    },
}


def aplicar_migraciones(engine: Engine) -> None:
    """Agrega columnas faltantes a tablas existentes (migración idempotente)."""
    inspector = inspect(engine)
    tablas = set(inspector.get_table_names())

    with engine.begin() as conn:
        for tabla, columnas in _COLUMNAS_NUEVAS.items():
            if tabla not in tablas:
                continue  # create_all ya la habrá creado con el esquema completo
            existentes = {col["name"] for col in inspector.get_columns(tabla)}
            for nombre, tipo in columnas.items():
                if nombre not in existentes:
                    conn.execute(text(f"ALTER TABLE {tabla} ADD COLUMN {nombre} {tipo}"))
