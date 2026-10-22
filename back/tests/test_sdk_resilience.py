"""
back/tests/test_sdk_resilience.py
Pruebas de seguridad, resiliencia y rate limiting para la plataforma Counter.
Gobernanza: Límite estricto < 150 líneas.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import unittest
from back.app import create_app
from back.logic.core.rate_limiter import rate_limiter


class CounterResilienceTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()
        rate_limiter.reset()

    def test_rate_limiter_protection(self):
        """El rate limiter debe bloquear con 429 tras saturar el límite de peticiones."""
        payload = {"site_key": "wk_test_12345", "events": [{"event_type": "ping"}]}

        # Realizar 120 peticiones permitidas
        for _ in range(120):
            res = self.client.post("/api/v1/telemetry", json=payload)
            self.assertEqual(res.status_code, 200)

        # La petición 121 debe ser rechazada con 429 Too Many Requests
        blocked_res = self.client.post("/api/v1/telemetry", json=payload)
        self.assertEqual(blocked_res.status_code, 429)
        self.assertIn("excedido", blocked_res.get_json()["error"].lower())

    def test_counter_download_endpoints(self):
        """Debe entregar la librería tanto vía script tag como archivo descargable."""
        for route in ["/counter.js", "/sdk/counter.js"]:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200)
            self.assertIn("javascript", res.content_type)

        dl_res = self.client.get("/download/counter.js")
        self.assertEqual(dl_res.status_code, 200)
        self.assertIn("attachment", dl_res.headers.get("Content-Disposition", ""))

    def test_api_status_route(self):
        """La ruta raíz de la API debe responder con el estado del servicio."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "online")


if __name__ == "__main__":
    unittest.main()
