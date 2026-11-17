# DECISIONES_DISENO.md

## Proyecto Semestral 2026 — Base de Datos (TDFI103)

**Caso:** 8 — Sistema Integral de Gestión de Reparación de Equipos Electrónicos  
**Grupo:** 8  
**Integrantes:** Benjamín Jiménez Noches y Diego González Pérez  
**Fecha de apertura del registro:** 16 de noviembre de 2026  
**Etapa:** 2 — Revisión de decisiones, GitHub y preparación de `SPEC.md`  
**Estado:** **Borrador de trabajo; ninguna decisión aprobada todavía**  
**Origen:** transcripción y reorganización del archivo `DecisionesPendientes.md` elaborado durante la Etapa 1.

> **IMPORTANTE PARA LA DEMOSTRACIÓN:** Este documento es un **insumo** para que el equipo tome decisiones, no una aprobación de ChatGPT ni del docente. Los campos de aprobación permanecen vacíos. Las alternativas que siguen son propuestas identificadas en el análisis de Fase 1 y Fase 2; deben contrastarse con los originales antes de modificar el MERE o programar.

## 1. Procedimiento de trabajo para iniciar el Video 2

1. Abrir este archivo y revisar las 14 decisiones, sin cambiar aún sus estados.
2. Tratar primero **D01–D07** (modelo y cálculos); luego **D08–D12** (PMV).
3. Para cada decisión, discutir las alternativas con los documentos originales abiertos; escribir en **Acuerdo adoptado** y **Justificación validada** únicamente lo efectivamente acordado por el grupo.
4. Registrar **responsable concreto, fecha y evidencia** (acta, versión del MERE, enlace a commit o prueba).
5. Cambiar a **Aprobada por el equipo** solamente cuando exista validación; en caso contrario mantener **Pendiente** o cambiar a **Requiere aclaración docente**.
6. Las decisiones **D13 y D14** requieren consulta docente; no se deben marcar como aprobadas por el equipo sin respuesta.
7. Preparar el borrador de `SPEC.md` exclusivamente con los requisitos confirmados y decisiones aprobadas. Etiquetar explícitamente los puntos abiertos. Guardar ambos documentos en `docs/` del repositorio, registrar un commit.

**Estados permitidos:** Pendiente · En discusión · Aprobada por el equipo · Requiere aclaración docente · Aclarada por docente.  
**Criterio de control:** una propuesta o alternativa sugerida no equivale a una decisión adoptada.

## 2. Registro de decisiones del modelo y de la aplicación

### D01 — Relación entre EVALUACIÓN y ORDEN_REPARACIÓN

**Descripción:**  
Revisar la modificación planteada durante la normalización de Fase 1, donde las evaluaciones pasan a relacionarse con los diagnósticos. Esta interpretación presenta una discrepancia con la definición original del caso, que identifica cada evaluación mediante el número de orden y un correlativo interno.

**Documentos y secciones de origen:**
- Fase 1, página 2: descripción del caso, EVALUACIÓN.
- Fase 1, página 3: regla de negocio 5.
- Fase 1, páginas 10–19: normalización y conclusiones.
- Fase 2, §5: corrección del MERE.

**Alternativas fundamentadas:**
- Mantener EVALUACIÓN dependiente de ORDEN_REPARACIÓN, conforme a la descripción original del caso.
- La asociación con DIAGNÓSTICO aparece en las conclusiones de Fase 1, pero no está respaldada como nueva regla por el enunciado oficial. No debe adoptarse sin aclaración.

**Impacto:**  
Cardinalidades, claves foráneas, consultas de evaluación, cálculo de promedios y dashboard.

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Pendiente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D02 — Identificación de DIAGNÓSTICO y EVALUACIÓN

**Descripción:**  
Validar cómo se implementarán las claves primarias de ambas entidades dependientes de ORDEN_REPARACIÓN.

**Documentos y secciones de origen:**
- Fase 1, página 2: definición de identificadores.
- Fase 1, página 5: entidades débiles.
- Fase 1, página 8: transformación al modelo relacional.
- Fase 2, §5: construcción del modelo definitivo.

**Alternativa fundamentada:**
- Utilizar claves primarias compuestas por número de orden y correlativo correspondiente, respetando la identificación establecida en el caso.

**Impacto:**  
Integridad referencial, unicidad de diagnósticos y evaluaciones, y modelo relacional.

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Pendiente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D03 — Representación de TRABAJADOR, TÉCNICO y funciones

