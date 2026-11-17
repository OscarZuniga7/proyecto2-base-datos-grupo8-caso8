-- CASO 8 | Fase 2 | 04_procedimientos.sql | MySQL 8.4
-- Requisitos oficiales R1, R4, R9, R10, R11, R12.
-- Instruccion: ejecutar con soporte para delimitador $$ (importación de archivo SQL).
USE caso8_reparaciones;
DELIMITER $$

-- R1: tipos de equipo con más órdenes en rango de fecha. Incluye sucursal.
DROP PROCEDURE IF EXISTS sp_r1_tipos_mas_ordenes$$
CREATE PROCEDURE sp_r1_tipos_mas_ordenes(IN p_desde DATE, IN p_hasta DATE)
BEGIN
 IF p_desde IS NULL OR p_hasta IS NULL OR p_desde > p_hasta THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='R1: rango de fechas invalido';
 END IF;
 SELECT CASE WHEN co.codigo_interno IS NOT NULL THEN 'COMPUTADOR'
             WHEN tm.codigo_interno IS NOT NULL THEN 'TELEFONO_MOVIL'
             WHEN ta.codigo_interno IS NOT NULL THEN 'TABLET'
             ELSE 'SIN_CLASIFICAR' END AS tipo_equipo,
        COUNT(*) AS cantidad_ordenes,
        COUNT(DISTINCT s.codigo_sucursal) AS sucursales_involucradas
 FROM orden_reparacion o
 JOIN sucursal s ON s.codigo_sucursal=o.codigo_sucursal
 JOIN equipo e ON e.codigo_interno=o.codigo_interno
 LEFT JOIN computador co ON co.codigo_interno=e.codigo_interno
 LEFT JOIN telefono_movil tm ON tm.codigo_interno=e.codigo_interno
 LEFT JOIN tablet ta ON ta.codigo_interno=e.codigo_interno
 WHERE o.fecha_recepcion BETWEEN p_desde AND p_hasta
 GROUP BY tipo_equipo
 ORDER BY cantidad_ordenes DESC,tipo_equipo;
END$$

-- R4: órdenes y CLIENTES distintos atendidos por sucursal en período.
DROP PROCEDURE IF EXISTS sp_r4_sucursales_actividad$$
CREATE PROCEDURE sp_r4_sucursales_actividad(IN p_desde DATE, IN p_hasta DATE)
BEGIN
 IF p_desde IS NULL OR p_hasta IS NULL OR p_desde > p_hasta THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='R4: rango de fechas invalido';
 END IF;
 SELECT s.codigo_sucursal,s.nombre AS sucursal,
        COUNT(o.numero_orden) AS cantidad_ordenes,
        COUNT(DISTINCT c.id_cliente) AS clientes_distintos
 FROM sucursal s
 LEFT JOIN orden_reparacion o ON o.codigo_sucursal=s.codigo_sucursal
   AND o.fecha_recepcion BETWEEN p_desde AND p_hasta
 LEFT JOIN cliente c ON c.id_cliente=o.id_cliente
 LEFT JOIN equipo e ON e.codigo_interno=o.codigo_interno
 GROUP BY s.codigo_sucursal,s.nombre
 ORDER BY cantidad_ordenes DESC,clientes_distintos DESC,s.codigo_sucursal;
END$$

-- R9: órdenes cuyo costo supera el promedio de órdenes del MISMO TIPO,
-- en el período. Subconsulta CORRELACIONADA sobre tipo_equipo.
-- p_tipo admite COMPUTADOR, TELEFONO_MOVIL, TABLET o SIN_CLASIFICAR.
DROP PROCEDURE IF EXISTS sp_r9_ordenes_sobre_promedio_tipo$$
CREATE PROCEDURE sp_r9_ordenes_sobre_promedio_tipo(
  IN p_tipo VARCHAR(30), IN p_desde DATE, IN p_hasta DATE)
