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
        tema = c1.text_input("Tema")
        responsable = c2.text_input("Responsable")
        hora_inicio = c3.time_input("Hora inicio", value=dt.time(9, 0))
        minutos = c4.number_input("Minutos", min_value=5, max_value=240, value=15, step=5)
        tipo = c5.selectbox("Tipo", ["Discusión","Decisión","Información"])
        objetivo = st.text_area("Objetivo (breve)", placeholder="¿Qué se busca lograr?")
        auto = st.checkbox("Auto-secuenciar después del último bloque")

        submitted = st.form_submit_button("Agregar")
        if submitted:
            if not tema.strip():
                st.error("El tema es obligatorio.")
            else:
                fecha = st.session_state.meta["fecha"]
                if auto and st.session_state.agenda:
                    last_end = st.session_state.agenda[-1]["_end_dt"]
                    start_dt = last_end
                    hora_inicio = last_end.time()
                else:
                    start_dt = dt.datetime.combine(fecha, hora_inicio)

                end_dt = start_dt + dt.timedelta(minutes=int(minutos))
                st.session_state.agenda.append({
                    "Tema": tema.strip(),
                    "Responsable": responsable.strip() if responsable else "—",
                    "Inicio": start_dt.strftime("%H:%M"),
                    "Fin": end_dt.strftime("%H:%M"),
                    "Min": int(minutos),
                    "Tipo": tipo,
                    "Objetivo": objetivo.strip(),
                    "_start_dt": start_dt,
                    "_end_dt": end_dt,
                })
                st.success(f"Agregado: {tema}")

    st.markdown("### Reordenar / Editar rápido")
    df = build_df()
    if df.empty:
        st.info("Aún no hay puntos.")
    else:
        # Lista con controles de reordenamiento/eliminación
        for i, item in enumerate(st.session_state.agenda):
            with st.container(border=True):
                c1, c2, c3, c4, c5 = st.columns([3,1.2,1.2,1,1])
                c1.write(f"**{item['Tema']}** — {item['Responsable']}")
                c2.write(f"{item['Inicio']} → {item['Fin']}")
                c3.write(f"{item['Tipo']}")
                c4.write(f"{item['Min']} min")

                move_up = c5.button("▲", key=f"up_{i}", help="Mover arriba", use_container_width=True)
                move_dn = c5.button("▼", key=f"dn_{i}", help="Mover abajo", use_container_width=True)
                del_it  = c5.button("🗑️", key=f"del_{i}", help="Eliminar", use_container_width=True)

                if move_up and i > 0:
                    st.session_state.agenda[i-1], st.session_state.agenda[i] = st.session_state.agenda[i], st.session_state.agenda[i-1]
                    st.rerun()
                if move_dn and i < len(st.session_state.agenda)-1:
                    st.session_state.agenda[i+1], st.session_state.agenda[i] = st.session_state.agenda[i], st.session_state.agenda[i+1]
                    st.rerun()
                if del_it:
                    del st.session_state.agenda[i]
                    st.rerun()

    st.markdown("### Exportar CSV")
    df = build_df()
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, file_name="agenda_simple.csv", mime="text/csv")

# =============================
# TAB: VISUALIZAR
# =============================
with tab_view:
    st.subheader("Timeline (Altair)")
    df = build_df()
    if df.empty:
        st.info("Añade puntos para ver la visualización.")
    else:
        # Data para Altair
        fecha = st.session_state.meta["fecha"]
        vis_df = pd.DataFrame([
            {
                "Tema": it["Tema"],
                "Responsable": it["Responsable"],
                "Inicio": it["_start_dt"],
                "Fin": it["_end_dt"],
                "Tipo": it["Tipo"],
                "Duración": it["Min"],
                "Tooltip": f"{it['Tema']} ({it['Inicio']}–{it['Fin']})"
            }
            for it in st.session_state.agenda
        ])
        # Ordenar por hora
        vis_df = vis_df.sort_values("Inicio")

        # Escala temporal
        base = alt.Chart(vis_df)

        bars = base.mark_bar().encode(
            x=alt.X("Inicio:T", title="Hora"),
            x2="Fin:T",
            y=alt.Y("Responsable:N", sort="-x", title="Responsable"),
            color=alt.Color("Tipo:N", legend=alt.Legend(title="Tipo")),
            tooltip=[
                alt.Tooltip("Tema:N"),
                alt.Tooltip("Responsable:N"),
                alt.Tooltip("Inicio:T", format="%H:%M"),
                alt.Tooltip("Fin:T", format="%H:%M"),
                alt.Tooltip("Duración:Q", title="Min"),
                alt.Tooltip("Tipo:N"),
            ],
        ).properties(
            height=380,
            width="container"
        )

        st.altair_chart(bars, use_container_width=True)

    st.markdown(
        f"**{st.session_state.meta['titulo']}** — "
        f"{st.session_state.meta['fecha'].strftime('%Y-%m-%d')} | "
        f"{st.session_state.meta['lugar']} | TZ: {st.session_state.meta['zona']}"
    )
    if st.session_state.meta["link"]:
        st.link_button("Abrir videollamada", st.session_state.meta["link"])

# =============================
# TAB: ACTA (Markdown)
# =============================
with tab_minutes:
    st.subheader("Acta automática (lista para copiar)")
    meta = st.session_state.meta
    df = build_df()

    md_lines = []
    md_lines.append(f"# {meta['titulo']}")
    md_lines.append(f"- **Fecha:** {meta['fecha'].strftime('%Y-%m-%d')}")
    md_lines.append(f"- **Lugar:** {meta['lugar']}")
    md_lines.append(f"- **Zona horaria:** {meta['zona']}")
    if meta["anfitrion"]:
        md_lines.append(f"- **Anfitrión:** {meta['anfitrion']}")
    if meta["link"]:
        md_lines.append(f"- **Link:** {meta['link']}")
    md_lines.append("\n## Agenda")

    if df.empty:
        md_lines.append("- *(Sin puntos cargados)*")
    else:
        for row in st.session_state.agenda:
            md_lines.append(
                f"- **{row['Inicio']}–{row['Fin']}** · **{row['Tema']}** "
                f"(Responsable: {row['Responsable']}; {row['Min']} min; {row['Tipo']})"
            )
            if row["Objetivo"]:
                md_lines.append(f"  - Objetivo: {row['Objetivo']}")

    md_lines.append("\n## Acuerdos y pendientes")
    md_lines.append("- ")
    markdown_text = "\n".join(md_lines)

    st.code(markdown_text, language="markdown")

    st.download_button(
        "⬇️ Descargar Acta (.md)",
        data=markdown_text.encode("utf-8"),
        file_name="acta_reunion.md",
        mime="text/markdown",
    )

# -----------------------------
# Nota de uso
# -----------------------------
with st.expander("💡 Tips rápidos"):
    st.markdown(
        """
- Marca **Auto-secuenciar** para encadenar bloques sin calcular horas.  
- En **Visualizar**, pasa el mouse sobre las barras para ver detalles.  
- El **Markdown** del acta se puede pegar directo en Notion/Docs/Slack.  
"""
    )
