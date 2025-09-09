import io
import uuid
from typing import List, Dict

import altair as alt
import pandas as pd
import streamlit as st
from PIL import Image

# ---------------------------------
# Configuración de página / Tema
# ---------------------------------
st.set_page_config(page_title="Makeup Real • Catálogo Rosa", page_icon="💄", layout="wide")
st.title("💄 Makeup Real — Catálogo Rosa con Imágenes")
st.caption("Sin dataset externo • Carga URLs o sube imágenes • Marcas reales • Todo en memoria")

# ---------------------------------
# Catálogo base (marcas reales)
# image_url: coloca aquí una URL válida (https://...) o deja vacío y sube la imagen
# ---------------------------------
BASE: List[Dict] = [
    {
        "id": 1, "nombre": "Fenty Icon Velvet Liquid Lipstick", "marca": "Fenty Beauty",
        "categoría": "Labios", "acabado": "Mate", "tono": "Pink Matter",
        "precio": 119.0, "rating": 4.7, "stock": 20,
        "cruelty_free": True, "vegano": True,
        "descripcion": "Labial líquido mate de alta pigmentación y larga duración.",
        "image_url": "",  # Pega aquí la URL real del producto (opcional)
        "image_bytes": None,
    },
    {
        "id": 2, "nombre": "Soft Pinch Liquid Blush", "marca": "Rare Beauty",
        "categoría": "Rostro", "acabado": "Satinado", "tono": "Happy (rosa frío)",
        "precio": 115.0, "rating": 4.8, "stock": 18,
        "cruelty_free": True, "vegano": True,
        "descripcion": "Rubor líquido de alta duración y difuminado fácil.",
        "image_url": "",
        "image_bytes": None,
    },
    {
        "id": 3, "nombre": "SuperStay Vinyl Ink", "marca": "Maybelline",
        "categoría": "Labios", "acabado": "Brillante", "tono": "Lippy (rosa malva)",
        "precio": 55.0, "rating": 4.4, "stock": 35,
        "cruelty_free": False, "vegano": False,
        "descripcion": "Color intenso de vinilo con fijación prolongada.",
        "image_url": "",
        "image_bytes": None,
    },
    {
        "id": 4, "nombre": "Powder Kiss Lipstick", "marca": "MAC",
        "categoría": "Labios", "acabado": "Mate difuminado", "tono": "Sultry Move (rosa nude)",
        "precio": 99.0, "rating": 4.6, "stock": 22,
        "cruelty_free": False, "vegano": False,
        "descripcion": "Labial mate con acabado borroso y cómodo.",
        "image_url": "",
        "image_bytes": None,
    },
    {
        "id": 5, "nombre": "Afterglow Liquid Blush", "marca": "NARS",
        "categoría": "Rostro", "acabado": "Glow", "tono": "Orgasm (rosa durazno)",
        "precio": 135.0, "rating": 4.7, "stock": 12,
        "cruelty_free": False, "vegano": False,
        "descripcion": "Rubor líquido luminoso con efecto saludable.",
        "image_url": "",
        "image_bytes": None,
    },
    {
        "id": 6, "nombre": "Halo Glow Blush Beauty Wand", "marca": "e.l.f.",
        "categoría": "Rostro", "acabado": "Glow", "tono": "Pink-Me-Up",
        "precio": 49.0, "rating": 4.5, "stock": 28,
        "cruelty_free": True, "vegano": True,
        "descripcion": "Rubor líquido con aplicador y brillo saludable.",
        "image_url": "",
        "image_bytes": None,
    },
    {
        "id": 7, "nombre": "Butter Gloss", "marca": "NYX",
        "categoría": "Labios", "acabado": "Brillante", "tono": "Crème Brulee (rosa claro)",
        "precio": 39.0, "rating": 4.3, "stock": 40,
        "cruelty_free": True, "vegano": False,
        "descripcion": "Brillo labial cremoso con color y sensación suave.",
        "image_url": "",
        "image_bytes": None,
    },
    {
        "id": 8, "nombre": "Infallible 24H Fresh Wear Blush", "marca": "L'Oréal",
        "categoría": "Rostro", "acabado": "Natural", "tono": "Confident Pink",
        "precio": 69.0, "rating": 4.2, "stock": 26,
        "cruelty_free": False, "vegano": False,
        "descripcion": "Rubor de larga duración resistente al sudor.",
        "image_url": "",
        "image_bytes": None,
    },
]

