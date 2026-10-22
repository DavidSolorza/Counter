"""
Excepciones tipadas de dominio y aplicación para WolfAnalytics.
Gobernanza: Límite estricto < 150 líneas.
"""

class AppException(Exception):
    """Excepción base de la aplicación."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class InvalidSiteKeyException(AppException):
    """Lanzada cuando una clave de sitio no existe en el sistema."""
    def __init__(self, message: str = "Licencia o Site Key inexistente."):
        super().__init__(message, status_code=403)


class InactiveSiteException(AppException):
    """Lanzada cuando un sitio existe pero su licencia está inactiva/bloqueada."""
    def __init__(self, message: str = "Licencia inactiva o suspendida. SDK bloqueado."):
        super().__init__(message, status_code=403)


class InvalidTelemetryPayloadException(AppException):
    """Lanzada cuando el payload de telemetría es inválido o está incompleto."""
    def __init__(self, message: str = "Payload de telemetría inválido o malformado."):
        super().__init__(message, status_code=400)
