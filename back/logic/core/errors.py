"""
back/logic/core/errors.py
Excepciones tipadas para el backend Counter.
Gobernanza: Límite estricto < 150 líneas.
"""

class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidSiteKeyException(AppException):
    def __init__(self, message: str = "Site Key inválida o inexistente.") -> None:
        super().__init__(message, status_code=403)


class InactiveSiteException(AppException):
    def __init__(self, message: str = "Licencia inactiva o suspendida.") -> None:
        super().__init__(message, status_code=403)


class InvalidPayloadException(AppException):
    def __init__(self, message: str = "Carga de telemetría malformada.") -> None:
        super().__init__(message, status_code=400)
