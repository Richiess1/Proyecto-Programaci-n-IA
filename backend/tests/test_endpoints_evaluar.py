"""Tests de integración de POST /ideas/{id}/evaluar — el endpoint clave.

Cubre tres cosas que no se pueden verificar solo con tests unitarios:
1. El mapeo completo excepción → status HTTP → cuerpo del contrato de error 4.6,
   tal como lo arman los `@app.exception_handler` de main.py.
2. La deduplicación (services/evaluacion_service.py) end-to-end: que una
   segunda evaluación de contenido idéntico NO vuelve a llamar al motor de IA.
3. Que la entrada incompleta corta en el flujo real (vía `evaluar_idea` real,
   sin mockear) antes de intentar tocar la IA.

El motor de IA (`evaluacion_service.evaluar_idea`) se mockea siempre que se
necesita un resultado exitoso o un error del proveedor — nunca se llama a
DeepSeek desde esta suite.
"""
from testing_setup import ApiTestCase, fake_resultado_motor_ia, idea_valida  # noqa: E402

import unittest  # noqa: E402

from app.ia.excepciones import (  # noqa: E402
    FormatoInesperado,
    LimiteTokensError,
    ProveedorIAError,
    RespuestaInvalidaIA,
)


class TestEvaluarIdeaExito(ApiTestCase):
    def test_evaluar_idea_completa_devuelve_200_con_resultado(self):
        idea = self.crear_idea()
        resultado = fake_resultado_motor_ia()
        resp, mock_evaluar = self.evaluar(idea["id"], resultado=resultado)

        self.assertEqual(resp.status_code, 200)
        cuerpo = resp.json()
        self.assertEqual(cuerpo["idea_id"], idea["id"])
        self.assertEqual(cuerpo["resultado"]["semaforo"], "verde")
        self.assertEqual(cuerpo["estado"], "pendiente")
        self.assertEqual(cuerpo["version"], 1)
        mock_evaluar.assert_called_once()

    def test_evaluar_idea_persiste_prompt_log_con_consumo_de_tokens(self):
        idea = self.crear_idea()
        resultado = fake_resultado_motor_ia(tokens_prompt=111, tokens_completion=222, tokens_cache_hit=33)
        resp, _ = self.evaluar(idea["id"], resultado=resultado)
        evaluacion_id = resp.json()["id"]

        from app.db import models

        log = self.db.query(models.PromptLog).filter_by(evaluacion_id=evaluacion_id).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.tokens_prompt, 111)
        self.assertEqual(log.tokens_completion, 222)
        self.assertEqual(log.tokens_cache_hit, 33)
        self.assertEqual(log.respuesta_cruda, resultado.respuesta_cruda)

    def test_evaluar_idea_inexistente_da_404(self):
        resp, mock_evaluar = self.evaluar("id-que-no-existe")
        self.assertEqual(resp.status_code, 404)
        self.assertEqual(resp.json()["detail"], "Idea no encontrada")
        mock_evaluar.assert_not_called()


class TestEvaluarIdeaEntradaIncompleta(ApiTestCase):
    def test_idea_con_campo_por_debajo_del_minimo_da_422(self):
        # No se mockea el motor: la ruta real (asegurar_completitud) debe
        # cortar sola, sin necesidad de un doble de la IA.
        idea = self.crear_idea(problema="muy corto")
        resp = self.client.post(f"/ideas/{idea['id']}/evaluar")

        self.assertEqual(resp.status_code, 422)
        error = resp.json()["error"]
        self.assertEqual(error["codigo"], "ENTRADA_INCOMPLETA")
        self.assertIn("Problema", error["mensaje"])

    def test_entrada_incompleta_no_genera_evaluacion_ni_prompt_log(self):
        idea = self.crear_idea(problema="muy corto")
        self.client.post(f"/ideas/{idea['id']}/evaluar")

        from app.db import models

        self.assertEqual(self.db.query(models.Evaluacion).count(), 0)
        self.assertEqual(self.db.query(models.PromptLog).count(), 0)


