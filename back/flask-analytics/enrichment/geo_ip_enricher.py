"""
backend/enrichment/geo_ip_enricher.py
Enriquecedor de IP y contexto geográfico sin llamadas síncronas bloqueantes.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Dict, Any, Optional
import ipaddress


class GeoIpEnricher:
    """Extrae la IP del cliente y añade información de red."""

    @staticmethod
    def extract_ip(headers: Dict[str, str], remote_addr: Optional[str]) -> str:
        forwarded = headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        return remote_addr or "127.0.0.1"

    @classmethod
    def enrich(cls, ip_str: str) -> Dict[str, Any]:
        is_private = True
        try:
            ip_obj = ipaddress.ip_address(ip_str)
            is_private = ip_obj.is_private or ip_obj.is_loopback
        except ValueError:
            pass

        return {
            "client_ip": ip_str,
            "is_local": is_private,
            "location": "Local Network" if is_private else "Global Web"
        }


geo_enricher = GeoIpEnricher()
