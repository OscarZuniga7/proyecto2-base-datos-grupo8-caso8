"""Consultas SQL de lectura sobre las tablas existentes del Caso 8."""
from sqlalchemy import text
from sqlalchemy.engine import Connection


def contar_clientes(conn: Connection) -> int:
    """Cuenta las filas de la tabla real cliente."""
    return int(conn.execute(text("SELECT COUNT(*) FROM cliente")).scalar_one())


def contar_ordenes(conn: Connection) -> int:
    """Cuenta las filas de la tabla real orden_reparacion."""
    return int(conn.execute(text("SELECT COUNT(*) FROM orden_reparacion")).scalar_one())
