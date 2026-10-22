"""
database/connection.py
Gestión de persistencia SQLite encapsulada y migraciones automáticas.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import ContextManager
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import os

BASE_DIR = Path(__file__).resolve().parent.parent
DB_FILE = os.getenv("WOLF_DB_PATH", str(BASE_DIR / "local_analytics.db"))
SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"


class DatabaseManager:
    """Administrador centralizado de conexiones y esquemas de persistencia."""

    def __init__(self, db_path: str = DB_FILE) -> None:
        self._db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    @contextmanager
    def session(self) -> ContextManager[sqlite3.Connection]:
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize_schema(self) -> None:
        """Aplica el DDL base y migraciones de forma idempotente."""
        initial_sql = SCHEMAS_DIR / "001_initial_schema.sql"
        with open(initial_sql, "r", encoding="utf-8") as f:
            script = f.read()

        with self.session() as conn:
            conn.executescript(script)
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(telemetry_events);")
            cols = [c["name"] for c in cursor.fetchall()]
            if "event_data" not in cols:
                mig_sql = SCHEMAS_DIR / "002_hybrid_json_schema.sql"
                if mig_sql.exists():
                    with open(mig_sql, "r", encoding="utf-8") as mf:
                        conn.executescript(mf.read())


db = DatabaseManager()
