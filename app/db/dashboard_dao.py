"""Video 8.2: consultas exclusivamente de lectura para P1-P4.
No depende de las vistas/procedimientos educativos R1-R12.
"""
from sqlalchemy import text


# Única clasificación a partir de los tres subtipos reales.
# Cuenta pertenencias antes de clasificar para NO ocultar datos inconsistentes.
_CLASIFICACION = """
WITH clasificacion AS (
    SELECT e.codigo_interno,
           (CASE WHEN co.codigo_interno IS NOT NULL THEN 1 ELSE 0 END
          + CASE WHEN tm.codigo_interno IS NOT NULL THEN 1 ELSE 0 END
          + CASE WHEN ta.codigo_interno IS NOT NULL THEN 1 ELSE 0 END) AS n_subtipos,
           CASE
             WHEN co.codigo_interno IS NOT NULL
                  AND tm.codigo_interno IS NULL AND ta.codigo_interno IS NULL THEN 'COMPUTADOR'
             WHEN tm.codigo_interno IS NOT NULL
                  AND co.codigo_interno IS NULL AND ta.codigo_interno IS NULL THEN 'TELEFONO_MOVIL'
             WHEN ta.codigo_interno IS NOT NULL
                  AND co.codigo_interno IS NULL AND tm.codigo_interno IS NULL THEN 'TABLET'
             WHEN co.codigo_interno IS NULL AND tm.codigo_interno IS NULL
                  AND ta.codigo_interno IS NULL THEN 'SIN_CLASIFICAR'
             ELSE 'INCONSISTENTE'
           END AS tipo_equipo
    FROM equipo e
    LEFT JOIN computador co ON co.codigo_interno=e.codigo_interno
    LEFT JOIN telefono_movil tm ON tm.codigo_interno=e.codigo_interno
    LEFT JOIN tablet ta ON ta.codigo_interno=e.codigo_interno
)
"""


def _filas(conn, consulta, parametros):
    return [dict(fila) for fila in conn.execute(text(consulta), parametros).mappings()]


def opciones_filtros(conn):
    sucursales = _filas(conn,
        "SELECT codigo_sucursal,nombre FROM sucursal ORDER BY nombre,codigo_sucursal", {})
    estados = _filas(conn,
        "SELECT DISTINCT estado_actual FROM orden_reparacion ORDER BY estado_actual", {})
    fechas = conn.execute(text("""
        SELECT MIN(fecha_recepcion) AS fecha_min,
               MAX(fecha_recepcion) AS fecha_max
        FROM orden_reparacion
    """)).mappings().one()
    return {"sucursales": sucursales,
            "estados": [fila["estado_actual"] for fila in estados],
            "fecha_min": fechas["fecha_min"], "fecha_max": fechas["fecha_max"]}


def p1_ordenes_tipo(conn, parametros):
    return _filas(conn, _CLASIFICACION + """
        SELECT c.tipo_equipo, COUNT(*) AS cantidad_ordenes
        FROM orden_reparacion o
        JOIN clasificacion c ON c.codigo_interno=o.codigo_interno
        WHERE o.fecha_recepcion BETWEEN :desde AND :hasta
          AND (:sucursal = '' OR o.codigo_sucursal=:sucursal)
          AND (:tipo = '' OR c.tipo_equipo=:tipo)
        GROUP BY c.tipo_equipo
        ORDER BY cantidad_ordenes DESC,c.tipo_equipo
    """, parametros)


def p2_distribucion(conn, parametros):
    return _filas(conn, _CLASIFICACION + """
        SELECT c.tipo_equipo, COUNT(*) AS cantidad_ordenes
        FROM orden_reparacion o
        JOIN clasificacion c ON c.codigo_interno=o.codigo_interno
        WHERE o.fecha_recepcion BETWEEN :desde AND :hasta
          AND (:sucursal = '' OR o.codigo_sucursal=:sucursal)
          AND c.n_subtipos=1
        GROUP BY c.tipo_equipo
        ORDER BY c.tipo_equipo
    """, parametros)


def p2_excluidas(conn, parametros):
    return _filas(conn, _CLASIFICACION + """
        SELECT c.tipo_equipo,COUNT(*) AS cantidad_ordenes
        FROM orden_reparacion o
        JOIN clasificacion c ON c.codigo_interno=o.codigo_interno
        WHERE o.fecha_recepcion BETWEEN :desde AND :hasta
          AND (:sucursal = '' OR o.codigo_sucursal=:sucursal)
          AND c.n_subtipos<>1
        GROUP BY c.tipo_equipo
    """, parametros)


def p3_costos_evaluaciones(conn, parametros):
    # Cada relación N:1 se consolida por numero_orden ANTES de unirse.
    return _filas(conn, """
        WITH mano AS (
            SELECT numero_orden, SUM(costo_mano_obra) AS costo_mano
            FROM intervencion_tecnica GROUP BY numero_orden
        ), repuestos AS (
            SELECT numero_orden, SUM(cantidad*precio_aplicado) AS costo_repuestos
            FROM detalle_repuesto GROUP BY numero_orden
        ), evaluaciones AS (
            SELECT numero_orden, COUNT(*) AS cantidad_evaluaciones,
                   AVG(calificacion) AS evaluacion_promedio,
                   MIN(fecha) AS primera_evaluacion
            FROM evaluacion GROUP BY numero_orden
        )
        SELECT o.numero_orden, o.fecha_recepcion, o.id_cliente,
               cl.nombre AS cliente, o.codigo_interno,
               e.marca, e.modelo, o.codigo_sucursal,
               s.nombre AS sucursal,
               COALESCE(m.costo_mano,0) AS costo_mano_obra,
               COALESCE(r.costo_repuestos,0) AS costo_repuestos,
               COALESCE(m.costo_mano,0)+COALESCE(r.costo_repuestos,0) AS costo_total,
               ev.cantidad_evaluaciones,ev.evaluacion_promedio,ev.primera_evaluacion
        FROM orden_reparacion o
        JOIN cliente cl ON cl.id_cliente=o.id_cliente
        JOIN equipo e ON e.codigo_interno=o.codigo_interno
        JOIN sucursal s ON s.codigo_sucursal=o.codigo_sucursal
        LEFT JOIN mano m ON m.numero_orden=o.numero_orden
        LEFT JOIN repuestos r ON r.numero_orden=o.numero_orden
        JOIN evaluaciones ev ON ev.numero_orden=o.numero_orden
        WHERE o.fecha_recepcion BETWEEN :desde AND :hasta
          AND (:sucursal = '' OR o.codigo_sucursal=:sucursal)
        ORDER BY o.numero_orden
    """, parametros)


def p4_estados_sucursal(conn, parametros):
    return _filas(conn, """
        SELECT s.codigo_sucursal,s.nombre AS sucursal,o.estado_actual,
               COUNT(*) AS cantidad_ordenes
        FROM orden_reparacion o
        JOIN sucursal s ON s.codigo_sucursal=o.codigo_sucursal
        WHERE o.fecha_recepcion BETWEEN :desde AND :hasta
          AND (:sucursal = '' OR o.codigo_sucursal=:sucursal)
          AND (:estado = '' OR o.estado_actual=:estado)
        GROUP BY s.codigo_sucursal,s.nombre,o.estado_actual
        ORDER BY s.nombre,o.estado_actual
    """, parametros)