**Descripción:**  
Resolver cómo representar al personal y su participación en intervenciones técnicas, considerando que un trabajador puede desempeñar más de una función.

**Documentos y secciones de origen:**
- Fase 1, página 2: descripción del personal.
- Fase 1, páginas 3–4: reglas de negocio 1 y 7.
- Fase 1, páginas 5 y 8: entidades y relaciones.
- Fase 2, §7: requerimiento R7.

**Alternativas fundamentadas:**
- Revisar la representación actual de TÉCNICO para incorporar las funciones descritas para los trabajadores.
- Considerar una representación de funciones múltiples, siempre que corresponda a las reglas originales del caso.

No se define todavía la estructura relacional concreta.

**Impacto:**  
Modelo de personal, asignación de intervenciones, control de funciones y consulta R7.

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Pendiente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D04 — Estructura de USUARIO, ROL y permisos

**Descripción:**  
Corregir la representación de usuarios y roles, que presenta inconsistencias en la definición de la entidad asociativa USUARIO_ROL.

**Documentos y secciones de origen:**
- Fase 1, página 2: acceso mediante usuarios y roles.
- Fase 1, página 4: regla de negocio 9.
- Fase 1, páginas 5 y 8: descripción de USUARIO_ROL.
- Fase 2, §10: control de usuarios.
- Rúbrica, criterio 4.

**Alternativa fundamentada:**
- Representar separadamente las cuentas de usuario, los roles y su asociación N:M, conforme al caso.

**Impacto:**  
Modelo relacional, autenticación, permisos y seguridad funcional del PMV.

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Pendiente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D05 — Implementación de la especialización de EQUIPO

**Descripción:**  
Definir la transformación relacional definitiva de COMPUTADOR, TELÉFONO MÓVIL y TABLET, corrigiendo inconsistencias en sus atributos.

**Documentos y secciones de origen:**
- Fase 1, página 2: descripción de subtipos.
- Fase 1, página 4: regla de negocio 10.
- Fase 1, páginas 5–8: MERE y modelo relacional.
- Fase 2, §5.

**Alternativa fundamentada:**
- Mantener la especialización parcial y disyuntiva declarada en Fase 1, conservando en EQUIPO los atributos comunes y en cada subtipo los específicos.

**Impacto:**  
Tablas, claves, relaciones, restricciones, formulario y CRUD de EQUIPO, requerimientos R1, R2, R5 y R9.

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Pendiente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D06 — Identificación de INTERVENCIÓN_TÉCNICA y TIPO DE TRABAJO

**Descripción:**  
Validar la relación entre intervenciones técnicas, órdenes, trabajadores y tipos de trabajo, incluida la identificación de cada intervención.

**Documentos y secciones de origen:**
- Fase 1, página 2: descripción de intervenciones.
- Fase 1, página 4: regla de negocio 7.
- Fase 1, páginas 5 y 8: descripción de entidades y FK.
- Fase 2, §7: requerimientos R3, R5, R6 y R7.

**Alternativa fundamentada:**
- Conservar el identificador de intervención documentado en Fase 1 y revisar las relaciones requeridas para representar técnico, orden y tipo de trabajo.

La forma definitiva de representar el tipo de trabajo permanece por definir.

**Impacto:**  
Claves foráneas, registro de intervenciones, costos de mano de obra y consultas SQL.

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Pendiente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D07 — Cálculo del costo total de reparación

**Descripción:**  
Definir cómo obtener correctamente el costo total de cada orden sin duplicar valores al combinar intervenciones y detalles de repuesto.

**Documentos y secciones de origen:**
- Fase 1, página 2: costos de intervenciones y repuestos.
- Fase 1, páginas 9–19: requerimientos y normalización.
- Fase 2, §7: R3, R5, R8, R9 y R12.

**Alternativa fundamentada:**
- Calcular el costo de reparación a partir de los costos de mano de obra y de los repuestos utilizados, conforme a los requerimientos oficiales.

**Aspecto por definir:**  
Procedimiento técnico de agregación para evitar duplicaciones cuando existan múltiples intervenciones y múltiples repuestos en una misma orden.

**Impacto:**  
Consultas SQL, vistas, procedimientos, dashboard y consistencia de resultados.


---

## 3. Decisiones pendientes del PMV

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Pendiente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D08 — Selección de las dos tablas para CRUD

