"""Capa de negocio: disponibilidad y resumen de actividad."""
import time
from sqlalchemy.exc import SQLAlchemyError

from db.connection import get_engine, check_connection
from db.dao import contar_clientes, contar_ordenes


class DatabaseUnavailable(Exception):
    """La base no respondió o las consultas no pudieron completarse."""


def obtener_resumen(max_intentos: int = 4, espera_segundos: float = 2.0) -> dict[str, int]:
    """Reintenta una conexión no lista y consulta ambas métricas en una sesión."""
    if max_intentos < 1:
        raise ValueError("max_intentos debe ser al menos 1")
    try:
        engine = get_engine()
    except (RuntimeError, ValueError) as exc:
        raise DatabaseUnavailable("Configuración de base de datos incompleta") from exc

    for intento in range(max_intentos):
        try:
            check_connection(engine)
            with engine.connect() as conn:
                return {
                    "clientes": contar_clientes(conn),
                    "ordenes": contar_ordenes(conn),
                }
        except SQLAlchemyError as exc:
            if intento == max_intentos - 1:
                raise DatabaseUnavailable(
                    "No fue posible consultar MySQL. Revise los contenedores y las credenciales."
                ) from exc
            time.sleep(espera_segundos)

    raise DatabaseUnavailable("No se pudo consultar MySQL")
