"""Negocio del dashboard: autorizaciones y filtros sin escrituras."""
from datetime import date
from sqlalchemy.exc import SQLAlchemyError
from db.connection import get_engine
from db import dashboard_dao, seguridad_dao
from services.seguridad_service import AccesoDenegado


class ErrorDashboard(Exception):
    """Fallo controlado en consulta o filtro."""


def _validar_actor(conn, actor_id):
    if (not isinstance(actor_id, int) or
        not (seguridad_dao.tiene_rol(conn, actor_id, 'Administrador') or
             seguridad_dao.tiene_rol(conn, actor_id, 'Consulta'))):
        raise AccesoDenegado('Debe iniciar sesión con un rol autorizado para consultar el dashboard.')


def _ejecutar(actor_id, funcion, *args):
    try:
        with get_engine().connect() as conn:
            _validar_actor(conn, actor_id)
            return funcion(conn, *args)
    except SQLAlchemyError as exc:
        raise ErrorDashboard('No fue posible consultar el dashboard en MySQL.') from exc


def obtener_filtros(actor_id):
    return _ejecutar(actor_id, dashboard_dao.opciones_filtros)


def consultar_pregunta(actor_id, pregunta, desde, hasta, sucursal='', tipo='', estado=''):
    if not isinstance(desde, date) or not isinstance(hasta, date) or desde > hasta:
        raise ErrorDashboard('El período seleccionado no es válido.')
    if pregunta not in ('P1', 'P2', 'P3', 'P4'):
        raise ErrorDashboard('Pregunta desconocida.')
    tipos = ('', 'COMPUTADOR', 'TELEFONO_MOVIL', 'TABLET',
             'SIN_CLASIFICAR', 'INCONSISTENTE')
    if tipo not in tipos:
        raise ErrorDashboard('Tipo de equipo inválido.')
    if not isinstance(sucursal, str) or len(sucursal) > 20:
        raise ErrorDashboard('Sucursal inválida.')
    if not isinstance(estado, str) or len(estado) > 80:
        raise ErrorDashboard('Estado inválido.')
    p = {'desde': desde, 'hasta': hasta, 'sucursal': sucursal,
         'tipo': tipo, 'estado': estado}
    def consulta(conn):
        # Validación contra catálogos efectivamente existentes.
        filtros = dashboard_dao.opciones_filtros(conn)
        if sucursal and sucursal not in {s['codigo_sucursal'] for s in filtros['sucursales']}:
            raise ErrorDashboard('La sucursal seleccionada no existe.')
        if estado and estado not in filtros['estados']:
            raise ErrorDashboard('El estado seleccionado no existe.')
        if pregunta == 'P1':
            return {'datos': dashboard_dao.p1_ordenes_tipo(conn, p)}
        if pregunta == 'P2':
            return {'datos': dashboard_dao.p2_distribucion(conn, p),
                    'excluidas': dashboard_dao.p2_excluidas(conn, p)}
        if pregunta == 'P3':
            return {'datos': dashboard_dao.p3_costos_evaluaciones(conn, p)}
        return {'datos': dashboard_dao.p4_estados_sucursal(conn, p)}
    return _ejecutar(actor_id, consulta)
