"""Pruebas de autenticación y autorización (sin modificar MySQL)."""
import unittest
from unittest.mock import patch
import bcrypt
from sqlalchemy import create_engine, text
from services import seguridad_service as auth
from services import operaciones_service as operaciones
from db import operaciones_dao as dao

class SeguridadVideo8(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine('sqlite+pysqlite:///:memory:')
        h = bcrypt.hashpw(b'ClaveSeguraDemo123!', bcrypt.gensalt(rounds=4)).decode()
        with self.engine.begin() as c:
            c.execute(text('CREATE TABLE usuario (id_usuario INTEGER PRIMARY KEY,id_trabajador INTEGER,nombre_usuario TEXT,clave_hash TEXT)'))
            c.execute(text('CREATE TABLE rol (id_rol INTEGER PRIMARY KEY,nombre TEXT)'))
            c.execute(text('CREATE TABLE usuario_rol (id_usuario INTEGER,id_rol INTEGER)'))
            c.execute(text('CREATE TABLE repuesto (numero_repuesto INTEGER PRIMARY KEY AUTOINCREMENT,tipo TEXT,precio_referencia NUMERIC,disponibilidad INTEGER)'))
            c.execute(text('INSERT INTO usuario VALUES (1,1,:u,:h),(2,2,:v,:h)'),
                      {'u':'admin_prueba','v':'consulta_prueba','h':h})
            c.execute(text("INSERT INTO rol VALUES (1,'Administrador'),(2,'Consulta')"))
            c.execute(text('INSERT INTO usuario_rol VALUES (1,1),(2,2)'))
        self.p1=patch.object(auth, 'get_engine', return_value=self.engine)
        self.p2=patch.object(operaciones, 'get_engine', return_value=self.engine)
        self.p1.start(); self.p2.start()

    def tearDown(self):
        self.p1.stop(); self.p2.stop()
        self.engine.dispose()

    def test_credenciales_validas(self):
        self.assertEqual(auth.autenticar('admin_prueba','ClaveSeguraDemo123!')['id_usuario'],1)
        self.assertEqual(auth.autenticar('consulta_prueba','ClaveSeguraDemo123!')['roles'],['Consulta'])

    def test_contrasena_incorrecta(self):
        with self.assertRaises(auth.AccesoDenegado):
            auth.autenticar('admin_prueba','incorrecta')

    def test_usuario_inexistente(self):
        with self.assertRaises(auth.AccesoDenegado):
            auth.autenticar('no_existe','ClaveSeguraDemo123!')

    def test_consulta_sin_permiso_de_escritura(self):
        with self.assertRaises(auth.AccesoDenegado):
            operaciones.crear_repuesto(actor_id=2, **operaciones.datos_repuesto('Demo',100,4))
        with self.engine.connect() as c:
            self.assertEqual(c.execute(text('SELECT COUNT(*) FROM repuesto')).scalar_one(),0)
        with self.assertRaises(auth.AccesoDenegado):
            operaciones.crear_repuesto(**operaciones.datos_repuesto('SinSesión',1,1))

    def test_administrador_puede_operar(self):
        numero = operaciones.crear_repuesto(actor_id=1, **operaciones.datos_repuesto('Demo',100,4))
        self.assertIsNotNone(numero)
        operaciones.actualizar_repuesto(numero,actor_id=1,**operaciones.datos_repuesto('Demo2',200,5))
        with self.engine.connect() as c:
            self.assertEqual(c.execute(text('SELECT tipo FROM repuesto WHERE numero_repuesto=:n'),{'n':numero}).scalar_one(),'Demo2')
        operaciones.borrar_repuesto(numero,actor_id=1)

    def test_cierre_de_sesion_no_autoriza(self):
        # La UI elimina auth_usuario_id de st.session_state al cerrar sesión.
        # Ninguna operación permite escritura sin una identidad autenticada.
        with self.assertRaises(auth.AccesoDenegado):
            operaciones.borrar_repuesto(999,actor_id=None)

if __name__ == '__main__':
    unittest.main()
