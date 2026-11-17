"""Pruebas unitarias sin servidor y prueba opcional de integración MySQL."""
import os
import unittest
from unittest.mock import MagicMock, patch

from db.dao import contar_clientes, contar_ordenes
from services.resumen_service import obtener_resumen


class TestDAO(unittest.TestCase):
    def test_contar_clientes(self):
        conn = MagicMock()
        conn.execute.return_value.scalar_one.return_value = 240
        self.assertEqual(contar_clientes(conn), 240)
        sql = str(conn.execute.call_args.args[0])
        self.assertIn("FROM cliente", sql)

    def test_contar_ordenes(self):
        conn = MagicMock()
        conn.execute.return_value.scalar_one.return_value = 540
        self.assertEqual(contar_ordenes(conn), 540)
        sql = str(conn.execute.call_args.args[0])
        self.assertIn("FROM orden_reparacion", sql)


class TestServicio(unittest.TestCase):
    @patch("services.resumen_service.contar_ordenes", return_value=540)
    @patch("services.resumen_service.contar_clientes", return_value=240)
    @patch("services.resumen_service.check_connection")
    @patch("services.resumen_service.get_engine")
    def test_resumen(self, motor, comprobar, clientes, ordenes):
        self.assertEqual(obtener_resumen(max_intentos=1), {"clientes": 240, "ordenes": 540})
        comprobar.assert_called_once()
        clientes.assert_called_once()
        ordenes.assert_called_once()


@unittest.skipUnless(os.getenv("RUN_DB_INTEGRATION") == "1", "Requiere RUN_DB_INTEGRATION=1")
class TestIntegracion(unittest.TestCase):
    def test_consulta_real(self):
        resumen = obtener_resumen()
        self.assertIsInstance(resumen["clientes"], int)
        self.assertIsInstance(resumen["ordenes"], int)
        self.assertGreaterEqual(resumen["clientes"], 0)
        self.assertGreaterEqual(resumen["ordenes"], 0)


if __name__ == "__main__":
    unittest.main()
