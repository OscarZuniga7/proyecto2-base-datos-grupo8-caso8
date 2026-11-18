"""Video 8: inicio de sesión y autorización, sin perder las funciones del Video 7."""
from datetime import date
import streamlit as st
from services.resumen_service import DatabaseUnavailable, obtener_resumen
from services import operaciones_service as svc
from services import seguridad_service as seguridad
from db import operaciones_dao as dao
from dashboard import mostrar_dashboard

st.set_page_config(page_title="Caso 8 | Reparaciones", page_icon="🔧", layout="wide")
st.title("🔧 Sistema de Gestión de Reparaciones")
st.caption("Proyecto Fase 2 · Grupo 8 · Control de usuarios (Video 8)")

usuario_id = st.session_state.get("auth_usuario_id")
principal = seguridad.obtener_sesion(usuario_id) if usuario_id is not None else None
if usuario_id is not None and principal is None:
    st.session_state.pop("auth_usuario_id", None)

if principal is None:
    st.subheader("Inicio de sesión")
    with st.form("form_login", clear_on_submit=True):
        nombre = st.text_input("Nombre de usuario")
        clave = st.text_input("Contraseña", type="password")
        ingresar = st.form_submit_button("Ingresar")
    if ingresar:
        try:
            sesion = seguridad.autenticar(nombre, clave)
            st.session_state["auth_usuario_id"] = sesion["id_usuario"]
            st.rerun()
        except seguridad.AccesoDenegado as exc:
            st.error(str(exc))
    st.stop()

actor_id = principal["id_usuario"]
es_admin = "Administrador" in principal["roles"]
col_info, col_cerrar = st.columns([5, 1])
col_info.caption(f"Sesión: {principal['nombre_usuario']} · Roles: {', '.join(principal['roles'])}")
if col_cerrar.button("Cerrar sesión"):
    st.session_state.pop("auth_usuario_id", None)
    st.rerun()


def informar(accion):
    try:
        resultado = accion()
        st.success(f"Operación confirmada en MySQL. {resultado if resultado is not None else ''}")
        return True
    except (svc.ErrorNegocio, DatabaseUnavailable, seguridad.AccesoDenegado) as exc:
        st.error(str(exc))
        return False


def cargar(dao_fn, *args):
    try:
        return svc.consultar(dao_fn, *args)
    except svc.ErrorNegocio as exc:
        st.error(str(exc))
        return []

inicio, ordenes, equipos_tab, repuestos_tab, dashboard_tab = st.tabs(
    ["Inicio · Video 6", "Registrar orden", "CRUD EQUIPO", "CRUD REPUESTO", "Dashboard · Video 8.2"]
)
with inicio:
    st.subheader('Conectividad y resumen (Video 6)')
    if st.button('Consultar datos',key='consultar_resumen'):
        try:
            with st.spinner('Verificando disponibilidad de MySQL...'):
                r=obtener_resumen()
            a,b=st.columns(2)
            a.metric('Clientes registrados',r['clientes'])
            b.metric('Órdenes de reparación',r['ordenes'])
            st.success('Consultas ejecutadas en caso8_reparaciones.')
        except DatabaseUnavailable as exc:
            st.warning(str(exc))
            st.info('Revise: docker compose ps y docker compose logs --tail=50 db')


