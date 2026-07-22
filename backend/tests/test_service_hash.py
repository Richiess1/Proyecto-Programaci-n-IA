"""Tests de app/services/evaluacion_service._hash_idea — clave de la dedup.

`_hash_idea` decide si una evaluación puede reutilizarse sin gastar tokens.
Un bug acá (p. ej. que el orden de las claves afecte el hash, o que el modelo
no forme parte de él) rompe la garantía de costo silenciosamente: o se gastan
tokens de más, o —peor— se reutiliza una evaluación de un modelo/prompt
distinto sin que nadie lo note. Se prueba directamente por ser una función
pura y crítica, aunque sea "privada" (`_hash_idea`).
"""
from testing_setup import idea_valida  # noqa: E402

import unittest  # noqa: E402
from unittest import mock  # noqa: E402

from app.services.evaluacion_service import _hash_idea  # noqa: E402

MODELO = "deepseek-chat"


class TestHashIdea(unittest.TestCase):
    def test_mismo_contenido_mismo_modelo_produce_mismo_hash(self):
        idea = idea_valida()
        self.assertEqual(_hash_idea(idea, MODELO), _hash_idea(idea, MODELO))

    def test_contenido_distinto_produce_hash_distinto(self):
        idea_a = idea_valida()
        idea_b = idea_valida(descripcion="Una descripción completamente distinta y única.")
        self.assertNotEqual(_hash_idea(idea_a, MODELO), _hash_idea(idea_b, MODELO))

    def test_mismo_contenido_distinto_modelo_produce_hash_distinto(self):
        idea = idea_valida()
        self.assertNotEqual(_hash_idea(idea, "deepseek-chat"), _hash_idea(idea, "otro-modelo"))

    def test_orden_de_insercion_de_claves_no_afecta_el_hash(self):
        idea_a = idea_valida()
        # Reconstruido con las mismas claves pero insertadas en otro orden.
        idea_b = {k: idea_a[k] for k in reversed(list(idea_a.keys()))}
        self.assertEqual(_hash_idea(idea_a, MODELO), _hash_idea(idea_b, MODELO))

    def test_campos_extra_al_hash_no_declarados_en_contenido_se_ignoran(self):
        # id, contexto de BD, etc. no deben afectar el hash: solo importan los
        # campos de _CAMPOS_CONTENIDO.
        idea_a = idea_valida()
        idea_b = dict(idea_a, id="algun-uuid-irrelevante")
        self.assertEqual(_hash_idea(idea_a, MODELO), _hash_idea(idea_b, MODELO))

    def test_cambiar_version_de_prompt_cambia_el_hash(self):
        idea = idea_valida()
        with mock.patch("app.services.evaluacion_service.PROMPT_VERSION", "version-actual"):
            hash_v1 = _hash_idea(idea, MODELO)
        with mock.patch("app.services.evaluacion_service.PROMPT_VERSION", "version-nueva"):
            hash_v2 = _hash_idea(idea, MODELO)
        self.assertNotEqual(hash_v1, hash_v2)

    def test_campo_none_y_campo_vacio_producen_el_mismo_hash(self):
        # `idea_dict.get(c, "") or ""`: None y "" deben normalizarse igual,
        # porque una Idea persistida en SQLite guarda opcionales vacíos como
        # NULL (None), no como "".
        idea_con_none = idea_valida(sector=None)
        idea_con_vacio = idea_valida(sector="")
        self.assertEqual(_hash_idea(idea_con_none, MODELO), _hash_idea(idea_con_vacio, MODELO))


if __name__ == "__main__":
    unittest.main()
