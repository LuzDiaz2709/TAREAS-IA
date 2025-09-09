import streamlit as st
import pandas as pd
import altair as alt

# -----------------------------
# Configuración
# -----------------------------
st.set_page_config(page_title="Makeup Visual", page_icon="💄", layout="wide")
st.title("💄 Makeup Visual — Catálogo & Insights")
st.caption("Sin base de datos externa • Todo se guarda en memoria de la sesión")

# -----------------------------
# Datos base (hardcode)
# -----------------------------
BASE_PRODUCTS = [
    {
        "id": 1, "nombre": "Labial Soft Kiss", "marca": "Rosalia", "categoría": "Labios",
        "acabado": "Mate", "tono": "Rosa malva", "precio": 36.9, "rating": 4.6,
        "cruelty_free": True, "vegano": True, "stock": 25,
        "descripcion": "Color intenso de larga duración con textura suave."
    },
    {
        "id": 2, "nombre": "Rubor Bloom", "marca": "PinkBerry", "categoría": "Rostro",
        "acabado": "Satinado", "tono": "Rosa durazno", "precio": 54.0, "rating": 4.4,
        "cruelty_free": True, "vegano": False, "stock": 18,
        "descripcion": "Rubor luminoso que se difumina sin esfuerzo."
    },
    {
        "id": 3, "nombre": "Sombra Rose Garden", "marca": "Aura", "categoría": "Ojos",
        "acabado": "Brillante", "tono": "Rosa champagne", "precio": 69.0, "rating": 4.7,
        "cruelty_free": True, "vegano": True, "stock": 12,
        "descripcion": "Tonos rosas versátiles para looks diarios y de noche."
    },
    {
        "id": 4, "nombre": "Base Velvet Skin", "marca": "Rosalia", "categoría": "Rostro",
        "acabado": "Natural", "tono": "Rosa neutro N2", "precio": 89.9, "rating": 4.3,
        "cruelty_free": False, "vegano": False, "stock": 10,
        "descripcion": "Cobertura media modulable con efecto segunda piel."
    },
    {
        "id": 5, "nombre": "Iluminador Pink Glow", "marca": "PinkBerry", "categoría": "Rostro",
        "acabado": "Glow", "tono": "Rosa perla", "precio": 59.0, "rating": 4.5,
        "cruelty_free": True, "vegano": True, "stock": 20,
        "descripcion": "Resplandor sutil sin partículas gruesas."
    },
    {
        "id": 6, "nombre": "Delineador Rosé Flick", "marca": "Aura", "categoría": "Ojos",
        "acabado": "Mate", "tono": "Rosa profundo", "precio": 41.5, "rating": 4.2,
        "cruelty_free": True, "vegano": False, "stock": 30,
        "descripcion": "Punta precisa y fórmula de secado rápido."
    },
]

if "productos" not in st.session_state:
    st.session_state.productos = BASE_PRODUCTS.copy()

