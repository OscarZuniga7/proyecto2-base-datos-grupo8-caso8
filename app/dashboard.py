"""Presentación del dashboard Video 8.2. No contiene SQL ni operaciones de escritura."""
from datetime import date
import pandas as pd
import plotly.express as px
import streamlit as st
from services import dashboard_service as ds
from services.seguridad_service import AccesoDenegado

TIPOS = ['Todos', 'COMPUTADOR', 'TELEFONO_MOVIL', 'TABLET',
         'SIN_CLASIFICAR', 'INCONSISTENTE']


def _df(filas):
    return pd.DataFrame(filas)


def _grafico_vacio(df, titulo):
    if df.empty:
        st.info(f'{titulo}: sin resultados para los filtros seleccionados.')
        return True
    return False


def mostrar_dashboard(actor_id):
    st.subheader('Dashboard de negocio · Video 8.2')
    st.caption('Solo lectura. P3 (costo) y P4 (D11) utilizan propuestas pendientes de ratificación.')
    try:
        filtros = ds.obtener_filtros(actor_id)
    except (ds.ErrorDashboard, AccesoDenegado) as exc:
        st.error(str(exc))
        return
    opciones = {'Todas las sucursales': ''}
    opciones.update({f"{s['nombre']} · {s['codigo_sucursal']}": s['codigo_sucursal']
                    for s in filtros['sucursales']})
    primera = filtros['fecha_min'] or date.today()
    ultima = filtros['fecha_max'] or date.today()
    if primera > ultima:
        primera, ultima = ultima, primera
    with st.form('dashboard_filtros'):
        col1, col2, col3 = st.columns(3)
        desde = col1.date_input('Desde · fecha de recepción', value=primera)
        hasta = col2.date_input('Hasta · fecha de recepción', value=ultima)
        sucursal_label = col3.selectbox('Sucursal', list(opciones))
        tipo = st.selectbox('Tipo de equipo para P1', TIPOS)
        estados = ['Todos los estados'] + list(filtros['estados'])
        estado = st.selectbox('Estado para P4', estados)
        aplicar = st.form_submit_button('Aplicar filtros')
    # Se consulta en el primer ingreso y al aplicar cambios; sin estado cacheado.
    if desde > hasta:
        st.warning('La fecha inicial no puede superar la fecha final.')
        return
    sucursal = opciones[sucursal_label]
    try:
        resultados = {
            nombre: ds.consultar_pregunta(actor_id, nombre, desde, hasta,
                        sucursal=sucursal,
                        tipo='' if tipo == 'Todos' else tipo,
                        estado='' if estado == 'Todos los estados' else estado)
            for nombre in ('P1', 'P2', 'P3', 'P4')
        }
    except (ds.ErrorDashboard, AccesoDenegado) as exc:
        st.error(str(exc))
        return

    p1, p2, p3, p4 = st.tabs(['P1 · Órdenes por tipo', 'P2 · Distribución %',
                              'P3 · Costos y evaluación', 'P4 · Estados por sucursal'])
    with p1:
        st.markdown('**¿Qué tipos de equipos generan más órdenes de reparación?**')
        df = _df(resultados['P1']['datos'])
        if not _grafico_vacio(df, 'P1'):
            st.plotly_chart(px.bar(df, x='tipo_equipo', y='cantidad_ordenes',
                                   text='cantidad_ordenes', title='Órdenes por tipo de equipo'),
                            use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption('SIN_CLASIFICAR se mantiene independiente; INCONSISTENTE señala pertenencia a varios subtipos.')

    with p2:
        st.markdown('**¿Cómo se distribuyen porcentualmente las órdenes entre computadores, teléfonos y tablets?**')
        df = _df(resultados['P2']['datos'])
        excl = _df(resultados['P2']['excluidas'])
        if not excl.empty:
            n = int(excl['cantidad_ordenes'].sum())
            st.warning(f'{n} órdenes de equipos sin clasificación única se excluyen del denominador de P2.')
            st.dataframe(excl, use_container_width=True, hide_index=True)
        if not _grafico_vacio(df, 'P2'):
            total = int(df['cantidad_ordenes'].sum())
            if total > 0:
                df['porcentaje'] = 100.0 * df['cantidad_ordenes'] / total
                st.plotly_chart(px.bar(df, x='tipo_equipo', y='porcentaje',
                                       text=df['porcentaje'].map(lambda x: f'{x:.1f}%'),
                                       title='Composición de órdenes clasificadas (%)'),
                                use_container_width=True)
                st.dataframe(df, use_container_width=True, hide_index=True)

    with p3:
        st.markdown('**¿Qué relación existe entre costo total y evaluación del cliente?**')
        df = _df(resultados['P3']['datos'])
        if not _grafico_vacio(df, 'P3'):
            for col in ('costo_mano_obra', 'costo_repuestos', 'costo_total', 'evaluacion_promedio'):
                df[col] = pd.to_numeric(df[col], errors='coerce')
            graf = df.dropna(subset=['costo_total', 'evaluacion_promedio'])
            if graf.empty:
                st.info('No existen parejas de costo y calificación válidas en este período.')
            else:
                st.plotly_chart(px.scatter(graf, x='costo_total', y='evaluacion_promedio',
                                           hover_data=['numero_orden', 'cliente', 'codigo_interno', 'sucursal'],
                                           title='Costo por orden vs. calificación promedio'),
                                use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        st.caption('Incluye únicamente órdenes con evaluación registrada. No es posible confirmar fecha posterior a ENTREGA porque el DDL no contiene fecha de entrega. Costo D07 pendiente de ratificación.')

    with p4:
        st.markdown('**¿Cómo se distribuyen las órdenes según estado actual y sucursal?**')
        st.caption('D11: pregunta propuesta e implementada para demostración; pendiente de aprobación formal.')
        df = _df(resultados['P4']['datos'])
        if not _grafico_vacio(df, 'P4'):
            st.plotly_chart(px.bar(df, x='sucursal', y='cantidad_ordenes',
                                   color='estado_actual', barmode='stack',
                                   title='Órdenes por estado actual y sucursal'),
                            use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
