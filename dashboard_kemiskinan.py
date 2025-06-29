import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from streamlit_folium import folium_static
import plotly.express as px

# === Konfigurasi halaman Streamlit ===
st.set_page_config(layout="wide")
st.title("📍 _City Lights, Shadows of Poverty_: Analisis Prediksi Spasial Kemiskinan Berbasis _Night-Time Satellite Data_ dan _Deep Learning_ di Provinsi Jawa Barat")

# === File paths (relatif terhadap repo/folder deployment) ===
csv_path = 'DATA_ANALISIS_PREDIKSI.csv'
shapefile_path = 'ADMIN_JAWABARAT_FIX.zip'

# === Skema warna Folium valid ===
valid_colorbrewer_schemes = [
    'YlGn', 'YlGnBu', 'GnBu', 'BuGn', 'PuBuGn', 'PuBu',
    'BuPu', 'RdPu', 'PuRd', 'OrRd', 'YlOrRd', 'YlOrBr',
    'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
    'Greys', 'PuOr', 'BrBG', 'PRGn', 'PiYG', 'RdBu',
    'RdGy', 'RdYlBu', 'Spectral', 'RdYlGn'
]

# === Load data dengan cache ===
@st.cache_data
def load_data(shapefile_path, csv_path):
    try:
        df = pd.read_csv(csv_path)
        gdf = gpd.read_file(shapefile_path).to_crs("EPSG:4326")
        gdf["geometry"] = gdf["geometry"].simplify(0.001)

        if 'KABUPATEN' not in df.columns or 'KABUPATEN' not in gdf.columns:
            st.error("❗ Kolom 'KABUPATEN' tidak ditemukan di file.")
            return None, None

        gdf = gdf.merge(df, on='KABUPATEN', how='left')
        return df, gdf
    except Exception as e:
        st.error(f"🚨 Gagal memuat data: {e}")
        return None, None

# === Load Data ===
df, gdf = load_data(shapefile_path, csv_path)
if df is None or gdf is None:
    st.stop()

# === Sidebar pilihan ===
option = st.sidebar.selectbox(
    "📊 Pilih Data yang Ingin Ditampilkan:",
    ['%Kemiskinan_Actual_2019', '%Kemiskinan_Predicted_2019', '%Kemiskinan_Actual_2024', '%Kemiskinan_Predicted_2024']
)

color_theme = st.sidebar.selectbox(
    "🎨 Pilih Skema Warna Visualisasi:",
    valid_colorbrewer_schemes,
    index=valid_colorbrewer_schemes.index('YlOrRd')
)

# === PETA + GAMBARA UMUM ===
st.subheader("🗺️ Peta Interaktif")
col1, col2 = st.columns([2, 1])

with col1:
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

    folium_static(m, width=850, height=550)

with col2:
    st.markdown("""
    ### 📌 Gambaran Umum

    Dashboard ini menampilkan **prediksi dan data aktual** tingkat kemiskinan di 27 kabupaten/kota di **Jawa Barat** untuk tahun **2019** dan **2024**.

    - Data menggunakan **citra malam hari (NTL)** dan indikator sosial ekonomi.
    - Peta menunjukkan distribusi spasial tingkat kemiskinan.
    - Warna gelap = tingkat kemiskinan tinggi.
    - Gunakan sidebar untuk memilih **tahun & tema warna**.

    🔍 **Tujuan:** analisis spasial kemiskinan dengan memanfaatkan **citra malam hari (NTL)**.
    """)

# === PLOTLY BAR CHART ===
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

# === TABEL DATA ===
st.subheader("📋 Tabel Data")
columns_to_show = ['KABUPATEN', '%Kemiskinan_Actual_2019', '%Kemiskinan_Predicted_2019', 'Abs_Error_2019',
                   '%Kemiskinan_Actual_2024', '%Kemiskinan_Predicted_2024', 'Abs_Error_2024']
st.dataframe(gdf[columns_to_show].sort_values(by='KABUPATEN').reset_index(drop=True))

# === INTERPRETASI (bawah dashboard) ===
st.subheader("🧭 Interpretasi Hasil Prediksi")
st.markdown("""
### ✅ Kinerja Model
- Rata-rata error absolut berada di kisaran **1–3%**.
- Konsistensi prediksi baik antara tahun 2019 dan 2024.

### 🔍 Temuan Penting
- Akurasi tinggi: **Cianjur, Sumedang, Bogor**.
- Overestimate: **Kota Tasikmalaya, Kab. Bandung**.
- Prediksi di **wilayah perkotaan** cenderung lebih variatif.

### 📌 Rekomendasi Kebijakan
- Model bisa digunakan untuk **monitoring cepat** daerah rawan kemiskinan.
- Potensial untuk digunakan sebagai basis **perencanaan intervensi** data-driven.

> ⚠️ Model ini masih bersifat eksploratif. Validasi lapangan tetap diperlukan.

---

### ⚠️ Keterbatasan Penelitian
- **Data makro:** Analisis masih terbatas pada tingkat kabupaten/kota (n=27), belum menjangkau desa/kelurahan.
- **Variabel terbatas:** Hanya mencakup indikator sosio-ekonomi, belum multidimensi.
- **Metodologi:** Jumlah data kecil menyebabkan nilai R² menurun pada 2019 dan 2024.
""")
