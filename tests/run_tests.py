"""
tests/run_tests.py
Batería de pruebas de integración para la arquitectura tripartita (sdk / backend / database).
Gobernanza: Límite estricto < 150 líneas.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import unittest
from backend.app import create_app


class TripartiteAnalyticsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_handshake_flow(self):
        # Clave válida
        ok_res = self.client.post("/api/v1/verify", json={"site_key": "wk_test_12345"})
        self.assertEqual(ok_res.status_code, 200)
        self.assertTrue(ok_res.get_json()["valid"])

        # Clave inválida
        err_res = self.client.post("/api/v1/verify", json={"site_key": "falsa_999"})
        self.assertEqual(err_res.status_code, 403)
        self.assertFalse(err_res.get_json()["valid"])

    def test_telemetry_with_performance_and_enrichment(self):
        payload = {
            "site_key": "wk_test_12345",
            "events": [
                {
                    "event_type": "web_vitals",
                    "page_url": "http://localhost/test",
                    "event_data": {"ttfb_ms": 85, "load_time_ms": 720}
                },
                {
                    "event_type": "client_error",
                    "page_url": "http://localhost/test",
                    "event_data": {"message": "Simulated error in checkout"}
                }
            ]
        }
        res = self.client.post(
            "/api/v1/telemetry",
            json=payload,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

        # Verificar enriquecimiento en base de datos
        events_res = self.client.get("/api/v1/events/wk_test_12345?limit=2")
        self.assertEqual(events_res.status_code, 200)
        stored_events = events_res.get_json()["events"]
        self.assertGreaterEqual(len(stored_events), 2)
        
        # Validar metadata inyectada por el backend
        first_event_data = stored_events[0]["event_data"]
        self.assertIn("_client", first_event_data)
        self.assertEqual(first_event_data["_client"]["browser"], "Chrome")
        self.assertEqual(first_event_data["_client"]["os"], "Windows")
        self.assertIn("_network", first_event_data)

    def test_sdk_distribution_endpoints(self):
        # Comprobar distribución desde /sdk/tracker.js y /tracker.js
        for route in ["/sdk/tracker.js", "/tracker.js"]:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200)
            self.assertIn("javascript", res.content_type)


if __name__ == "__main__":
    unittest.main()
