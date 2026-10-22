"""
Ejecutor de pruebas de integración usando unittest estándar de Python.
Gobernanza: Límite estricto < 150 líneas.
"""
import sys
from pathlib import Path

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

    def test_verify_invalid_site_key(self):
        response = self.client.post("/api/v1/verify", json={"site_key": "clave_falsa_999"})
        self.assertEqual(response.status_code, 403)
        self.assertFalse(response.get_json()["valid"])

    def test_telemetry_flexible_json_payload(self):
        payload = {
            "site_key": "wk_test_12345",
            "events": [
                {
                    "event_type": "click",
                    "page_url": "https://midominio.com/tienda",
                    "event_data": {
                        "element": "button#buy-now",
                        "price": 45.0,
                        "currency": "USD",
                        "custom_attr": "promo_verano"
                    }
                }
            ]
        }
        response = self.client.post("/api/v1/telemetry", json=payload)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["success"])

        # Verificar que se recupera con el objeto JSON íntegro
        stats_resp = self.client.get("/api/v1/events/wk_test_12345?limit=1")
        self.assertEqual(stats_resp.status_code, 200)
        events = stats_resp.get_json()["events"]
        self.assertGreater(len(events), 0)
        saved_data = events[0]["event_data"]
        self.assertEqual(saved_data.get("price"), 45.0)
        self.assertEqual(saved_data.get("currency"), "USD")
        self.assertEqual(saved_data.get("custom_attr"), "promo_verano")

    def test_tracker_script_served(self):
        response = self.client.get("/tracker.js")
        self.assertEqual(response.status_code, 200)
        self.assertIn("javascript", response.content_type)


if __name__ == "__main__":
    unittest.main()