with ordenes:
    if es_admin:
        st.subheader('A. Nueva orden de reparación')
        clientes=cargar(dao.clientes)
        sucursales=cargar(dao.sucursales)
        estados=cargar(dao.estados_existentes)
        if not estados:
            st.warning('No hay estados registrados en la base. Deben ratificar un catálogo válido antes de crear órdenes.')
        if clientes and sucursales and estados:
            cmap={f"{x['nombre']} · {x['id_cliente']}":x['id_cliente'] for x in clientes}
            cliente_label=st.selectbox('Cliente existente',list(cmap))
            cliente_id=cmap[cliente_label]
            lista_equipo=cargar(dao.equipos_de_cliente,cliente_id)
            mapa_equipo={f"{e['codigo_interno']} · {e['marca']} {e['modelo']}":e['codigo_interno'] for e in lista_equipo}
            if not lista_equipo:
                st.info('Este cliente no tiene equipos registrados. Créelo primero en CRUD EQUIPO.')
            else:
                with st.form('crear_orden',clear_on_submit=False):
                    el=st.selectbox('Equipo del cliente',list(mapa_equipo))
                    smap={f"{s['nombre']} · {s['codigo_sucursal']}":s['codigo_sucursal'] for s in sucursales}
                    sl=st.selectbox('Sucursal',list(smap))
                    f1=st.date_input('Fecha de recepción',value=date.today())
                    f2=st.date_input('Fecha comprometida',value=date.today())
                    problema=st.text_area('Problema informado')
                    estado=st.selectbox('Estado actual (registrado en BD)',estados)
                    ok=st.form_submit_button('Registrar orden')
                if ok:
                    informar(lambda: f"N° de orden {svc.registrar_orden(cliente_id,mapa_equipo[el],smap[sl],f1,f2,problema,estado, actor_id=actor_id)}")
    else:
        st.info("Rol de consulta: sin permiso para registrar órdenes.")
    st.write('Últimas órdenes')
    st.dataframe(cargar(dao.ordenes_recientes),use_container_width=True,hide_index=True)
    st.caption('El DDL permite registrar una orden sin diagnóstico inmediato; esta limitación de integridad sigue pendiente en el modelo.')

with equipos_tab:
    st.subheader("CRUD EQUIPO (tabla base)")
    st.info("Se muestran los datos de EQUIPO; los subtipos se administrarán en otra etapa.")
    clientes=cargar(dao.clientes)
    if es_admin:
        if clientes:
            cmap={f"{c['nombre']} · {c['id_cliente']}":c['id_cliente'] for c in clientes}
            with st.expander('Crear nuevo equipo',expanded=False):
                with st.form('equipo_crear'):
                    codigo=st.text_input('Código interno único',max_chars=30)
                    lc=st.selectbox('Cliente propietario',list(cmap),key='cliente_equipo_crear')
                    marca=st.text_input('Marca',max_chars=100)
                    modelo=st.text_input('Modelo',max_chars=100)
                    serie=st.text_input('Número de serie',max_chars=100)
                    conservacion=st.text_input('Estado de conservación',max_chars=100)
                    usar_fecha=st.checkbox('Registrar fecha aproximada de compra')
                    compra=st.date_input('Fecha aproximada de compra') if usar_fecha else None
                    ok=st.form_submit_button('Crear equipo')
                if ok:
                    try:
                        datos=svc.datos_equipo(codigo,cmap[lc],marca,modelo,serie,compra,conservacion)
                        informar(lambda:svc.crear_equipo(actor_id=actor_id, **datos))
                    except svc.ErrorNegocio as exc: st.error(str(exc))
    filtro=st.text_input('Buscar equipos por código, marca, modelo o serie')
    encontrados=cargar(dao.equipos,filtro)
    st.dataframe(encontrados,use_container_width=True,hide_index=True)
    if es_admin:
        if encontrados and clientes:
            seleccion=st.selectbox('Equipo para modificar/eliminar',[e['codigo_interno'] for e in encontrados])
            actual=next(e for e in encontrados if e['codigo_interno']==seleccion)
            id_to_label={v:k for k,v in cmap.items()}
            with st.form('equipo_editar'):
                id_label=st.selectbox('Cliente',list(cmap),index=list(cmap).index(id_to_label[actual['id_cliente']]))
                marca=st.text_input('Marca',value=actual['marca'],key='eq_m')
                modelo=st.text_input('Modelo',value=actual['modelo'],key='eq_mod')
                serie=st.text_input('N° serie',value=actual['numero_serie'],key='eq_s')
                con=st.text_input('Conservación',value=actual['estado_conservacion'],key='eq_c')
                incluye=st.checkbox('Conservar/editar fecha de compra',value=actual['fecha_aprox_compra'] is not None)
                fecha=st.date_input('Fecha compra',value=actual['fecha_aprox_compra'] or date.today()) if incluye else None
                guardar=st.form_submit_button('Guardar cambios')
            if guardar:
                try:
                    d=svc.datos_equipo(seleccion,cmap[id_label],marca,modelo,serie,fecha,con)
                    d.pop('codigo_interno')
                    informar(lambda:svc.actualizar_equipo(seleccion,actor_id=actor_id,**d))
                except svc.ErrorNegocio as exc:st.error(str(exc))
            st.warning('La eliminación física fallará si hay órdenes o registros en subtipos que dependan de este equipo. No se eliminarán esas dependencias.')
            confirmar=st.checkbox(f'Confirmo eliminar el equipo {seleccion}',key='conf_equipo')
            if st.button('Eliminar equipo',disabled=not confirmar):
                informar(lambda:svc.borrar_equipo(seleccion,actor_id=actor_id))
    
    else:
        st.caption("Solo lectura. El rol Consulta no permite crear, modificar ni eliminar equipos.")

