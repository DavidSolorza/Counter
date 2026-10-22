"""
Cliente HTTP nativo base usando urllib estándar (Cero SDKs comerciales opacos).
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Dict, Any, Optional
import urllib.request
import urllib.error
import json


class NativeHttpClient:
    """Cliente HTTP estándar para llamadas y webhooks sin dependencias pesadas."""

    def __init__(self, timeout: int = 10) -> None:
        self._timeout = timeout

    def post(self, url: str, data: Dict[str, Any], headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        req_headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if headers:
            req_headers.update(headers)

        json_data = json.dumps(data).encode("utf-8")
        request = urllib.request.Request(url, data=json_data, headers=req_headers, method="POST")

        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                body = response.read().decode("utf-8")
                return json.loads(body) if body else {}
        except urllib.error.HTTPError as ex:
            err_body = ex.read().decode("utf-8")
            return {"error": str(ex), "status_code": ex.code, "detail": err_body}
        except urllib.error.URLError as ex:
            return {"error": "Connection error", "reason": str(ex.reason)}


http_client = NativeHttpClient()
