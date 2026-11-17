# SPEC.md

# Proyecto Fase 2 — Sistema Integral de Gestión de Reparación de Equipos Electrónicos

**Asignatura:** TDFI103 — Bases de Datos  
**Proyecto:** Proyecto Semestral 2026, Fase 2  
**Caso:** 8  
**Grupo:** 8  
**Integrantes:** Benjamín Jiménez Noches y Diego González Pérez  
**Versión:** 0.1 — Borrador provisional  
**Estado:** En elaboración, sujeto a validación de decisiones de diseño

---

## 1. Objetivo y alcance

### 1.1 Objetivo general

Implementar una base de datos relacional en MySQL para administrar la gestión de reparación de equipos electrónicos y desarrollar un Producto Mínimo Viable (PMV) integrado mediante Python y Streamlit.

La solución deberá permitir gestionar información relacionada con clientes, equipos, sucursales, órdenes de reparación, diagnósticos, intervenciones técnicas, trabajadores, repuestos, evaluaciones de servicio y usuarios.

La Fase 2 continúa el trabajo de modelamiento realizado en Fase 1 y requiere corregir las inconsistencias detectadas.

**Fuente:** F2, §§1–2.

### 1.2 Alcance obligatorio

El proyecto comprende:

1. Corrección del MERE de Fase 1.
2. Construcción del modelo relacional definitivo.
3. Implementación de la base de datos en MySQL 8.x.
4. Poblamiento con datos sintéticos coherentes y reproducibles.
5. Desarrollo de 12 requerimientos SQL mediante 6 vistas y 6 procedimientos almacenados.
6. Construcción de un PMV con cuatro funcionalidades obligatorias.
7. Integración del PMV con la misma base de datos.
8. Despliegue mediante Docker y Docker Compose.
9. Pruebas, documentación y evidencias de funcionamiento.
10. Matriz de responsabilidades, bitácoras individuales e informe final.
11. Presentación y defensa del proyecto.

### 1.3 Límites del alcance

- Las vistas y procedimientos almacenados constituyen evidencia independiente del aprendizaje SQL y no sustituyen las funcionalidades del PMV.
- El PMV debe funcionar como una única aplicación integrada.
- No debe incorporarse una base de datos alternativa.
- No se incluyen funcionalidades adicionales sin necesidad justificada.
- Ninguna decisión pendiente de modelamiento se considerará aprobada por su aparición en esta especificación.

---

## 2. Documentos y trazabilidad

| Referencia | Documento | Utilización |
|---|---|---|
| F1 | `InformeFase1_Grupo8.pdf.pdf` | Descripción original, reglas de negocio, entidades y modelamiento |
| F2 | `Caso8_ProyectoFase2.pdf` | Requisitos obligatorios y condiciones de implementación |
| RUB | `RubricaProyectoFase2.pdf` | Criterios de calidad, evaluación y aceptación |
| DD | `DECISIONES_DISENO.md` | Seguimiento de decisiones D01–D14 |
| DP | `DECISIONES_PENDIENTES.md` | Registro inicial de asuntos no resueltos |

### 2.1 Criterios de interpretación

- **Requisito oficial:** establecido en F1 o F2 y exigible para el proyecto.
- **Diseño provisional:** representación que debe validarse.
- **Propuesta técnica:** alternativa aún no adoptada.
- **Decisión pendiente:** asunto sin aprobación documentada.
- **Decisión aprobada:** acuerdo explícito registrado posteriormente en DD.

En caso de discrepancia entre este documento y un requisito oficial, se revisará la especificación antes de implementar.

---

## 3. Requisitos obligatorios

