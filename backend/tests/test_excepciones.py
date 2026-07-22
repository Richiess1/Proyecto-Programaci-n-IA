"""Tests de app/ia/excepciones.py — mapeo excepción → código del contrato 4.6.

Este mapeo es lo que `main.py` usa para armar la respuesta de error; si un
`codigo` cambia sin querer, el contrato con el frontend se rompe en silencio
(el frontend decide su mensaje según `error.codigo`). Estos tests fijan ese
contrato.
"""
import unittest  # noqa: E402

from app.ia.excepciones import (  # noqa: E402
    EntradaIncompletaError,
    FormatoInesperado,
    LimiteTokensError,
    MotorIAError,
    ProveedorIAError,
    RespuestaInvalidaIA,
)

CODIGOS_ESPERADOS = {
    RespuestaInvalidaIA: "IA_RESPUESTA_INVALIDA",
    ProveedorIAError: "IA_PROVEEDOR",
    LimiteTokensError: "IA_LIMITE_TOKENS",
    FormatoInesperado: "FORMATO_INESPERADO",
    EntradaIncompletaError: "ENTRADA_INCOMPLETA",
}


class TestCodigosDeError(unittest.TestCase):
    def test_cada_excepcion_tiene_el_codigo_del_contrato_4_6(self):
        for cls, codigo_esperado in CODIGOS_ESPERADOS.items():
            with self.subTest(cls=cls.__name__):
                self.assertEqual(cls.codigo, codigo_esperado)

    def test_todas_heredan_de_motor_ia_error(self):
        for cls in CODIGOS_ESPERADOS:
            with self.subTest(cls=cls.__name__):
                self.assertTrue(issubclass(cls, MotorIAError))

    def test_mensaje_se_preserva(self):
        exc = ProveedorIAError("mensaje de prueba")
        self.assertEqual(exc.mensaje, "mensaje de prueba")
        self.assertEqual(str(exc), "mensaje de prueba")


class TestEntradaIncompletaError(unittest.TestCase):
    def test_campos_default_a_lista_vacia(self):
        exc = EntradaIncompletaError("falta info")
        self.assertEqual(exc.campos, [])

    def test_campos_se_preservan(self):
        exc = EntradaIncompletaError("falta info", campos=["Nombre", "Problema"])
        self.assertEqual(exc.campos, ["Nombre", "Problema"])


if __name__ == "__main__":
    unittest.main()
