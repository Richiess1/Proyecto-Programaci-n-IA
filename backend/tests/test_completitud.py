"""Tests de app/ia/completitud.py — guardia de costo (RNF-03/RNF-04).

Cubre: qué se considera "campo insuficiente", que el mínimo es por caracteres
reales (post-strip, no solo "no vacío"), y que `asegurar_completitud` corta
con la excepción tipada correcta sin tocar nada más.
"""
from testing_setup import idea_valida  # noqa: E402

import unittest  # noqa: E402

from app.ia.completitud import UMBRALES_MINIMOS, asegurar_completitud, revisar_completitud  # noqa: E402
from app.ia.excepciones import EntradaIncompletaError  # noqa: E402


class TestRevisarCompletitud(unittest.TestCase):
    def test_idea_completa_no_tiene_faltantes(self):
        self.assertEqual(revisar_completitud(idea_valida()), [])

    def test_campo_ausente_del_dict_cuenta_como_faltante(self):
        idea = idea_valida()
        del idea["problema"]
        faltantes = revisar_completitud(idea)
        self.assertTrue(any("Problema" in f for f in faltantes))

    def test_campo_solo_con_espacios_cuenta_como_vacio(self):
        idea = idea_valida(descripcion="                         ")
        faltantes = revisar_completitud(idea)
        self.assertTrue(any("Descripción" in f for f in faltantes))

    def test_campo_por_debajo_del_minimo_de_caracteres(self):
        # "problema" exige 25 caracteres reales; 10 no alcanza aunque no esté vacío.
        idea = idea_valida(problema="muy corto")
        faltantes = revisar_completitud(idea)
        self.assertTrue(any("Problema" in f for f in faltantes))

    def test_nombre_exige_solo_3_caracteres(self):
        # El nombre se exime del mínimo largo (por naturaleza es corto).
        idea = idea_valida(nombre="Abc")
        self.assertEqual(revisar_completitud(idea), [])

    def test_reporta_todos_los_campos_faltantes_a_la_vez(self):
        idea = {k: "" for k in UMBRALES_MINIMOS}
        faltantes = revisar_completitud(idea)
        self.assertEqual(len(faltantes), len(UMBRALES_MINIMOS))

    def test_mensaje_incluye_el_minimo_exigido(self):
        idea = idea_valida(publico_objetivo="corto")
        faltantes = revisar_completitud(idea)
        etiqueta, minimo = UMBRALES_MINIMOS["publico_objetivo"]
        self.assertTrue(any(f"{minimo} caracteres" in f for f in faltantes))


class TestAsegurarCompletitud(unittest.TestCase):
    def test_idea_completa_no_lanza(self):
        asegurar_completitud(idea_valida())  # no debe lanzar

    def test_idea_incompleta_lanza_entrada_incompleta_error(self):
        idea = idea_valida(problema="corto")
        with self.assertRaises(EntradaIncompletaError) as ctx:
            asegurar_completitud(idea)
        self.assertEqual(ctx.exception.codigo, "ENTRADA_INCOMPLETA")

    def test_excepcion_lista_los_campos_faltantes_en_campos(self):
        idea = idea_valida(problema="corto", publico_objetivo="corto")
        with self.assertRaises(EntradaIncompletaError) as ctx:
            asegurar_completitud(idea)
        self.assertEqual(len(ctx.exception.campos), 2)

    def test_mensaje_de_la_excepcion_es_legible(self):
        idea = idea_valida(problema="corto")
        with self.assertRaises(EntradaIncompletaError) as ctx:
            asegurar_completitud(idea)
        self.assertIn("Completá o ampliá", ctx.exception.mensaje)


if __name__ == "__main__":
    unittest.main()