| ID | Requisito | Origen |
|---|---|---|
| REQ-01 | Corregir MERE de Fase 1 | F2 §§1, 4, 5 |
| REQ-02 | Implementar el modelo relacional definitivo en MySQL Workbench | F2 §§3–5 |
| REQ-03 | Crear script integral ejecutable desde cero | F2 §8 |
| REQ-04 | Generar datos sintéticos suficientes y coherentes | F2 §6 |
| REQ-05 | Implementar 6 vistas y 6 procedimientos almacenados | F2 §§7–9 |
| REQ-06 | Documentar ejecución y resultados de los 12 requerimientos | F2 §9 |
| REQ-07 | Desarrollar formulario transaccional real | F2 §10 |
| REQ-08 | Implementar CRUD sobre al menos 2 tablas básicas | F2 §10 |
| REQ-09 | Implementar inicio de sesión y al menos 2 roles efectivos | F2 §10 |
| REQ-10 | Construir dashboard con 4 preguntas de negocio | F2 §10.1 |
| REQ-11 | Utilizar el stack tecnológico obligatorio | F2 §3 |
| REQ-12 | Organizar arquitectura trazable, conexión y acceso a datos | RUB C5 |
| REQ-13 | Desplegar el PMV mediante Docker Compose | F2 §12, RUB C6 |
| REQ-14 | Documentar el uso y validación de IA | F2 §11 |
| REQ-15 | Mantener matriz de responsabilidades y bitácoras | F2 §§14–15 |
| REQ-16 | Elaborar informe final y entregar los archivos solicitados | F2, portada y §13 |
| REQ-17 | Preparar presentación y defensa | F2 §16 |

---

## 4. Actores y casos de uso

### 4.1 Actores identificados en el caso

| Actor o perfil | Fundamento | Observación |
|---|---|---|
| Cliente | F1, página 2 | Entrega equipos y puede evaluar el servicio |
| Administrativo | F1, página 2 | Función del personal; permisos de aplicación por definir |
| Técnico electrónico | F1, página 2 | Participa en reparaciones |
| Especialista en software | F1, página 2 | Función del personal |
| Supervisor | F1, página 2 | Función del personal |
| Usuario autorizado | F1, página 2 y F2 §10 | Accede al PMV según sus permisos |

La aparición de un perfil en el caso no significa que deba poseer necesariamente una cuenta de aplicación.

La correspondencia definitiva entre trabajadores, funciones, usuarios y roles se resolverá mediante D03, D04 y D10.

### 4.2 Casos de uso del negocio

| ID | Caso de uso | Información o proceso asociado |
|---|---|---|
| CU-01 | Registrar un cliente | Identificación, contacto y clasificación |
| CU-02 | Registrar un equipo | Identificación y características del equipo |
| CU-03 | Recibir equipo y generar orden | Cliente, equipo, sucursal, problema y fechas |
| CU-04 | Registrar diagnóstico | Orden, falla, gravedad y recomendación |
| CU-05 | Registrar intervención técnica | Orden, trabajador, trabajo, duración y costo |
| CU-06 | Registrar repuestos utilizados | Orden, repuesto, cantidad, precio y fecha |
| CU-07 | Registrar evaluación del servicio | Orden, calificación, plazo y comentario |
| CU-08 | Consultar información de reparaciones | Requerimientos SQL R1–R12 |
| CU-09 | Acceder con credenciales | Usuario y roles |
| CU-10 | Consultar indicadores | Dashboard del PMV |

**Observación:** CU-01 a CU-10 representan procesos del caso. No todos constituyen pantallas o funcionalidades obligatorias del PMV.

### 4.3 Casos de uso obligatorios del PMV

| ID | Funcionalidad | Estado de definición |
|---|---|---|
| PMV-01 | Formulario transaccional | Operación definitiva pendiente, D09 |
| PMV-02 | CRUD de dos tablas | Tablas pendientes, D08 |
| PMV-03 | Autenticación y roles | Permisos pendientes, D10 |
| PMV-04 | Dashboard de cuatro preguntas | Cuarta pregunta pendiente, D11 |

---

## 5. Reglas de negocio

Las siguientes reglas se basan en la descripción original y en las diez reglas redactadas por el equipo durante Fase 1.

