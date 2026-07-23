"""Tests de app/ia/cliente_ia.py — el punto donde se habla con DeepSeek.

Es el único módulo que hace red real en producción; en tests se reemplaza
`OpenAI` por un doble (`FakeOpenAIClient`) para que la suite sea determinista,
gratis y no dependa de que exista una API key real. Cubre el mapeo completo
del contrato de error 4.6 tal como lo define `cliente_ia.generar_evaluacion`.
"""
from testing_setup import fake_openai_response, FakeOpenAIClient  # noqa: E402

import unittest  # noqa: E402
from unittest import mock  # noqa: E402

import httpx  # noqa: E402
from openai import APIConnectionError, APIError, APIStatusError, RateLimitError  # noqa: E402

from app.ia.cliente_ia import generar_evaluacion  # noqa: E402
from app.ia.excepciones import FormatoInesperado, LimiteTokensError, ProveedorIAError, RespuestaInvalidaIA  # noqa: E402

SYSTEM_PROMPT = "system de prueba"
DATOS_IDEA = "datos de prueba"

EVALUACION_JSON_VALIDA = """
{
  "semaforo": "verde",
  "justificacion_semaforo": "justificación",
  "diagnostico": "diagnóstico",
  "foda": {"fortalezas": ["a"], "debilidades": ["b"], "oportunidades": ["c"], "amenazas": ["d"]},
  "supuestos_criticos": ["s"],
  "riesgos": ["r"],
  "propuesta_valor_mejorada": "mejorada",
  "preguntas_aclaracion": [],
  "plan_validacion": [{"tipo": "entrevista", "descripcion": "d", "metrica": "m"}],
  "criterios_evaluados": {
    "problema": "ok", "mercado": "ok", "cliente": "ok", "diferenciacion": "ok",
    "riesgos": "ok", "monetizacion": "ok", "factibilidad": "ok"
  }
}
"""

_REQUEST = httpx.Request("POST", "https://api.deepseek.com/chat/completions")


def _status_error(status_code: int, message: str = "error del proveedor") -> APIStatusError:
    respuesta = httpx.Response(status_code, request=_REQUEST, json={"error": {"message": message}})
    return APIStatusError(message, response=respuesta, body=None)


def _rate_limit_error(message: str = "rate limited") -> RateLimitError:
    respuesta = httpx.Response(429, request=_REQUEST)
    return RateLimitError(message, response=respuesta, body=None)


class TestGenerarEvaluacionExito(unittest.TestCase):
    def test_respuesta_valida_se_parsea_y_valida_correctamente(self):
        respuesta = fake_openai_response(EVALUACION_JSON_VALIDA, prompt_tokens=120, completion_tokens=340, cache_hit_tokens=80)
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(respuesta=respuesta)):
            resultado = generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)

        self.assertEqual(resultado.evaluacion.semaforo.value, "verde")
        self.assertEqual(resultado.tokens_prompt, 120)
        self.assertEqual(resultado.tokens_completion, 340)
        self.assertEqual(resultado.tokens_cache_hit, 80)
        self.assertEqual(resultado.prompt, f"{SYSTEM_PROMPT}\n\n{DATOS_IDEA}")
        self.assertEqual(resultado.respuesta_cruda, EVALUACION_JSON_VALIDA)

    def test_sin_campo_de_cache_hit_tokens_default_a_cero(self):
        # DeepSeek es quien manda `prompt_cache_hit_tokens`; otro proveedor
        # compatible con la API de OpenAI podría no mandarlo.
        respuesta = fake_openai_response(EVALUACION_JSON_VALIDA)  # sin cache_hit_tokens
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(respuesta=respuesta)):
            resultado = generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)
        self.assertEqual(resultado.tokens_cache_hit, 0)


class TestGenerarEvaluacionErroresDelProveedor(unittest.TestCase):
    def test_rate_limit_error_mapea_a_limite_tokens(self):
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(excepcion=_rate_limit_error())):
            with self.assertRaises(LimiteTokensError):
                generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)

    def test_api_status_error_429_mapea_a_limite_tokens(self):
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(excepcion=_status_error(429))):
            with self.assertRaises(LimiteTokensError):
                generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)

    def test_api_status_error_500_mapea_a_proveedor_ia_error(self):
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(excepcion=_status_error(500, "boom"))):
            with self.assertRaises(ProveedorIAError) as ctx:
                generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)
        self.assertIn("500", str(ctx.exception))
        self.assertIn("boom", str(ctx.exception))

    def test_api_status_error_401_mapea_a_proveedor_ia_error(self):
        # Caso real observado manualmente: API key inválida.
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(excepcion=_status_error(401, "invalid api key"))):
            with self.assertRaises(ProveedorIAError):
                generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)

    def test_connection_error_mapea_a_proveedor_ia_error(self):
        excepcion = APIConnectionError(message="no se pudo conectar", request=_REQUEST)
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(excepcion=excepcion)):
            with self.assertRaises(ProveedorIAError):
                generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)

    def test_api_error_generico_mapea_a_proveedor_ia_error(self):
        excepcion = APIError("error genérico", request=_REQUEST, body=None)
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(excepcion=excepcion)):
            with self.assertRaises(ProveedorIAError):
                generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)


class TestGenerarEvaluacionRespuestaMalFormada(unittest.TestCase):
    def test_respuesta_truncada_por_limite_de_tokens(self):
        respuesta = fake_openai_response(EVALUACION_JSON_VALIDA, finish_reason="length")
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(respuesta=respuesta)):
            with self.assertRaises(LimiteTokensError):
                generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)

    def test_respuesta_vacia_mapea_a_formato_inesperado(self):
        respuesta = fake_openai_response("")
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(respuesta=respuesta)):
            with self.assertRaises(FormatoInesperado):
                generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)

    def test_respuesta_none_mapea_a_formato_inesperado(self):
        respuesta = fake_openai_response(None)
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(respuesta=respuesta)):
            with self.assertRaises(FormatoInesperado):
                generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)

    def test_respuesta_no_es_json_parseable(self):
        respuesta = fake_openai_response("esto no es json { { {")
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(respuesta=respuesta)):
            with self.assertRaises(FormatoInesperado):
                generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)

    def test_json_valido_pero_no_cumple_el_contrato_4_2(self):
        respuesta = fake_openai_response('{"semaforo": "verde"}')  # faltan casi todos los campos
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(respuesta=respuesta)):
            with self.assertRaises(RespuestaInvalidaIA):
                generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)

    def test_semaforo_con_valor_invalido_es_respuesta_invalida(self):
        json_invalido = EVALUACION_JSON_VALIDA.replace('"verde"', '"azul"')
        respuesta = fake_openai_response(json_invalido)
        with mock.patch("app.ia.cliente_ia.OpenAI", FakeOpenAIClient(respuesta=respuesta)):
            with self.assertRaises(RespuestaInvalidaIA):
                generar_evaluacion(SYSTEM_PROMPT, DATOS_IDEA)


if __name__ == "__main__":
    unittest.main()
