import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import plotly.express as px

# Set Streamlit page config
st.set_page_config(layout="wide")
st.title("📍 Dashboard Prediksi Kemiskinan Jawa Barat")

# File paths
csv_path = 'DATA_ANALISIS_PREDIKSI.csv'
shapefile_path = 'ADMIN_JAWABARAT_FIX.zip'

# Valid color schemes for Folium (ColorBrewer-compatible)
valid_colorbrewer_schemes = [
    'YlGn', 'YlGnBu', 'GnBu', 'BuGn', 'PuBuGn', 'PuBu',
    'BuPu', 'RdPu', 'PuRd', 'OrRd', 'YlOrRd', 'YlOrBr',
    'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
    'Greys', 'PuOr', 'BrBG', 'PRGn', 'PiYG', 'RdBu',
    'RdGy', 'RdYlBu', 'Spectral', 'RdYlGn'
]

# Load and cache data
@st.cache_data
def load_data(shapefile_path, csv_path):
    try:
        df = pd.read_csv(csv_path)
        gdf = gpd.read_file(shapefile_path).to_crs("EPSG:4326")
        gdf["geometry"] = gdf["geometry"].simplify(0.001)

        if 'KABUPATEN' not in df.columns or 'KABUPATEN' not in gdf.columns:
            st.error("❗ Kolom 'KABUPATEN' tidak ditemukan di salah satu file.")
            return None, None

        gdf = gdf.merge(df, on='KABUPATEN', how='left')
        return df, gdf
    except Exception as e:
        st.error(f"🚨 Gagal memuat data: {e}")
        return None, None

# Load data
df, gdf = load_data(shapefile_path, csv_path)
if df is None or gdf is None:
    st.stop()

# Sidebar selectors
option = st.sidebar.selectbox(
    "📊 Pilih Data yang Ingin Ditampilkan:",
    ['Actual_2019', 'Predicted_2019', 'Actual_2024', 'Predicted_2024']
)

color_theme = st.sidebar.selectbox(
    "🎨 Pilih Skema Warna Visualisasi:",
    valid_colorbrewer_schemes,
    index=valid_colorbrewer_schemes.index('YlOrRd')
)

# ========================== SECTION: MAP ==============================
st.subheader("🗺️ Peta Interaktif Prediksi Kemiskinan")

m = folium.Map(location=[-6.9, 107.6], zoom_start=8)

folium.Choropleth(
    geo_data=gdf,
    data=gdf,
    columns=['KABUPATEN', option],
    key_on='feature.properties.KABUPATEN',
    fill_color=color_theme,
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name=option
).add_to(m)

folium.GeoJson(
    gdf,
    name="Labels",
    tooltip=folium.GeoJsonTooltip(fields=['KABUPATEN'], aliases=["Kabupaten:"])
).add_to(m)

folium_static(m, width=1000, height=600)

# ======================= SECTION: INTERPRETASI ========================
st.subheader("🧭 Interpretasi Hasil Prediksi")

st.markdown("""
### 📌 Gambaran Umum
Model memprediksi persentase kemiskinan untuk 27 kabupaten/kota di Jawa Barat berdasarkan citra malam hari (NTL) dan data sosial ekonomi untuk tahun **2019** dan **2024**.

### ✅ Kinerja Model
- Rata-rata error absolut antara hasil prediksi dan data aktual berada di kisaran **1–3%**.
- Model menunjukkan kinerja **konsisten** antar tahun, namun terdapat variasi antar wilayah.

### 🔍 Temuan Penting
- **Akurasi tinggi** terlihat di wilayah seperti **Cianjur**, **Sumedang**, dan **Bogor**.
- Sebaliknya, wilayah seperti **Kota Tasikmalaya** dan **Kab. Bandung** menunjukkan **selisih cukup besar**, mengindikasikan perlunya penyempurnaan model di wilayah tersebut.

### 📈 Pola Regional
- Wilayah **perkotaan** seperti **Kota Depok** dan **Bekasi** cenderung **overestimate**.
- **Wilayah pedesaan** menunjukkan hasil prediksi yang lebih stabil dan dekat nilai aktual.

### 💡 Implikasi Kebijakan
- Model dapat digunakan untuk **monitoring cepat** daerah rawan kemiskinan bahkan sebelum data resmi tersedia.
- Membantu pemerintah dalam **menentukan prioritas intervensi** berbasis data prediktif.

> ⚠️ Catatan: Model ini bersifat eksploratif dan **tidak menggantikan data resmi**. Validasi dan penyempurnaan lebih lanjut disarankan sebelum digunakan untuk pengambilan keputusan kebijakan.
""")

# ========================= SECTION: CHART =============================
st.subheader("📊 Visualisasi Distribusi")

fig = px.bar(
    gdf.sort_values(by=option, ascending=False),
    x='KABUPATEN',
    y=option,
    color=option,
    color_continuous_scale=color_theme,
    title=f"Distribusi {option} per Kabupaten"
)
fig.update_layout(xaxis_tickangle=-45, height=500)
st.plotly_chart(fig, use_container_width=True)

# ========================== SECTION: TABLE ============================
st.subheader("📋 Tabel Data")

columns_to_show = ['KABUPATEN', 'Actual_2019', 'Predicted_2019', 'Abs_Error_2019',
                   'Actual_2024', 'Predicted_2024', 'Abs_Error_2024']

st.dataframe(gdf[columns_to_show].sort_values(by='KABUPATEN').reset_index(drop=True))