**Descripción:**  
Seleccionar al menos dos tablas básicas o maestras para implementar operaciones de creación, consulta, modificación y eliminación o desactivación.

**Documentos y secciones de origen:**
- Fase 2, §10: CRUD de tablas básicas.
- Rúbrica, criterio 4.

**Alternativas fundamentadas:**
- EQUIPO y REPUESTO, mencionadas como ejemplos en el enunciado.
- Otras dos tablas básicas del modelo definitivo que cumplan la misma exigencia.

**Impacto:**  
Pantallas Streamlit, operaciones de persistencia, validaciones y pruebas de integridad.

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Pendiente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D09 — Operación del formulario transaccional

**Descripción:**  
Definir la operación que registrará el formulario transaccional del PMV.

**Documentos y secciones de origen:**
- Fase 2, §10: formulario transaccional.
- Rúbrica, criterio 4.

**Alternativas fundamentadas:**
- Registrar una nueva orden de reparación asociada a cliente, equipo y sucursal, como establece el ejemplo oficial.
- Otra transacción equivalente y debidamente justificada, permitida por el enunciado.

**Impacto:**  
Formulario, validaciones, claves foráneas, acceso a datos y registro real de la transacción.

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Pendiente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D10 — Permisos efectivos de los roles

**Descripción:**  
Definir al menos dos roles y especificar qué funcionalidades podrán utilizar.

**Documentos y secciones de origen:**
- Fase 1, página 2: administrativos, técnicos y supervisores.
- Fase 1, página 4: regla de negocio 9.
- Fase 2, §10: control de usuarios.
- Rúbrica, criterio 4.

**Alternativas fundamentadas:**
- Seleccionar al menos dos roles entre los mencionados en el caso, tales como administrativo, técnico y supervisor.

**Aspectos por definir:**
- Roles seleccionados.
- Permisos efectivos de cada rol.
- Funcionalidades restringidas.
- Comportamiento ante accesos no autorizados.

**Impacto:**  
Autenticación, navegación, control de acceso y evaluación funcional.

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Pendiente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D11 — Cuarta pregunta del dashboard

**Descripción:**  
Formular una cuarta pregunta de negocio relevante, distinta de las tres preguntas originales de Fase 1.

**Documentos y secciones de origen:**
- Fase 1, página 9: preguntas de negocio.
- Fase 2, §§2 y 10.1.
- Rúbrica, criterio 4.

**Alternativas fundamentadas:**  
El enunciado permite proponer una pregunta nueva, siempre que no sea equivalente a las anteriores. No establece una lista cerrada de alternativas.

**Aspectos por definir:**
- Redacción de la nueva pregunta.
- Justificación de su relevancia.
- Consulta SQL necesaria.
- Visualización y filtros.
- Decisión empresarial que podría apoyar.

**Impacto:**  
Dashboard, consultas SQL, documentación y presentación.

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Pendiente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D12 — Organización de la arquitectura del PMV

**Descripción:**  
Definir una estructura de archivos y componentes comprensible que permita integrar interfaz, lógica de aplicación y acceso a MySQL.

**Documentos y secciones de origen:**
- Fase 2, §§3 y 10.
- Rúbrica, criterio 5: arquitectura, integración y trazabilidad técnica.

**Alternativa fundamentada:**
- Separar presentación, lógica y acceso a datos mediante DAO o una capa equivalente, centralizando la conexión y declarando las dependencias.

La rúbrica menciona `app.py`, páginas, `conexion.py`, DAO y `requirements.txt` como componentes que el equipo debe poder identificar y explicar.

**Impacto:**  
Organización del repositorio, mantenibilidad, integración, pruebas y defensa técnica individual.


---

## 4. Decisiones que requieren aclaración docente

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Pendiente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D13 — Asignación de cuatro responsables principales en un equipo de dos estudiantes

**Descripción:**  
El Grupo 8 tiene dos integrantes, mientras que Fase 2 exige que las cuatro funcionalidades del PMV tengan responsables principales distintos.

**Documentos y secciones de origen:**
- Fase 1, página 1: identificación de dos integrantes.
- Fase 2, §14: plan de responsabilidades y condiciones de participación.
- Rúbrica, criterio 7.

**Alternativas fundamentadas:**
- Solicitar al docente una aclaración o excepción para equipos de dos integrantes.
- Proponer que cada integrante asuma el liderazgo de dos funcionalidades, sujeto a autorización docente.

