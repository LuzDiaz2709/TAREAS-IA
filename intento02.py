import io
import json
import base64
from typing import List, Dict

import altair as alt
import pandas as pd
import streamlit as st
from PIL import Image

# =========================
# Configuración
# =========================
st.set_page_config(page_title="Makeup Rosa — Catálogo", page_icon="💖", layout="wide")
st.title("💖 Makeup Rosa — Catálogo con Favoritos, Comparador y JSON")
st.caption("Sin dataset externo • Persistencia vía exportar/importar JSON • Estética rosa")

# =========================
# Utilidades
# =========================
def imgfile_to_b64(file) -> str:
    """Convierte un archivo de imagen a base64 (JPEG) para persistir en JSON."""
    try:
        img = Image.open(file).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=90)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception:
        return ""

def b64_to_bytes(b64: str) -> bytes | None:
    try:
        return base64.b64decode(b64.encode("utf-8"))
    except Exception:
        return None

def to_df(items: List[Dict]) -> pd.DataFrame:
    if not items:
        return pd.DataFrame(columns=[
            "id","nombre","marca","categoría","acabado","tono","precio","rating",
            "cruelty_free","vegano","stock","descripcion","image_url","image_b64"
        ])
    return pd.DataFrame(items)

def safe_float(x, default=0.0):
    try:
        return float(x)
    except Exception:
        return default

# =========================
# Catálogo base (marcas reales)
# =========================
BASE: List[Dict] = [
    {"id":1,"nombre":"Liquid Blush","marca":"Rare Beauty","categoría":"Rostro","acabado":"Satinado","tono":"Happy",
     "precio":115.0,"rating":4.8,"cruelty_free":True,"vegano":True,"stock":15,
     "descripcion":"Rubor líquido de alta pigmentación y difuminado fácil.",
     "image_url":"", "image_b64":""},
    {"id":2,"nombre":"Velvet Liquid Lipstick","marca":"Fenty Beauty","categoría":"Labios","acabado":"Mate","tono":"Pink Matter",
     "precio":119.0,"rating":4.7,"cruelty_free":True,"vegano":True,"stock":20,
     "descripcion":"Labial líquido mate de larga duración.",
     "image_url":"", "image_b64":""},
    {"id":3,"nombre":"Butter Gloss","marca":"NYX","categoría":"Labios","acabado":"Brillante","tono":"Crème Brulee",
     "precio":39.0,"rating":4.3,"cruelty_free":True,"vegano":False,"stock":40,
     "descripcion":"Brillo labial cremoso con color suave.",
     "image_url":"", "image_b64":""},
    {"id":4,"nombre":"Powder Kiss Lipstick","marca":"MAC","categoría":"Labios","acabado":"Mate difuminado","tono":"Sultry Move",
     "precio":99.0,"rating":4.6,"cruelty_free":False,"vegano":False,"stock":18,
     "descripcion":"Acabado borroso cómodo para uso diario.",
     "image_url":"", "image_b64":""},
    {"id":5,"nombre":"Afterglow Liquid Blush","marca":"NARS","categoría":"Rostro","acabado":"Glow","tono":"Orgasm",
     "precio":135.0,"rating":4.7,"cruelty_free":False,"vegano":False,"stock":12,
     "descripcion":"Rubor líquido luminoso efecto saludable.",
     "image_url":"", "image_b64":""},
    {"id":6,"nombre":"Halo Glow Blush Wand","marca":"e.l.f.","categoría":"Rostro","acabado":"Glow","tono":"Pink-Me-Up",
     "precio":49.0,"rating":4.5,"cruelty_free":True,"vegano":True,"stock":28,
     "descripcion":"Rubor con aplicador y brillo saludable.",
     "image_url":"", "image_b64":""},
    {"id":7,"nombre":"SuperStay Vinyl Ink","marca":"Maybelline","categoría":"Labios","acabado":"Brillante","tono":"Lippy",
     "precio":55.0,"rating":4.4,"cruelty_free":False,"vegano":False,"stock":35,
     "descripcion":"Vinilo de alto impacto y fijación.",
     "image_url":"", "image_b64":""},
    {"id":8,"nombre":"Infallible Fresh Wear Blush","marca":"L'Oréal","categoría":"Rostro","acabado":"Natural","tono":"Confident Pink",
     "precio":69.0,"rating":4.2,"cruelty_free":False,"vegano":False,"stock":26,
     "descripcion":"Rubor resistente al sudor y transferencia.",
     "image_url":"", "image_b64":""},
]

# =========================
# Estado
# =========================
if "items" not in st.session_state:
    st.session_state.items = BASE.copy()
