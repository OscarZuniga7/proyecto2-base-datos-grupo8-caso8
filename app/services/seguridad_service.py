"""Autenticación y autorización del PMV, separadas de Streamlit y de SQL."""
import bcrypt
from sqlalchemy.exc import SQLAlchemyError
from db.connection import get_engine
from db import seguridad_dao as dao


class AccesoDenegado(Exception):
    """Credenciales no válidas o permiso insuficiente."""


# Se usa para verificar una contraseña incluso si el usuario no existe.
# No corresponde a ninguna cuenta real.
_HASH_FICTICIO = bcrypt.hashpw(b"dummy-does-not-authenticate", bcrypt.gensalt(rounds=12))


def autenticar(nombre_usuario, contrasena):
    nombre = str(nombre_usuario or "").strip()
    if not nombre or not isinstance(contrasena, str) or not contrasena:
        raise AccesoDenegado("Credenciales inválidas.")
    try:
        with get_engine().connect() as conn:
            fila = dao.usuario_por_nombre(conn, nombre)
            hash_guardado = str(fila["clave_hash"]) if fila else ""
            # Las cuentas sintéticas antiguas usan PBKDF2; sólo se aceptan
            # hashes bcrypt aprovisionados explícitamente para esta etapa.
            hash_verificable = hash_guardado.startswith(("$2a$", "$2b$", "$2y$"))
            candidato = hash_guardado.encode() if hash_verificable else _HASH_FICTICIO
            try:
                valido = bcrypt.checkpw(contrasena.encode("utf-8"), candidato)
            except (ValueError, TypeError):
                valido = False
            if not fila or not hash_verificable or not valido:
                raise AccesoDenegado("Credenciales inválidas.")
            roles = dao.roles_de_usuario(conn, fila["id_usuario"])
            if not roles:
                raise AccesoDenegado("Cuenta sin roles habilitados.")
            return {"id_usuario": fila["id_usuario"],
                    "nombre_usuario": fila["nombre_usuario"], "roles": roles}
    except SQLAlchemyError as exc:
        raise AccesoDenegado("No se pudo consultar MySQL; revise los servicios.") from exc


def obtener_sesion(usuario_id):
    """Revalida usuario y roles en MySQL en cada ejecución de la interfaz."""
    if not isinstance(usuario_id, int):
        return None
    try:
        with get_engine().connect() as conn:
            usuario = dao.usuario_por_id(conn, usuario_id)
            if not usuario:
                return None
            roles = dao.roles_de_usuario(conn, usuario_id)
            if not roles:
                return None
            return {"id_usuario": usuario_id,
                    "nombre_usuario": usuario["nombre_usuario"], "roles": roles}
    except SQLAlchemyError:
        return None


def exigir_administrador(conn, usuario_id):
    """Autoriza cada transacción según el rol REAL en BD, no según botones."""
    if not isinstance(usuario_id, int) or not dao.tiene_rol(conn, usuario_id, "Administrador"):
        raise AccesoDenegado("Acceso denegado: se requiere el rol Administrador.")
