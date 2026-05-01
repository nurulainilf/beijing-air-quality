import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
import os

# Setup Page & Style
st.set_page_config(page_title="Beijing Air Quality Dashboard", layout="wide")
sns.set_style("whitegrid")

@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "main_data.csv")
    df = pd.read_csv(file_path)
    df['date'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    return df

# Initialize Data
all_df = load_data()

# --- SIDEBAR ---
with st.sidebar:
    st.title("Air Quality Analysis")
    st.image("https://asiasociety.org/sites/default/files/styles/1200w/public/1/101123_beijing_air.jpg") 
    
    st.markdown("### Profil Penulis")
    st.write(f"**Nama:** Nurul Ainil Fitri")
    st.divider()
    
    st.markdown("### Filter Analisis")

    # Filter Tahun Aotizhongxin
    year_aoti = st.selectbox(
        "Pilih Tahun Analisis Aotizhongxin:", 
        options=sorted(all_df['year'].unique()), 
        index=1 # Default 2014
    )

    # Filter Tahun Wanliu
    selected_year = st.selectbox(
        "Pilih Tahun Analisis Wanliu:", 
        options=sorted(all_df['year'].unique()), 
        index=3 # Default 2016
    )

# --- MAIN PAGE ---
st.title("📊 Beijing Air Quality Dashboard")
st.markdown("Analisis Karakteristik Udara Aotizhongxin dan Korelasi Meteorologi di Wanliu.")

# Metrics Section
main_df = all_df.copy()

col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric("Total Observasi", f"{len(main_df):,}")
with col_m2:
    avg_pm = main_df['PM2.5'].mean()
    st.metric("Avg PM2.5 (Keseluruhan)", f"{avg_pm:.2f} µg/m³" if not pd.isna(avg_pm) else "0.00")
with col_m3:
    st.metric("Lokasi Fokus", "Aotizhongxin & Wanliu")

st.divider()

# --- BAGIAN 1: KARAKTERISTIK AOTIZHONGXIN ---
st.header(f"1. Karakteristik PM2.5 di Aotizhongxin Musim Dingin (Tahun {year_aoti})")

winter_months = [11, 12, 1, 2]
aoti_winter = all_df[
    (all_df['station'] == 'Aotizhongxin') & 
    (all_df['year'].isin([year_aoti - 1, year_aoti, year_aoti + 1])) & 
    (all_df['month'].isin(winter_months))
].copy()

# Fungsi label dinamis berdasarkan tahun yang dipilih
def get_winter_label(row, selected_year):
    # Periode 1: Tahun Sebelumnya - Tahun Terpilih
    if (row['year'] == selected_year - 1 and row['month'] >= 11) or (row['year'] == selected_year and row['month'] <= 2):
        return f'Winter {selected_year-1}-{selected_year}'
    # Periode 2: Tahun Terpilih - Tahun Sesudahnya
    elif (row['year'] == selected_year and row['month'] >= 11) or (row['year'] == selected_year + 1 and row['month'] <= 2):
        return f'Winter {selected_year}-{selected_year+1}'
    return None

# Terapkan fungsi dengan parameter year_aoti
aoti_winter['winter_period'] = aoti_winter.apply(get_winter_label, axis=1, args=(year_aoti,))
aoti_winter_clean = aoti_winter.dropna(subset=['winter_period'])

if not aoti_winter_clean.empty:
    winter_avg = aoti_winter_clean.groupby('winter_period')['PM2.5'].mean().reset_index()
    
    winter_avg = winter_avg.sort_values('winter_period')
    
    c1, c2 = st.columns([2, 1])
    with c1:
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=winter_avg, x='winter_period', y='PM2.5', palette='coolwarm', ax=ax)
        
        for p in ax.patches:
            ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()),
                        ha='center', va='center', xytext=(0, 9), textcoords='offset points')
                       
        ax.set_title(f"Perbandingan Rata-rata PM2.5 Musim Dingin Sekitar {year_aoti}")
        ax.set_ylim(0, winter_avg['PM2.5'].max() + 50)
        st.pyplot(fig)
        st.caption(f"> **Keterangan:** Menampilkan perbandingan musim dingin periode {year_aoti-1}/{year_aoti} dan {year_aoti}/{year_aoti+1}.")

    with c2:
        st.write(f"**Rata-rata Periode:**")
        for index, row in winter_avg.iterrows():
            st.write(f"- {row['winter_period']}: **{row['PM2.5']:.2f} µg/m³**")
        
        if len(winter_avg) == 2:
            val1 = winter_avg.iloc[0]['PM2.5']
            val2 = winter_avg.iloc[1]['PM2.5']
            diff = ((val2 - val1) / val1) * 100
            kondisi = "kenaikan" if diff > 0 else "penurunan"
            st.info(f"Terjadi {kondisi} konsentrasi sebesar ~{abs(diff):.1f}% antara kedua periode.")
else:
    st.warning(f"Data perbandingan untuk tahun {year_aoti} tidak mencukupi.")


