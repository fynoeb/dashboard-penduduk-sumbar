import streamlit as st
import pandas as pd

# Konfigurasi Halaman
st.set_page_config(page_title="Dashboard Penduduk Sumbar", layout="wide")

# Fungsi untuk memuat dan membersihkan data Excel
@st.cache_data
def load_data():
    file_name = 'Perkembangan Penduduk Sumatera Barat.xlsx'
    df = pd.read_excel(file_name, sheet_name='Data 1', header=2)
    df.rename(columns={'Unnamed: 0': 'Wilayah'}, inplace=True)
    df = df.dropna(subset=['Wilayah'])
    return df

df = load_data()

st.sidebar.title("Navigasi")
halaman = st.sidebar.radio("Pilih Halaman:", ["Overview Dataset", "Analisis Trend Tahunan"])

if halaman == "Overview Dataset":
    st.title("Data Penduduk Sumatera Barat")
    st.write("Eksplorasi data mentah perkembangan penduduk dari file Excel.")
    st.dataframe(df, use_container_width=True)

elif halaman == "Analisis Trend Tahunan":
    st.title("Trend Penduduk per Wilayah")
    wilayah_pilihan = st.selectbox("Pilih Kabupaten/Kota:", df['Wilayah'].unique())
    df_filter = df[df['Wilayah'] == wilayah_pilihan]
    tahun_kolom = [col for col in df.columns if isinstance(col, (int, float))]
    tahun_kolom.sort()
    
    chart_data = pd.DataFrame({
        'Tahun': tahun_kolom,
        'Populasi': df_filter[tahun_kolom].values[0]
    })
    
    chart_data['Populasi'] = pd.to_numeric(chart_data['Populasi'], errors='coerce')
    chart_data = chart_data.dropna()
    
    st.write(f"### Grafik Pertumbuhan: **{wilayah_pilihan}**")
    st.line_chart(data=chart_data, x='Tahun', y='Populasi')
