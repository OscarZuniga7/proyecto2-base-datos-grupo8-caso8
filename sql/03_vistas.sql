-- CASO 8 | Fase 2 | 03_vistas.sql | MySQL 8.4
-- Requisitos oficiales: R2, R3, R5, R6, R7, R8.
-- No modifica tablas ni datos. Compatible con DDL provisional adjunto.
USE caso8_reparaciones;

-- R2: distribución porcentual de órdenes de COMPUTADOR / TELEFONO_MOVIL / TABLET por sucursal.
-- Denominador = órdenes de las TRES categorías oficiales dentro de cada sucursal.
-- Los equipos sin clasificar se excluyen deliberadamente de este porcentaje.
DROP VIEW IF EXISTS v_r2_distribucion_equipos_sucursal;
CREATE VIEW v_r2_distribucion_equipos_sucursal AS
WITH base AS (
  SELECT s.codigo_sucursal, s.nombre AS sucursal,
         CASE WHEN co.codigo_interno IS NOT NULL THEN 'COMPUTADOR'
              WHEN tm.codigo_interno IS NOT NULL THEN 'TELEFONO_MOVIL'
              WHEN ta.codigo_interno IS NOT NULL THEN 'TABLET'
              ELSE 'SIN_CLASIFICAR' END AS tipo_equipo
  FROM orden_reparacion o
  JOIN sucursal s ON s.codigo_sucursal = o.codigo_sucursal
  JOIN equipo e ON e.codigo_interno = o.codigo_interno
  LEFT JOIN computador co ON co.codigo_interno = e.codigo_interno
  LEFT JOIN telefono_movil tm ON tm.codigo_interno = e.codigo_interno
  LEFT JOIN tablet ta ON ta.codigo_interno = e.codigo_interno
), totales AS (
 SELECT codigo_sucursal, sucursal, tipo_equipo, COUNT(*) AS cantidad_ordenes
 FROM base WHERE tipo_equipo <> 'SIN_CLASIFICAR'
 GROUP BY codigo_sucursal, sucursal, tipo_equipo
)
SELECT codigo_sucursal, sucursal, tipo_equipo, cantidad_ordenes,
       ROUND(100.0 * cantidad_ordenes /
         NULLIF(SUM(cantidad_ordenes) OVER (PARTITION BY codigo_sucursal),0),2) AS porcentaje_sucursal
FROM totales;

-- R3: costo por orden vs evaluación posterior del cliente.
-- Agregar primero cada relación 1:N evita multiplicar costos por productos cartesianos.
-- Si una orden tiene múltiples evaluaciones, se presenta su promedio y su cantidad.
DROP VIEW IF EXISTS v_r3_costo_evaluacion;
CREATE VIEW v_r3_costo_evaluacion AS
WITH mano AS (
 SELECT numero_orden, SUM(costo_mano_obra) AS costo_mano_obra
 FROM intervencion_tecnica GROUP BY numero_orden
), piezas AS (
 SELECT numero_orden, SUM(cantidad * precio_aplicado) AS costo_repuestos
 FROM detalle_repuesto GROUP BY numero_orden
), notas AS (
 SELECT numero_orden, COUNT(*) AS cantidad_evaluaciones,
        ROUND(AVG(calificacion),2) AS calificacion_promedio,
        MIN(fecha) AS primera_evaluacion
 FROM evaluacion GROUP BY numero_orden
)
SELECT o.numero_orden, o.fecha_recepcion, o.codigo_sucursal, o.id_cliente,
       o.codigo_interno,
       COALESCE(m.costo_mano_obra,0) AS costo_mano_obra,
       COALESCE(p.costo_repuestos,0) AS costo_repuestos,
       COALESCE(m.costo_mano_obra,0)+COALESCE(p.costo_repuestos,0) AS costo_total,
       n.cantidad_evaluaciones,n.calificacion_promedio,n.primera_evaluacion
FROM orden_reparacion o
JOIN notas n ON n.numero_orden=o.numero_orden
LEFT JOIN mano m ON m.numero_orden=o.numero_orden
LEFT JOIN piezas p ON p.numero_orden=o.numero_orden;

