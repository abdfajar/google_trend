import streamlit as st
from pytrends.request import TrendReq
import pandas as pd
from io import BytesIO

# Konfigurasi halaman Streamlit
st.set_page_config(page_title="Google Trends Regional", layout="wide")
st.title("📈 Google Trends Regional Indonesia")

# Inisialisasi pytrends
pytrends = TrendReq(hl='id', tz=360)

# =====================
# Data wilayah (geo code)
# =====================
wilayah = {
    "Nasional": "",
    "Sumatera": {
        "Aceh": "ID-AC", "Sumatera Utara": "ID-SU", "Sumatera Barat": "ID-SB",
        "Riau": "ID-RI", "Kepulauan Riau": "ID-KR", "Jambi": "ID-JA",
        "Sumatera Selatan": "ID-SS", "Bangka Belitung": "ID-BB", "Lampung": "ID-LA"
    },
    "Jawa": {
        "Jakarta": "ID-JK", "Jawa Barat": "ID-JB", "Banten": "ID-BT",
        "Jawa Tengah": "ID-JT", "DI Yogyakarta": "ID-YO", "Jawa Timur": "ID-JI"
    },
    "Kalimantan": {
        "Kalimantan Barat": "ID-KB", "Kalimantan Tengah": "ID-KT",
        "Kalimantan Selatan": "ID-KS", "Kalimantan Timur": "ID-KI",
        "Kalimantan Utara": "ID-KU"
    },
    "Sulawesi": {
        "Sulawesi Utara": "ID-SA", "Sulawesi Tengah": "ID-ST",
        "Sulawesi Selatan": "ID-SN", "Sulawesi Tenggara": "ID-SG",
        "Gorontalo": "ID-GO", "Sulawesi Barat": "ID-SR"
    },
    "Bali dan Nusa Tenggara": {
        "Bali": "ID-BA", "NTB": "ID-NB", "NTT": "ID-NT"
    },
    "Maluku dan Papua": {
        "Maluku": "ID-MA", "Maluku Utara": "ID-MU", "Papua": "ID-PA", "Papua Barat": "ID-PB"
    }
}

# =====================
# PILIH LOKASI
# =====================
pulau = st.sidebar.selectbox("🗺️ Pilih Pulau/Wilayah", list(wilayah.keys()))
geo_code = ""

if pulau == "Nasional":
    lokasi = "Indonesia"
    geo_code = ""
else:
    provinsi = st.sidebar.selectbox("🏛️ Pilih Provinsi", list(wilayah[pulau].keys()))
    geo_code = wilayah[pulau][provinsi]
    lokasi = provinsi

# =====================
# PILIH MENU
# =====================
menu = st.sidebar.radio("📌 Pilih Jenis Data", ["Trending Topics", "Interest Over Time", "Related Topics"])

# Fungsi untuk ekspor ke CSV
def download_csv(df, filename):
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download CSV",
        data=csv,
        file_name=filename,
        mime='text/csv'
    )

# =====================
# TRENDING TOPICS
# =====================
if menu == "Trending Topics":
    st.header(f"🔥 Trending Pencarian di {lokasi}")
    if geo_code == "":
        trending = pytrends.trending_searches(pn='indonesia')
        st.dataframe(trending, use_container_width=True)
        download_csv(trending.rename(columns={0: "Topik"}), f"trending_{lokasi.lower()}.csv")
    else:
        st.info("Google Trends belum menyediakan fitur real-time trending untuk provinsi. Coba gunakan menu 'Interest Over Time'.")

# =====================
# INTEREST OVER TIME
# =====================
elif menu == "Interest Over Time":
    st.header(f"📊 Minat Pencarian - {lokasi}")
    keyword_input = st.text_input("Masukkan kata kunci (pisahkan dengan koma):", value="Pemilu, IKN, Smart City")

    if keyword_input:
        keywords = [kw.strip() for kw in keyword_input.split(',')]
        pytrends.build_payload(keywords, geo=geo_code, timeframe='now 7-d')
        data = pytrends.interest_over_time()

        if not data.empty:
            st.line_chart(data[keywords])
            st.dataframe(data.reset_index(), use_container_width=True)
            download_csv(data.reset_index(), f"trend_{lokasi.lower()}.csv")
        else:
            st.warning("Data tidak ditemukan. Coba kata kunci atau lokasi lain.")

# =====================
# RELATED TOPICS
# =====================
elif menu == "Related Topics":
    st.header(f"🔎 Topik Terkait - {lokasi}")
    keyword = st.text_input("Masukkan satu kata kunci utama:", value="Pemilu")

    if keyword:
        pytrends.build_payload([keyword], geo=geo_code, timeframe='now 7-d')
        related = pytrends.related_queries()

        if related.get(keyword) and related[keyword]['rising'] is not None:
            df_rising = related[keyword]['rising']
            st.dataframe(df_rising, use_container_width=True)
            download_csv(df_rising, f"related_topics_{keyword.lower()}_{lokasi.lower()}.csv")
        else:
            st.info("Tidak ada data topik naik daun untuk kata kunci ini.")

# Footer
st.markdown("---")
st.caption("Dibuat dengan ❤️ menggunakan Streamlit dan Pytrends")