| ID | Regla de negocio | Fuente |
|---|---|---|
| RN-01 | Cada intervención técnica debe asociarse con un trabajador habilitado para la función correspondiente | F1, regla 1 |
| RN-02 | Una orden de reparación debe asociarse a un equipo y cliente registrados | F1, regla 2 |
| RN-03 | Los diagnósticos dependen de la orden y se identifican mediante un correlativo interno | F1, regla 3 y caso |
| RN-04 | Una orden puede utilizar varios repuestos y un repuesto puede utilizarse en distintas órdenes | F1, regla 4 |
| RN-05 | Las evaluaciones dependen de órdenes de reparación y pueden incorporar comentarios opcionales | F1, regla 5 y caso |
| RN-06 | Los clientes deben poseer identificación única y datos de contacto | F1, regla 6 |
| RN-07 | Las intervenciones registran técnico, tipo de trabajo, duración y costo de mano de obra | F1, regla 7 |
| RN-08 | Cada orden de reparación debe asociarse con una sucursal | F1, regla 8 |
| RN-09 | Cada cuenta de usuario debe tener uno o más roles autorizados | F1, regla 9 |
| RN-10 | La especialización de EQUIPO es parcial y disyuntiva | F1, regla 10 |

### 5.1 Reglas adicionales expresamente descritas en el caso

- Una orden registra fecha de recepción, problema informado, estado actual y fecha comprometida.
- Un diagnóstico registra falla detectada, gravedad y recomendación técnica.
- Un detalle de repuesto registra cantidad, precio aplicado y fecha de incorporación.
- Una evaluación registra fecha, calificación y cumplimiento del plazo.
- Un trabajador puede desempeñar más de una función.
- Algunos equipos pueden permanecer sin clasificar.
- El acceso a funcionalidades debe respetar los roles autorizados.

### 5.2 Reglas pendientes de validación

- D01: relación definitiva de EVALUACIÓN.
- D02: identificación relacional de diagnósticos y evaluaciones.
- D03: representación de funciones del personal.
- D04: estructura de usuarios y roles.
- D05: implementación de subtipos.
- D06: representación del tipo de trabajo.
- D07: cálculo de costos sin duplicaciones.

**Restricción:** no se definirán nuevas reglas de cardinalidad, obligatoriedad o integridad sin respaldo documental o decisión justificada.

---

## 6. Modelo de datos provisional

### 6.1 Entidades y atributos identificados

El inventario siguiente recoge las entidades y atributos que figuran en la descripción del caso y en el trabajo de Fase 1.

No representa todavía el modelo relacional aprobado.

| Entidad | Atributos documentados | Identificación / relaciones |
|---|---|---|
| CLIENTE | Identificación, nombre, teléfono, clasificación y datos de contacto | Identificación única; relación con equipos y órdenes |
| SUCURSAL | Código, nombre, dirección, comuna, capacidad, horario | Código de sucursal; relación con órdenes |
| EQUIPO | Código interno, marca, modelo, número de serie, fecha aproximada de compra, conservación | Código interno; relaciones con cliente, órdenes y subtipos |
| COMPUTADOR | Sistema operativo, memoria, almacenamiento | Subtipo de EQUIPO |
| TELEFONO_MOVIL | Operador, IMEI, versión del sistema | Subtipo de EQUIPO |
| TABLET | Tamaño de pantalla, capacidad, conectividad | Subtipo de EQUIPO |
| ORDEN_REPARACION | Número de orden, fecha de recepción, problema informado, estado, fecha comprometida | Número de orden; referencias a cliente, equipo y sucursal |
| DIAGNOSTICO | Correlativo, fecha, falla detectada, gravedad, recomendación, observaciones | Dependiente de orden; D02 |
| INTERVENCION_TECNICA | Identificador, fecha, duración, resultado, observaciones, costo de mano de obra | Orden, trabajador/técnico y tipo de trabajo; D03 y D06 |
| REPUESTO | Identificador y datos de tipo, precio y disponibilidad | Identificación según modelo definitivo |
| DETALLE_REPUESTO | Cantidad, precio aplicado, fecha de incorporación | Asociación entre orden y repuesto |
| TRABAJADOR / TECNICO | Identificación y antecedentes del personal | Representación definitiva pendiente, D03 |
| EVALUACION | Correlativo, fecha, calificación, cumplimiento del plazo, comentario | Dependiente de orden; D01 y D02 |
| USUARIO | Identificación y datos de cuenta | Asociación con trabajador y roles por validar |
| ROL | Identificador y descripción del rol | Asociación con usuarios |
| USUARIO_ROL | Referencias de usuario y rol | Entidad asociativa; D04 |

