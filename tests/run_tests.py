"""
Ejecutor de pruebas de integración usando unittest estándar de Python.
Gobernanza: Límite estricto < 150 líneas.
"""
import sys
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import unittest
from app import create_app


class AnalyticsSystemTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_verify_valid_site_key(self):
        response = self.client.post("/api/v1/verify", json={"site_key": "wk_test_12345"})
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["valid"])
        self.assertIn("desbloqueado", data["message"].lower())

    def test_verify_invalid_site_key(self):
        response = self.client.post("/api/v1/verify", json={"site_key": "clave_falsa_999"})
        self.assertEqual(response.status_code, 403)
        data = response.get_json()
        self.assertFalse(data["valid"])

    def test_telemetry_ingestion(self):
        payload = {
            "site_key": "wk_test_12345",
            "events": [
                {"type": "pageview", "target": "Inicio", "url": "http://localhost/test"},
                {"type": "click", "target": "BUTTON#btn-comprar", "url": "http://localhost/test"}
            ]
        }
        response = self.client.post("/api/v1/telemetry", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["stored"], 2)

    def test_tracker_script_served(self):
        response = self.client.get("/tracker.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("javascript", response.content_type)


if __name__ == "__main__":
    unittest.main()