# -----------------------------
# Sidebar: filtros
# -----------------------------
with st.sidebar:
    st.header("🎯 Filtros")
    marcas = sorted({p["marca"] for p in st.session_state.productos})
    cats = sorted({p["categoría"] for p in st.session_state.productos})
    acabados = sorted({p["acabado"] for p in st.session_state.productos})

    f_marca = st.multiselect("Marca", options=marcas, default=marcas)
    f_cat = st.multiselect("Categoría", options=cats, default=cats)
    f_acabado = st.multiselect("Acabado", options=acabados, default=acabados)
    f_precio = st.slider("Precio máximo (S/.)", 20.0, 120.0, 120.0, step=1.0)
    f_cruelty = st.selectbox("Cruelty-free", ["Todos", "Sí", "No"])
    f_vegano = st.selectbox("Vegano", ["Todos", "Sí", "No"])

    st.markdown("---")
    st.subheader("➕ Agregar producto rápido")
    with st.form("add_product", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre")
        marca = c2.text_input("Marca")
        categoria = c1.selectbox("Categoría", ["Rostro", "Ojos", "Labios"])
        acabado = c2.selectbox("Acabado", ["Mate", "Satinado", "Brillante", "Glow", "Natural"])
        tono = c1.text_input("Tono", value="Rosa")
        precio = c2.number_input("Precio (S/.)", min_value=0.0, value=49.9, step=0.5)
        rating = c1.slider("Rating", 1.0, 5.0, 4.5, step=0.1)
        stock = c2.number_input("Stock", min_value=0, value=10, step=1)
        cruelty_free = c1.checkbox("Cruelty-free", value=True)
        vegano = c2.checkbox("Vegano", value=False)
        descripcion = st.text_area("Descripción", value="Descripción breve del producto.")
        add = st.form_submit_button("Agregar")

    if add:
        new_id = max(p["id"] for p in st.session_state.productos) + 1 if st.session_state.productos else 1
        st.session_state.productos.append({
            "id": new_id, "nombre": nombre or "Nuevo Producto", "marca": marca or "Marca",
            "categoría": categoria, "acabado": acabado, "tono": tono,
            "precio": float(precio), "rating": float(rating), "cruelty_free": bool(cruelty_free),
            "vegano": bool(vegano), "stock": int(stock), "descripcion": descripcion.strip(),
        })
        st.success("Producto agregado.")

# -----------------------------
# Aplicar filtros
# -----------------------------
df = pd.DataFrame(st.session_state.productos)
mask = (
    df["marca"].isin(f_marca)
    & df["categoría"].isin(f_cat)
    & df["acabado"].isin(f_acabado)
    & (df["precio"] <= f_precio)
)
if f_cruelty != "Todos":
    mask &= df["cruelty_free"] == (f_cruelty == "Sí")
if f_vegano != "Todos":
    mask &= df["vegano"] == (f_vegano == "Sí")
df_f = df[mask].reset_index(drop=True)

# -----------------------------
# Métricas
# -----------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Productos visibles", len(df_f))
c2.metric("Precio promedio (S/.)", f"{df_f['precio'].mean():.2f}" if not df_f.empty else "—")
c3.metric("Rating promedio", f"{df_f['rating'].mean():.2f}" if not df_f.empty else "—")
c4.metric("Stock total", int(df_f["stock"].sum()) if not df_f.empty else 0)

# -----------------------------
# Tabs principales
# -----------------------------
tab_catalogo, tab_insights, tab_comparar = st.tabs(["📒 Catálogo", "📊 Insights", "⚖️ Comparador"])

# ===== Catálogo =====
with tab_catalogo:
    if df_f.empty:
        st.info("No hay productos con los filtros actuales.")
    else:
        for _, row in df_f.iterrows():
            with st.container(border=True):
                cc1, cc2, cc3, cc4 = st.columns([3, 1.2, 1.2, 1])
                cc1.markdown(f"**{row['nombre']}** — {row['marca']}")
                cc1.markdown(f"_{row['descripcion']}_")
                cc2.markdown(f"**Categoría:** {row['categoría']}  \n**Acabado:** {row['acabado']}")
                cc3.markdown(f"**Tono:** {row['tono']}  \n**Rating:** ⭐ {row['rating']}")
                cc4.markdown(f"**S/. {row['precio']:.2f}**  \nStock: {int(row['stock'])}")
                cbt1, cbt2, cbt3 = st.columns([1,1,1])
                cbt1.write("Cruelty-free: " + ("✅" if row["cruelty_free"] else "❌"))
                cbt2.write("Vegano: " + ("✅" if row["vegano"] else "❌"))
                if cbt3.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                    st.session_state.productos = [p for p in st.session_state.productos if p["id"] != row["id"]]
                    st.rerun()

    st.download_button(
        "⬇️ Exportar CSV",
        data=df_f.to_csv(index=False).encode("utf-8"),
        file_name="makeup_catalogo.csv",
        mime="text/csv"
    )

# ===== Insights =====
with tab_insights:
    if df_f.empty:
        st.info("Agrega o ajusta filtros para ver gráficos.")
    else:
        left, right = st.columns(2)

        # Distribución por categoría
        cat_counts = df_f.groupby("categoría").size().reset_index(name="count")
        chart_cat = (
            alt.Chart(cat_counts)
            .mark_bar()
            .encode(
                x=alt.X("categoría:N", title="Categoría"),
                y=alt.Y("count:Q", title="Productos"),
                tooltip=["categoría", "count"]
            )
            .properties(height=320)
        )
        left.altair_chart(chart_cat, use_container_width=True)

        # Precio vs rating
        chart_scatter = (
            alt.Chart(df_f)
            .mark_circle(size=120)
            .encode(
                x=alt.X("precio:Q", title="Precio (S/.)"),
                y=alt.Y("rating:Q", title="Rating"),
                color=alt.Color("acabado:N", title="Acabado"),
                tooltip=["nombre", "marca", "precio", "rating", "acabado", "categoría"]
            )
            .properties(height=320)
        )
        right.altair_chart(chart_scatter, use_container_width=True)

        # Top marcas por rating promedio
        st.markdown("#### ⭐ Promedio de rating por marca")
        rating_marca = df_f.groupby("marca")["rating"].mean().reset_index()
        chart_brand = (
            alt.Chart(rating_marca)
            .mark_bar()
            .encode(
                x=alt.X("marca:N", title="Marca"),
                y=alt.Y("rating:Q", title="Rating promedio"),
                tooltip=["marca", alt.Tooltip("rating:Q", format=".2f")]
            )
            .properties(height=280)
        )
        st.altair_chart(chart_brand, use_container_width=True)

# ===== Comparador =====
with tab_comparar:
    st.subheader("Selecciona hasta 3 productos para comparar")
    opciones = df["nombre"].tolist()
    sel = st.multiselect("Productos", options=opciones, max_selections=3)
    if not sel:
        st.info("Elige productos para ver la comparativa.")
    else:
        comp = df[df["nombre"].isin(sel)].copy()
        comp = comp[["nombre","marca","categoría","acabado","tono","precio","rating","cruelty_free","vegano","stock","descripcion"]]
        st.dataframe(comp, use_container_width=True, height=220)

        # Radar-like (simulado con barras normalizadas)
        st.markdown("##### Comparativa visual (precio y rating normalizados)")
        comp_norm = comp.assign(
            precio_n = (comp["precio"] - comp["precio"].min()) / (comp["precio"].max() - comp["precio"].min() + 1e-9),
            rating_n = (comp["rating"] - comp["rating"].min()) / (comp["rating"].max() - comp["rating"].min() + 1e-9),
        )[["nombre","precio_n","rating_n"]].melt("nombre", var_name="métrica", value_name="valor")

        chart_comp = (
            alt.Chart(comp_norm)
            .mark_bar()
            .encode(
                x=alt.X("nombre:N", title="Producto"),
                y=alt.Y("valor:Q", title="Valor normalizado (0-1)"),
                color=alt.Color("métrica:N", title="Métrica"),
                tooltip=["nombre","métrica", alt.Tooltip("valor:Q", format=".2f")]
            )
            .properties(height=260)
        )
        st.altair_chart(chart_comp, use_container_width=True)

# -----------------------------
# Nota final
# -----------------------------
with st.expander("💡 Tips"):
    st.markdown(
        """
- Todo vive en memoria de la sesión. Al recargar, vuelves al catálogo base.
- Usa **Agregar producto** en la barra lateral para extender tu catálogo rosa.
- Exporta el **CSV** del catálogo filtrado para compartirlo o documentarlo.
        """
    )

