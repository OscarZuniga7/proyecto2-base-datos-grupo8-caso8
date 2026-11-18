"""Persistencia parametrizada. Solo tablas y columnas del DDL original."""
from sqlalchemy import text, bindparam, Numeric
from sqlalchemy.engine import Connection


def _rows(conn: Connection, sql: str, **values):
    return [dict(r) for r in conn.execute(text(sql), values).mappings().all()]


def clientes(conn):
    return _rows(conn, "SELECT id_cliente,nombre FROM cliente ORDER BY nombre,id_cliente")


def sucursales(conn):
    return _rows(conn, "SELECT codigo_sucursal,nombre FROM sucursal ORDER BY nombre,codigo_sucursal")


def estados_existentes(conn):
    # No se crea un catálogo de estados ni se inventan valores.
    return [r['estado_actual'] for r in _rows(conn, "SELECT DISTINCT estado_actual FROM orden_reparacion ORDER BY estado_actual")]


def equipos_de_cliente(conn, id_cliente):
    return _rows(conn, "SELECT codigo_interno,marca,modelo FROM equipo WHERE id_cliente=:cliente ORDER BY codigo_interno", cliente=id_cliente)


def equipos(conn, filtro=''):
    return _rows(conn, """SELECT codigo_interno,id_cliente,marca,modelo,numero_serie,fecha_aprox_compra,estado_conservacion
       FROM equipo WHERE codigo_interno LIKE :f OR marca LIKE :f OR modelo LIKE :f OR numero_serie LIKE :f
       ORDER BY codigo_interno LIMIT 300""", f=f'%{filtro}%')


def repuestos(conn, filtro=''):
    return _rows(conn, """SELECT numero_repuesto,tipo,precio_referencia,disponibilidad
       FROM repuesto WHERE CAST(numero_repuesto AS CHAR) LIKE :f OR tipo LIKE :f
       ORDER BY numero_repuesto LIMIT 300""", f=f'%{filtro}%')


def ordenes_recientes(conn):
    return _rows(conn, """SELECT numero_orden,id_cliente,codigo_interno,codigo_sucursal,fecha_recepcion,
       fecha_comprometida,estado_actual FROM orden_reparacion ORDER BY numero_orden DESC LIMIT 15""")


def crear_orden(conn, data):
    result = conn.execute(text("""INSERT INTO orden_reparacion
      (id_cliente,codigo_interno,codigo_sucursal,fecha_recepcion,fecha_comprometida,problema_informado,estado_actual)
      VALUES (:id_cliente,:codigo_interno,:codigo_sucursal,:fecha_recepcion,:fecha_comprometida,:problema_informado,:estado_actual)"""), data)
    return result.lastrowid


def crear_equipo(conn, data):
    conn.execute(text("""INSERT INTO equipo
      (codigo_interno,id_cliente,marca,modelo,numero_serie,fecha_aprox_compra,estado_conservacion)
      VALUES (:codigo_interno,:id_cliente,:marca,:modelo,:numero_serie,:fecha_aprox_compra,:estado_conservacion)"""), data)


def modificar_equipo(conn, codigo, data):
    return conn.execute(text("""UPDATE equipo SET id_cliente=:id_cliente,marca=:marca,modelo=:modelo,
      numero_serie=:numero_serie,fecha_aprox_compra=:fecha_aprox_compra,
      estado_conservacion=:estado_conservacion WHERE codigo_interno=:codigo"""), {**data, 'codigo':codigo}).rowcount


def eliminar_equipo(conn, codigo):
    return conn.execute(text('DELETE FROM equipo WHERE codigo_interno=:codigo'), {'codigo':codigo}).rowcount


def crear_repuesto(conn, data):
    return conn.execute(text("""INSERT INTO repuesto (tipo,precio_referencia,disponibilidad)
      VALUES (:tipo,:precio_referencia,:disponibilidad)""").bindparams(bindparam("precio_referencia", type_=Numeric(12,2))), data).lastrowid


def modificar_repuesto(conn, numero, data):
    return conn.execute(text("""UPDATE repuesto SET tipo=:tipo,precio_referencia=:precio_referencia,
      disponibilidad=:disponibilidad WHERE numero_repuesto=:numero""").bindparams(bindparam("precio_referencia", type_=Numeric(12,2))), {**data,'numero':numero}).rowcount


def eliminar_repuesto(conn, numero):
    return conn.execute(text('DELETE FROM repuesto WHERE numero_repuesto=:numero'), {'numero':numero}).rowcount
