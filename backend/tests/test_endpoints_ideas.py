"""Tests de integración de POST/GET /ideas — contrato 4.1, sin tocar la IA.

Usa TestClient de FastAPI sobre una base SQLite temporal (ver testing_setup);
no hay mocks acá porque estos endpoints no llaman al motor de IA.
"""
from testing_setup import ApiTestCase, idea_valida  # noqa: E402

import unittest  # noqa: E402


class TestCrearIdea(ApiTestCase):
    def test_crear_idea_valida_devuelve_200_con_id(self):
        resp = self.client.post("/ideas", json=idea_valida())
        self.assertEqual(resp.status_code, 200)
        cuerpo = resp.json()
        self.assertTrue(cuerpo["id"])
        self.assertEqual(cuerpo["nombre"], "TutorLocal")

    def test_crear_idea_persiste_campos_opcionales_vacios_por_default(self):
        resp = self.client.post("/ideas", json=idea_valida())
        cuerpo = resp.json()
        self.assertEqual(cuerpo["sector"], "")
        self.assertEqual(cuerpo["competencia_conocida"], "")

    def test_crear_idea_acepta_campos_opcionales(self):
        resp = self.client.post("/ideas", json=idea_valida(sector="EdTech", pais_mercado="El Salvador"))
        cuerpo = resp.json()
        self.assertEqual(cuerpo["sector"], "EdTech")
        self.assertEqual(cuerpo["pais_mercado"], "El Salvador")

    def test_crear_idea_sin_campo_obligatorio_da_422(self):
        idea = idea_valida()
        del idea["nombre"]
        resp = self.client.post("/ideas", json=idea)
        self.assertEqual(resp.status_code, 422)
        # Formato B (§5): error estándar de FastAPI, con "detail".
        self.assertIn("detail", resp.json())

    def test_crear_idea_con_campo_obligatorio_vacio_da_422(self):
        resp = self.client.post("/ideas", json=idea_valida(problema=""))
        self.assertEqual(resp.status_code, 422)

    def test_crear_idea_excede_longitud_maxima_da_422(self):
        # `nombre` tiene max_length=120 (anti-abuso de costo, ver contrato 4.1).
        resp = self.client.post("/ideas", json=idea_valida(nombre="x" * 121))
        self.assertEqual(resp.status_code, 422)

    def test_crear_idea_sin_id_genera_uuid(self):
        resp = self.client.post("/ideas", json=idea_valida())
        id_generado = resp.json()["id"]
        self.assertEqual(len(id_generado), 36)  # shape de UUID4
        self.assertEqual(id_generado.count("-"), 4)

    def test_crear_idea_respeta_id_explicito_del_cliente(self):
        # HALLAZGO (ver docs/PRUEBAS.md): el endpoint usa `exclude_none=True`,
        # que solo descarta `id=None`. Si el cliente manda un id explícito, se
        # persiste tal cual — no hay validación server-side que lo rechace ni
        # que fuerce un UUID nuevo en ese caso.
        resp = self.client.post("/ideas", json=idea_valida(id="id-elegido-por-el-cliente"))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["id"], "id-elegido-por-el-cliente")


class TestObtenerIdeas(ApiTestCase):
    def test_listado_vacio_al_inicio(self):
        resp = self.client.get("/ideas")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])

    def test_listado_incluye_todas_las_ideas_creadas(self):
        self.crear_idea(nombre="Idea Uno")
        self.crear_idea(nombre="Idea Dos")
        resp = self.client.get("/ideas")
        nombres = {i["nombre"] for i in resp.json()}
        self.assertEqual(nombres, {"Idea Uno", "Idea Dos"})

    def test_obtener_idea_por_id_existente(self):
        idea = self.crear_idea(nombre="Idea Puntual")
        resp = self.client.get(f"/ideas/{idea['id']}")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["nombre"], "Idea Puntual")

    def test_obtener_idea_inexistente_da_404(self):
        resp = self.client.get("/ideas/id-que-no-existe")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["detail"], "Idea no encontrada")


if __name__ == "__main__":
    unittest.main()
