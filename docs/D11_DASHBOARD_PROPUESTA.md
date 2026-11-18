# Dashboard P1–P4 — propuestas sujetas a ratificación

## D07 — Regla provisional de costos

**Estado:** Pendiente de ratificación por el equipo.

Propuesta para cada orden `o`:

`costo_total(o) = SUM(intervencion_tecnica.costo_mano_obra) + SUM(detalle_repuesto.cantidad * detalle_repuesto.precio_aplicado)`

Las dos sumas se agregan por `numero_orden` **antes** de sus respectivos `JOIN`. Los importes ausentes se interpretan como cero para el cálculo provisional. No se almacena una nueva columna.

P3 representa la **calificación media por orden** cuando existen varias evaluaciones. Solo aparecen órdenes con evaluaciones reales. Se muestran la cantidad y la primera fecha de evaluación. No puede demostrarse que la evaluación sea posterior a la entrega: el DDL no contiene fecha efectiva de entrega.

**Fuentes:** SPEC.md §§5, 7, 8, 14; DDL: `orden_reparacion`, `intervencion_tecnica`, `detalle_repuesto`, `evaluacion`.

## D11 — Cuarta pregunta del dashboard

**Pregunta exacta:** ¿Cómo se distribuyen las órdenes de reparación según su estado actual y sucursal?

**Estado:** Pendiente de ratificación por el equipo, aunque implementada como demostración.

- **Justificación:** permite observar acumulaciones de órdenes en cada estado por sucursal.
- **Tablas:** `orden_reparacion` y `sucursal`, sin crear entidades adicionales.
- **Columnas:** `o.codigo_sucursal`, `o.fecha_recepcion`, `o.estado_actual`, `s.codigo_sucursal`, `s.nombre`.
- **SQL:** `app/db/dashboard_dao.py`, función `p4_estados_sucursal`; consulta independiente en `sql/06_verificacion_dashboard.sql`.
- **Visualización:** barras apiladas por sucursal, segmentadas por estado.
- **Filtros:** período de recepción, sucursal, estado.
- **Decisión de negocio que podría apoyar:** priorización de revisión operativa en sucursales con mayor acumulación de órdenes de determinados estados.
- **Validación pendiente:** el equipo debe ratificar la pregunta, el criterio de clasificación de estados y las interpretaciones.

## Especialización EQUIPO

P1 incluye `SIN_CLASIFICAR`. Si una PK aparece en más de un subtipo, se rotula `INCONSISTENTE` para no ocultar el problema del DDL.
P2 divide el total **solo entre equipos con exactamente un subtipo**; documenta por separado las órdenes excluidas. No modifica ningún dato.

## Separación de evidencias

Las consultas P1–P4 del PMV son autónomas y no reutilizan las seis vistas ni los seis procedimientos almacenados de la sección 7 del enunciado.
