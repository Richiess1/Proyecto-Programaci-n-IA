"""Tests de app/ia/motor_ia.py — orquestación completitud → prompt → cliente.

El caso que más importa aquí es el negativo: una idea incompleta debe cortar
ANTES de tocar al proveedor de IA (cero tokens gastados). Si alguien reordena
`evaluar_idea` y ese orden se invierte, este test lo detecta sin necesitar una
llamada real a DeepSeek.
"""
from testing_setup import idea_valida  # noqa: E402

import unittest  # noqa: E402
from unittest import mock  # noqa: E402

from app.ia.excepciones import EntradaIncompletaError  # noqa: E402
from app.ia.motor_ia import evaluar_idea  # noqa: E402
from app.schemas.evaluacion import ResultadoMotorIA  # noqa: E402


class TestEvaluarIdea(unittest.TestCase):
    def test_idea_incompleta_no_llama_al_cliente_ia(self):
        idea = idea_valida(problema="corto")
        with mock.patch("app.ia.motor_ia.generar_evaluacion") as mock_generar:
            with self.assertRaises(EntradaIncompletaError):
                evaluar_idea(idea)
        mock_generar.assert_not_called()

    def test_idea_completa_llama_al_cliente_con_prompt_construido(self):
        idea = idea_valida()
        resultado_falso = mock.Mock(spec=ResultadoMotorIA)
        with mock.patch("app.ia.motor_ia.generar_evaluacion", return_value=resultado_falso) as mock_generar:
            resultado = evaluar_idea(idea)

        self.assertIs(resultado, resultado_falso)
        mock_generar.assert_called_once()
        (system_prompt, datos_idea), _ = mock_generar.call_args
        self.assertIn("Sos un analista de negocios senior", system_prompt)
        self.assertIn(idea["nombre"], datos_idea)

    def test_error_del_cliente_ia_sube_sin_modificarse(self):
        from app.ia.excepciones import ProveedorIAError

        idea = idea_valida()
        with mock.patch(
            "app.ia.motor_ia.generar_evaluacion",
            side_effect=ProveedorIAError("Falló la conexión"),
        ):
            with self.assertRaises(ProveedorIAError):
                evaluar_idea(idea)


if __name__ == "__main__":
    unittest.main()