with repuestos_tab:
    st.subheader("CRUD REPUESTO")
    if es_admin:
        with st.expander('Crear repuesto',expanded=False):
            with st.form('repuesto_crear'):
                tipo=st.text_input('Tipo de repuesto',max_chars=100)
                precio=st.number_input('Precio referencia',min_value=0.0,step=100.0,format='%.2f')
                stock=st.number_input('Disponibilidad',min_value=0,step=1)
                ok=st.form_submit_button('Crear repuesto')
            if ok:
                try:
                    datos=svc.datos_repuesto(tipo,precio,stock)
                    informar(lambda:f"ID {svc.crear_repuesto(actor_id=actor_id,**datos)}")
                except svc.ErrorNegocio as exc:st.error(str(exc))
    filtro=st.text_input('Buscar repuesto por número o tipo')
    encontrados=cargar(dao.repuestos,filtro)
    st.dataframe(encontrados,use_container_width=True,hide_index=True)
    if es_admin:
        if encontrados:
            numero=st.selectbox('Repuesto para modificar/eliminar',[x['numero_repuesto'] for x in encontrados])
            actual=next(r for r in encontrados if r['numero_repuesto']==numero)
            with st.form('repuesto_editar'):
                tipo=st.text_input('Tipo',value=actual['tipo'],key='r_tipo')
                precio=st.number_input('Precio',min_value=0.0,value=float(actual['precio_referencia']),step=100.0,format='%.2f')
                stock=st.number_input('Disponibilidad',min_value=0,value=int(actual['disponibilidad']),step=1)
                guardar=st.form_submit_button('Guardar repuesto')
            if guardar:
                try:
                    datos=svc.datos_repuesto(tipo,precio,stock)
                    informar(lambda:svc.actualizar_repuesto(numero,actor_id=actor_id,**datos))
                except svc.ErrorNegocio as exc:st.error(str(exc))
            st.warning('Solo se permite borrar si el repuesto no está referenciado en DETALLE_REPUESTO.')
            confirmar=st.checkbox(f'Confirmo eliminar repuesto {numero}',key='conf_repuesto')
            if st.button('Eliminar repuesto',disabled=not confirmar):
                informar(lambda:svc.borrar_repuesto(numero,actor_id=actor_id))
    
    else:
        st.caption("Solo lectura. El rol Consulta no permite modificar repuestos.")

st.divider()
with dashboard_tab:
    mostrar_dashboard(actor_id)

st.caption("Video 8.2: dashboard P1-P4; D07 y D11 sujetos a ratificación.")
