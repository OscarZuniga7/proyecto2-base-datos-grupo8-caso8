-- Video 8.2: comprobaciones independientes (solo SELECT) para phpMyAdmin.
-- Ajustar fechas/sucursal/estado según los datos presentes. No altera registros.
USE caso8_reparaciones;
SET @desde = '2025-01-01';
SET @hasta = '2026-12-31';
SET @sucursal = '';  -- vacío: todas; alternativamente código existente
SET @estado = '';    -- vacío: todos; alternativamente estado existente

-- P1: ranking por tipo, detectando ausencias o especializaciones múltiples.
WITH clasificacion AS (
 SELECT e.codigo_interno,
   CASE WHEN (co.codigo_interno IS NOT NULL)+(tm.codigo_interno IS NOT NULL)+(ta.codigo_interno IS NOT NULL)>1 THEN 'INCONSISTENTE'
        WHEN co.codigo_interno IS NOT NULL THEN 'COMPUTADOR'
        WHEN tm.codigo_interno IS NOT NULL THEN 'TELEFONO_MOVIL'
        WHEN ta.codigo_interno IS NOT NULL THEN 'TABLET'
        ELSE 'SIN_CLASIFICAR' END AS tipo_equipo
 FROM equipo e LEFT JOIN computador co ON e.codigo_interno=co.codigo_interno
 LEFT JOIN telefono_movil tm ON e.codigo_interno=tm.codigo_interno
 LEFT JOIN tablet ta ON e.codigo_interno=ta.codigo_interno
)
SELECT c.tipo_equipo, COUNT(*) cantidad_ordenes
FROM orden_reparacion o JOIN clasificacion c ON c.codigo_interno=o.codigo_interno
WHERE o.fecha_recepcion BETWEEN @desde AND @hasta
AND (@sucursal='' OR o.codigo_sucursal=@sucursal)
GROUP BY c.tipo_equipo ORDER BY cantidad_ordenes DESC;

-- P2: denominador solo entre equipos con un subtipo único.
WITH clasificacion AS (
 SELECT e.codigo_interno,
   CASE WHEN co.codigo_interno IS NOT NULL THEN 'COMPUTADOR'
        WHEN tm.codigo_interno IS NOT NULL THEN 'TELEFONO_MOVIL'
        WHEN ta.codigo_interno IS NOT NULL THEN 'TABLET' END AS tipo_equipo,
   (co.codigo_interno IS NOT NULL)+(tm.codigo_interno IS NOT NULL)+(ta.codigo_interno IS NOT NULL) n_subtipos
 FROM equipo e LEFT JOIN computador co ON e.codigo_interno=co.codigo_interno
 LEFT JOIN telefono_movil tm ON e.codigo_interno=tm.codigo_interno
 LEFT JOIN tablet ta ON e.codigo_interno=ta.codigo_interno
), conteos AS (
 SELECT c.tipo_equipo,COUNT(*) AS cantidad
 FROM orden_reparacion o JOIN clasificacion c ON c.codigo_interno=o.codigo_interno
 WHERE o.fecha_recepcion BETWEEN @desde AND @hasta
 AND (@sucursal='' OR o.codigo_sucursal=@sucursal) AND c.n_subtipos=1
 GROUP BY c.tipo_equipo
)
SELECT tipo_equipo,cantidad,
 ROUND(100.0*cantidad/NULLIF(SUM(cantidad) OVER(),0),2) AS porcentaje
FROM conteos ORDER BY tipo_equipo;

-- P2 control: cantidad de órdenes excluidas por ausencia/múltiples subtipos.
SELECT COUNT(*) AS ordenes_no_clasificadas_univocamente
FROM orden_reparacion o JOIN equipo e ON e.codigo_interno=o.codigo_interno
LEFT JOIN computador co ON co.codigo_interno=e.codigo_interno
LEFT JOIN telefono_movil tm ON tm.codigo_interno=e.codigo_interno
LEFT JOIN tablet ta ON ta.codigo_interno=e.codigo_interno
WHERE o.fecha_recepcion BETWEEN @desde AND @hasta
AND (@sucursal='' OR o.codigo_sucursal=@sucursal)
AND ((co.codigo_interno IS NOT NULL)+(tm.codigo_interno IS NOT NULL)+(ta.codigo_interno IS NOT NULL))<>1;

-- P3: costo de mano + detalles de repuestos, agregados por separado.
WITH mano AS (
 SELECT numero_orden,SUM(costo_mano_obra) AS importe
 FROM intervencion_tecnica GROUP BY numero_orden
), rep AS (
 SELECT numero_orden,SUM(cantidad*precio_aplicado) AS importe
 FROM detalle_repuesto GROUP BY numero_orden
), notas AS (
 SELECT numero_orden,COUNT(*) AS n_evaluaciones,
        AVG(calificacion) AS evaluacion_promedio,MIN(fecha) AS primera_evaluacion
 FROM evaluacion GROUP BY numero_orden
)
SELECT o.numero_orden,o.id_cliente,c.nombre AS cliente,o.codigo_interno,
       s.nombre AS sucursal,COALESCE(m.importe,0) AS mano_obra,
       COALESCE(r.importe,0) AS repuestos,
       COALESCE(m.importe,0)+COALESCE(r.importe,0) AS costo_total,
       n.n_evaluaciones,n.evaluacion_promedio,n.primera_evaluacion
FROM orden_reparacion o JOIN cliente c ON c.id_cliente=o.id_cliente
JOIN sucursal s ON s.codigo_sucursal=o.codigo_sucursal
JOIN notas n ON n.numero_orden=o.numero_orden
LEFT JOIN mano m ON m.numero_orden=o.numero_orden
LEFT JOIN rep r ON r.numero_orden=o.numero_orden
WHERE o.fecha_recepcion BETWEEN @desde AND @hasta
AND (@sucursal='' OR o.codigo_sucursal=@sucursal)
ORDER BY o.numero_orden;

-- P4: estados y sucursales con filtro opcional.
SELECT s.codigo_sucursal,s.nombre AS sucursal,o.estado_actual,
       COUNT(*) AS cantidad_ordenes
FROM orden_reparacion o JOIN sucursal s ON s.codigo_sucursal=o.codigo_sucursal
WHERE o.fecha_recepcion BETWEEN @desde AND @hasta
AND (@sucursal='' OR o.codigo_sucursal=@sucursal)
AND (@estado='' OR o.estado_actual=@estado)
GROUP BY s.codigo_sucursal,s.nombre,o.estado_actual
ORDER BY s.nombre,o.estado_actual;
