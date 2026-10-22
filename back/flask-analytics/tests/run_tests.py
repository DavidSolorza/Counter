"""
back/flask-analytics/tests/run_tests.py
Pruebas automatizadas para el microservicio de analítica Flask.
Gobernanza: Límite estricto < 150 líneas.
"""
import sys
from pathlib import Path

FLASK_DIR = Path(__file__).resolve().parent.parent
if str(FLASK_DIR) not in sys.path:
    sys.path.insert(0, str(FLASK_DIR))

import unittest
from app import create_app


class AnalyticsMicroserviceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def test_health_check(self):
        res = self.client.get("/health")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "UP")
        self.assertEqual(data.get("database"), "analytics.db")

    def test_collect_telemetry_batch(self):
        payload = {
            "site_key": "wk_test_12345",
            "events": [
                {
                    "event_type": "click",
                    "page_url": "http://localhost:5000/test",
                    "event_data": {"element": "button#demo", "visual": {"type": "button", "text": "Demo"}}
                },
                {
                    "event_type": "scroll_milestone",
                    "page_url": "http://localhost:5000/test",
                    "event_data": {"depth": "75%"}
                }
            ]
        }
        res = self.client.post("/api/v1/telemetry/collect", json=payload)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(res.get_json().get("success"))

        summary = self.client.get("/api/v1/analytics/summary/wk_test_12345")
        self.assertEqual(summary.status_code, 200)
        self.assertIn("total_events", summary.get_json())


if __name__ == "__main__":
    unittest.main()