**Observaciones:**

1. La tabla de Fase 1 presenta algunos atributos intercambiados entre COMPUTADOR y TABLET; aquí se reproducen los atributos de la descripción original del caso.
2. Las referencias a TRABAJADOR y TÉCNICO no constituyen una decisión de mantener ambas como tablas independientes.
3. TIPO DE TRABAJO se menciona en el caso y las reglas, pero su representación definitiva sigue pendiente.
4. Los nombres físicos, tipos de datos y restricciones deberán definirse y aprobarse en el modelo relacional final.

### 6.2 Claves primarias y foráneas por validar

| Componente | PK identificada o prevista en F1 | FK o relación por validar |
|---|---|---|
| CLIENTE | Identificador de cliente | Sin FK establecida |
| SUCURSAL | Código de sucursal | Sin FK establecida |
| EQUIPO | Código interno | Cliente; D05 |
| Subtipos de EQUIPO | Código interno heredado | EQUIPO |
| ORDEN_REPARACION | Número de orden | CLIENTE, EQUIPO, SUCURSAL |
| DIAGNOSTICO | Orden + correlativo | ORDEN_REPARACION |
| EVALUACION | Orden + correlativo | ORDEN_REPARACION |
| INTERVENCION_TECNICA | Identificador de intervención | Orden, trabajador y tipo de trabajo |
| REPUESTO | Identificador de repuesto | Sin FK establecida |
| DETALLE_REPUESTO | Identificación asociativa por validar | Orden y repuesto |
| USUARIO | Identificador de usuario | Asociación con trabajador por validar |
| ROL | Identificador por definir | Sin FK establecida |
| USUARIO_ROL | Identificación asociativa por validar | USUARIO y ROL |

La tabla indica elementos por comprobar, no una aprobación de las estructuras propuestas.

### 6.3 Relaciones documentadas

- CLIENTE–EQUIPO: relación de titularidad descrita en Fase 1.
- CLIENTE–ORDEN_REPARACION: un cliente puede registrar varias órdenes.
- EQUIPO–ORDEN_REPARACION: un equipo puede originar órdenes a lo largo del tiempo.
- SUCURSAL–ORDEN_REPARACION: cada orden corresponde a una sucursal.
- ORDEN_REPARACION–DIAGNOSTICO: relación identificadora.
- ORDEN_REPARACION–EVALUACION: relación identificadora descrita en el caso.
- ORDEN_REPARACION–INTERVENCION_TECNICA: asociación de trabajos realizados.
- ORDEN_REPARACION–REPUESTO: relación N:M mediante DETALLE_REPUESTO.
- TRABAJADOR/TÉCNICO–INTERVENCION_TECNICA: asignación de trabajo.
- USUARIO–ROL: relación N:M.
- EQUIPO–subtipos: especialización parcial y disyuntiva.

### 6.4 Restricciones y normalización

El modelo final deberá establecer las restricciones necesarias de PK, FK, `NOT NULL`, `UNIQUE`, `CHECK` y demás condiciones justificadas.

Se deberá comprobar la coherencia del modelo con las reglas de negocio y revisar las dependencias funcionales utilizadas en Fase 1.

No se considerará terminada esta sección hasta disponer de:

- Imagen legible del MERE corregido.
- Modelo relacional final en MySQL Workbench.
- Justificación documentada de las correcciones.
- Correspondencia entre modelo, script y base implementada.

---

## 7. Requerimientos SQL

**Fuente:** F2, §7.

Los doce requerimientos se resolverán sobre el modelo definitivo.

