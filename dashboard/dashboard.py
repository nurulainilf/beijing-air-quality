import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

# Setup Page & Style
st.set_page_config(page_title="Beijing Air Quality Dashboard", layout="wide")
sns.set_style("whitegrid")

@st.cache_data
def load_data():
    df = pd.read_csv("main_data.csv")
    df['date'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    return df

# Initialize Data
main_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("Air Quality Analysis")
    st.image("https://asiasociety.org/sites/default/files/styles/1200w/public/1/101123_beijing_air.jpg") 
    
    st.markdown("### Profil Penulis")
    st.write(f"**Nama:** Nurul Ainil Fitri")
    st.write(f"**Email:** nurulainilf@gmail.com")
    st.write(f"**ID Dicoding:** nurulainilf")

    st.divider()
    st.markdown("### Filter Analisis")
    selected_year = st.selectbox(
        "Pilih Tahun untuk Analisis Wanliu:", 
        options=sorted(main_df['year'].unique()), 
        index=3 # Default ke 2016
    )

# --- MAIN PAGE ---
st.title("📊 Beijing Air Quality Dashboard")
st.markdown("Analisis Karakteristik Udara Aotizhongxin dan Korelasi Meteorologi di Wanliu.")

# Metrics Section (Ganti ke rata-rata yang lebih umum atau dinamis)
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Total Observasi", f"{len(main_df):,}")
    st.caption("Data yang ditampilkan hanya 50% sampel data untuk optimalisasi performa di Streamlit Cloud.")
with col_m2:
    avg_pm = main_df['PM2.5'].mean()
    st.metric("Avg PM2.5 (Keseluruhan)", f"{avg_pm:.2f} µg/m³")
with col_m3:
    st.metric("Lokasi Fokus", "Aotizhongxin & Wanliu")

st.divider()

# --- BAGIAN 1: KARAKTERISTIK AOTIZHONGXIN ---
st.header("1. Karakteristik PM2.5 di Aotizhongxin (Musim Dingin)")

winter_months = [11, 12, 1, 2]
aoti_winter = main_df[(main_df['station'] == 'Aotizhongxin') & (main_df['month'].isin(winter_months))].copy()

def get_winter_label(row):
    if (row['year'] == 2014 and row['month'] >= 11) or (row['year'] == 2015 and row['month'] <= 2):
        return 'Winter 2014-2015'
    elif (row['year'] == 2015 and row['month'] >= 11) or (row['year'] == 2016 and row['month'] <= 2):
        return 'Winter 2015-2016'
    return None

aoti_winter['winter_period'] = aoti_winter.apply(get_winter_label, axis=1)
aoti_winter_clean = aoti_winter.dropna(subset=['winter_period'])
winter_avg = aoti_winter_clean.groupby('winter_period')['PM2.5'].mean().reset_index()

c1, c2 = st.columns([2, 1])

with c1:
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(data=winter_avg, x='winter_period', y='PM2.5', palette='coolwarm', ax=ax)
    
    # Menambahkan label angka
    for p in ax.patches:
        ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                    ha='center', va='center', xytext=(0, 9), textcoords='offset points')
                    
    ax.set_title("Perbandingan Rata-rata PM2.5 Musim Dingin")
    ax.set_ylim(0, 120)
    st.pyplot(fig)

with c2:
    st.warning("⚠️ Tren Menurun Tidak Terdeteksi")
    st.write(f"**Rata-rata Periode:**")
    st.write(f"- 2014/2015: **81.49 µg/m³**")
    st.write(f"- 2015/2016: **97.57 µg/m³**")
    st.info("Terjadi kenaikan konsentrasi sebesar ~19.7% pada periode kedua.")

# --- BAGIAN 2: ANALISIS WANLIU (INTERAKTIF) ---
st.header(f"2. Faktor Meteorologi di Stasiun Wanliu ({selected_year})")

wanliu_year = main_df[(main_df['station'] == 'Wanliu') & (main_df['year'] == selected_year)].copy()

tab1, tab2, tab3 = st.tabs(["Korelasi Angin (WSPM)", "Distribusi Bulanan", "Kategori Kualitas Udara"])

with tab1:
    st.subheader("Hubungan PM2.5 dengan Kecepatan Angin")
    # Menggunakan seluruh data tahun terpilih untuk korelasi
    corr_val = wanliu_year[['PM2.5', 'WSPM']].corr().iloc[0,1]
    
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    # Menggunakan agregasi bulanan untuk line chart agar tidak berantakan
    monthly_trend = wanliu_year.groupby('month').agg({'PM2.5':'mean', 'WSPM':'mean'}).reset_index()
    
    ax2_twin = ax2.twinx()
    sns.lineplot(data=monthly_trend, x='month', y='PM2.5', marker='o', color='red', label='PM2.5', ax=ax2)
    sns.lineplot(data=monthly_trend, x='month', y='WSPM', marker='s', color='blue', label='Angin (WSPM)', ax=ax2_twin)
    
    ax2.set_ylabel("PM2.5", color='red')
    ax2_twin.set_ylabel("WSPM", color='blue')
    st.pyplot(fig2)
    st.write(f"**Koefisien Korelasi:** {corr_val:.2f}")
    st.write("Insight: Kecepatan angin rendah di akhir tahun sering bertepatan dengan lonjakan PM2.5.")

with tab2:
    st.subheader("Distribusi PM2.5 per Bulan (Boxplot)")
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='month', y='PM2.5', data=wanliu_year, palette='viridis', ax=ax3)
    ax3.axhline(150, color='red', linestyle='--', label='Batas Unhealthy (EPA)')
    ax3.legend()
    st.pyplot(fig3)

with tab3:
    st.subheader("Proporsi Kategori Kualitas Udara")
    def categorize_epa(val):
        if val <= 35: return 'Baik'
        elif val <= 75: return 'Sedang'
        elif val <= 150: return 'Tidak Sehat'
        else: return 'Sangat Berbahaya'
    
    wanliu_year['category'] = wanliu_year['PM2.5'].apply(categorize_epa)
    cat_counts = wanliu_year['category'].value_counts()
    
    # Urutkan kategori agar konsisten di chart
    order = ['Baik', 'Sedang', 'Tidak Sehat', 'Sangat Berbahaya']
    cat_counts = cat_counts.reindex(order).fillna(0)
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        fig4, ax4 = plt.subplots()
        ax4.pie(cat_counts, labels=cat_counts.index, autopct='%1.1f%%', 
                colors=['#4CAF50', '#FFEB3B', '#FF9800', '#F44336'])
        st.pyplot(fig4)
    with col_p2:
        st.write("**Detail Jumlah Jam Pemantauan:**")
        st.table(cat_counts)

st.divider()
st.caption(f"Copyright © 2026 | Nurul Ainil Fitri | Data Source: Air Quality Dataset")
