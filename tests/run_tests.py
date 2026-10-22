"""
tests/run_tests.py
Batería de pruebas de integración para la arquitectura tripartita y motor analítico.
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
        ok_res = self.client.post("/api/v1/verify", json={"site_key": "wk_test_12345"})
        self.assertEqual(ok_res.status_code, 200)
        self.assertTrue(ok_res.get_json()["valid"])

        err_res = self.client.post("/api/v1/verify", json={"site_key": "falsa_999"})
        self.assertEqual(err_res.status_code, 403)
        self.assertFalse(err_res.get_json()["valid"])

    def test_telemetry_with_rage_clicks_and_scroll(self):
        payload = {
            "site_key": "wk_test_12345",
            "events": [
                {
                    "event_type": "rage_click",
                    "page_url": "http://localhost/test",
                    "event_data": {"element": "button#broken-btn", "clicks": 3}
                },
                {
                    "event_type": "scroll_milestone",
                    "page_url": "http://localhost/test",
                    "event_data": {"depth": "50%"}
                }
            ]
        }
        res = self.client.post(
            "/api/v1/telemetry",
            json=payload,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"}
        )
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json()["success"])

        # Verificar motor de agregación
        summary_res = self.client.get("/api/v1/analytics/summary/wk_test_12345")
        self.assertEqual(summary_res.status_code, 200)
        data = summary_res.get_json()
        self.assertIn("rage_clicks", data)
        self.assertIn("scroll_milestones", data)
        self.assertGreaterEqual(data["rage_clicks"], 1)

    def test_sdk_distribution_endpoints(self):
        for route in ["/sdk/tracker.js", "/counter.js", "/download/counter.js"]:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200)


if __name__ == "__main__":
    unittest.main()
