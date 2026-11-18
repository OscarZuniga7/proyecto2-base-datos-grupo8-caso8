"""Video 7: conserva resumen del Video 6, agrega orden y CRUD básicos."""
from datetime import date
from decimal import Decimal
import streamlit as st
from services.resumen_service import DatabaseUnavailable, obtener_resumen
from services import operaciones_service as svc
from db import operaciones_dao as dao

st.set_page_config(page_title='Caso 8 | Reparaciones', page_icon='🔧', layout='wide')
st.title('🔧 Sistema de Gestión de Reparaciones')
st.caption('Proyecto Fase 2 · Grupo 8 · Universidad Andrés Bello · Video 7')

def informar(accion):
    try:
        resultado = accion()
        st.success(f'Operación confirmada en MySQL. {resultado if resultado is not None else ""}')
        return True
    except (svc.ErrorNegocio, DatabaseUnavailable) as exc:
        st.error(str(exc))
        return False

def cargar(dao_fn,*args):
    try:
        return svc.consultar(dao_fn,*args)
    except svc.ErrorNegocio as exc:
        st.error(str(exc))
        return []

inicio,ordenes,equipos_tab,repuestos_tab = st.tabs(['Inicio · Video 6','Registrar orden','CRUD EQUIPO','CRUD REPUESTO'])

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
                informar(lambda: f"N° de orden {svc.registrar_orden(cliente_id,mapa_equipo[el],smap[sl],f1,f2,problema,estado)}")
    st.write('Últimas órdenes')
    st.dataframe(cargar(dao.ordenes_recientes),use_container_width=True,hide_index=True)
    st.caption('El DDL permite registrar una orden sin diagnóstico inmediato; esta limitación de integridad sigue pendiente en el modelo.')

with equipos_tab:
    st.subheader('B1. CRUD de EQUIPO (tabla base)')
    st.info('Esta etapa administra atributos de EQUIPO. No crea ni modifica atributos de COMPUTADOR, TELEFONO_MOVIL o TABLET.')
    clientes=cargar(dao.clientes)
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
                    informar(lambda:svc.crear_equipo(**datos))
                except svc.ErrorNegocio as exc: st.error(str(exc))
    filtro=st.text_input('Buscar equipos por código, marca, modelo o serie')
    encontrados=cargar(dao.equipos,filtro)
    st.dataframe(encontrados,use_container_width=True,hide_index=True)
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
                informar(lambda:svc.actualizar_equipo(seleccion,**d))
            except svc.ErrorNegocio as exc:st.error(str(exc))
        st.warning('La eliminación física fallará si hay órdenes o registros en subtipos que dependan de este equipo. No se eliminarán esas dependencias.')
        confirmar=st.checkbox(f'Confirmo eliminar el equipo {seleccion}',key='conf_equipo')
        if st.button('Eliminar equipo',disabled=not confirmar):
            informar(lambda:svc.borrar_equipo(seleccion))

with repuestos_tab:
    st.subheader('B2. CRUD de REPUESTO')
    with st.expander('Crear repuesto',expanded=False):
        with st.form('repuesto_crear'):
            tipo=st.text_input('Tipo de repuesto',max_chars=100)
            precio=st.number_input('Precio referencia',min_value=0.0,step=100.0,format='%.2f')
            stock=st.number_input('Disponibilidad',min_value=0,step=1)
            ok=st.form_submit_button('Crear repuesto')
        if ok:
            try:
                datos=svc.datos_repuesto(tipo,precio,stock)
                informar(lambda:f"ID {svc.crear_repuesto(**datos)}")
            except svc.ErrorNegocio as exc:st.error(str(exc))
    filtro=st.text_input('Buscar repuesto por número o tipo')
    encontrados=cargar(dao.repuestos,filtro)
    st.dataframe(encontrados,use_container_width=True,hide_index=True)
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
                informar(lambda:svc.actualizar_repuesto(numero,**datos))
            except svc.ErrorNegocio as exc:st.error(str(exc))
        st.warning('Solo se permite borrar si el repuesto no está referenciado en DETALLE_REPUESTO.')
        confirmar=st.checkbox(f'Confirmo eliminar repuesto {numero}',key='conf_repuesto')
        if st.button('Eliminar repuesto',disabled=not confirmar):
            informar(lambda:svc.borrar_repuesto(numero))

st.divider()
st.caption('Video 7: sin autenticación, sin dashboard definitivo y sin integrar vistas/procedimientos.')