| ID | Requerimiento | Objeto | Condición técnica principal |
|---|---|---|---|
| R1 | Tipos de equipos con mayor cantidad de órdenes por período | Procedure | Fechas, clasificación, equipo, orden y sucursal |
| R2 | Distribución porcentual de órdenes por tipo de equipo y sucursal | View | Clasificación, equipo, orden y sucursal |
| R3 | Relación entre costo de reparación y evaluación del cliente | View | Costos de mano de obra y repuestos, evaluación |
| R4 | Sucursales con mayor cantidad de órdenes y clientes | Procedure | Fechas, sucursal, orden, cliente y equipo |
| R5 | Costo promedio de reparación por tipo de equipo | View | Agrupación, intervenciones y repuestos |
| R6 | Fallas con más intervenciones y mayor costo promedio | View | Diagnósticos, intervenciones y agrupaciones |
| R7 | Técnicos con más intervenciones y costo total de mano de obra | View | Agregaciones y HAVING |
| R8 | Clientes con más órdenes y mayor costo acumulado | View | Agrupación de órdenes y costos |
| R9 | Órdenes sobre el costo promedio de su mismo tipo | Procedure | Tipo, rango de fechas y subconsulta correlacionada |
| R10 | Repuestos con uso superior al promedio de una sucursal | Procedure | Sucursal y subconsulta correlacionada |
| R11 | Clientes sobre los promedios de órdenes y evaluaciones | Procedure | Fechas, agrupación y comparaciones |
| R12 | Sucursales cuyo costo promedio supera el promedio general | Procedure | Fechas, subconsulta y agrupación |

### 7.1 Condiciones de implementación

- R1, R4, R9, R10, R11 y R12: procedimientos almacenados.
- R2, R3, R5, R6, R7 y R8: vistas.
- Los procedimientos deberán recibir los parámetros pertinentes establecidos por el enunciado.
- Se deberán utilizar las tablas, relaciones, agrupaciones y subconsultas requeridas.
- No se reemplazará una vista por un procedimiento ni viceversa.

### 7.2 Evidencia obligatoria por requerimiento

Para cada R1–R12 se documentará:

1. Identificador y pregunta de negocio.
2. Código SQL completo de creación del objeto.
3. Sentencia de consulta o ejecución.
4. Captura del resultado real en Workbench.
5. Interpretación de dos a cuatro líneas.

**Criterio de separación:** estas evidencias SQL son independientes de las cuatro funcionalidades del PMV.

---

## 8. Funcionalidades obligatorias del PMV

**Fuente:** F2, §§10–10.1.

### PMV-01 — Formulario transaccional

**Requisito oficial:** registrar una nueva orden de reparación asociada a cliente, equipo y sucursal, u otra operación equivalente y justificada.

**Condiciones:**
- Selección de datos existentes.
- Validación de campos.
- Registro de problema informado.
- Registro de fechas relevantes.
- Cumplimiento de claves foráneas.
- Persistencia efectiva en MySQL.

**Operación adoptada:** Pendiente (D09).

**Pruebas previstas:** ingreso válido, campos incompletos, referencias inválidas y confirmación de persistencia.

### PMV-02 — CRUD sobre tablas básicas

**Requisito oficial:** operaciones de creación, consulta, modificación y eliminación o desactivación sobre al menos dos tablas maestras o básicas.

EQUIPO y REPUESTO son ejemplos propuestos por el enunciado.

**Tablas seleccionadas:** Pendiente (D08).

**Condiciones:**
- Operaciones sobre la base real.
- Validación de datos.
- Respeto de restricciones.
- Desactivación lógica cuando una eliminación física afecte la integridad referencial.

**Pruebas previstas:** alta, consulta, actualización, eliminación/desactivación y comprobación de restricciones.

### PMV-03 — Control de usuarios

**Requisito oficial:** inicio de sesión y al menos dos roles con permisos diferenciados.

**Roles adoptados:** Pendiente (D10).

**Condiciones:**
- Autenticación funcional.
- Permisos que modifiquen efectivamente el acceso a funcionalidades.
- Control de acceso según el rol autorizado.
- Integración con el PMV.

No se requieren funcionalidades avanzadas de seguridad.

**Pruebas previstas:** credenciales válidas e inválidas, roles diferentes e intentos de acceso a funcionalidades no autorizadas.

### PMV-04 — Dashboard

El dashboard responderá cuatro preguntas de negocio.

