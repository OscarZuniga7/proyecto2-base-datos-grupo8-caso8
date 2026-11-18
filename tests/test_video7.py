"""Pruebas de operaciones y restricciones con SQLite en memoria; no modifica MySQL."""
import unittest
from datetime import date
from unittest.mock import patch
from sqlalchemy import create_engine, text, event
from sqlalchemy.exc import IntegrityError
from db import operaciones_dao as dao
from services import operaciones_service as svc


class Video7(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite+pysqlite:///:memory:')
        @event.listens_for(self.engine, 'connect')
        def fk_on(conn, rec):
            conn.execute('PRAGMA foreign_keys=ON')
        with self.engine.begin() as c:
            c.execute(text('CREATE TABLE usuario (id_usuario INTEGER PRIMARY KEY, nombre_usuario TEXT, clave_hash TEXT)'))
            c.execute(text('CREATE TABLE rol (id_rol INTEGER PRIMARY KEY, nombre TEXT)'))
            c.execute(text('CREATE TABLE usuario_rol (id_usuario INTEGER, id_rol INTEGER)'))
            c.execute(text("INSERT INTO usuario VALUES (1,'admin_demo','bcrypt-demo'),(2,'consulta_demo','bcrypt-demo')"))
            c.execute(text("INSERT INTO rol VALUES (1,'Administrador'),(2,'Consulta')"))
            c.execute(text("INSERT INTO usuario_rol VALUES (1,1),(2,2)"))
            c.execute(text('CREATE TABLE cliente (id_cliente TEXT PRIMARY KEY, nombre TEXT NOT NULL)'))
            c.execute(text('CREATE TABLE sucursal (codigo_sucursal TEXT PRIMARY KEY, nombre TEXT NOT NULL)'))
            c.execute(text('CREATE TABLE equipo (codigo_interno TEXT PRIMARY KEY, id_cliente TEXT NOT NULL, marca TEXT NOT NULL, modelo TEXT NOT NULL, numero_serie TEXT NOT NULL, fecha_aprox_compra DATE, estado_conservacion TEXT NOT NULL, FOREIGN KEY(id_cliente) REFERENCES cliente(id_cliente), UNIQUE(codigo_interno,id_cliente))'))
            c.execute(text('CREATE TABLE orden_reparacion (numero_orden INTEGER PRIMARY KEY AUTOINCREMENT, id_cliente TEXT NOT NULL, codigo_interno TEXT NOT NULL, codigo_sucursal TEXT NOT NULL, fecha_recepcion DATE NOT NULL, fecha_comprometida DATE NOT NULL, problema_informado TEXT NOT NULL, estado_actual TEXT NOT NULL, FOREIGN KEY(codigo_interno,id_cliente) REFERENCES equipo(codigo_interno,id_cliente), FOREIGN KEY(codigo_sucursal) REFERENCES sucursal(codigo_sucursal))'))
            c.execute(text('CREATE TABLE repuesto (numero_repuesto INTEGER PRIMARY KEY AUTOINCREMENT, tipo TEXT NOT NULL, precio_referencia NUMERIC NOT NULL CHECK(precio_referencia>=0), disponibilidad INTEGER NOT NULL CHECK(disponibilidad>=0))'))
            c.execute(text('CREATE TABLE detalle_repuesto (numero_orden INTEGER, numero_repuesto INTEGER, FOREIGN KEY(numero_repuesto) REFERENCES repuesto(numero_repuesto))'))
            c.execute(text("INSERT INTO cliente VALUES ('C1','Cliente uno'),('C2','Cliente dos')"))
            c.execute(text("INSERT INTO sucursal VALUES ('S1','Principal')"))
            c.execute(text("INSERT INTO equipo VALUES ('E1','C1','Marca','Modelo','Serie',NULL,'Bueno')"))
            c.execute(text("INSERT INTO orden_reparacion (id_cliente,codigo_interno,codigo_sucursal,fecha_recepcion,fecha_comprometida,problema_informado,estado_actual) VALUES ('C1','E1','S1','2026-11-01','2026-11-02','Problema','Recibida')"))
        self.patcher=patch.object(svc,'get_engine',return_value=self.engine)
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.engine.dispose()

    def test_crear_consultar_actualizar_equipo(self):
        d=svc.datos_equipo('E2','C2','A','B','S2',None,'Bueno')
        svc.crear_equipo(actor_id=1,**d)
        self.assertEqual(len(svc.consultar(dao.equipos_de_cliente,'C2')),1)
        d['marca']='Otra'
        d.pop('codigo_interno')
        svc.actualizar_equipo('E2',actor_id=1,**d)
        self.assertEqual(svc.consultar(dao.equipos,'E2')[0]['marca'],'Otra')
        svc.borrar_equipo('E2',actor_id=1)
        self.assertEqual(svc.consultar(dao.equipos,'E2'),[])

    def test_rechaza_eliminar_equipo_con_orden(self):
        with self.assertRaises(svc.ErrorNegocio):
            svc.borrar_equipo('E1',actor_id=1)
        self.assertEqual(len(svc.consultar(dao.equipos,'E1')),1)

    def test_crear_orden_y_filtrar_por_cliente(self):
        with self.assertRaises(svc.ErrorNegocio):
            svc.registrar_orden('C2','E1','S1',date(2026,11,1),date(2026,11,3),'Problema','Recibida',actor_id=1)
        n=svc.registrar_orden('C1','E1','S1',date(2026,11,1),date(2026,11,3),'Problema','Recibida',actor_id=1)
        self.assertIsNotNone(n)
        self.assertEqual(len(svc.consultar(dao.ordenes_recientes)),2)

    def test_repuesto_crud_y_bloqueo_referenciado(self):
        d=svc.datos_repuesto('Pantalla',100,5)
        n=svc.crear_repuesto(actor_id=1,**d)
        self.assertEqual(len(svc.consultar(dao.repuestos,'Pantalla')),1)
        svc.actualizar_repuesto(n,actor_id=1,**svc.datos_repuesto('Pantalla nueva',120,6))
        self.assertEqual(svc.consultar(dao.repuestos,'Pantalla nueva')[0]['disponibilidad'],6)
        with self.engine.begin() as c:
            c.execute(text('INSERT INTO detalle_repuesto (numero_orden,numero_repuesto) VALUES (1,:n)'),{'n':n})
        with self.assertRaises(svc.ErrorNegocio):
            svc.borrar_repuesto(n,actor_id=1)
        with self.engine.begin() as c:
            c.execute(text('DELETE FROM detalle_repuesto WHERE numero_repuesto=:n'),{'n':n})
        svc.borrar_repuesto(n,actor_id=1)
        self.assertEqual(svc.consultar(dao.repuestos,'Pantalla nueva'),[])

    def test_rollback_ante_fallo_y_duplicados(self):
        datos=svc.datos_equipo('E1','C1','A','B','S2',None,'Bueno')
        with self.assertRaises(svc.ErrorNegocio):
            svc.crear_equipo(actor_id=1,**datos)
        self.assertEqual(len(svc.consultar(dao.equipos,'E1')),1)
        with self.assertRaises(svc.ErrorNegocio):
            svc.crear_repuesto(actor_id=1,**svc.datos_repuesto('Negativo',-1,0))

if __name__=='__main__':
    unittest.main()