class TestEvaluarIdeaErroresDelProveedor(ApiTestCase):
    def test_proveedor_ia_error_da_503(self):
        idea = self.crear_idea()
        resp, _ = self.evaluar(idea["id"], excepcion=ProveedorIAError("No se pudo conectar."))
        self.assertEqual(resp.status_code, 503)
        self.assertEqual(resp.json()["error"], {"codigo": "IA_PROVEEDOR", "mensaje": "No se pudo conectar."})

    def test_limite_tokens_error_da_429(self):
        idea = self.crear_idea()
        resp, _ = self.evaluar(idea["id"], excepcion=LimiteTokensError("Límite alcanzado."))
        self.assertEqual(resp.status_code, 429)
        self.assertEqual(resp.json()["error"]["codigo"], "IA_LIMITE_TOKENS")

    def test_formato_inesperado_da_500(self):
        idea = self.crear_idea()
        resp, _ = self.evaluar(idea["id"], excepcion=FormatoInesperado("JSON no parseable."))
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.json()["error"]["codigo"], "FORMATO_INESPERADO")

    def test_respuesta_invalida_ia_da_502(self):
        idea = self.crear_idea()
        resp, _ = self.evaluar(idea["id"], excepcion=RespuestaInvalidaIA("No cumple el contrato 4.2."))
        self.assertEqual(resp.status_code, 502)
        self.assertEqual(resp.json()["error"]["codigo"], "IA_RESPUESTA_INVALIDA")

    def test_error_del_proveedor_no_persiste_evaluacion_a_medias(self):
        idea = self.crear_idea()
        self.evaluar(idea["id"], excepcion=ProveedorIAError("falló"))

        from app.db import models

        self.assertEqual(self.db.query(models.Evaluacion).count(), 0)


class TestEvaluarIdeaDeduplicacion(ApiTestCase):
    def test_reevaluar_misma_idea_sin_cambios_no_vuelve_a_llamar_a_la_ia(self):
        idea = self.crear_idea()
        resp1, mock1 = self.evaluar(idea["id"])
        resp2, mock2 = self.evaluar(idea["id"])

        mock1.assert_called_once()
        mock2.assert_not_called()  # se sirvió desde caché, sin llamar al motor
        self.assertEqual(resp1.json()["id"], resp2.json()["id"])

    def test_dos_ideas_con_contenido_identico_comparten_resultado_sin_doble_llamada(self):
        contenido = idea_valida(nombre="Idea Repetida")
        idea_a = self.crear_idea(**contenido)
        idea_b = self.crear_idea(**contenido)

        resp_a, mock_a = self.evaluar(idea_a["id"])
        resp_b, mock_b = self.evaluar(idea_b["id"])

        mock_a.assert_called_once()
        mock_b.assert_not_called()
        # Contenido idéntico -> mismo resultado, pero cada idea tiene su propia
        # fila de Evaluacion (ids de evaluación distintos, idea_id distinto).
        self.assertEqual(resp_a.json()["resultado"], resp_b.json()["resultado"])
        self.assertNotEqual(resp_a.json()["id"], resp_b.json()["id"])
        self.assertEqual(resp_b.json()["idea_id"], idea_b["id"])

    def test_reutilizacion_entre_ideas_deja_prompt_log_marcado(self):
        contenido = idea_valida(nombre="Idea Repetida Dos")
        idea_a = self.crear_idea(**contenido)
        idea_b = self.crear_idea(**contenido)
        self.evaluar(idea_a["id"])
        resp_b, _ = self.evaluar(idea_b["id"])

        from app.db import models

        log_b = self.db.query(models.PromptLog).filter_by(evaluacion_id=resp_b.json()["id"]).first()
        self.assertIn("reutilizado", log_b.respuesta_cruda)
        self.assertEqual(log_b.tokens_prompt, 0)

    def test_cambiar_contenido_evita_la_cache_y_llama_de_nuevo_a_la_ia(self):
        idea = self.crear_idea()
        self.evaluar(idea["id"])

        # "Reevaluar" tras editar la idea: se crea una idea nueva con contenido
        # distinto (el servicio no tiene endpoint de edición), el hash cambia
        # y debe volver a llamar al motor.
        idea_editada = self.crear_idea(descripcion="Una descripción distinta a la original, sin relación.")
        resp, mock_evaluar = self.evaluar(idea_editada["id"])

        mock_evaluar.assert_called_once()
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
