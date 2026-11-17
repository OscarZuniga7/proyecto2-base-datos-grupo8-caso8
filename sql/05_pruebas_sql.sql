-- CASO 8 | 05_pruebas_sql.sql | MySQL 8.4
-- Ejecutar DESPUES de 03_vistas.sql y 04_procedimientos.sql.
-- Fechas tomadas para abarcar el conjunto sintético adjunto (2025/2026).
-- Resultados vacíos son posibles cuando el filtro es más exigente que los datos.
USE caso8_reparaciones;

-- CONTROL 0: existen los 6 objetos de cada clase
SELECT TABLE_NAME AS vista FROM information_schema.VIEWS
WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME LIKE 'v_r%'
ORDER BY TABLE_NAME;
SELECT ROUTINE_NAME AS procedimiento FROM information_schema.ROUTINES
WHERE ROUTINE_SCHEMA=DATABASE() AND ROUTINE_TYPE='PROCEDURE'
 AND ROUTINE_NAME LIKE 'sp_r%'
ORDER BY ROUTINE_NAME;

-- R1 - Procedure: tipos de equipo con más órdenes en período
CALL sp_r1_tipos_mas_ordenes('2025-01-01','2026-12-31');

-- R2 - View: porcentajes por sucursal, entre tres tipos clasificados
SELECT * FROM v_r2_distribucion_equipos_sucursal
ORDER BY codigo_sucursal, cantidad_ordenes DESC;
-- La suma debe ser ~100% en cada sucursal que tenga equipos clasificados.
SELECT codigo_sucursal,ROUND(SUM(porcentaje_sucursal),2) AS suma_porcentajes
FROM v_r2_distribucion_equipos_sucursal GROUP BY codigo_sucursal;

-- R3 - View: costos totales y evaluaciones, una fila por orden evaluada
SELECT * FROM v_r3_costo_evaluacion
ORDER BY costo_total DESC LIMIT 30;
-- No duplicados por orden en la vista:
SELECT numero_orden, COUNT(*) AS filas FROM v_r3_costo_evaluacion
GROUP BY numero_orden HAVING COUNT(*) > 1;

-- R4 - Procedure: sucursales, órdenes y clientes únicos por período
CALL sp_r4_sucursales_actividad('2025-01-01','2026-12-31');

-- R5 - View: costos medios por clasificación
SELECT * FROM v_r5_costo_promedio_tipo
ORDER BY costo_promedio_total DESC;

-- R6 - View: fallas detectadas y trabajos de las órdenes donde constan
-- ATENCIÓN: no demuestra que una intervención particular resuelva esa falla.
SELECT * FROM v_r6_fallas_intervenciones
ORDER BY intervenciones_en_ordenes_con_falla DESC LIMIT 30;

-- R7 - View: técnicos/trabajadores, intervenciones y mano de obra (HAVING)
SELECT * FROM v_r7_tecnicos_intervenciones
ORDER BY cantidad_intervenciones DESC LIMIT 30;

-- R8 - View: órdenes y costos por cliente
SELECT * FROM v_r8_clientes_costos
ORDER BY cantidad_ordenes DESC,costo_acumulado DESC LIMIT 30;

-- R9 - Procedure: órdenes > costo medio de su tipo en periodo
CALL sp_r9_ordenes_sobre_promedio_tipo('COMPUTADOR','2025-01-01','2026-12-31');

-- R10 - Procedure: repuestos usados sobre su media en la sucursal SUC001
CALL sp_r10_repuestos_sobre_promedio('SUC001');

-- R11 - Procedure: clientes sobre medias de órdenes y calificación
CALL sp_r11_clientes_sobre_promedios('2025-01-01','2026-12-31');

-- R12 - Procedure: sucursales con costo medio sobre media de sucursales
CALL sp_r12_sucursales_costo_sobre_promedio('2025-01-01','2026-12-31');

-- CONTROL FINAL 1: integridad de referencias en órdenes (0 huérfanos)
SELECT COUNT(*) AS ordenes_con_referencia_invalida
FROM orden_reparacion o
LEFT JOIN cliente c ON c.id_cliente=o.id_cliente
LEFT JOIN equipo e ON e.codigo_interno=o.codigo_interno AND e.id_cliente=o.id_cliente
LEFT JOIN sucursal s ON s.codigo_sucursal=o.codigo_sucursal
WHERE c.id_cliente IS NULL OR e.codigo_interno IS NULL OR s.codigo_sucursal IS NULL;

-- CONTROL FINAL 2: cardinalidad de filas principales
SELECT (SELECT COUNT(*) FROM orden_reparacion) AS total_ordenes,
       (SELECT COUNT(*) FROM diagnostico) AS total_diagnosticos,
       (SELECT COUNT(*) FROM intervencion_tecnica) AS total_intervenciones,
       (SELECT COUNT(*) FROM evaluacion) AS total_evaluaciones,
       (SELECT COUNT(*) FROM detalle_repuesto) AS total_detalles_repuesto;

-- CONTROL FINAL 3: validar disyunción, que las FK del DDL NO garantizan.
-- Esperado 0 si los datos cargados respetan especialización disyuntiva.
SELECT COUNT(*) AS equipos_con_multiples_subtipos
FROM equipo e
LEFT JOIN computador co ON co.codigo_interno=e.codigo_interno
LEFT JOIN telefono_movil tm ON tm.codigo_interno=e.codigo_interno
LEFT JOIN tablet ta ON ta.codigo_interno=e.codigo_interno
WHERE (IF(co.codigo_interno IS NULL,0,1)
     + IF(tm.codigo_interno IS NULL,0,1)
     + IF(ta.codigo_interno IS NULL,0,1)) > 1;