**Impacto:**  
Matriz de responsabilidades, bitácoras, cumplimiento del enunciado y evaluación de gestión del equipo.

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Requiere aclaración docente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar (docente para la resolución)._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

### D14 — Referencias ajenas al caso en el poblamiento de datos

**Descripción:**  
La sección de poblamiento de Fase 2 menciona parques, áreas, excursiones y especies, conceptos ajenos al sistema de reparación de equipos electrónicos.

**Documento y sección de origen:**
- Fase 2, §6: poblamiento de la base de datos.

**Alternativa fundamentada:**
- Solicitar confirmación docente de que debe aplicarse la tabla específica de sucursales, clientes, equipos, órdenes, diagnósticos, intervenciones, repuestos, trabajadores, evaluaciones y usuarios/roles que aparece en esa misma sección.

**Impacto:**  
Interpretación de los requisitos de población, diseño del generador de datos y validación del proyecto.

**Registro de acuerdo (para completar por el equipo):**
- **Estado actual:** Requiere aclaración docente.
- **Acuerdo adoptado:** _Sin acuerdo registrado._
- **Justificación validada:** _Pendiente; citar regla, sección y evidencia concreta._
- **Responsable de seguimiento:** _Por asignar (docente para la resolución)._
- **Fecha de revisión/aprobación:** _Pendiente._
- **Evidencia o enlace al cambio:** _Pendiente._
- **Impacto verificado en MERE / SQL / PMV:** _Pendiente._

---

## 3. Tablero de seguimiento de la Etapa 2

| ID | Tema | Estado inicial | Acuerdo validado | Evidencia |
|---|---|---|---|---|
| D01 | Relación entre EVALUACIÓN y ORDEN_REPARACIÓN | Pendiente | — | — |
| D02 | Identificación de DIAGNÓSTICO y EVALUACIÓN | Pendiente | — | — |
| D03 | Representación de TRABAJADOR, TÉCNICO y funciones | Pendiente | — | — |
| D04 | Estructura de USUARIO, ROL y permisos | Pendiente | — | — |
| D05 | Implementación de la especialización de EQUIPO | Pendiente | — | — |
| D06 | Identificación de INTERVENCIÓN_TÉCNICA y TIPO DE TRABAJO | Pendiente | — | — |
| D07 | Cálculo del costo total de reparación | Pendiente | — | — |
| D08 | Selección de las dos tablas para CRUD | Pendiente | — | — |
| D09 | Operación del formulario transaccional | Pendiente | — | — |
| D10 | Permisos efectivos de los roles | Pendiente | — | — |
| D11 | Cuarta pregunta del dashboard | Pendiente | — | — |
| D12 | Organización de la arquitectura del PMV | Pendiente | — | — |
| D13 | Asignación de cuatro responsables principales en un equipo de dos estudiantes | Requiere aclaración docente | — | — |
| D14 | Referencias ajenas al caso en el poblamiento de datos | Requiere aclaración docente | — | — |

**Resumen inicial:** 12 decisiones técnicas pendientes de validación del equipo y 2 consultas a resolver con el docente. **Aprobadas: 0.**

## 4. Comprobación para producir `SPEC.md`

- [ ] D01–D07 revisadas frente al MERE y las reglas originales.
- [ ] Registro de acuerdos de arquitectura y PMV D08–D12 actualizado, sin inventar decisiones.
- [ ] D13 y D14 enviadas a consulta docente o registradas como abiertas.
- [ ] Se explicitan supuestos y elementos aún abiertos en `SPEC.md`.
- [ ] Se guarda este registro en `docs/DECISIONES_DISENO.md`.
- [ ] Se realiza commit con mensaje descriptivo y se registra el enlace en las evidencias del equipo.

## 5. Fuentes citadas por el análisis inicial

- Informe de Fase 1 del Grupo 8, citado en `DecisionesPendientes.md` como `InformeFase1_Grupo8.pdf.pdf` (verificar el nombre real del archivo local).
- Enunciado oficial `Caso8_ProyectoFase2.pdf`.
- Rúbrica oficial `RubricaProyectoFase2.pdf`.

**Nota:** Las citas de páginas y secciones reproducen las referencias consignadas en el análisis de Etapa 1 y deben corroborarse al abrir los documentos originales. Este registro no contiene SQL ni código Python.
