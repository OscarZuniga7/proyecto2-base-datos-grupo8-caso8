"""Configuración centralizada de SQLAlchemy para MySQL."""
import os
from functools import lru_cache

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine


def database_url() -> URL:
    """Construye una URL segura sin concatenar contraseñas manualmente."""
    password = os.getenv("DB_PASSWORD")
    if not password:
        raise RuntimeError("Falta la variable de entorno DB_PASSWORD")
    return URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("DB_USER", "root"),
        password=password,
        host=os.getenv("DB_HOST", "db"),
        port=int(os.getenv("DB_PORT", "3306")),
        database=os.getenv("DB_NAME", "caso8_reparaciones"),
        query={"charset": "utf8mb4"},
    )


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    """Crea el pool una sola vez; no abre la conexión hasta que se solicita."""
    return create_engine(
        database_url(),
        pool_pre_ping=True,
        pool_recycle=1800,
        connect_args={"connect_timeout": 3},
    )


def check_connection(engine: Engine) -> None:
    """Si MySQL no está disponible, SQLAlchemy emitirá una excepción."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