if "favs" not in st.session_state:
    st.session_state.favs = set()
if "page" not in st.session_state:
    st.session_state.page = 1

# =========================
# Sidebar: filtros + Alta + Import/Export
# =========================
with st.sidebar:
    st.header("🎯 Filtros")
    df_all = to_df(st.session_state.items)
    marcas = sorted(df_all["marca"].unique().tolist()) if not df_all.empty else []
    cats = sorted(df_all["categoría"].unique().tolist()) if not df_all.empty else []
    acabados = sorted(df_all["acabado"].unique().tolist()) if not df_all.empty else []

    q = st.text_input("🔎 Buscar (nombre/tono/marca)")
    f_marca = st.multiselect("Marca", marcas, default=marcas)
    f_cat = st.multiselect("Categoría", cats, default=cats)
    f_acab = st.multiselect("Acabado", acabados, default=acabados)
    f_precio = st.slider("Precio máx (S/.)", 20.0, 200.0, 200.0, step=1.0)
    st.markdown("---")

    st.subheader("➕ Agregar producto")
    with st.form("form_add", clear_on_submit=True):
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre")
        marca = c2.selectbox("Marca", ["Rare Beauty","Fenty Beauty","Maybelline","MAC","NARS","e.l.f.","NYX","L'Oréal","Otra"])
        categoria = c1.selectbox("Categoría", ["Rostro","Ojos","Labios"])
        acabado = c2.selectbox("Acabado", ["Mate","Satinado","Brillante","Glow","Natural","Mate difuminado"])
        tono = c1.text_input("Tono / Color", value="Rosa")
        precio = safe_float(c2.number_input("Precio (S/.)", min_value=0.0, value=59.0, step=0.5), 59.0)
        rating = safe_float(c1.slider("Rating", 1.0, 5.0, 4.5, step=0.1), 4.5)
        stock = int(c2.number_input("Stock", min_value=0, value=10, step=1))
        cruelty = c1.checkbox("Cruelty-free", value=True)
        vegan = c2.checkbox("Vegano", value=False)
        desc = st.text_area("Descripción", value="Descripción breve del producto.")

        st.markdown("**Imagen** (elige una opción)")
        url_img = st.text_input("URL de imagen (https://...)")
        up_img = st.file_uploader("o sube una imagen", type=["jpg","jpeg","png","webp"])

        submitted = st.form_submit_button("Agregar")
        if submitted:
            new_id = max([it["id"] for it in st.session_state.items]) + 1 if st.session_state.items else 1
            image_b64 = imgfile_to_b64(up_img) if up_img else ""
            st.session_state.items.append({
                "id": new_id, "nombre": nombre or "Nuevo Producto", "marca": marca,
                "categoría": categoria, "acabado": acabado, "tono": tono,
                "precio": float(precio), "rating": float(rating), "stock": int(stock),
                "cruelty_free": bool(cruelty), "vegano": bool(vegan),
                "descripcion": (desc or "").strip(),
                "image_url": (url_img or "").strip(),
                "image_b64": image_b64,
            })
            st.success("Producto agregado.")

    st.markdown("---")
    st.subheader("📦 Importar / Exportar")
    exp = st.download_button(
        "⬇️ Exportar catálogo (.json)",
        data=json.dumps(st.session_state.items, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name="makeup_catalogo.json",
        mime="application/json",
        use_container_width=True
    )
    up_json = st.file_uploader("Importar JSON", type=["json"])
    if up_json is not None:
        try:
            data = json.load(up_json)
            assert isinstance(data, list)
            # Validación mínima de claves
            cleaned = []
            for i, it in enumerate(data, start=1):
                cleaned.append({
                    "id": int(it.get("id", i)),
                    "nombre": str(it.get("nombre","Producto")),
                    "marca": str(it.get("marca","Marca")),
                    "categoría": str(it.get("categoría","Rostro")),
                    "acabado": str(it.get("acabado","Mate")),
                    "tono": str(it.get("tono","Rosa")),
                    "precio": float(it.get("precio",0)),
                    "rating": float(it.get("rating",0)),
                    "cruelty_free": bool(it.get("cruelty_free", False)),
                    "vegano": bool(it.get("vegano", False)),
                    "stock": int(it.get("stock",0)),
                    "descripcion": str(it.get("descripcion","")),
                    "image_url": str(it.get("image_url","")),
                    "image_b64": str(it.get("image_b64","")),
                })
            st.session_state.items = cleaned
            st.session_state.page = 1
            st.success("Catálogo importado.")
        except Exception as e:
            st.error(f"No se pudo importar el JSON: {e}")

    st.markdown("---")
    if st.button("🔄 Reiniciar al catálogo base"):
        st.session_state.items = BASE.copy()
        st.session_state.favs = set()
        st.session_state.page = 1
        st.success("Catálogo reiniciado.")

# =========================
# Filtrado
# =========================
df = to_df(st.session_state.items)
mask = (
    df["marca"].isin(f_marca) &
    df["categoría"].isin(f_cat) &
    df["acabado"].isin(f_acab) &
    (df["precio"] <= f_precio)
)
if q:
    ql = q.lower()
    mask &= (
        df["nombre"].str.lower().str.contains(ql) |
        df["tono"].str.lower().str.contains(ql) |
        df["marca"].str.lower().str.contains(ql)
    )
df_f = df[mask].reset_index(drop=True)

# =========================
# Métricas
# =========================
c1, c2, c3, c4 = st.columns(4)
c1.metric("Productos visibles", len(df_f))
c2.metric("Precio promedio (S/.)", f"{df_f['precio'].mean():.2f}" if not df_f.empty else "—")
c3.metric("Rating promedio", f"{df_f['rating'].mean():.2f}" if not df_f.empty else "—")
c4.metric("Stock total", int(df_f["stock"].sum()) if not df_f.empty else 0)

# =========================
# Paginación
# =========================
PER_PAGE = 6
total_pages = max(1, (len(df_f) + PER_PAGE - 1) // PER_PAGE)
st.session_state.page = min(st.session_state.page, total_pages)
colp1, colp2, colp3 = st.columns([1, 2, 1])
with colp1:
    if st.button("⬅️ Anterior", disabled=(st.session_state.page <= 1)):
        st.session_state.page -= 1
with colp3:
    if st.button("Siguiente ➡️", disabled=(st.session_state.page >= total_pages)):
        st.session_state.page += 1
colp2.markdown(f"<div style='text-align:center'>Página **{st.session_state.page} / {total_pages}**</div>", unsafe_allow_html=True)

start = (st.session_state.page - 1) * PER_PAGE
end = start + PER_PAGE
page_df = df_f.iloc[start:end]

# =========================
# Tabs
# =========================
tab_catalogo, tab_insights, tab_comp = st.tabs(["📒 Catálogo", "📊 Insights", "⚖️ Comparador"])

# ===== Catálogo (tarjetas con favoritos) =====
with tab_catalogo:
    if page_df.empty:
        st.info("No hay productos con los filtros actuales.")
    else:
        cols_per_row = 3
        chunks = [page_df.iloc[i:i+cols_per_row] for i in range(0, len(page_df), cols_per_row)]
        for ch in chunks:
            cols = st.columns(cols_per_row)
            for idx, (_, row) in enumerate(ch.iterrows()):
                with cols[idx]:
                    with st.container(border=True):
                        # Mostrar imagen (image_b64 > image_url > placeholder)
                        showed = False
                        if isinstance(row["image_b64"], str) and row["image_b64"]:
                            b = b64_to_bytes(row["image_b64"])
                            if b:
                                st.image(b, use_container_width=True)
                                showed = True
                        if not showed and isinstance(row["image_url"], str) and row["image_url"]:
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
                        st.markdown(f"<div style='color:#4a044e'>{row['descripcion']}</div>", unsafe_allow_html=True)

                        cta1, cta2, cta3 = st.columns(3)
                        is_fav = row["id"] in st.session_state.favs
                        fav_label = "❤️ Quitar" if is_fav else "🤍 Favorito"
                        if cta1.button(fav_label, key=f"fav_{row['id']}"):
                            if is_fav:
                                st.session_state.favs.remove(row["id"])
                            else:
                                st.session_state.favs.add(row["id"])
                        if cta2.button("🗑️ Eliminar", key=f"del_{row['id']}"):
                            st.session_state.items = [p for p in st.session_state.items if p["id"] != row["id"]]
                            if row["id"] in st.session_state.favs:
                                st.session_state.favs.remove(row["id"])
                            st.rerun()
                        if cta3.button("✏️ Editar", key=f"edit_{row['id']}"):
                            with st.modal(f"Editar: {row['nombre']}"):
                                ec1, ec2 = st.columns(2)
                                nn = ec1.text_input("Nombre", value=row["nombre"])
                                nm = ec2.text_input("Marca", value=row["marca"])
                                nc = ec1.selectbox("Categoría", ["Rostro","Ojos","Labios"], index=["Rostro","Ojos","Labios"].index(row["categoría"]))
                                na = ec2.text_input("Acabado", value=row["acabado"])
                                nt = ec1.text_input("Tono", value=row["tono"])
                                np = ec2.number_input("Precio", min_value=0.0, value=float(row["precio"]), step=0.5)
                                nr = ec1.slider("Rating", 1.0, 5.0, float(row["rating"]), step=0.1)
                                ns = ec2.number_input("Stock", min_value=0, value=int(row["stock"]), step=1)
                                ncr = ec1.checkbox("Cruelty-free", value=bool(row["cruelty_free"]))
                                nvg = ec2.checkbox("Vegano", value=bool(row["vegano"]))
                                nd = st.text_area("Descripción", value=row["descripcion"])

                                st.markdown("**Imagen**")
                                nurl = st.text_input("URL", value=row["image_url"])
                                nup = st.file_uploader("Subir nueva imagen", type=["jpg","jpeg","png","webp"], key=f"up_{row['id']}")

                                if st.button("Guardar cambios", use_container_width=True):
                                    image_b64 = row["image_b64"]
                                    if nup is not None:
                                        image_b64 = imgfile_to_b64(nup)
                                    # persistir
                                    for it in st.session_state.items:
                                        if it["id"] == row["id"]:
                                            it.update({
                                                "nombre": nn, "marca": nm, "categoría": nc, "acabado": na,
                                                "tono": nt, "precio": float(np), "rating": float(nr),
                                                "stock": int(ns), "cruelty_free": bool(ncr), "vegano": bool(nvg),
                                                "descripcion": nd, "image_url": nurl, "image_b64": image_b64
                                            })
                                            break
                                    st.success("Actualizado.")
                                    st.rerun()

        st.markdown("#### ❤️ Favoritos")
        if not st.session_state.favs:
            st.write("_Aún no has marcado favoritos._")
        else:
            fav_df = df[df["id"].isin(list(st.session_state.favs))]
            st.dataframe(fav_df[["nombre","marca","precio","rating","categoría","acabado","tono"]], use_container_width=True, height=200)

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
                tooltip=["categoría","count"]
            )
            .properties(height=320)
        )
        left.altair_chart(chart_cat, use_container_width=True)

        # Precio vs Rating por marca
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

        st.markdown("#### 💵 Precio promedio por marca")
        brand_price = df_f.groupby("marca")["precio"].mean().reset_index()
        chart_price = (
            alt.Chart(brand_price)
            .mark_bar()
            .encode(
                x=alt.X("marca:N", title="Marca"),
                y=alt.Y("precio:Q", title="Precio promedio"),
                tooltip=["marca", alt.Tooltip("precio:Q", format=".2f")]
            )
            .properties(height=280)
        )
        st.altair_chart(chart_price, use_container_width=True)

