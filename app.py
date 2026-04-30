import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Dashboard Spasio-Temporal Sumbar", layout="wide")

# Koordinat kasar untuk Kabupaten/Kota di Sumatera Barat
KOORDINAT_SUMBAR = {
    'Kepulauan Mentawai': [-2.2415, 99.5826],
    'Pesisir Selatan': [-1.3541, 100.5694],
    'Kab.Solok': [-0.9419, 100.6710],
    'Sijunjung': [-0.6934, 101.2001],
    'Tanah Datar': [-0.4705, 100.5815],
    'Padang Pariaman': [-0.6276, 100.2831],
    'Agam': [-0.2762, 100.1065],
    'Lima Puluh Kota': [0.1174, 100.6033],
    'Pasaman': [0.1770, 100.1654],
    'Solok Selatan': [-1.1557, 101.3543],
    'Dharmasraya': [-1.0267, 101.5997],
    'Pasaman Barat': [0.1607, 99.7186],
    'Padang': [-0.9492, 100.3543],
    'Kota Padang': [-0.9492, 100.3543],
    'Solok': [-0.7937, 100.6625],
    'Kota Solok': [-0.7937, 100.6625],
    'Sawahlunto': [-0.6811, 100.7766],
    'Kota Sawahlunto': [-0.6811, 100.7766],
    'Padang Panjang': [-0.4632, 100.4026],
    'Kota Padang Panjang': [-0.4632, 100.4026],
    'Bukittinggi': [-0.3051, 100.3692],
    'Kota Bukittinggi': [-0.3051, 100.3692],
    'Payakumbuh': [-0.2263, 100.6300],
    'Kota Payakumbuh': [-0.2263, 100.6300],
    'Pariaman': [-0.6256, 100.1187],
    'Kota Pariaman': [-0.6256, 100.1187]
}

@st.cache_data
def load_data():
    file_name = 'Perkembangan Penduduk Sumatera Barat.xlsx'
    df = pd.read_excel(file_name, sheet_name='Data 1', header=2)
    df.rename(columns={'Unnamed: 0': 'Wilayah'}, inplace=True)
    df = df.dropna(subset=['Wilayah'])
    
    # Bersihkan spasi berlebih pada nama wilayah
    df['Wilayah'] = df['Wilayah'].str.strip()
    return df

df = load_data()

st.sidebar.title("Navigasi Spasio-Temporal")
halaman = st.sidebar.radio("Pilih Halaman:", ["Dataset Mentah", "Peta Leaflet Interaktif"])

if halaman == "Dataset Mentah":
    st.title("Data Penduduk Sumatera Barat")
    st.dataframe(df, use_container_width=True)

elif halaman == "Peta Leaflet Interaktif":
    st.title("Peta Sebaran Penduduk Sumatera Barat")
    st.write("Representasi **spasio-temporal**. Geser slider tahun untuk melihat perubahan populasi (ukuran bubble merepresentasikan jumlah penduduk).")
    
    # 1. Ekstraksi daftar tahun untuk slider (Aspek Temporal)
    tahun_kolom = [col for col in df.columns if isinstance(col, (int, float))]
    tahun_kolom.sort()
    
    # Widget Slider Tahun
    tahun_pilihan = st.slider("Pilih Tahun:", min_value=int(min(tahun_kolom)), max_value=int(max(tahun_kolom)), step=1)
    
    # 2. Setup Base Map Leaflet (Aspek Spasial) - Titik tengah di Padang
    m = folium.Map(location=[-0.9492, 100.3543], zoom_start=8, tiles='CartoDB positron')
    
    # 3. Plotting Data ke Peta
    for index, row in df.iterrows():
        wilayah = row['Wilayah']
        populasi = row.get(tahun_pilihan, None)
        
        # Cek apakah koordinat wilayah tersedia dan populasinya valid
        if wilayah in KOORDINAT_SUMBAR and pd.notna(populasi) and populasi != "-":
            try:
                populasi_int = int(populasi)
                # Skala ukuran bubble (dibagi agar tidak menutupi seluruh peta)
                radius_bubble = populasi_int / 30000 
                
                # Buat Marker Lingkaran di Leaflet
                folium.CircleMarker(
                    location=KOORDINAT_SUMBAR[wilayah],
                    radius=radius_bubble,
                    popup=f"<b>{wilayah}</b><br>Tahun {tahun_pilihan}: {populasi_int:,} jiwa",
                    tooltip=wilayah,
                    color="#3186cc",
                    fill=True,
                    fill_color="#3186cc",
                    fill_opacity=0.6
                ).add_to(m)
            except ValueError:
                continue

    # 4. Render map ke Streamlit
    st_folium(m, width=800, height=500)