"""
back/logic/core/rate_limiter.py
Limitador de tasa en memoria (Sliding Window) para protección contra spam y DoS.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import Dict, List
import time


class MemoryRateLimiter:
    """Implementa limitación de peticiones por clave (IP o Site Key)."""

    def __init__(self) -> None:
        self._requests: Dict[str, List[float]] = {}

    def is_allowed(self, identifier: str, max_requests: int = 120, window_seconds: int = 60) -> bool:
        now = time.time()
        cutoff = now - window_seconds

        if identifier not in self._requests:
            self._requests[identifier] = []

        self._requests[identifier] = [t for t in self._requests[identifier] if t > cutoff]

        if len(self._requests[identifier]) >= max_requests:
            return False

        self._requests[identifier].append(now)
        return True

    def reset(self) -> None:
        """Limpia el registro de peticiones (útil para pruebas)."""
        self._requests.clear()


rate_limiter = MemoryRateLimiter()