# --- BAGIAN 2: ANALISIS WANLIU ---
st.header(f"2. Faktor Meteorologi di Stasiun Wanliu ({selected_year})")

# Filter berdasarkan input selected_year
wanliu_year = all_df[(all_df['station'] == 'Wanliu') & (all_df['year'] == selected_year)].copy()

tab1, tab2, tab3, tab4 = st.tabs(["Matriks Korelasi", "Distribusi Bulanan PM2.5", "Korelasi Angin (WSPM)", "Kategori Kualitas Udara"])

with tab1:
    st.subheader("Matriks Korelasi PM2.5 vs Faktor Meteorologi")
    
    # Filter kolom numerik
    cols_corr = ['PM2.5', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
    correlation_matrix = wanliu_year[cols_corr].corr()
    
    # Membuat plot
    fig_corr, ax_corr = plt.subplots(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap='RdYlGn', center=0, ax=ax_corr)
    st.pyplot(fig_corr)
    
    # Mengambil nilai korelasi secara dinamis
    wspm_corr = correlation_matrix.loc['PM2.5', 'WSPM']
    temp_corr = correlation_matrix.loc['PM2.5', 'TEMP']
    
    # Menentukan variabel mana yang paling berpengaruh (berdasarkan nilai absolut korelasi)
    # Kita bandingkan nilai korelasi PM2.5 terhadap faktor lainnya
    top_corr_factor = correlation_matrix['PM2.5'].drop('PM2.5').abs().idxmax()
    top_corr_value = correlation_matrix.loc['PM2.5', top_corr_factor]

    # Menampilkan Insight Dinamis
    st.markdown(f"""
    **Insight:**
    * **Faktor Dominan:** Berdasarkan data tahun {selected_year}, faktor meteorologi yang memiliki hubungan paling kuat dengan konsentrasi PM2.5 adalah **{top_corr_factor}** dengan koefisien korelasi sebesar **{top_corr_value:.2f}**.
    * **Analisis Kecepatan Angin (WSPM):** Kecepatan angin menunjukkan korelasi sebesar **{wspm_corr:.2f}**. Nilai negatif ini mengindikasikan hubungan terbalik, di mana setiap peningkatan kecepatan angin cenderung membantu proses dispersi (penyebaran) polutan, sehingga konsentrasi PM2.5 di permukaan menurun.
    * **Variabel Lain:** Suhu (TEMP) memiliki korelasi sebesar **{temp_corr:.2f}**. Secara keseluruhan, hasil ini menunjukkan bahwa faktor cuaca memang memengaruhi kualitas udara, namun sifatnya kompleks dan dipengaruhi oleh berbagai variabel secara simultan.
    """)

with tab2:
    st.subheader("Distribusi PM2.5 per Bulan")
    
    # Inisialisasi Plot
    fig3, ax3 = plt.subplots(figsize=(12, 6))
    sns.boxplot(x='month', y='PM2.5', data=wanliu_year, palette='viridis', ax=ax3)
    ax3.axhline(150, color='red', linestyle='--', label='Ambang Batas Unhealthy (150 µg/m³)')
    ax3.legend()
    st.pyplot(fig3)

    # --- PERHITUNGAN DINAMIS UNTUK INSIGHT ---
    # 1. Mencari bulan dengan median PM2.5 tertinggi
    monthly_stats = wanliu_year.groupby('month')['PM2.5'].median()
    max_median_month = monthly_stats.idxmax()
    max_median_value = monthly_stats.max()

    # 2. Mencari nilai pencilan (outlier) tertinggi
    max_outlier = wanliu_year['PM2.5'].max()

    # 3. Menghitung persentase data di atas ambang batas (150)
    above_threshold = (wanliu_year['PM2.5'] > 150).mean() * 100

    st.markdown(f"""
    **Insight:**
    * **Variabilitas Polusi Akhir Tahun:** Berdasarkan data tahun {selected_year}, bulan **{max_median_month}** menunjukkan tingkat polusi tertinggi dengan nilai median sebesar **{max_median_value:.2f} $\mu g/m^3$**. Rentang antarkuartil (*interquartile range*) yang lebar pada akhir tahun mengindikasikan variabilitas polusi yang sangat tinggi.
    * **Identifikasi Outlier Ekstrem:** Terdeteksi lonjakan konsentrasi ekstrem (outlier) hingga mencapai **{max_outlier:.2f} $\mu g/m^3$**. Hal ini mengonfirmasi adanya anomali polusi udara berat pada jam-jam tertentu yang melampaui kondisi normal bulanan.
    * **Analisis Ambang Batas:** Secara keseluruhan di tahun {selected_year}, sebanyak **{above_threshold:.1f}%** dari total waktu pemantauan berada di atas ambang batas 150 $\mu g/m^3$.
    * **Stabilitas Musim Panas:** Sebaran data pada pertengahan tahun cenderung lebih stabil dan berada di bawah garis merah, memvalidasi bahwa kondisi meteorologi musim panas lebih efektif dalam mendispersi polutan.
    * **Catatan Standar:** Garis ambang batas 150 $\mu g/m^3$ merujuk pada standar kategori **'Unhealthy'** menurut US-EPA Air Quality Index (AQI).
    """)

with tab3:
    st.subheader("Hubungan PM2.5 dengan Kecepatan Angin")
    
    # Menghitung korelasi secara dinamis
    corr_val = wanliu_year[['PM2.5', 'WSPM']].corr().iloc[0,1]
    
    # Agregasi bulanan
    monthly_trend = wanliu_year.groupby('month').agg({'PM2.5':'mean', 'WSPM':'mean'}).reset_index()
    
    # Visualisasi
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    ax2_twin = ax2.twinx()
    
    sns.lineplot(data=monthly_trend, x='month', y='PM2.5', marker='o', color='red', label='PM2.5', ax=ax2)
    sns.lineplot(data=monthly_trend, x='month', y='WSPM', marker='s', color='blue', label='Angin (WSPM)', ax=ax2_twin)
    
    ax2.set_ylabel("PM2.5 (µg/m³)", color='red')
    ax2_twin.set_ylabel("WSPM (m/s)", color='blue')
    ax2.set_title(f"Tren PM2.5 vs Kecepatan Angin - Tahun {selected_year}")
    
    st.pyplot(fig2)

    # --- LOGIKA INSIGHT DINAMIS ---
    # Mencari bulan dengan kecepatan angin terendah
    min_wind_month = monthly_trend.loc[monthly_trend['WSPM'].idxmin(), 'month']
    min_wind_value = monthly_trend['WSPM'].min()
    
    # Mencari bulan dengan polusi tertinggi untuk dikaitkan dengan angin
    max_pm_month = monthly_trend.loc[monthly_trend['PM2.5'].idxmax(), 'month']
    
    # Menentukan kekuatan korelasi secara deskriptif
    strength = "lemah" if abs(corr_val) < 0.3 else "sedang" if abs(corr_val) < 0.7 else "kuat"

    st.markdown(f"""
    **Insight:**
    * **Analisis Korelasi:** Koefisien korelasi sebesar **{corr_val:.2f}** menunjukkan adanya hubungan negatif yang **{strength}** antara kecepatan angin dan konsentrasi polutan.
    * **Pola Musiman:** Terlihat pola di mana peningkatan kecepatan angin (WSPM) cenderung diikuti dengan penurunan konsentrasi PM2.5. Hal ini mengonfirmasi peran angin sebagai agen pembersih polutan (*pollutant dispersion*).
    * **Titik Kritis:** Pada tahun {selected_year}, kecepatan angin terendah rata-rata terjadi di bulan **{int(min_wind_month)}** ({min_wind_value:.2f} m/s). Kondisi udara yang tenang (*stagnant air*) ini berisiko tinggi memicu penumpukan polutan karena minimnya sirkulasi udara di permukaan.
    * **Korelasi Visual:** Puncak polusi tertinggi di bulan **{int(max_pm_month)}** tampak bertepatan dengan periode di mana kecepatan angin berada pada level rendah/menurun, memperkuat hipotesis bahwa faktor meteorologi lokal sangat memengaruhi kualitas udara di Wanliu.
    """)

with tab4:
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

    # --- LOGIKA INSIGHT DINAMIS ---
    # Mencari kategori yang paling dominan
    most_common_cat = cat_counts.idxmax()
    most_common_pct = (cat_counts.max() / cat_counts.sum()) * 100
    
    # Menghitung total jam dalam kondisi tidak sehat (Tidak Sehat + Sangat Berbahaya)
    unhealthy_total_pct = ((cat_counts['Tidak Sehat'] + cat_counts['Sangat Berbahaya']) / cat_counts.sum()) * 100

    st.markdown(f"""
    **Insight:**
    * **Dominansi Kualitas Udara:** Pada tahun {selected_year}, kualitas udara di stasiun Wanliu paling sering berada pada kategori **{most_common_cat}** dengan proporsi mencapai **{most_common_pct:.1f}%** dari total waktu pemantauan.
    * **Paparan Risiko Kesehatan:** Perlu menjadi perhatian bahwa akumulasi kategori 'Tidak Sehat' dan 'Sangat Berbahaya' mencapai **{unhealthy_total_pct:.1f}%**. Hal ini menunjukkan bahwa masyarakat masih sering terpapar polusi udara yang melampaui ambang batas aman kesehatan.
    * **Efektivitas Standar:** Penggunaan kategorisasi berdasarkan standar **US-EPA AQI** memberikan gambaran yang lebih praktis bagi pengambilan kebijakan terkait peringatan kesehatan publik (*public health advisory*) pada hari-hari dengan polusi tinggi.
    """)

st.divider()
st.caption(f"Copyright © 2026 | Nurul Ainil Fitri | Data Source: Air Quality Dataset")