-- R5: costo promedio por tipo, sumando previamente costos por orden.
DROP VIEW IF EXISTS v_r5_costo_promedio_tipo;
CREATE VIEW v_r5_costo_promedio_tipo AS
WITH mano AS (
 SELECT numero_orden, SUM(costo_mano_obra) AS importe FROM intervencion_tecnica GROUP BY numero_orden
), piezas AS (
 SELECT numero_orden, SUM(cantidad*precio_aplicado) AS importe FROM detalle_repuesto GROUP BY numero_orden
), ordenes AS (
 SELECT o.numero_orden,
   CASE WHEN co.codigo_interno IS NOT NULL THEN 'COMPUTADOR'
        WHEN tm.codigo_interno IS NOT NULL THEN 'TELEFONO_MOVIL'
        WHEN ta.codigo_interno IS NOT NULL THEN 'TABLET'
        ELSE 'SIN_CLASIFICAR' END AS tipo_equipo,
   COALESCE(m.importe,0) AS costo_mano_obra,
   COALESCE(p.importe,0) AS costo_repuestos
 FROM orden_reparacion o
 JOIN equipo e ON e.codigo_interno=o.codigo_interno
 LEFT JOIN computador co ON co.codigo_interno=e.codigo_interno
 LEFT JOIN telefono_movil tm ON tm.codigo_interno=e.codigo_interno
 LEFT JOIN tablet ta ON ta.codigo_interno=e.codigo_interno
 LEFT JOIN mano m ON m.numero_orden=o.numero_orden
 LEFT JOIN piezas p ON p.numero_orden=o.numero_orden
)
SELECT tipo_equipo, COUNT(*) AS cantidad_ordenes,
 ROUND(AVG(costo_mano_obra),2) AS promedio_mano_obra,
 ROUND(AVG(costo_repuestos),2) AS promedio_repuestos,
 ROUND(AVG(costo_mano_obra+costo_repuestos),2) AS costo_promedio_total
FROM ordenes GROUP BY tipo_equipo;

-- R6: fallas detectadas en órdenes y número de intervenciones de ESAS ÓRDENES.
-- LIMITACIÓN: no existe FK diagnostico -> intervencion_tecnica; NO atribuye
-- causalmente cada intervención a la falla. Órdenes con varias fallas contribuyen
-- a varios grupos. DISTINCT evita duplicar diagnósticos de una misma falla/orden.
DROP VIEW IF EXISTS v_r6_fallas_intervenciones;
CREATE VIEW v_r6_fallas_intervenciones AS
WITH fallas_orden AS (
  SELECT DISTINCT numero_orden, falla_detectada FROM diagnostico
), mano AS (
  SELECT numero_orden, COUNT(*) AS numero_intervenciones,
         SUM(costo_mano_obra) AS importe
  FROM intervencion_tecnica GROUP BY numero_orden
), piezas AS (
  SELECT numero_orden, SUM(cantidad*precio_aplicado) AS importe
  FROM detalle_repuesto GROUP BY numero_orden
)
SELECT f.falla_detectada,
 COUNT(DISTINCT o.numero_orden) AS ordenes_con_falla,
 SUM(COALESCE(m.numero_intervenciones,0)) AS intervenciones_en_ordenes_con_falla,
 ROUND(AVG(COALESCE(m.importe,0)+COALESCE(p.importe,0)),2)
   AS costo_promedio_ordenes_con_falla
FROM fallas_orden f
JOIN orden_reparacion o ON o.numero_orden=f.numero_orden
JOIN equipo e ON e.codigo_interno=o.codigo_interno
LEFT JOIN mano m ON m.numero_orden=o.numero_orden
LEFT JOIN piezas p ON p.numero_orden=o.numero_orden
GROUP BY f.falla_detectada;

-- R7: técnicos/trabajadores con intervenciones, costo de su mano de obra.
-- HAVING demuestra agrupación sobre grupos con al menos una intervención.
DROP VIEW IF EXISTS v_r7_tecnicos_intervenciones;
CREATE VIEW v_r7_tecnicos_intervenciones AS
SELECT t.id_trabajador, t.nombre AS trabajador,
       COUNT(i.id_intervencion) AS cantidad_intervenciones,
       ROUND(SUM(i.costo_mano_obra),2) AS costo_total_mano_obra
FROM trabajador t
JOIN intervencion_tecnica i ON i.id_trabajador=t.id_trabajador
JOIN orden_reparacion o ON o.numero_orden=i.numero_orden
GROUP BY t.id_trabajador, t.nombre
HAVING COUNT(i.id_intervencion)>0;

-- R8: número de órdenes por cliente y costo acumulado de esas órdenes.
DROP VIEW IF EXISTS v_r8_clientes_costos;
CREATE VIEW v_r8_clientes_costos AS
WITH mano AS (
 SELECT numero_orden, SUM(costo_mano_obra) AS importe FROM intervencion_tecnica GROUP BY numero_orden
), piezas AS (
 SELECT numero_orden,SUM(cantidad*precio_aplicado) AS importe FROM detalle_repuesto GROUP BY numero_orden
), costos AS (
 SELECT o.numero_orden, o.id_cliente,
        COALESCE(m.importe,0)+COALESCE(p.importe,0) AS costo_total
 FROM orden_reparacion o
 LEFT JOIN mano m ON m.numero_orden=o.numero_orden
 LEFT JOIN piezas p ON p.numero_orden=o.numero_orden
)
SELECT c.id_cliente, c.nombre AS cliente,
 COUNT(k.numero_orden) AS cantidad_ordenes,
 ROUND(COALESCE(SUM(k.costo_total),0),2) AS costo_acumulado
FROM cliente c
LEFT JOIN costos k ON k.id_cliente=c.id_cliente
GROUP BY c.id_cliente,c.nombre;
