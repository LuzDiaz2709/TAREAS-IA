import datetime as dt
from typing import List, Dict

import pandas as pd
import plotly.express as px
import streamlit as st


# -----------------------------
# Configuración básica de página
# -----------------------------
st.set_page_config(
    page_title="Agenda de Reunión",
    page_icon="🗓️",
    layout="wide",
)

st.title("🗓️ Agenda de Reunión")
st.caption("Crea, visualiza y comparte tu agenda sin necesidad de cargar datasets.")

# -----------------------------
# Estado inicial
# -----------------------------
if "agenda_items" not in st.session_state:
    st.session_state.agenda_items: List[Dict] = []

if "meeting_meta" not in st.session_state:
    st.session_state.meeting_meta = {
        "title": "Reunión de seguimiento",
        "date": dt.date.today(),
        "location": "Virtual",
        "host": "",
        "link": "",
        "timezone": "America/Lima",
    }

# -----------------------------
# Sidebar: datos de la reunión
# -----------------------------
with st.sidebar:
    st.subheader("⚙️ Configuración de la reunión")
    st.session_state.meeting_meta["title"] = st.text_input(
        "Título", value=st.session_state.meeting_meta["title"]
    )
    st.session_state.meeting_meta["date"] = st.date_input(
        "Fecha", value=st.session_state.meeting_meta["date"]
    )
    st.session_state.meeting_meta["location"] = st.text_input(
        "Lugar / Sala", value=st.session_state.meeting_meta["location"]
    )
    st.session_state.meeting_meta["host"] = st.text_input(
        "Anfitrión", value=st.session_state.meeting_meta["host"]
    )
    st.session_state.meeting_meta["link"] = st.text_input(
        "Link de videollamada (opcional)", value=st.session_state.meeting_meta["link"]
    )
    st.session_state.meeting_meta["timezone"] = st.text_input(
        "Zona horaria", value=st.session_state.meeting_meta["timezone"]
    )

    st.markdown("---")
    if st.button("🧹 Vaciar agenda"):
        st.session_state.agenda_items = []
        st.success("Agenda vaciada.")

# -----------------------------
# Formulario: nuevo punto
# -----------------------------
st.header("➕ Agregar punto de agenda")

with st.form("agenda_form", clear_on_submit=True):
    cols = st.columns([2, 1.2, 1.2, 1, 1.4])
    topic = cols[0].text_input("Tema")
    owner = cols[1].text_input("Responsable")
    start_time = cols[2].time_input("Hora de inicio", value=dt.time(9, 0))
    duration_min = cols[3].number_input("Min", min_value=5, max_value=240, value=15, step=5)
    type_ = cols[4].selectbox("Tipo", ["Discusión", "Decisión", "Información"])

    objective = st.text_area("Objetivo (breve)", placeholder="¿Qué se debe lograr en este bloque?")

    colb1, colb2, colb3 = st.columns([1, 1, 3])

    auto_chain = colb1.checkbox("Auto-secuenciar desde el último fin")
    add = colb2.form_submit_button("Agregar")

    # Lógica de agregado
    if add:
        if not topic.strip():
            st.error("El tema es obligatorio.")
        else:
            meeting_date = st.session_state.meeting_meta["date"]

            # Si auto-secuenciar, calcular la hora de inicio = fin del último bloque
            if auto_chain and st.session_state.agenda_items:
                last_end = st.session_state.agenda_items[-1]["end_dt"]
                start_dt = last_end
                start_time = last_end.time()
            else:
                start_dt = dt.datetime.combine(meeting_date, start_time)

            end_dt = start_dt + dt.timedelta(minutes=int(duration_min))

            st.session_state.agenda_items.append(
                {
                    "Topic": topic.strip(),
                    "Owner": owner.strip(),
                    "Type": type_,
                    "Objective": objective.strip(),
                    "Start": start_time.strftime("%H:%M"),
                    "End": end_dt.time().strftime("%H:%M"),
                    "Duration_min": int(duration_min),
                    "start_dt": start_dt,
                    "end_dt": end_dt,
                }
            )
            st.success(f"Punto agregado: {topic}")

# -----------------------------
# Vista: resumen
# -----------------------------
st.header("📋 Resumen")
meta = st.session_state.meeting_meta
colm1, colm2, colm3, colm4 = st.columns(4)
colm1.metric("Título", meta["title"])
colm2.metric("Fecha", meta["date"].strftime("%Y-%m-%d"))
colm3.metric("Lugar", meta["location"])
colm4.metric("Anfitrión", meta["host"] if meta["host"] else "—")
if meta["link"]:
    st.markdown(f"**Link:** {meta['link']}")

# -----------------------------
# Tabla y exportación
# -----------------------------
def build_df() -> pd.DataFrame:
    if not st.session_state.agenda_items:
        return pd.DataFrame(columns=["Topic", "Owner", "Type", "Objective", "Start", "End", "Duration_min"])
    df = pd.DataFrame(st.session_state.agenda_items)
    # Columnas amigables
    df = df[["Topic", "Owner", "Type", "Objective", "Start", "End", "Duration_min"]].rename(
        columns={
            "Topic": "Tema",
            "Owner": "Responsable",
            "Type": "Tipo",
            "Objective": "Objetivo",
            "Start": "Inicio",
            "End": "Fin",
            "Duration_min": "Minutos",
        }
    )
    return df

df = build_df()

st.subheader("🗂️ Detalle")
st.dataframe(df, use_container_width=True, height=280)

# Exportar CSV
csv = df.to_csv(index=False).encode("utf-8")
st.download_button("⬇️ Descargar CSV", csv, file_name="agenda.csv", mime="text/csv")

# -----------------------------
# Visualización: timeline (Gantt)
# -----------------------------
st.header("📊 Visualización (Timeline)")

if st.session_state.agenda_items:
    gantt_df = pd.DataFrame(
        [
            {
                "Tema": it["Topic"],
                "Responsable": it["Owner"] if it["Owner"] else "—",
                "Tipo": it["Type"],
                "Inicio": it["start_dt"],
                "Fin": it["end_dt"],
            }
            for it in st.session_state.agenda_items
        ]
    )
    fig = px.timeline(
        gantt_df,
        x_start="Inicio",
        x_end="Fin",
        y="Responsable",
        color="Tipo",
        hover_data=["Tema"],
    )
    fig.update_yaxes(autorange="reversed")  # Estilo Gantt
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        height=420,
        title=f"Agenda | {meta['title']} — {meta['date'].strftime('%Y-%m-%d')} ({meta['timezone']})",
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("Añade puntos de agenda para ver la línea de tiempo.")

# -----------------------------
# Notas/Consejos
# -----------------------------
with st.expander("💡 Consejos rápidos"):
    st.markdown(
        """
- Usa **Auto-secuenciar** para encadenar bloques sin calcular horas manualmente.  
- El **CSV** exportado sirve para enviar la agenda por correo o cargarla en otra herramienta.  
- Puedes fijar un **ancho amplio** (layout *wide*) para ver mejor la línea de tiempo.  
"""
    )

