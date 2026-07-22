"""Infraestructura común para las pruebas automatizadas del backend.

No es un archivo de test (no empieza con `test_`, así que `unittest discover`
lo ignora) — es el punto de entrada que todo test debe usar para:

1. Fijar `DATABASE_URL` y `IA_API_KEY` como variables de entorno ANTES de
   importar cualquier cosa de `app`. `app.core.config.Settings` y
   `app.db.session` leen esas variables al importarse (no son perezosas), así
   que si un test importara `app.main` directamente y por accidente antes que
   este módulo, la suite terminaría usando `backend/evaluador.db` (la base de
   desarrollo) y/o una API key real. Todo archivo de test debe hacer
   `from tests.testing_setup import ...` como su primer import de `app`.
2. Exponer `ApiTestCase`, una base de `unittest.TestCase` con una base SQLite
   temporal limpia por test y un `TestClient` con `get_db` sobreescrito.
3. Exponer helpers para construir payloads válidos y resultados falsos del
   motor de IA, y `patch_motor_ia(...)` para simular el motor sin red.

Nota sobre el framework: el proyecto usa `unittest` (stdlib) en vez de pytest
porque este entorno de desarrollo no tuvo acceso a PyPI al escribir la suite
(ver docs/PRUEBAS.md, sección "Herramientas"). Las clases son
`unittest.TestCase` estándar, así que si más adelante hay red disponible,
`pip install pytest && pytest backend/tests` las ejecuta tal cual — pytest
descubre y corre TestCase de unittest de forma nativa, sin cambiar una línea.
"""
from __future__ import annotations

import os
import sys
import tempfile
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# --- Entorno de test: DEBE fijarse antes del primer import de `app` ---
os.environ["IA_API_KEY"] = "test-key-unittest-no-es-real"
_TEST_DB_PATH = Path(tempfile.gettempdir()) / f"evaluador_test_{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_TEST_DB_PATH}"

from fastapi.testclient import TestClient  # noqa: E402

from app.db.session import Base, SessionLocal, engine, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.schemas.evaluacion import (  # noqa: E402
    CriteriosEvaluados,
    EvaluacionIA,
    Foda,
    PasoValidacion,
    ResultadoMotorIA,
    Semaforo,
)


# ── Payloads de ejemplo ───────────────────────────────────────────────────

def idea_valida(**overrides) -> dict:
    """Payload mínimo válido para `POST /ideas` (contrato 4.1), con overrides."""
    datos = {
        "nombre": "TutorLocal",
        "descripcion": "Plataforma que conecta estudiantes con tutores verificados en su zona.",
        "problema": "A los estudiantes les cuesta encontrar tutores de confianza cerca de su casa.",
        "publico_objetivo": "Padres de estudiantes de secundaria en zonas urbanas.",
        "propuesta_valor": "Tutores verificados, agenda flexible y pago seguro.",
    }
    datos.update(overrides)
    return datos


def fake_evaluacion_ia(semaforo: Semaforo = Semaforo.VERDE, **overrides) -> EvaluacionIA:
    """EvaluacionIA (contrato 4.2) válida, para no depender de la IA real en tests."""
    base = dict(
        semaforo=semaforo,
        justificacion_semaforo="Justificación de prueba.",
        diagnostico="Diagnóstico de prueba.",
        foda=Foda(
            fortalezas=["fortaleza de prueba"],
            debilidades=["debilidad de prueba"],
            oportunidades=["oportunidad de prueba"],
            amenazas=["amenaza de prueba"],
        ),
        supuestos_criticos=["supuesto de prueba"],
        riesgos=["riesgo de prueba"],
        propuesta_valor_mejorada="Propuesta de valor mejorada de prueba.",
        preguntas_aclaracion=[],
        plan_validacion=[PasoValidacion(tipo="entrevista", descripcion="d", metrica="m")],
        criterios_evaluados=CriteriosEvaluados(
            problema="ok", mercado="ok", cliente="ok", diferenciacion="ok",
            riesgos="ok", monetizacion="ok", factibilidad="ok",
        ),
    )
    base.update(overrides)
    return EvaluacionIA(**base)


