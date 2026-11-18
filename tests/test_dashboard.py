"""Pruebas de P1-P4 con SQLite TEMPORAL; no modifican la base MySQL real."""
import unittest
from datetime import date
from unittest.mock import patch
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool
from db import dashboard_dao as dao
from services import dashboard_service as svc
from services.seguridad_service import AccesoDenegado


class PruebasDashboard(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite://', poolclass=StaticPool,
                                    connect_args={'check_same_thread': False})
        with self.engine.begin() as c:
            for tabla in (
                'CREATE TABLE cliente(id_cliente TEXT PRIMARY KEY,nombre TEXT)',
                'CREATE TABLE sucursal(codigo_sucursal TEXT PRIMARY KEY,nombre TEXT)',
                'CREATE TABLE equipo(codigo_interno TEXT PRIMARY KEY,id_cliente TEXT,marca TEXT,modelo TEXT)',
                'CREATE TABLE computador(codigo_interno TEXT PRIMARY KEY)',
                'CREATE TABLE telefono_movil(codigo_interno TEXT PRIMARY KEY)',
                'CREATE TABLE tablet(codigo_interno TEXT PRIMARY KEY)',
                'CREATE TABLE orden_reparacion(numero_orden INTEGER PRIMARY KEY,id_cliente TEXT,codigo_interno TEXT,codigo_sucursal TEXT,fecha_recepcion TEXT,estado_actual TEXT)',
                'CREATE TABLE intervencion_tecnica(numero_orden INTEGER,costo_mano_obra NUMERIC)',
                'CREATE TABLE detalle_repuesto(numero_orden INTEGER,cantidad INTEGER,precio_aplicado NUMERIC)',
                'CREATE TABLE evaluacion(numero_orden INTEGER,calificacion NUMERIC,fecha TEXT)'
            ):
                c.execute(text(tabla))
            sql = [
                "INSERT INTO cliente VALUES ('C1','Cliente Uno')",
                "INSERT INTO sucursal VALUES ('S1','Central')",
                "INSERT INTO equipo VALUES ('E1','C1','Marca','Modelo')",
                "INSERT INTO equipo VALUES ('E2','C1','Marca','Modelo')",
                "INSERT INTO computador VALUES ('E1')",
                "INSERT INTO orden_reparacion VALUES (1,'C1','E1','S1','2026-10-15','En proceso')",
                "INSERT INTO orden_reparacion VALUES (2,'C1','E2','S1','2026-10-16','Pendiente')",
                "INSERT INTO intervencion_tecnica VALUES (1,100)",
                "INSERT INTO intervencion_tecnica VALUES (1,200)",
                "INSERT INTO detalle_repuesto VALUES (1,2,10)",
                "INSERT INTO detalle_repuesto VALUES (1,3,20)",
                "INSERT INTO evaluacion VALUES (1,4.0,'2026-10-18')",
                "INSERT INTO evaluacion VALUES (1,5.0,'2026-10-19')",
            ]
            for q in sql:
                c.execute(text(q))
        self.p = {'desde': date(2026,10,1),'hasta':date(2026,10,31),
                  'sucursal':'','tipo':'','estado':''}

    def tearDown(self):
        self.engine.dispose()

    def test_p1_incluye_sin_clasificar(self):
        with self.engine.connect() as c:
            r = {x['tipo_equipo']: x['cantidad_ordenes'] for x in dao.p1_ordenes_tipo(c,self.p)}
        self.assertEqual(r, {'COMPUTADOR':1,'SIN_CLASIFICAR':1})

    def test_p2_excluye_sin_clasificar(self):
        with self.engine.connect() as c:
            r=dao.p2_distribucion(c,self.p)
            excl=dao.p2_excluidas(c,self.p)
        self.assertEqual(sum(x['cantidad_ordenes'] for x in r),1)
        self.assertEqual(excl[0]['tipo_equipo'],'SIN_CLASIFICAR')

    def test_p3_no_multiplica_costos_evaluaciones(self):
        with self.engine.connect() as c:
            r=dao.p3_costos_evaluaciones(c,self.p)
        self.assertEqual(len(r),1)
        self.assertEqual(float(r[0]['costo_total']), 380.0)  # 100+200+2*10+3*20
        self.assertEqual(float(r[0]['evaluacion_promedio']), 4.5)
        self.assertEqual(r[0]['cantidad_evaluaciones'],2)

    def test_p4_filtra_estado(self):
        p={**self.p,'estado':'Pendiente'}
        with self.engine.connect() as c:
            r=dao.p4_estados_sucursal(c,p)
        self.assertEqual(len(r),1)
        self.assertEqual(r[0]['cantidad_ordenes'],1)

    def test_sin_datos_en_periodo(self):
        p={**self.p,'desde':date(2024,1,1),'hasta':date(2024,1,2)}
        with self.engine.connect() as c:
            self.assertEqual(dao.p1_ordenes_tipo(c,p),[])
            self.assertEqual(dao.p3_costos_evaluaciones(c,p),[])

    def test_rango_invalido(self):
        with self.assertRaises(svc.ErrorDashboard):
            svc.consultar_pregunta(1,'P1',date(2026,12,1),date(2026,1,1))

    def test_autorizacion_en_servicio(self):
        with patch.object(svc, 'get_engine', return_value=self.engine), \
             patch.object(svc.seguridad_dao, 'tiene_rol', return_value=False):
            with self.assertRaises(AccesoDenegado):
                svc.consultar_pregunta(99,'P4',self.p['desde'],self.p['hasta'])
        with patch.object(svc, 'get_engine', return_value=self.engine), \
             patch.object(svc.seguridad_dao, 'tiene_rol',
                          side_effect=lambda conn,uid,rol: uid==3 and rol=='Consulta'):
            r=svc.consultar_pregunta(3,'P4',self.p['desde'],self.p['hasta'])
            self.assertEqual(len(r['datos']),2)


if __name__ == '__main__':
    unittest.main()