| Pregunta | Contenido | Representación oficial |
|---|---|---|
| P1 | Tipos de equipos con más órdenes en un período | Ranking o barras, filtros de período, sucursal y tipo |
| P2 | Distribución porcentual de órdenes por tipo de equipo | Composición o barras, filtros por sucursal y período |
| P3 | Relación entre costo total y evaluación posterior | Dispersión y tabla de detalle por orden, cliente, equipo y sucursal |
| P4 | Pregunta nueva propuesta por el equipo | Visualización y filtros justificados |

**Cuarta pregunta:** Pendiente (D11).

Para P4 se deberán documentar la pregunta, justificación, consulta SQL, representación y decisión empresarial que podría apoyar.

Las cuatro preguntas se resolverán sobre la misma base de datos.

---

## 9. Arquitectura tecnológica

### 9.1 Herramientas obligatorias

| Componente | Tecnología |
|---|---|
| MERE | ERDPlus o equivalente |
| Base de datos | MySQL 8.x |
| Diseño y validación | MySQL Workbench |
| Lenguaje | Python 3.12 o superior |
| Conexión a MySQL | SQLAlchemy y PyMySQL |
| Generación de datos | Faker o equivalente |
| Procesamiento de datos | Pandas |
| Visualizaciones | Plotly |
| Aplicación web | Streamlit |
| Asistencia IA | Herramienta aprendida en curso NoCode |
| Despliegue | Docker y Docker Compose |

**Fuente:** F2, §3.

### 9.2 Organización lógica requerida

La rúbrica exige distinguir responsabilidades técnicas, por ejemplo:

- Capa de presentación: interfaz y páginas Streamlit.
- Lógica de aplicación: validación y coordinación de operaciones.
- Acceso a datos: DAO o capa equivalente.
- Conexión a MySQL: configuración y gestión centralizada.
- Configuración: dependencias y variables de entorno.

**Decisión sobre archivos y carpetas:** Pendiente (D12).

La rúbrica hace referencia a componentes como `app.py`, `conexion.py`, DAO y `requirements.txt`. La estructura concreta deberá mantenerse comprensible y justificarse.

### 9.3 Despliegue

El proyecto incluirá:

- Dockerfile funcional para la aplicación.
- `docker-compose.yml`.
- Servicios `app` y `db`.
- Imagen versionada de MySQL 8.x.
- Volumen persistente.
- Variables de entorno y puertos.
- Instalación de dependencias.
- Inicialización de la base desde los scripts entregados.
- Gestión de disponibilidad de MySQL.
- Instrucciones de ejecución.

La aplicación ejecutada en Docker debe ser la misma que se entregue para evaluación.

---

## 10. Plan de implementación

| Etapa | Actividades | Evidencia de cierre |
|---|---|---|
| E1 — Revisión | Validar reglas, MERE y decisiones D01–D07 | MERE corregido y decisiones registradas |
| E2 — Modelo relacional | Construir y comprobar el modelo Workbench | Diagrama final y restricciones |
| E3 — Base de datos | Crear script integral y poblar tablas | BD reconstruible y datos coherentes |
| E4 — SQL avanzado | Resolver R1–R12 | Objetos SQL y resultados verificados |
| E5 — PMV | Implementar cuatro funcionalidades | Aplicación integrada funcionando |
| E6 — Docker | Construir y ejecutar contenedores | Despliegue reproducible |
| E7 — Documentación | Reunir evidencias, matriz y bitácoras | Informe completo y consistente |
| E8 — Defensa | Preparar exposición y preguntas | Presentación y dominio técnico |

### 10.1 Plan de pruebas

