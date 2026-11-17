-- CASO 8 / FASE 2 — DDL PROVISIONAL (hipotesis D01–D07, NO aprobadas)
-- MySQL 8.0.16+ para CHECK. Ejecutar solo en entorno de desarrollo.
-- ADVERTENCIA: DROP DATABASE elimina TODOS los objetos y datos existentes.
-- Revisar/ratificar el MERE antes de considerar este archivo definitivo.

-- BLOQUE 1. Reconstruccion reproducible del esquema.
DROP DATABASE IF EXISTS caso8_reparaciones;
CREATE DATABASE caso8_reparaciones CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
USE caso8_reparaciones;

-- BLOQUE 2. Entidades maestras descritas en el caso.
CREATE TABLE cliente (
  id_cliente VARCHAR(30) PRIMARY KEY,
  nombre VARCHAR(160) NOT NULL,
  telefono VARCHAR(30) NOT NULL,
  clasificacion VARCHAR(60) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE sucursal (
  codigo_sucursal VARCHAR(20) PRIMARY KEY,
  nombre VARCHAR(120) NOT NULL,
  direccion VARCHAR(200) NOT NULL,
  comuna VARCHAR(100) NOT NULL,
  capacidad_atencion INT NOT NULL,
  horario_funcionamiento VARCHAR(120) NOT NULL,
  CONSTRAINT chk_sucursal_capacidad CHECK (capacidad_atencion >= 0)
) ENGINE=InnoDB;

-- BLOQUE 3. EQUIPO y especializacion parcial/disyuntiva (D05).
-- ATENCION: las FK por si solas NO impiden pertenecer a dos subtipos.
CREATE TABLE equipo (
  codigo_interno VARCHAR(30) PRIMARY KEY,
  id_cliente VARCHAR(30) NOT NULL,
  marca VARCHAR(100) NOT NULL,
  modelo VARCHAR(100) NOT NULL,
  numero_serie VARCHAR(100) NOT NULL,
  fecha_aprox_compra DATE NULL,
  estado_conservacion VARCHAR(100) NOT NULL,
  CONSTRAINT uq_equipo_cliente UNIQUE (codigo_interno, id_cliente),
  CONSTRAINT fk_equipo_cliente FOREIGN KEY (id_cliente)
    REFERENCES cliente(id_cliente)
) ENGINE=InnoDB;

CREATE TABLE computador (
  codigo_interno VARCHAR(30) PRIMARY KEY,
  sistema_operativo VARCHAR(100) NOT NULL,
  memoria VARCHAR(100) NOT NULL,
  tipo_almacenamiento VARCHAR(100) NOT NULL,
  CONSTRAINT fk_computador_equipo FOREIGN KEY (codigo_interno)
    REFERENCES equipo(codigo_interno)
) ENGINE=InnoDB;

CREATE TABLE telefono_movil (
  codigo_interno VARCHAR(30) PRIMARY KEY,
  operador VARCHAR(100) NOT NULL,
  imei VARCHAR(30) NOT NULL,
  version_sistema VARCHAR(100) NOT NULL,
  CONSTRAINT uq_telefono_imei UNIQUE (imei),
  CONSTRAINT fk_telefono_equipo FOREIGN KEY (codigo_interno)
    REFERENCES equipo(codigo_interno)
) ENGINE=InnoDB;

CREATE TABLE tablet (
  codigo_interno VARCHAR(30) PRIMARY KEY,
  tamano_pantalla VARCHAR(60) NOT NULL,
  capacidad VARCHAR(100) NOT NULL,
  conectividad VARCHAR(100) NOT NULL,
  CONSTRAINT fk_tablet_equipo FOREIGN KEY (codigo_interno)
    REFERENCES equipo(codigo_interno)
) ENGINE=InnoDB;

-- BLOQUE 4. Personal y sus funciones multiples (D03: propuesta, NO ratificada).
CREATE TABLE trabajador (
  id_trabajador INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(160) NOT NULL,
  contacto VARCHAR(160) NULL
) ENGINE=InnoDB;

CREATE TABLE funcion (
  id_funcion INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(100) NOT NULL,
  CONSTRAINT uq_funcion_nombre UNIQUE (nombre)
) ENGINE=InnoDB;

CREATE TABLE trabajador_funcion (
  id_trabajador INT NOT NULL,
  id_funcion INT NOT NULL,
  PRIMARY KEY (id_trabajador, id_funcion),
  CONSTRAINT fk_tf_trabajador FOREIGN KEY (id_trabajador)
    REFERENCES trabajador(id_trabajador),
  CONSTRAINT fk_tf_funcion FOREIGN KEY (id_funcion)
    REFERENCES funcion(id_funcion)
) ENGINE=InnoDB;

-- BLOQUE 5. Ordenes, entidades debiles y proceso de reparacion (D01, D02, D06).
CREATE TABLE orden_reparacion (
  numero_orden INT AUTO_INCREMENT PRIMARY KEY,
  id_cliente VARCHAR(30) NOT NULL,
  codigo_interno VARCHAR(30) NOT NULL,
  codigo_sucursal VARCHAR(20) NOT NULL,
  fecha_recepcion DATE NOT NULL,
  problema_informado TEXT NOT NULL,
  estado_actual VARCHAR(80) NOT NULL,
  fecha_comprometida DATE NOT NULL,
  CONSTRAINT fk_orden_cliente FOREIGN KEY (id_cliente)
    REFERENCES cliente(id_cliente),
  CONSTRAINT fk_orden_equipo_cliente FOREIGN KEY (codigo_interno, id_cliente)
    REFERENCES equipo(codigo_interno, id_cliente),
  CONSTRAINT fk_orden_sucursal FOREIGN KEY (codigo_sucursal)
    REFERENCES sucursal(codigo_sucursal)
) ENGINE=InnoDB;

CREATE TABLE diagnostico (
  numero_orden INT NOT NULL,
  correlativo_diagnostico INT NOT NULL,
  fecha DATE NOT NULL,
  falla_detectada VARCHAR(250) NOT NULL,
  nivel_gravedad VARCHAR(80) NOT NULL,
  recomendacion_tecnica TEXT NOT NULL,
  observaciones TEXT NULL,
  PRIMARY KEY (numero_orden, correlativo_diagnostico),
  CONSTRAINT chk_diagnostico_correlativo CHECK (correlativo_diagnostico > 0),
  CONSTRAINT fk_diagnostico_orden FOREIGN KEY (numero_orden)
    REFERENCES orden_reparacion(numero_orden)
) ENGINE=InnoDB;

CREATE TABLE evaluacion (
  numero_orden INT NOT NULL,
  correlativo_evaluacion INT NOT NULL,
  fecha DATE NOT NULL,
  calificacion DECIMAL(4,2) NOT NULL,
  cumplimiento_plazo BOOLEAN NOT NULL,
  comentario TEXT NULL,
  PRIMARY KEY (numero_orden, correlativo_evaluacion),
  CONSTRAINT chk_evaluacion_correlativo CHECK (correlativo_evaluacion > 0),
  CONSTRAINT chk_evaluacion_calificacion CHECK (calificacion >= 0),
  CONSTRAINT chk_evaluacion_plazo CHECK (cumplimiento_plazo IN (0,1)),
  CONSTRAINT fk_evaluacion_orden FOREIGN KEY (numero_orden)
    REFERENCES orden_reparacion(numero_orden)
) ENGINE=InnoDB;

-- El tipo de trabajo se almacena como atributo descriptivo provisional:
-- un catalogo TIPO_TRABAJO podria requerir ratificacion adicional en D06.
CREATE TABLE intervencion_tecnica (
  id_intervencion INT AUTO_INCREMENT PRIMARY KEY,
  numero_orden INT NOT NULL,
  id_trabajador INT NOT NULL,
  tipo_trabajo VARCHAR(120) NOT NULL,
  fecha DATE NOT NULL,
  duracion_minutos INT NOT NULL,
  resultado TEXT NOT NULL,
  observaciones TEXT NULL,
  costo_mano_obra DECIMAL(12,2) NOT NULL,
  CONSTRAINT chk_intervencion_duracion CHECK (duracion_minutos > 0),
  CONSTRAINT chk_intervencion_costo CHECK (costo_mano_obra >= 0),
  CONSTRAINT fk_intervencion_orden FOREIGN KEY (numero_orden)
    REFERENCES orden_reparacion(numero_orden),
  CONSTRAINT fk_intervencion_trabajador FOREIGN KEY (id_trabajador)
    REFERENCES trabajador(id_trabajador)
) ENGINE=InnoDB;

-- BLOQUE 6. Repuestos consumidos por orden (D07).
CREATE TABLE repuesto (
  numero_repuesto INT AUTO_INCREMENT PRIMARY KEY,
  tipo VARCHAR(100) NOT NULL,
  precio_referencia DECIMAL(12,2) NOT NULL,
  disponibilidad INT NOT NULL,
  CONSTRAINT chk_repuesto_precio CHECK (precio_referencia >= 0),
  CONSTRAINT chk_repuesto_disponibilidad CHECK (disponibilidad >= 0)
) ENGINE=InnoDB;

-- PK compuesta: un registro por par orden/repuesto, supuesto a ratificar.
-- Si se necesita registrar varias incorporaciones del mismo repuesto por orden,
-- hay que revisar esta identificacion ANTES de poblar la BD.
CREATE TABLE detalle_repuesto (
  numero_orden INT NOT NULL,
  numero_repuesto INT NOT NULL,
  cantidad INT NOT NULL,
  precio_aplicado DECIMAL(12,2) NOT NULL,
  fecha_incorporacion DATE NOT NULL,
  PRIMARY KEY (numero_orden, numero_repuesto),
  CONSTRAINT chk_detalle_cantidad CHECK (cantidad > 0),
  CONSTRAINT chk_detalle_precio CHECK (precio_aplicado >= 0),
  CONSTRAINT fk_detalle_orden FOREIGN KEY (numero_orden)
    REFERENCES orden_reparacion(numero_orden),
  CONSTRAINT fk_detalle_repuesto FOREIGN KEY (numero_repuesto)
    REFERENCES repuesto(numero_repuesto)
) ENGINE=InnoDB;

-- BLOQUE 7. Cuentas y roles (D04, aun no aprobada).
-- 'clave_hash' no representa una contrasena en texto claro.
CREATE TABLE usuario (
  id_usuario INT AUTO_INCREMENT PRIMARY KEY,
  id_trabajador INT NOT NULL,
  nombre_usuario VARCHAR(100) NOT NULL,
  clave_hash VARCHAR(255) NOT NULL,
  CONSTRAINT uq_usuario_trabajador UNIQUE (id_trabajador),
  CONSTRAINT uq_usuario_nombre UNIQUE (nombre_usuario),
  CONSTRAINT fk_usuario_trabajador FOREIGN KEY (id_trabajador)
    REFERENCES trabajador(id_trabajador)
) ENGINE=InnoDB;

CREATE TABLE rol (
  id_rol INT AUTO_INCREMENT PRIMARY KEY,
  nombre VARCHAR(80) NOT NULL,
  descripcion VARCHAR(250) NULL,
  CONSTRAINT uq_rol_nombre UNIQUE (nombre)
) ENGINE=InnoDB;

CREATE TABLE usuario_rol (
  id_usuario INT NOT NULL,
  id_rol INT NOT NULL,
  PRIMARY KEY (id_usuario, id_rol),
  CONSTRAINT fk_ur_usuario FOREIGN KEY (id_usuario)
    REFERENCES usuario(id_usuario),
  CONSTRAINT fk_ur_rol FOREIGN KEY (id_rol)
    REFERENCES rol(id_rol)
) ENGINE=InnoDB;

-- BLOQUE 8. Comprobacion estructural (solo consultas de metadatos, SIN datos de prueba).
SHOW TABLES;
SELECT table_name, constraint_name, constraint_type
FROM information_schema.table_constraints
WHERE table_schema = DATABASE()
ORDER BY table_name, constraint_type, constraint_name;

-- PENDIENTE DE RATIFICACION / NO GARANTIZADO SOLO CON ESTE DDL:
-- 1) Disyuncion de COMPUTADOR/TELEFONO_MOVIL/TABLET (D05).
-- 2) Al menos un rol por usuario y al menos un diagnostico por orden.
-- 3) Habilitacion/certificacion del trabajador para cada tipo de trabajo (D03/D06).
-- 4) Secuencia automatica del correlativo dentro de cada orden (D02).
-- 5) Momento valido de evaluacion: despues de la entrega del equipo.
-- 6) Limite superior y escala de calificacion no definidos por el caso.
-- 7) Desactivar/eliminar registros con historial requiere politica de aplicacion.
-- 8) Unicidad orden/repuesto impide mas de una incorporacion del mismo repuesto.
-- 9) Costos totales (D07) se calcularan luego, no se almacenan ni crean vistas ahora.
