"""
back/flask-analytics/database/connection.py
Conexión SQLite nativa para el microservicio de analítica.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import ContextManager
from contextlib import contextmanager
from pathlib import Path
import sqlite3
import os

DB_PATH = Path(__file__).resolve().parent.parent / "analytics.db"
SCHEMAS_DIR = Path(__file__).resolve().parent / "schemas"


class AnalyticsDatabaseManager:
    def __init__(self, db_path: str = str(DB_PATH)) -> None:
        self._db_path = db_path

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
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
        schema_file = SCHEMAS_DIR / "001_analytics_schema.sql"
        if schema_file.exists():
            with open(schema_file, "r", encoding="utf-8") as f:
                script = f.read()
            with self.session() as conn:
                conn.executescript(script)


db = AnalyticsDatabaseManager()