if "items" not in st.session_state:
    st.session_state.items = BASE.copy()

# ---------------------------------
# Sidebar: filtros y alta de items
# ---------------------------------
with st.sidebar:
    st.header("🎯 Filtros")
    df_all = pd.DataFrame(st.session_state.items)
    marcas = sorted(df_all["marca"].unique().tolist()) if not df_all.empty else []
    cats = sorted(df_all["categoría"].unique().tolist()) if not df_all.empty else []
    acabados = sorted(df_all["acabado"].unique().tolist()) if not df_all.empty else []

    f_marca = st.multiselect("Marca", marcas, default=marcas)
    f_cat = st.multiselect("Categoría", cats, default=cats)
    f_acab = st.multiselect("Acabado", acabados, default=acabados)
    f_precio = st.slider("Precio máx (S/.)", 20.0, 200.0, 200.0, step=1.0)
    st.markdown("---")

    st.subheader("➕ Agregar producto")
    with st.form("form_add", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre del producto")
        marca = c2.selectbox("Marca", ["Fenty Beauty","Rare Beauty","Maybelline","MAC","NARS","e.l.f.","NYX","L'Oréal","Otra"])
        categoria = c1.selectbox("Categoría", ["Rostro","Ojos","Labios"])
        acabado = c2.selectbox("Acabado", ["Mate","Satinado","Brillante","Glow","Natural","Mate difuminado"])
        tono = c1.text_input("Tono / Nombre de color", value="Rosa")
        precio = c2.number_input("Precio (S/.)", min_value=0.0, value=59.0, step=0.5)
        rating = c1.slider("Rating", 1.0, 5.0, 4.5, step=0.1)
        stock = c2.number_input("Stock", min_value=0, value=10, step=1)
        cruelty = c1.checkbox("Cruelty-free", value=True)
        vegan = c2.checkbox("Vegano", value=False)
        desc = st.text_area("Descripción", value="Descripción breve del producto.")

        st.markdown("**Imagen** (elige una opción)")
        url_img = st.text_input("URL de imagen (https://...)", placeholder="Pega aquí un enlace directo a JPG/PNG/WebP")
        up_img = st.file_uploader("Subir archivo", type=["jpg","jpeg","png","webp"])

        submitted = st.form_submit_button("Agregar")
        if submitted:
            new_id = (max([it["id"] for it in st.session_state.items]) + 1) if st.session_state.items else 1
            img_bytes = None
            if up_img is not None:
                # Validar imagen
                try:
                    img = Image.open(up_img).convert("RGB")
                    buf = io.BytesIO()
                    img.save(buf, format="JPEG", quality=90)
                    img_bytes = buf.getvalue()
                except Exception:
                    st.warning("No se pudo procesar la imagen subida. Se guardará sin imagen.")
            st.session_state.items.append({
                "id": new_id, "nombre": nombre or "Nuevo Producto", "marca": marca,
                "categoría": categoria, "acabado": acabado, "tono": tono,
                "precio": float(precio), "rating": float(rating), "stock": int(stock),
                "cruelty_free": bool(cruelty), "vegano": bool(vegan),
                "descripcion": (desc or "").strip(),
                "image_url": (url_img or "").strip(),
                "image_bytes": img_bytes,
            })
            st.success("Producto agregado.")

    st.markdown("---")
    if st.button("🧹 Vaciar catálogo (volver al base)"):
        st.session_state.items = BASE.copy()
        st.success("Catálogo reiniciado.")

# ---------------------------------
# Aplicar filtros
# ---------------------------------
df = pd.DataFrame(st.session_state.items)
mask = (
    df["marca"].isin(f_marca) &
    df["categoría"].isin(f_cat) &
    df["acabado"].isin(f_acab) &
    (df["precio"] <= f_precio)
)
df_f = df[mask].reset_index(drop=True)

# ---------------------------------
# Métricas
# ---------------------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Productos visibles", len(df_f))
c2.metric("Precio promedio (S/.)", f"{df_f['precio'].mean():.2f}" if not df_f.empty else "—")
c3.metric("Rating promedio", f"{df_f['rating'].mean():.2f}" if not df_f.empty else "—")
c4.metric("Stock total", int(df_f['stock'].sum()) if not df_f.empty else 0)

# ---------------------------------
# Tabs
# ---------------------------------
tab_catalogo, tab_insights = st.tabs(["📒 Catálogo (con imágenes)", "📊 Insights"])

# ===== Catálogo con tarjetas =====
with tab_catalogo:
    if df_f.empty:
        st.info("No hay productos con los filtros actuales.")
    else:
        # Grid en filas de a 3
        cols_per_row = 3
        rows = [df_f.iloc[i:i+cols_per_row] for i in range(0, len(df_f), cols_per_row)]
        for chunk in rows:
            cols = st.columns(cols_per_row)
            for idx, (_, row) in enumerate(chunk.iterrows()):
                with cols[idx]:
                    with st.container(border=True):
                        # Imagen: prioridad a image_bytes; si no, usa image_url; si no, placeholder
                        showed = False
                        if row["image_bytes"] is not None:
                            try:
                                st.image(row["image_bytes"], use_container_width=True)
                                showed = True
                            except Exception:
                                pass
                        if not showed and row["image_url"]:
                            try:
                                st.image(row["image_url"], use_container_width=True)
                                showed = True
                            except Exception:
                                pass
                        if not showed:
                            st.markdown(
                                "<div style='width:100%;height:180px;background:linear-gradient(135deg,#fce7f3,#ffe4f0);"
                                "border-radius:12px;display:flex;align-items:center;justify-content:center;"
                                "color:#9d174d;font-weight:600;'>Imagen no disponible</div>",
                                unsafe_allow_html=True
                            )

                        st.markdown(f"**{row['nombre']}**")
                        st.markdown(f"{row['marca']} • {row['categoría']} • {row['acabado']}")
                        st.markdown(f"_Tono:_ {row['tono']}")
                        st.markdown(f"**S/. {row['precio']:.2f}** · ⭐ {row['rating']:.1f} · Stock: {int(row['stock'])}")
                        st.markdown(
                            f"<div style='color:#4a044e'>{row['descripcion']}</div>",
                            unsafe_allow_html=True
                        )
                        cc1, cc2, cc3 = st.columns(3)
                        cc1.write("Cruelty-free: " + ("✅" if row["cruelty_free"] else "❌"))
                        cc2.write("Vegano: " + ("✅" if row["vegano"] else "❌"))
                        if cc3.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                            st.session_state.items = [p for p in st.session_state.items if p["id"] != row["id"]]
                            st.rerun()

    st.download_button(
        "⬇️ Exportar CSV (vista filtrada)",
        data=df_f.drop(columns=["image_bytes"]).to_csv(index=False).encode("utf-8"),
        file_name="makeup_real_filtrado.csv",
        mime="text/csv"
    )

# ===== Insights =====
with tab_insights:
    if df_f.empty:
        st.info("Ajusta filtros para ver gráficos.")
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

        # Precio vs Rating
        chart_scatter = (
            alt.Chart(df_f)
            .mark_circle(size=120)
            .encode(
                x=alt.X("precio:Q", title="Precio (S/.)"),
                y=alt.Y("rating:Q", title="Rating"),
                color=alt.Color("marca:N", title="Marca"),
                tooltip=["nombre","marca","precio","rating","categoría","acabado","tono"]
            )
            .properties(height=320)
        )
        right.altair_chart(chart_scatter, use_container_width=True)

# ---------------------------------
# Tips
# ---------------------------------
with st.expander("💡 Tips para imágenes reales"):
    st.markdown(
        """
- **URL de imagen**: usa enlaces directos a archivos `.jpg`, `.png` o `.webp` (por ejemplo, páginas de producto de la marca o retailers).
- **Subir archivo**: si tienes la foto en tu PC, súbela y se guardará en la sesión.
- Si ves “Imagen no disponible”, revisa que el enlace sea directo (termina en `.jpg`, `.png` o `.webp`) o vuelve a subir el archivo.
- Este demo no persiste en disco: al recargar la app, vuelves al catálogo base.
"""
    )