| ID | Prueba | Resultado esperado |
|---|---|---|
| T01 | Ejecutar script desde cero | BD y objetos creados sin errores |
| T02 | Verificar claves y restricciones | Datos inconsistentes rechazados |
| T03 | Comprobar población | Datos suficientes, variados y relacionados |
| T04 | Ejecutar seis vistas | Resultados coherentes con R2, R3, R5, R6, R7 y R8 |
| T05 | Ejecutar seis procedimientos | Parámetros y resultados coherentes |
| T06 | Registrar transacción PMV | Registro persistido correctamente |
| T07 | Ejecutar CRUD | Operaciones efectivas sobre dos tablas |
| T08 | Comprobar control de acceso | Permisos diferenciados y efectivos |
| T09 | Validar dashboard | Cuatro preguntas correctamente respondidas |
| T10 | Levantar Docker Compose | Aplicación y BD operativas |
| T11 | Verificar persistencia | Datos conservados conforme a configuración |
| T12 | Contrastar informe y repositorio | Archivos, evidencias y producto consistentes |

### 10.2 Poblamiento

Los rangos indicados en F2 §6 son orientativos. El criterio principal es que los registros permitan validar los doce requerimientos SQL y producir visualizaciones significativas.

Se deberán utilizar datos sintéticos y comprobar:

- Integridad de claves foráneas.
- Distribución por sucursales.
- Diversidad de equipos.
- Diferentes fechas y estados de órdenes.
- Diagnósticos e intervenciones variados.
- Diferentes costos y repuestos.
- Evaluaciones con calificaciones diversas.
- Usuarios con permisos diferenciados.

**Aclaración pendiente:** D14, sobre referencias ajenas al Caso 8 en el texto introductorio del poblamiento.

---

## 11. Criterios de aceptación

### 11.1 Aceptación técnica

| ID | Criterio | Evidencia |
|---|---|---|
| AC-01 | El MERE final respeta las reglas de negocio | Diagrama y justificación |
| AC-02 | El modelo relacional corresponde a la BD implementada | Workbench y script |
| AC-03 | El script reconstruye la BD desde cero | Ejecución verificada |
| AC-04 | Los datos son coherentes y suficientes | Pruebas y resultados |
| AC-05 | Existen 6 vistas y 6 procedimientos correctos | Ejecuciones de R1–R12 |
| AC-06 | El formulario registra una operación real | Prueba funcional |
| AC-07 | El CRUD funciona sobre dos tablas | Pruebas de operaciones |
| AC-08 | Dos roles modifican efectivamente los permisos | Pruebas de acceso |
| AC-09 | Dashboard responde las cuatro preguntas | Consultas y visualizaciones |
| AC-10 | Arquitectura y conexión son trazables | Código y estructura del repositorio |
| AC-11 | Docker permite ejecutar el PMV integrado | Contenedores operativos |
| AC-12 | El informe coincide con la implementación | Revisión documental |
| AC-13 | Matriz y bitácoras evidencian participación real | Documentación individual |
| AC-14 | Los estudiantes explican todos los componentes | Presentación y defensa |

### 11.2 Correspondencia con la rúbrica

| Criterio | Puntaje |
|---|---:|
| C1 — Consistencia del modelo | 8 |
| C2 — Construcción y población | 6 |
| C3 — Requerimientos SQL | 10 |
| C4 — Funcionalidades del PMV | 10 |
| C5 — Arquitectura e integración | 8 |
| C6 — Docker | 6 |
| C7 — Responsabilidades y bitácoras | 4 |
| C8 — Informe | 8 |
| C9 — Presentación grupal | 5 |
| C10 — Disertación individual | 15 |
| C11 — Defensa individual | 20 |
| **Total** | **100** |

Los criterios AC constituyen una organización de verificación de este borrador; no reemplazan las descripciones de desempeño de la rúbrica oficial.

---

## 12. Responsabilidades, documentación e IA

### 12.1 Matriz de responsabilidades

El equipo deberá establecer responsables principales y colaboradores para las actividades exigidas en F2 §14.

**Asignaciones individuales:** Pendientes.

**D13:** requiere aclaración docente debido a la condición de cuatro responsables principales distintos para las funcionalidades del PMV y la composición actual del Grupo 8, de dos integrantes.

No se asignan responsabilidades individuales en este borrador.

### 12.2 Bitácoras individuales

Cada integrante registrará:

- Fecha.
- Actividad realizada.
- Etapa o componente.
- Evidencia.
- Horas.
- Resultado o dificultad.

