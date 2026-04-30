import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import numpy as np

st.set_page_config(page_title="Dashboard Spasio-Temporal Sumbar", layout="wide")

# Kamus koordinat fix untuk mapping Leaflet
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
    'Kota Solok': [-0.7937, 100.6625],
    'Sawahlunto': [-0.6811, 100.7766],
    'Padang Panjang': [-0.4632, 100.4026],
    'Bukittinggi': [-0.3051, 100.3692],
    'Payakumbuh': [-0.2263, 100.6300],
    'Pariaman': [-0.6256, 100.1187]
}

@st.cache_data
def load_data():
    file_name = 'Perkembangan Penduduk Sumatera Barat.xlsx'
    
    # Ambil baris ke-3 (index 2) sebagai header
    df = pd.read_excel(file_name, header=2)
    
    # Amankan kolom pertama dengan merename-nya jadi 'Wilayah' secara absolut
    df = df.rename(columns={df.columns[0]: 'Wilayah'})
    
    # Bersihkan nama wilayah dari spasi berlebih
    df = df.dropna(subset=['Wilayah'])
    df['Wilayah'] = df['Wilayah'].astype(str).str.strip()
    
    # Hapus baris 'Catatan' di paling bawah
    df = df[~df['Wilayah'].str.contains('Catatan', case=False, na=False)]
    
    # Ambil list kolom yang isinya tahun (angka)
    tahun_kolom = [col for col in df.columns if isinstance(col, (int, float)) or str(col).isdigit()]
    
    # Ubah tanda '-' jadi NaN, lalu paksa konversi semua data ke angka (numeric)
    for col in tahun_kolom:
        df[col] = pd.to_numeric(df[col].replace('-', np.nan), errors='coerce')
        
    return df, sorted(list(tahun_kolom))

# Load data dengan fungsi yang sudah diperbaiki
df, list_tahun = load_data()

st.sidebar.title("Navigasi Spasio-Temporal")
halaman = st.sidebar.radio("Pilih Halaman:", ["Dataset Bersih", "Peta Leaflet Interaktif"])

if halaman == "Dataset Bersih":
    st.title("Data Penduduk Sumatera Barat")
    st.write("Tabel ini sudah dibersihkan dari simbol strip dan baris catatan.")
    st.dataframe(df, use_container_width=True)

elif halaman == "Peta Leaflet Interaktif":
    st.title("Peta Sebaran Penduduk Sumatera Barat")
    
    # Slider menggunakan list tahun yang sudah di-sort
    tahun_pilihan = st.slider("Geser Tahun:", min_value=int(min(list_tahun)), max_value=int(max(list_tahun)), step=1)
    
    # Setup Base Map - Fokus di Sumatera Barat
    m = folium.Map(location=[-0.9492, 100.3543], zoom_start=8, tiles='CartoDB positron')
    
    # Plotting Data
    for index, row in df.iterrows():
        wilayah = row['Wilayah']
        # Cek ketersediaan populasi di tahun terpilih
        if tahun_pilihan in df.columns:
            populasi = row[tahun_pilihan]
            
            # Cek apakah koordinat ada dan data populasi valid (bukan NaN)
            if wilayah in KOORDINAT_SUMBAR and pd.notna(populasi):
                populasi_int = int(populasi)
                
                # Skala bubble agar pas di peta
                radius_bubble = populasi_int / 30000 
                
                folium.CircleMarker(
                    location=KOORDINAT_SUMBAR[wilayah],
                    radius=radius_bubble,
                    popup=f"<b>{wilayah}</b><br>Tahun {tahun_pilihan}: {populasi_int:,} jiwa",
                    tooltip=wilayah,
                    color="#FF4B4B", # Warna merah ala Streamlit
                    fill=True,
                    fill_color="#FF4B4B",
                    fill_opacity=0.6
                ).add_to(m)

    # Render map Leaflet
    st_folium(m, width=800, height=500)
