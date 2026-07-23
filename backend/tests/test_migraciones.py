"""Tests de app/db/migraciones.py — el mecanismo casero de "ALTER TABLE".

No usa `testing_setup` (no necesita la app ni el motor de IA): crea su propio
engine SQLite en memoria para simular una base "vieja" (sin las columnas
nuevas) y verificar que `aplicar_migraciones` las agrega, sin romper si se
corre más de una vez (arranca en cada `main.py`, así que debe ser idempotente).
"""
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import create_engine, inspect, text  # noqa: E402

from app.db.migraciones import aplicar_migraciones  # noqa: E402


def _engine_con_tablas_viejas():
    """Un engine con `evaluaciones` y `prompt_logs` en su esquema ANTES de
    las columnas agregadas por migraciones.py (sin idea_hash / tokens_*)."""
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(text("CREATE TABLE ideas (id VARCHAR PRIMARY KEY)"))
        conn.execute(text("CREATE TABLE evaluaciones (id VARCHAR PRIMARY KEY, idea_id VARCHAR)"))
        conn.execute(text("CREATE TABLE prompt_logs (id VARCHAR PRIMARY KEY, evaluacion_id VARCHAR)"))
    return engine


class TestAplicarMigraciones(unittest.TestCase):
    def test_agrega_columnas_faltantes(self):
        engine = _engine_con_tablas_viejas()
        aplicar_migraciones(engine)

        columnas_evaluaciones = {c["name"] for c in inspect(engine).get_columns("evaluaciones")}
        columnas_prompt_logs = {c["name"] for c in inspect(engine).get_columns("prompt_logs")}

        self.assertIn("idea_hash", columnas_evaluaciones)
        self.assertIn("tokens_prompt", columnas_prompt_logs)
        self.assertIn("tokens_completion", columnas_prompt_logs)
        self.assertIn("tokens_cache_hit", columnas_prompt_logs)

    def test_es_idempotente_correrla_dos_veces(self):
        engine = _engine_con_tablas_viejas()
        aplicar_migraciones(engine)
        aplicar_migraciones(engine)  # no debe lanzar "duplicate column"

    def test_no_falla_si_la_tabla_todavia_no_existe(self):
        # create_all() la crea completa aparte; migraciones.py solo debe
        # saltarla, no fallar por "no such table".
        engine = create_engine("sqlite:///:memory:")
        aplicar_migraciones(engine)

    def test_no_toca_columnas_que_ya_existen(self):
        engine = _engine_con_tablas_viejas()
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE evaluaciones ADD COLUMN idea_hash VARCHAR"))
            conn.execute(text("INSERT INTO evaluaciones (id, idea_id, idea_hash) VALUES ('e1', 'i1', 'hash-preexistente')"))

        aplicar_migraciones(engine)  # no debe recrear/vaciar la columna existente

        with engine.connect() as conn:
            valor = conn.execute(text("SELECT idea_hash FROM evaluaciones WHERE id = 'e1'")).scalar()
        self.assertEqual(valor, "hash-preexistente")


if __name__ == "__main__":
    unittest.main()
