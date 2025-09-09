import datetime as dt
from typing import List, Dict

import altair as alt
import pandas as pd
import streamlit as st


# -----------------------------
# Configuración básica
# -----------------------------
st.set_page_config(page_title="Agenda Simple", page_icon="📝", layout="wide")
st.title("📝 Agenda de Reunión — Versión Simple")
st.caption("Edición básica, visualización tipo timeline con Altair y exportación a CSV/Markdown.")

# -----------------------------
# Estado inicial
# -----------------------------
if "agenda" not in st.session_state:
    st.session_state.agenda: List[Dict] = []

if "meta" not in st.session_state:
    st.session_state.meta = {
        "titulo": "Reunión general",
        "fecha": dt.date.today(),
        "zona": "America/Lima",
        "lugar": "Virtual",
        "anfitrion": "",
        "link": "",
    }

# -----------------------------
# Sidebar (metadatos)
# -----------------------------
with st.sidebar:
    st.subheader("⚙️ Datos de la reunión")
    st.session_state.meta["titulo"]   = st.text_input("Título", st.session_state.meta["titulo"])
    st.session_state.meta["fecha"]    = st.date_input("Fecha", st.session_state.meta["fecha"])
    st.session_state.meta["lugar"]    = st.text_input("Lugar / Sala", st.session_state.meta["lugar"])
    st.session_state.meta["anfitrion"]= st.text_input("Anfitrión", st.session_state.meta["anfitrion"])
    st.session_state.meta["link"]     = st.text_input("Link (opcional)", st.session_state.meta["link"])
    st.session_state.meta["zona"]     = st.text_input("Zona horaria", st.session_state.meta["zona"])

    st.markdown("---")
    if st.button("🧹 Vaciar agenda"):
        st.session_state.agenda = []
        st.success("Agenda vaciada.")

# -----------------------------
# Helper: construir DataFrame
# -----------------------------
def build_df() -> pd.DataFrame:
    if not st.session_state.agenda:
        return pd.DataFrame(columns=["Tema","Responsable","Inicio","Fin","Min","Tipo","Objetivo"])
    df = pd.DataFrame(st.session_state.agenda)
    df = df[["Tema","Responsable","Inicio","Fin","Min","Tipo","Objetivo"]]
    return df

# -----------------------------
# Pestañas
# -----------------------------
tab_edit, tab_view, tab_minutes = st.tabs(["✍️ Editar", "📊 Visualizar", "🧾 Acta (Markdown)"])

# =============================
# TAB: EDITAR
# =============================
with tab_edit:
    st.subheader("Agregar punto de agenda")
    with st.form("form_add", clear_on_submit=True):
        c1, c2, c3, c4, c5 = st.columns([2, 1.2, 1.2, 1, 1.2])
