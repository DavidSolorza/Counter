"""
backend/enrichment/user_agent_parser.py
Parser nativo ultrarrápido de User-Agent sin librerías externas pesadas.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Dict, Any


class UserAgentParser:
    """Extrae navegador, sistema operativo y tipo de dispositivo del User-Agent."""

    @staticmethod
    def parse(user_agent_str: str) -> Dict[str, Any]:
        ua = (user_agent_str or "").lower()

        # Detección de Dispositivo
        device = "desktop"
        if "tablet" in ua or "ipad" in ua:
            device = "tablet"
        elif "mobile" in ua or "android" in ua or "iphone" in ua:
            device = "mobile"

        # Detección de Sistema Operativo
        os_name = "Other"
        if "windows" in ua:
            os_name = "Windows"
        elif "macintosh" in ua or "mac os" in ua:
            os_name = "macOS"
        elif "iphone" in ua or "ipad" in ua:
            os_name = "iOS"
        elif "android" in ua:
            os_name = "Android"
        elif "linux" in ua:
            os_name = "Linux"

        # Detección de Navegador
        browser = "Other"
        if "edg/" in ua:
            browser = "Edge"
        elif "opr/" in ua or "opera" in ua:
            browser = "Opera"
        elif "chrome/" in ua and "chromium" not in ua:
            browser = "Chrome"
        elif "firefox/" in ua:
            browser = "Firefox"
        elif "safari/" in ua and "chrome" not in ua:
            browser = "Safari"

        return {
            "browser": browser,
            "os": os_name,
            "device": device
        }


ua_parser = UserAgentParser()
