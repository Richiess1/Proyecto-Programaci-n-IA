"""Tests de POST /comparar — contrato 4.5.

Incluye un caso (`test_comparar_usa_la_ultima_evaluacion_insertada`) que
documenta un comportamiento observado, no un contrato garantizado: ver el
HALLAZGO en el docstring de ese test y en docs/PRUEBAS.md.
"""
from testing_setup import ApiTestCase  # noqa: E402

import unittest  # noqa: E402

from app.db import models  # noqa: E402

CRITERIOS_BASE = {
    "problema": "ok", "mercado": "ok", "cliente": "ok", "diferenciacion": "ok",
    "riesgos": "ok", "monetizacion": "ok", "factibilidad": "ok",
}


class TestComparar(ApiTestCase):
    def _insertar_evaluacion(self, idea_id: str, semaforo: str = "verde") -> None:
        ev = models.Evaluacion(
            idea_id=idea_id,
            modelo_ia="deepseek-chat-test",
            estado="pendiente",
            resultado={"semaforo": semaforo, "criterios_evaluados": CRITERIOS_BASE},
        )
        self.db.add(ev)
        self.db.commit()

    def test_solo_incluye_ideas_con_al_menos_una_evaluacion(self):
        idea_evaluada = self.crear_idea(nombre="Evaluada")
        idea_sin_evaluar = self.crear_idea(nombre="Sin evaluar")
        self._insertar_evaluacion(idea_evaluada["id"])

        resp = self.client.post("/comparar", json={"idea_ids": [idea_evaluada["id"], idea_sin_evaluar["id"]]})

        self.assertEqual(resp.status_code, 200)
        nombres = [i["nombre"] for i in resp.json()["ideas"]]
        self.assertEqual(nombres, ["Evaluada"])

    def test_devuelve_los_7_criterios_en_orden_fijo(self):
        idea = self.crear_idea()
        self._insertar_evaluacion(idea["id"])
        resp = self.client.post("/comparar", json={"idea_ids": [idea["id"]]})
        self.assertEqual(
            resp.json()["criterios"],
            ["problema", "mercado", "cliente", "diferenciacion", "riesgos", "monetizacion", "factibilidad"],
        )

    def test_idea_inexistente_se_omite_sin_error(self):
        idea = self.crear_idea()
        self._insertar_evaluacion(idea["id"])
        resp = self.client.post("/comparar", json={"idea_ids": [idea["id"], "id-fantasma"]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["ideas"]), 1)

    def test_ninguna_idea_evaluada_devuelve_lista_vacia(self):
        idea = self.crear_idea()
        resp = self.client.post("/comparar", json={"idea_ids": [idea["id"]]})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["ideas"], [])

    def test_lista_vacia_de_ids_da_422(self):
        # ComparacionReq exige min_length=1 (contrato 4.5).
        resp = self.client.post("/comparar", json={"idea_ids": []})
        self.assertEqual(resp.status_code, 422)

    def test_mas_de_20_ideas_da_422(self):
        # Tope anti-abuso: max_length=20.
        resp = self.client.post("/comparar", json={"idea_ids": [f"id-{i}" for i in range(21)]})
        self.assertEqual(resp.status_code, 422)

    def test_exactamente_20_ideas_es_valido(self):
        resp = self.client.post("/comparar", json={"idea_ids": [f"id-{i}" for i in range(20)]})
        self.assertEqual(resp.status_code, 200)  # todas inexistentes, pero la validación de tamaño pasa
        self.assertEqual(resp.json()["ideas"], [])

    def test_comparar_usa_la_ultima_evaluacion_insertada(self):
        """HALLAZGO: `generar_comparacion` toma `idea.evaluaciones[-1]` (último
        elemento de la relación) en vez de ordenar explícitamente por `fecha`.
        En la práctica coincide con "la más reciente" porque SQLite devuelve
        las filas en orden de inserción para una consulta sin ORDER BY, pero
        eso no es un contrato garantizado por SQL — un cambio de motor de BD,
        o una futura carga con `order_by` distinto en el modelo, podría romper
        este supuesto en silencio. Este test documenta el comportamiento
        actual; si se agrega `order_by(Evaluacion.fecha)` a la relación en
        `models.py`, el test debe seguir pasando sin cambios.
        """
        idea = self.crear_idea()
        self._insertar_evaluacion(idea["id"], semaforo="rojo")
        self._insertar_evaluacion(idea["id"], semaforo="verde")

        resp = self.client.post("/comparar", json={"idea_ids": [idea["id"]]})
        self.assertEqual(resp.json()["ideas"][0]["semaforo"], "verde")


if __name__ == "__main__":
    unittest.main()
