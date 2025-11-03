# app.py
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

# ---- Configuración de la página
st.set_page_config(page_title="Vehicles EDA", layout="wide")

# ---- Encabezado
st.header("Análisis exploratorio de anuncios de vehículos")

# ---- Carga de datos (cacheada para rapidez)
DATA_PATH = Path(__file__).parent / "data" / "vehicles_us.csv"

@st.cache_data(show_spinner=False)
def load_data(path: Path) -> pd.DataFrame:
    # low_memory=False mejora la inferencia de tipos
    return pd.read_csv(path, low_memory=False)

try:
    car_data = load_data(DATA_PATH)
    st.caption(f"Archivo cargado: `{DATA_PATH.name}` · "
               f"Filas: {len(car_data):,} · Columnas: {len(car_data.columns)}")
except FileNotFoundError:
    st.error(f"No se encontró el archivo en `{DATA_PATH}`. "
             "Asegúrate de colocar `vehicles_us.csv` dentro de la carpeta `data/`.")
    st.stop()

# ---- Botones requeridos
col1, col2 = st.columns(2)

with col1:
    hist_button = st.button("Construir histograma (odometer)")
with col2:
    scatter_button = st.button("Construir diagrama de dispersión (odometer vs price)")

# Histograma
if hist_button:
    st.write("**Creación de un histograma para la columna `odometer`**")
    if "odometer" in car_data.columns:
        fig = px.histogram(car_data, x="odometer", nbins=60,
                           title="Distribución de odómetro")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("La columna `odometer` no existe en el dataset.")

# Dispersión
if scatter_button:
    st.write("**Creación de un diagrama de dispersión `odometer` vs `price`**")
    need = {"odometer", "price"}
    if need.issubset(car_data.columns):
        color_col = "model_year" if "model_year" in car_data.columns else None
        fig = px.scatter(car_data.dropna(subset=list(need)),
                         x="odometer", y="price", color=color_col,
                         title="Precio vs Odómetro" + (" (color: model_year)" if color_col else ""))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Faltan columnas: {list(need - set(car_data.columns))}")

# ---- Modo avanzado (opcional): casillas de verificación
with st.expander("Modo avanzado (opcional): generar gráficos con casillas de verificación"):
    c1, c2 = st.columns(2)
    with c1:
        build_hist = st.checkbox("Histograma personalizado")
        # Sugerimos columnas numéricas para el histograma
        num_cols = car_data.select_dtypes(include="number").columns.tolist()
        x_hist = st.selectbox("Columna para histograma", options=num_cols, index=num_cols.index("odometer") if "odometer" in num_cols else 0)
    with c2:
        build_scatter = st.checkbox("Dispersión personalizada")
        x_scatter = st.selectbox("Eje X (num)", options=num_cols, index=num_cols.index("odometer") if "odometer" in num_cols else 0)
        y_scatter = st.selectbox("Eje Y (num)", options=num_cols, index=num_cols.index("price") if "price" in num_cols else 0)
        color_opt = [None] + car_data.columns.tolist()
        color_scatter = st.selectbox("Color (opcional)", options=color_opt, index=color_opt.index("model_year") if "model_year" in color_opt else 0)

    if build_hist:
        st.write(f"**Histograma de `{x_hist}`**")
        fig = px.histogram(car_data, x=x_hist, nbins=60, title=f"Distribución de {x_hist}")
        st.plotly_chart(fig, use_container_width=True)

    if build_scatter:
        st.write(f"**Dispersión `{x_scatter}` vs `{y_scatter}`**")
        fig = px.scatter(car_data.dropna(subset=[x_scatter, y_scatter]),
                         x=x_scatter, y=y_scatter, color=color_scatter if color_scatter else None,
                         title=f"{y_scatter} vs {x_scatter}" + (f" (color: {color_scatter})" if color_scatter else ""))
        st.plotly_chart(fig, use_container_width=True)

#st.caption("Tip: ejecuta `streamlit run app.py` para ver esta app en tu navegador.")