def fake_resultado_motor_ia(**overrides) -> ResultadoMotorIA:
    """ResultadoMotorIA (sección 6, v1.2) — lo que `evaluar_idea` devolvería."""
    base = dict(
        evaluacion=fake_evaluacion_ia(),
        prompt="system+user de prueba",
        respuesta_cruda='{"fake": true}',
        modelo_ia="deepseek-chat-test",
        tokens_prompt=100,
        tokens_completion=50,
        tokens_cache_hit=0,
    )
    base.update(overrides)
    return ResultadoMotorIA(**base)


def patch_motor_ia(resultado: ResultadoMotorIA | None = None, excepcion: Exception | None = None):
    """Parchea el motor de IA en el punto donde `evaluacion_service` lo importa.

    Evita cualquier llamada de red real a DeepSeek durante los tests. Usar
    `excepcion` para simular fallos del proveedor (ver test_endpoints_evaluar).
    """
    if excepcion is not None:
        return mock.patch("app.services.evaluacion_service.evaluar_idea", side_effect=excepcion)
    return mock.patch(
        "app.services.evaluacion_service.evaluar_idea",
        return_value=resultado if resultado is not None else fake_resultado_motor_ia(),
    )


def fake_openai_response(
    content: str | None,
    finish_reason: str = "stop",
    prompt_tokens: int = 10,
    completion_tokens: int = 5,
    cache_hit_tokens: int | None = None,
):
    """Doble de una `ChatCompletion` del SDK de OpenAI (usa SimpleNamespace, no
    MagicMock: así `getattr(x, "attr", default)` respeta el default cuando el
    atributo no existe, en vez de que MagicMock invente uno)."""
    message = SimpleNamespace(content=content)
    choice = SimpleNamespace(message=message, finish_reason=finish_reason)
    uso_kwargs = {"prompt_tokens": prompt_tokens, "completion_tokens": completion_tokens}
    if cache_hit_tokens is not None:
        uso_kwargs["prompt_cache_hit_tokens"] = cache_hit_tokens
    return SimpleNamespace(choices=[choice], usage=SimpleNamespace(**uso_kwargs))


class _FakeCompletions:
    def __init__(self, respuesta=None, excepcion: Exception | None = None):
        self._respuesta = respuesta
        self._excepcion = excepcion

    def create(self, **kwargs):
        if self._excepcion is not None:
            raise self._excepcion
        return self._respuesta


class FakeOpenAIClient:
    """Doble de `openai.OpenAI`: mismo shape (`.chat.completions.create`)."""

    def __init__(self, respuesta=None, excepcion: Exception | None = None):
        self.chat = SimpleNamespace(completions=_FakeCompletions(respuesta, excepcion))

    def __call__(self, *args, **kwargs):
        # Permite usar la instancia como "clase" al parchear OpenAI(...).
        return self


# ── Caso base para tests que golpean la API HTTP ──────────────────────────

class ApiTestCase(unittest.TestCase):
    """DB SQLite temporal, limpia en cada test; TestClient con `get_db` propio."""

    def setUp(self) -> None:
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

        def _override_get_db():
            try:
                yield self.db
            finally:
                pass

        app.dependency_overrides[get_db] = _override_get_db
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()
        self.db.close()
        Base.metadata.drop_all(bind=engine)

    def crear_idea(self, **overrides) -> dict:
        resp = self.client.post("/ideas", json=idea_valida(**overrides))
        assert resp.status_code == 200, resp.text
        return resp.json()

    def evaluar(self, idea_id: str, resultado: ResultadoMotorIA | None = None, excepcion: Exception | None = None):
        with patch_motor_ia(resultado=resultado, excepcion=excepcion) as mock_evaluar:
            resp = self.client.post(f"/ideas/{idea_id}/evaluar")
        return resp, mock_evaluar
