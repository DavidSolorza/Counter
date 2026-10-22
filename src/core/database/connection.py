"""
Gestión de persistencia SQLite encapsulada.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import ContextManager
from contextlib import contextmanager
import sqlite3
from src.core.config.settings import settings


class DatabaseManager:
    """Administrador de conexiones y ciclo de vida de SQLite."""

    def __init__(self, db_path: str = str(settings.DB_PATH)) -> None:
        self._db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        """Crea y retorna una nueva conexión con row_factory Row activado."""
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @contextmanager
    def session(self) -> ContextManager[sqlite3.Connection]:
        """Context manager transaccional para operaciones seguras."""
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_schema(self, schema_file: str = str(settings.SCHEMA_PATH)) -> None:
        """Ejecuta el script DDL inicial de forma idempotente."""
        with open(schema_file, "r", encoding="utf-8") as f:
            ddl_script = f.read()
        
        with self.session() as conn:
            conn.executescript(ddl_script)


db_manager = DatabaseManager()
