"""Tests de app/ia/prompts.py — construcción del prompt enviado a la IA.

No valida el contenido del SYSTEM_PROMPT palabra por palabra (eso es
responsabilidad de prompt-engineering, no de esta suite); valida el contrato
mecánico: qué recibe el modelo y cómo se marcan los campos ausentes, que es lo
que sostiene la garantía "la IA no inventa datos" (RNF-03).
"""
from testing_setup import idea_valida  # noqa: E402

import unittest  # noqa: E402

from app.ia.prompts import (  # noqa: E402
    PROMPT_VERSION,
    SYSTEM_PROMPT,
    construir_datos_idea,
    construir_prompt,
)


class TestConstruirDatosIdea(unittest.TestCase):
    def test_campo_con_valor_aparece_tal_cual(self):
        datos = construir_datos_idea(idea_valida(sector="EdTech"))
        self.assertIn("Sector: EdTech", datos)

    def test_campo_vacio_se_marca_no_proporcionado(self):
        idea = idea_valida()
        idea["sector"] = ""
        datos = construir_datos_idea(idea)
        self.assertIn("Sector: (no proporcionado)", datos)

    def test_campo_ausente_del_dict_se_marca_no_proporcionado(self):
        idea = idea_valida()  # no incluye "canales"
        datos = construir_datos_idea(idea)
        self.assertIn("Canales: (no proporcionado)", datos)

    def test_incluye_marcadores_de_inicio_y_fin(self):
        datos = construir_datos_idea(idea_valida())
        self.assertIn("--- DATOS DE LA IDEA (analizá solo esto) ---", datos)
        self.assertIn("--- FIN DE LOS DATOS ---", datos)

    def test_no_incluye_datos_fuera_del_bloque_de_campos_conocidos(self):
        # Un campo no reconocido en la Idea (p. ej. inyectado a mano) no debe
        # aparecer: solo se listan los campos de _CAMPOS_IDEA.
        idea = idea_valida()
        idea["campo_desconocido"] = "no debería aparecer"
        datos = construir_datos_idea(idea)
        self.assertNotIn("no debería aparecer", datos)


class TestConstruirPrompt(unittest.TestCase):
    def test_prompt_completo_concatena_system_y_datos(self):
        idea = idea_valida()
        prompt = construir_prompt(idea)
        self.assertTrue(prompt.startswith(SYSTEM_PROMPT))
        self.assertIn(construir_datos_idea(idea), prompt)

    def test_prompt_version_es_string_no_vacio(self):
        self.assertIsInstance(PROMPT_VERSION, str)
        self.assertTrue(PROMPT_VERSION.strip())


if __name__ == "__main__":
    unittest.main()
