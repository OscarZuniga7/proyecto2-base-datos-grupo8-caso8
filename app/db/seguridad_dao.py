"""Consultas parametrizadas sobre las tablas reales usuario, rol y usuario_rol."""
from sqlalchemy import text


def usuario_por_nombre(conn, nombre):
    return conn.execute(text("""
        SELECT id_usuario, id_trabajador, nombre_usuario, clave_hash
        FROM usuario WHERE nombre_usuario = :nombre
    """), {"nombre": nombre}).mappings().first()


def usuario_por_id(conn, usuario_id):
    return conn.execute(text("""
        SELECT id_usuario, nombre_usuario FROM usuario WHERE id_usuario = :id
    """), {"id": usuario_id}).mappings().first()


def roles_de_usuario(conn, usuario_id):
    return [r[0] for r in conn.execute(text("""
        SELECT r.nombre FROM rol r
        JOIN usuario_rol ur ON ur.id_rol = r.id_rol
        WHERE ur.id_usuario = :id
        ORDER BY r.nombre
    """), {"id": usuario_id}).all()]


def tiene_rol(conn, usuario_id, nombre_rol):
    return conn.execute(text("""
        SELECT 1 FROM usuario u
        JOIN usuario_rol ur ON u.id_usuario = ur.id_usuario
        JOIN rol r ON ur.id_rol = r.id_rol
        WHERE u.id_usuario = :id AND r.nombre = :rol LIMIT 1
    """), {"id": usuario_id, "rol": nombre_rol}).first() is not None