BEGIN
 IF p_desde IS NULL OR p_hasta IS NULL OR p_desde > p_hasta THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='R9: rango de fechas invalido';
 END IF;
 IF p_tipo IS NULL OR p_tipo NOT IN ('COMPUTADOR','TELEFONO_MOVIL','TABLET','SIN_CLASIFICAR') THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='R9: tipo invalido';
 END IF;
 WITH mano AS (
  SELECT numero_orden,SUM(costo_mano_obra) AS importe
  FROM intervencion_tecnica GROUP BY numero_orden
 ), piezas AS (
  SELECT numero_orden,SUM(cantidad*precio_aplicado) AS importe
  FROM detalle_repuesto GROUP BY numero_orden
 ), costos AS (
  SELECT o.numero_orden,o.fecha_recepcion,o.codigo_interno,
   CASE WHEN co.codigo_interno IS NOT NULL THEN 'COMPUTADOR'
        WHEN tm.codigo_interno IS NOT NULL THEN 'TELEFONO_MOVIL'
        WHEN ta.codigo_interno IS NOT NULL THEN 'TABLET'
        ELSE 'SIN_CLASIFICAR' END AS tipo_equipo,
   COALESCE(m.importe,0)+COALESCE(p.importe,0) AS costo_total
  FROM orden_reparacion o
  JOIN equipo e ON e.codigo_interno=o.codigo_interno
  LEFT JOIN computador co ON co.codigo_interno=e.codigo_interno
  LEFT JOIN telefono_movil tm ON tm.codigo_interno=e.codigo_interno
  LEFT JOIN tablet ta ON ta.codigo_interno=e.codigo_interno
  LEFT JOIN mano m ON m.numero_orden=o.numero_orden
  LEFT JOIN piezas p ON p.numero_orden=o.numero_orden
  WHERE o.fecha_recepcion BETWEEN p_desde AND p_hasta
 )
 SELECT k.numero_orden,k.codigo_interno,k.tipo_equipo,k.fecha_recepcion,
        k.costo_total,
        (SELECT ROUND(AVG(k2.costo_total),2) FROM costos k2
         WHERE k2.tipo_equipo=k.tipo_equipo) AS promedio_mismo_tipo
 FROM costos k
 WHERE k.tipo_equipo=p_tipo
   AND k.costo_total > (SELECT AVG(k3.costo_total) FROM costos k3
                       WHERE k3.tipo_equipo=k.tipo_equipo)
 ORDER BY k.costo_total DESC,k.numero_orden;
END$$

-- R10: uso por repuesto y sucursal; promedio de cantidad TOTAL entre los
-- repuestos USADOS en esa sucursal. Subconsulta correlacionada por sucursal.
DROP PROCEDURE IF EXISTS sp_r10_repuestos_sobre_promedio$$
CREATE PROCEDURE sp_r10_repuestos_sobre_promedio(IN p_sucursal VARCHAR(20))
BEGIN
 IF p_sucursal IS NULL OR NOT EXISTS (
   SELECT 1 FROM sucursal WHERE codigo_sucursal=p_sucursal
 ) THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='R10: sucursal inexistente';
 END IF;
 WITH consumos AS (
 SELECT s.codigo_sucursal,s.nombre AS sucursal,
        r.numero_repuesto,r.tipo AS tipo_repuesto,
        SUM(d.cantidad) AS cantidad_total
 FROM sucursal s
 JOIN orden_reparacion o ON o.codigo_sucursal=s.codigo_sucursal
 JOIN detalle_repuesto d ON d.numero_orden=o.numero_orden
 JOIN repuesto r ON r.numero_repuesto=d.numero_repuesto
 GROUP BY s.codigo_sucursal,s.nombre,r.numero_repuesto,r.tipo
 )
 SELECT c.codigo_sucursal,c.sucursal,c.numero_repuesto,c.tipo_repuesto,
        c.cantidad_total,
        (SELECT ROUND(AVG(c2.cantidad_total),2)
         FROM consumos c2 WHERE c2.codigo_sucursal=c.codigo_sucursal)
           AS promedio_uso_repuestos_sucursal
 FROM consumos c
 WHERE c.codigo_sucursal=p_sucursal
 AND c.cantidad_total > (
   SELECT AVG(c3.cantidad_total) FROM consumos c3
   WHERE c3.codigo_sucursal=c.codigo_sucursal
 )
 ORDER BY c.cantidad_total DESC,c.numero_repuesto;
END$$

