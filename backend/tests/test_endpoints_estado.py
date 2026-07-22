"""Tests de PATCH /evaluaciones/{id}/estado (seguimiento manual, §3.5)."""
from testing_setup import ApiTestCase  # noqa: E402

import unittest  # noqa: E402


class TestCambiarEstado(ApiTestCase):
    def _crear_idea_evaluada(self) -> dict:
        idea = self.crear_idea()
        resp, _ = self.evaluar(idea["id"])
        return resp.json()

    def test_cambiar_estado_devuelve_evaluacion_actualizada(self):
        evaluacion = self._crear_idea_evaluada()
        resp = self.client.patch(f"/evaluaciones/{evaluacion['id']}/estado", json={"estado": "aceptado"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["estado"], "aceptado")

    def test_estado_es_texto_libre_sin_lista_cerrada(self):
        # El README de integración lo documenta explícitamente (§3.5): no hay
        # enum de estados en el backend, es texto libre.
        evaluacion = self._crear_idea_evaluada()
        resp = self.client.patch(f"/evaluaciones/{evaluacion['id']}/estado", json={"estado": "un-estado-cualquiera"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["estado"], "un-estado-cualquiera")

    def test_cambiar_estado_de_evaluacion_inexistente_da_404(self):
        resp = self.client.patch("/evaluaciones/id-que-no-existe/estado", json={"estado": "aceptado"})
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["detail"], "Evaluacion no encontrada")

    def test_cambiar_estado_sin_body_da_422(self):
        evaluacion = self._crear_idea_evaluada()
        resp = self.client.patch(f"/evaluaciones/{evaluacion['id']}/estado", json={})
        self.assertEqual(resp.status_code, 422)

    def test_cambiar_estado_persiste_el_cambio(self):
        evaluacion = self._crear_idea_evaluada()
        self.client.patch(f"/evaluaciones/{evaluacion['id']}/estado", json={"estado": "descartado"})

        resp = self.client.get(f"/ideas/{evaluacion['idea_id']}/evaluaciones")
        self.assertEqual(resp.json()[0]["estado"], "descartado")


if __name__ == "__main__":
    unittest.main()