# ===== Comparador =====
with tab_comp:
    opciones = df_f["nombre"].tolist()
    sel = st.multiselect("Selecciona hasta 4 productos", options=opciones, max_selections=4)
    if not sel:
        st.info("Elige productos para comparar.")
    else:
        comp = df[df["nombre"].isin(sel)].copy()
        show_cols = ["nombre","marca","categoría","acabado","tono","precio","rating","cruelty_free","vegano","stock","descripcion"]
        st.dataframe(comp[show_cols], use_container_width=True, height=240)

        st.markdown("##### Comparativa visual (normalizada 0-1)")
        comp_norm = comp.assign(
            precio_n = (comp["precio"] - comp["precio"].min()) / (comp["precio"].max() - comp["precio"].min() + 1e-9),
            rating_n = (comp["rating"] - comp["rating"].min()) / (comp["rating"].max() - comp["rating"].min() + 1e-9),
            stock_n  = (comp["stock"]  - comp["stock"].min())  / (comp["stock"].max()  - comp["stock"].min()  + 1e-9),
        )[["nombre","precio_n","rating_n","stock_n"]].melt("nombre", var_name="métrica", value_name="valor")

        chart_comp = (
            alt.Chart(comp_norm)
            .mark_bar()
            .encode(
                x=alt.X("nombre:N", title="Producto"),
                y=alt.Y("valor:Q", title="Valor normalizado"),
                color=alt.Color("métrica:N", title="Métrica"),
                tooltip=["nombre","métrica", alt.Tooltip("valor:Q", format=".2f")]
            )
            .properties(height=260)
        )
        st.altair_chart(chart_comp, use_container_width=True)

# =========================
# Tips
# =========================
with st.expander("💡 Tips rápidos"):
    st.markdown(
        """
- **Favoritos** se guardan en esta sesión; para persistir el catálogo, usa **Exportar JSON**.
- Puedes **importar** el mismo JSON más adelante para recuperar todo (incluidas imágenes subidas, embebidas en base64).
- Para imágenes por **URL**, prefiere enlaces directos a `.jpg`, `.png` o `.webp`.
"""
    )

