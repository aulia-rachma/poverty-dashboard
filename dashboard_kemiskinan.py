import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import plotly.express as px

# Set Streamlit page config
st.set_page_config(layout="wide")
st.title("📍 Dashboard Prediksi Kemiskinan Jawa Barat")

# File paths (relative to repo root)
csv_path = 'DATA_ANALISIS_PREDIKSI.csv'
shapefile_path = 'ADMIN_JAWABARAT_FIX.zip'

# Load and cache data
@st.cache_data
@st.cache_data
def load_data(shapefile_path, csv_path):
    try:
        df = pd.read_csv(csv_path)
        gdf = gpd.read_file(shapefile_path).to_crs("EPSG:4326")

        # ✅ HANYA menyederhanakan kolom geometry, bukan seluruh gdf
        gdf["geometry"] = gdf["geometry"].simplify(0.001)

        if 'KABUPATEN' not in df.columns:
            st.error("❗ Kolom 'KABUPATEN' tidak ditemukan di CSV.")
            return None, None
        if 'KABUPATEN' not in gdf.columns:
            st.error("❗ Kolom 'KABUPATEN' tidak ditemukan di Shapefile.")
            return None, None

        gdf = gdf.merge(df, on='KABUPATEN', how='left')
        return df, gdf
    except Exception as e:
        st.error(f"🚨 Gagal memuat data: {e}")
        return None, None

# Load data
df, gdf = load_data(shapefile_path, csv_path)

# Stop if data failed to load
if df is None or gdf is None:
    st.stop()

# Sidebar selector
option = st.sidebar.selectbox(
    "Pilih Data yang Ingin Ditampilkan di Peta:",
    ['Actual_2019', 'Predicted_2019', 'Actual_2024', 'Predicted_2024']
)

# Interactive Folium Map
st.subheader("🗺️ Peta Interaktif")
m = folium.Map(location=[-6.9, 107.6], zoom_start=8)

# Choropleth
folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=['KABUPATEN', option],
    key_on='feature.properties.KABUPATEN',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=option
).add_to(m)

# Optional: Tooltip
folium.GeoJson(
    gdf,
    name="Labels",
    tooltip=folium.GeoJsonTooltip(fields=['KABUPATEN'], aliases=["Kabupaten:"])
).add_to(m)

folium_static(m, width=1000, height=600)

# Plotly Bar Chart
st.subheader("📊 Visualisasi Distribusi")
fig = px.bar(
    gdf.sort_values(by=option, ascending=False),
    x='KABUPATEN',
    y=option,
    color=option,
    color_continuous_scale='YlOrRd',
    title=f"Distribusi {option} per Kabupaten"
)
fig.update_layout(xaxis_tickangle=-45, height=500)
st.plotly_chart(fig, use_container_width=True)

# Data Table
st.subheader("📋 Tabel Data Lengkap")
columns_to_show = ['KABUPATEN', 'Actual_2019', 'Predicted_2019', 'Abs_Error_2019',
                   'Actual_2024', 'Predicted_2024', 'Abs_Error_2024']
st.dataframe(gdf[columns_to_show].sort_values(by='KABUPATEN').reset_index(drop=True))
