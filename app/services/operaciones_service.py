"""Reglas de presentación/negocio, transacciones y manejo de errores."""
from datetime import date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from db.connection import get_engine
from db import operaciones_dao as dao


class ErrorNegocio(Exception):
    pass


def consultar(funcion, *args):
    try:
        with get_engine().connect() as conn:
            return funcion(conn, *args)
    except SQLAlchemyError as exc:
        raise ErrorNegocio('No fue posible consultar MySQL. Revise los registros de app y db.') from exc


def ejecutar(funcion, *args):
    try:
        # engine.begin confirma automáticamente; si falla ejecuta ROLLBACK.
        with get_engine().begin() as conn:
            return funcion(conn, *args)
    except IntegrityError as exc:
        raise ErrorNegocio('Operación rechazada: clave duplicada o registro relacionado por FK. No se modificaron datos.') from exc
    except SQLAlchemyError as exc:
        raise ErrorNegocio('No se pudo guardar. Se revirtió la transacción; revise el registro del contenedor.') from exc


def _texto(valor, nombre, maximo=None):
    s = str(valor or '').strip()
    if not s or (maximo is not None and len(s) > maximo):
        raise ErrorNegocio(f'{nombre}: valor vacío o longitud mayor que {maximo}.')
    return s


def registrar_orden(id_cliente,codigo_interno,codigo_sucursal,fecha_recepcion,fecha_comprometida,problema,estado):
    datos = dict(id_cliente=_texto(id_cliente,'Cliente',30),codigo_interno=_texto(codigo_interno,'Equipo',30),
      codigo_sucursal=_texto(codigo_sucursal,'Sucursal',20),fecha_recepcion=fecha_recepcion,
      fecha_comprometida=fecha_comprometida,problema_informado=_texto(problema,'Problema'),
      estado_actual=_texto(estado,'Estado',80))
    if not isinstance(fecha_recepcion,date) or not isinstance(fecha_comprometida,date):
        raise ErrorNegocio('Las fechas deben ser válidas.')
    if fecha_comprometida < fecha_recepcion:
        raise ErrorNegocio('La fecha comprometida no puede anteceder a la recepción (validación propuesta).')
    # Revalidar dentro de la transacción; la FK compuesta da protección adicional.
    def operacion(conn):
        if codigo_interno not in {e['codigo_interno'] for e in dao.equipos_de_cliente(conn,id_cliente)}:
            raise ErrorNegocio('El equipo no pertenece al cliente seleccionado.')
        if estado not in dao.estados_existentes(conn):
            raise ErrorNegocio('El estado no figura entre los estados ya usados en la base.')
        return dao.crear_orden(conn,datos)
    return ejecutar(operacion)


def datos_equipo(codigo,id_cliente,marca,modelo,serie,compra,conservacion):
    return dict(codigo_interno=_texto(codigo,'Código',30), id_cliente=_texto(id_cliente,'Cliente',30),
      marca=_texto(marca,'Marca',100),modelo=_texto(modelo,'Modelo',100),
      numero_serie=_texto(serie,'N° de serie',100),fecha_aprox_compra=compra,
      estado_conservacion=_texto(conservacion,'Conservación',100))


def crear_equipo(**datos):
    return ejecutar(dao.crear_equipo, datos)


def actualizar_equipo(codigo, **datos):
    n = ejecutar(dao.modificar_equipo,codigo,datos)
    if n == 0: raise ErrorNegocio('Equipo no encontrado o sin cambios.')
    return n


def borrar_equipo(codigo):
    n = ejecutar(dao.eliminar_equipo,codigo)
    if n == 0: raise ErrorNegocio('Equipo no encontrado.')
    return n


def datos_repuesto(tipo,precio,disponibilidad):
    tipo = _texto(tipo,'Tipo',100)
    precio = Decimal(str(precio))
    if not precio.is_finite() or precio < 0 or precio > Decimal('9999999999.99') or disponibilidad < 0:
        raise ErrorNegocio('Precio o disponibilidad fuera del rango permitido.')
    return dict(tipo=tipo,precio_referencia=precio,disponibilidad=int(disponibilidad))


def crear_repuesto(**datos):
    return ejecutar(dao.crear_repuesto,datos)


def actualizar_repuesto(numero,**datos):
    n = ejecutar(dao.modificar_repuesto,numero,datos)
    if n == 0: raise ErrorNegocio('Repuesto no encontrado o sin cambios.')
    return n


def borrar_repuesto(numero):
    n = ejecutar(dao.eliminar_repuesto,numero)
    if n == 0: raise ErrorNegocio('Repuesto no encontrado.')
    return n
