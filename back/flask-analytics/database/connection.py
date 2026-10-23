"""
back/flask-analytics/database/connection.py
Conexión PostgreSQL (con pool de conexiones) para el microservicio de analítica.
Gobernanza: Límite estricto < 150 líneas.
"""
from typing import ContextManager, Any
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool

try:
    from core.config import config
except ImportError:
    from ..core.config import config


class AnalyticsDatabaseManager:
    def __init__(self, dsn: str = config.DATABASE_URL) -> None:
        self._dsn = dsn
        self._pool: ThreadedConnectionPool | None = None

    def _get_pool(self) -> ThreadedConnectionPool | None:
        if self._pool is None:
            try:
                self._pool = ThreadedConnectionPool(
                    minconn=1,
                    maxconn=20,
                    dsn=self._dsn,
                    cursor_factory=RealDictCursor
                )
            except Exception as e:
                print(f"[Counter PG Pool Error]: {e}")
                self._pool = None
        return self._pool

    def get_connection(self) -> Any:
        pool = self._get_pool()
        if pool is not None:
            return pool.getconn()
        return psycopg2.connect(self._dsn, cursor_factory=RealDictCursor)

    def release_connection(self, conn: Any) -> None:
        if conn is None:
            return
        pool = self._get_pool()
        if pool is not None:
            try:
                pool.putconn(conn)
                return
            except Exception:
                pass
        try:
            conn.close()
        except Exception:
            pass

    @contextmanager
    def session(self) -> ContextManager[Any]:
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            self.release_connection(conn)

    def initialize_schema(self) -> None:
        """Verifica conectividad con PostgreSQL y asegura función auxiliar json_extract."""
        try:
            with self.session() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE OR REPLACE FUNCTION json_extract(data jsonb, path text)
                        RETURNS text LANGUAGE sql IMMUTABLE AS $$
                            SELECT jsonb_extract_path_text(data, VARIADIC string_to_array(regexp_replace(path, '^\\$\\.?', ''), '.'));
                        $$;
                    """)
        except Exception as e:
            print(f"[Counter DB Init Warning]: {e}")


db = AnalyticsDatabaseManager()