-- R11: clientes con (1) más órdenes que la media de órdenes POR CLIENTE
-- (incluye clientes sin órdenes) y (2) evaluación media mayor que la media
-- de todas las evaluaciones de órdenes recibidas en el rango.
-- La relación adicional EQUIPO existe en el modelo; no multiplica filas.
DROP PROCEDURE IF EXISTS sp_r11_clientes_sobre_promedios$$
CREATE PROCEDURE sp_r11_clientes_sobre_promedios(IN p_desde DATE, IN p_hasta DATE)
BEGIN
 IF p_desde IS NULL OR p_hasta IS NULL OR p_desde > p_hasta THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='R11: rango de fechas invalido';
 END IF;
 WITH por_cliente AS (
  SELECT c.id_cliente,c.nombre AS cliente,
         COUNT(DISTINCT o.numero_orden) AS cantidad_ordenes,
         AVG(ev.calificacion) AS promedio_evaluacion
  FROM cliente c
  LEFT JOIN orden_reparacion o ON o.id_cliente=c.id_cliente
    AND o.fecha_recepcion BETWEEN p_desde AND p_hasta
  LEFT JOIN equipo eq ON eq.codigo_interno=o.codigo_interno
  LEFT JOIN evaluacion ev ON ev.numero_orden=o.numero_orden
  GROUP BY c.id_cliente,c.nombre
 ), promedio_global AS (
  SELECT AVG(ev.calificacion) AS promedio_evaluaciones
  FROM evaluacion ev
  JOIN orden_reparacion o ON o.numero_orden=ev.numero_orden
  WHERE o.fecha_recepcion BETWEEN p_desde AND p_hasta
 )
 SELECT pc.id_cliente,pc.cliente,pc.cantidad_ordenes,
        ROUND(pc.promedio_evaluacion,2) AS promedio_evaluacion_cliente,
        (SELECT ROUND(AVG(pc2.cantidad_ordenes),2) FROM por_cliente pc2)
            AS promedio_ordenes_clientes,
        ROUND(pg.promedio_evaluaciones,2) AS promedio_general_evaluaciones
 FROM por_cliente pc
 CROSS JOIN promedio_global pg
 WHERE pc.cantidad_ordenes > (SELECT AVG(pc3.cantidad_ordenes) FROM por_cliente pc3)
   AND pc.promedio_evaluacion > pg.promedio_evaluaciones
 ORDER BY pc.cantidad_ordenes DESC,pc.promedio_evaluacion DESC;
END$$

-- R12: sucursales con coste promedio por orden superior a la media
-- NO ponderada de los promedios de sucursales que tuvieron órdenes.
DROP PROCEDURE IF EXISTS sp_r12_sucursales_costo_sobre_promedio$$
CREATE PROCEDURE sp_r12_sucursales_costo_sobre_promedio(IN p_desde DATE, IN p_hasta DATE)
BEGIN
 IF p_desde IS NULL OR p_hasta IS NULL OR p_desde > p_hasta THEN
   SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='R12: rango de fechas invalido';
 END IF;
 WITH mano AS (
  SELECT numero_orden,SUM(costo_mano_obra) AS importe FROM intervencion_tecnica GROUP BY numero_orden
 ), piezas AS (
  SELECT numero_orden,SUM(cantidad*precio_aplicado) AS importe FROM detalle_repuesto GROUP BY numero_orden
 ), costo_orden AS (
  SELECT s.codigo_sucursal,s.nombre AS sucursal,o.numero_orden,
     COALESCE(m.importe,0)+COALESCE(p.importe,0) AS costo_total
  FROM sucursal s JOIN orden_reparacion o ON o.codigo_sucursal=s.codigo_sucursal
  LEFT JOIN mano m ON m.numero_orden=o.numero_orden
  LEFT JOIN piezas p ON p.numero_orden=o.numero_orden
  WHERE o.fecha_recepcion BETWEEN p_desde AND p_hasta
 ), por_sucursal AS (
  SELECT codigo_sucursal,sucursal,COUNT(*) AS cantidad_ordenes,
   AVG(costo_total) AS costo_promedio_sucursal
  FROM costo_orden GROUP BY codigo_sucursal,sucursal
 )
 SELECT ps.codigo_sucursal,ps.sucursal,ps.cantidad_ordenes,
        ROUND(ps.costo_promedio_sucursal,2) AS costo_promedio_sucursal,
        (SELECT ROUND(AVG(ps2.costo_promedio_sucursal),2) FROM por_sucursal ps2)
          AS promedio_general_sucursales
 FROM por_sucursal ps
 WHERE ps.costo_promedio_sucursal > (
   SELECT AVG(ps3.costo_promedio_sucursal) FROM por_sucursal ps3
 )
 ORDER BY ps.costo_promedio_sucursal DESC,ps.codigo_sucursal;
END$$
DELIMITER ;
