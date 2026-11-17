"""Capa de presentación: primera pantalla del PMV Caso 8."""
import streamlit as st
from services.resumen_service import DatabaseUnavailable, obtener_resumen

st.set_page_config(page_title="Caso 8 | Reparaciones", page_icon="🔧", layout="centered")
st.title("🔧 Sistema de Gestión de Reparaciones")
st.caption("Proyecto Fase 2 · Grupo 8 · Universidad Andrés Bello")
st.write("Primera versión: comprobación de conectividad y consultas de lectura a MySQL.")

if st.button("Consultar datos", type="primary"):
    try:
        with st.spinner("Verificando disponibilidad de MySQL..."):
            resumen = obtener_resumen()
        col1, col2 = st.columns(2)
        col1.metric("Clientes registrados", resumen["clientes"])
        col2.metric("Órdenes de reparación", resumen["ordenes"])
        st.success("Consultas ejecutadas en la base de datos caso8_reparaciones.")
    except DatabaseUnavailable as exc:
        st.warning(str(exc))
        st.info("Revise: docker compose ps y docker compose logs --tail=50 db")

st.divider()
st.caption("Etapa inicial: sin CRUD, autenticación ni dashboard definitivo.")