Cada estudiante incorporará una síntesis individual de sus aportes y aprendizajes.

### 12.3 Uso de inteligencia artificial

La IA podrá apoyar el modelamiento, SQL, poblamiento, Python y Docker.

El equipo deberá:

- Revisar las propuestas generadas.
- Ejecutar y comprobar los resultados.
- Verificar integridad y reglas de negocio.
- Conservar evidencias resumidas del uso y validación.
- Comprender y explicar todos los componentes incorporados.

La IA no sustituye las decisiones ni la defensa técnica del equipo.

---

## 13. Entregables

| Entregable | Contenido mínimo |
|---|---|
| Informe final | Estructura establecida en F2 §13 |
| Script integral SQL | BD, tablas, restricciones, datos, vistas y procedimientos |
| Script de generación de datos | Poblamiento masivo |
| Código fuente PMV | Streamlit y dependencias |
| Archivos Docker | Dockerfile y docker-compose.yml |
| Presentación | Diapositivas utilizadas en la disertación |

La entrega se realizará mediante Canvas según la fecha indicada por el docente.

Los documentos `SPEC.md` y `DECISIONES_DISENO.md` se utilizan como instrumentos de planificación y trazabilidad; no se presentan aquí como entregables adicionales oficialmente exigidos.

---

## 14. Decisiones pendientes

**Fuente:** Registro DD, versión inicial.

| ID | Asunto | Estado |
|---|---|---|
| D01 | Relación EVALUACIÓN–ORDEN_REPARACION | Pendiente |
| D02 | Claves de DIAGNOSTICO y EVALUACION | Pendiente |
| D03 | Representación de TRABAJADOR y TÉCNICO | Pendiente |
| D04 | Estructura USUARIO–ROL | Pendiente |
| D05 | Especialización de EQUIPO | Pendiente |
| D06 | INTERVENCION_TECNICA y tipo de trabajo | Pendiente |
| D07 | Cálculo del costo de reparación | Pendiente |
| D08 | Tablas seleccionadas para CRUD | Pendiente |
| D09 | Operación del formulario transaccional | Pendiente |
| D10 | Roles y permisos del PMV | Pendiente |
| D11 | Cuarta pregunta del dashboard | Pendiente |
| D12 | Arquitectura y estructura de archivos | Pendiente |
| D13 | Responsables principales del PMV | Pendiente — aclaración docente |
| D14 | Referencias ajenas al caso en poblamiento | Pendiente — aclaración docente |

### 14.1 Condiciones para cerrar decisiones

Cada decisión deberá actualizarse en `DECISIONES_DISENO.md` indicando:

1. Alternativa adoptada.
2. Justificación.
3. Responsable o participantes de la aprobación.
4. Fecha real.
5. Estado.
6. Evidencia de validación.

Los cambios aprobados que afecten esta especificación deberán incorporarse a `SPEC.md`, manteniendo coherencia con el modelo y el producto.

**No existen decisiones aprobadas documentadas en el registro inicial utilizado para esta versión.**

---

## 15. Control de versiones

| Versión | Descripción | Estado |
|---|---|---|
| 0.1 | Borrador inicial basado en F1, F2, rúbrica y decisiones pendientes | Provisional |

Las modificaciones posteriores deberán registrarse cuando existan acuerdos o cambios efectivos.

---

## 16. Condiciones para iniciar la implementación

Antes de crear las estructuras afectadas, deberán estar resueltas y documentadas las decisiones de modelamiento correspondientes.

La implementación progresará utilizando:

- Requisitos oficiales confirmados.
- Modelos revisados y consistentes.
- Decisiones aprobadas y documentadas.
- Evidencias de pruebas verificables.

Los puntos pendientes no se transformarán automáticamente en decisiones por la generación de código con IA.

**Próximo hito:** aprobación del MERE y modelo relacional definitivo, seguida de la implementación controlada de la base de datos.

---

**Fin de SPEC.md — Borrador versión 0.1**

*Este documento es una especificación provisional. No contiene acuerdos de diseño atribuidos al equipo sin evidencia ni autoriza cambios contrarios al enunciado oficial.*
