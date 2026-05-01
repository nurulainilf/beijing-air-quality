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
    # Pastikan kolom date untuk filter global
    df['date'] = pd.to_datetime(df[['year', 'month', 'day', 'hour']])
    return df

# Initialize Data
all_df = load_data()

# --- SIDEBAR (GLOBAL FILTER) ---
with st.sidebar:
    st.title("Air Quality Analysis")
    st.image("https://asiasociety.org/sites/default/files/styles/1200w/public/1/101123_beijing_air.jpg") 
    
    st.markdown("### Profil Penulis")
    st.write(f"**Nama:** Nurul Ainil Fitri")
    st.divider()
    
    st.markdown("### Filter Global")
    
    # Filter 1: Rentang Waktu
    min_date = all_df["date"].min()
    max_date = all_df["date"].max()
    start_date, end_date = st.date_input(
        label='Rentang Waktu:',
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )
    
    # Filter 2: Pilih Stasiun (Hanya 2 stasiun target)
    target_stations = ["Aotizhongxin", "Wanliu"]
    selected_stations = st.multiselect(
        label="Pilih Stasiun Fokus:",
        options=target_stations,
        default=target_stations
    )

# --- LOGIKA FILTERING ---
main_df = all_df[
    (all_df["date"] >= pd.to_datetime(start_date)) & 
    (all_df["date"] <= pd.to_datetime(end_date)) &
    (all_df["station"].isin(selected_stations))
]

# --- MAIN PAGE ---
st.title("📊 Air Quality Dashboard: Aotizhongxin vs Wanliu")

if not selected_stations:
    st.warning("⚠️ Silakan pilih minimal satu stasiun di sidebar.")
else:
    # Metrik Utama (Global)
    col_m1, col_m2, col_m3, col_m4 = st.columns([1, 1.5, 1, 1.2])
    with col_m1:
        st.metric("Total Observasi", f"{len(main_df):,}")
    with col_m2:
        avg_pm = main_df['PM2.5'].mean()
        st.metric("Avg PM2.5 (Gabungan)", f"{avg_pm:.2f} µg/m³" if not pd.isna(avg_pm) else "0.00")
    with col_m3:
        st.metric("Stasiun Aktif", len(selected_stations))
    with col_m4:
        st.metric("Rentang Hari", f"{(pd.to_datetime(end_date) - pd.to_datetime(start_date)).days} Hari")
        st.caption(f"Data dari {start_date} sampai {end_date}")

    st.divider()

    # --- GLOBAL VISUALIZATION (GABUNGAN) ---
    st.header("📈 Tren Kualitas Udara Gabungan")
    
    # Grafik Tren Bulanan Perbandingan
    # Otomatis menyesuaikan jumlah garis berdasarkan stasiun yang dipilih
    monthly_compare = main_df.groupby(['month', 'station'])['PM2.5'].mean().reset_index()
    
    fig_compare, ax_compare = plt.subplots(figsize=(12, 5))
    sns.lineplot(
        data=monthly_compare, 
        x='month', 
        y='PM2.5', 
        hue='station', 
        marker='o', 
        palette='Set1', 
        ax=ax_compare
    )
    ax_compare.set_title("Perbandingan Tren PM2.5 Bulanan")
    ax_compare.set_ylabel("Rata-rata PM2.5 (µg/m³)")
    ax_compare.set_xticks(range(1, 13))
    st.pyplot(fig_compare)

    # --- ANALISIS PER STASIUN (Hanya muncul jika dipilih) ---
    col_a, col_b = st.columns([1, 1])

    with col_a:
        if "Aotizhongxin" in selected_stations:
            st.subheader("📍 Aotizhongxin")
            aoti_data = main_df[main_df['station'] == 'Aotizhongxin']
            st.write(f"Rata-rata: **{aoti_data['PM2.5'].mean():.2f} µg/m³**")
        else:
            st.info("Analisis Aotizhongxin dinonaktifkan.")

    with col_b:
        if "Wanliu" in selected_stations:
            st.subheader("📍 Wanliu")
            wanliu_data = main_df[main_df['station'] == 'Wanliu']
            st.write(f"Rata-rata: **{wanliu_data['PM2.5'].mean():.2f} µg/m³**")
        else:
            st.info("Analisis Wanliu dinonaktifkan.")
    
    # --- LOGIKA INSIGHT DINAMIS ---
    # Hitung rata-rata per stasiun dari data yang sudah difilter
    station_stats = main_df.groupby('station')['PM2.5'].mean().sort_values(ascending=False)
    
    if len(station_stats) > 1:
        highest_stat = station_stats.index[0]
        highest_val = station_stats.values[0]
        lowest_stat = station_stats.index[1]
        lowest_val = station_stats.values[1]
        diff_val = highest_val - lowest_val
        
        insight_text = f"""
        **Insight Global:**
        * **Perbandingan Stasiun:** Berdasarkan rentang waktu yang dipilih, stasiun **{highest_stat}** memiliki rata-rata konsentrasi PM2.5 yang lebih tinggi (**{highest_val:.2f} µg/m³**) dibandingkan dengan **{lowest_stat}** (**{lowest_val:.2f} µg/m³**).
        * **Selisih Konsentrasi:** Terdapat selisih rata-rata sebesar **{diff_val:.2f} µg/m³** di antara kedua stasiun tersebut.
        * **Analisis Tren:** Jika pola garis pada grafik di atas saling mengikuti (berhimpitan), hal ini mengindikasikan bahwa fluktuasi kualitas udara lebih dipengaruhi oleh faktor regional Beijing secara luas dibandingkan aktivitas lokal di sekitar stasiun.
        """
    else:
        # Jika user cuma pilih 1 stasiun
        curr_stat = station_stats.index[0]
        curr_val = station_stats.values[0]
        insight_text = f"""
        **Insight Global:**
        * **Analisis Tunggal:** Saat ini dashboard hanya menampilkan data untuk stasiun **{curr_stat}** dengan rata-rata konsentrasi sebesar **{curr_val:.2f} µg/m³**.
        * Untuk melihat perbandingan kualitas udara antar wilayah, silakan pilih stasiun tambahan pada menu filter di sidebar.
        """

    st.markdown(insight_text)

    st.divider()

# --- BAGIAN 1: KARAKTERISTIK AOTIZHONGXIN ---
if "Aotizhongxin" in selected_stations:
    st.header("1. Karakteristik PM2.5 di Aotizhongxin (Musim Dingin)")
    
    winter_months = [11, 12, 1, 2]
    aoti_data = main_df[main_df['station'] == 'Aotizhongxin'].copy()
    
    # Fungsi label dinamis agar tidak hardcoded
    def get_winter_label(row):
        year = row['year']
        month = row['month']
        if month >= 11:
            return f"Winter {year}-{year+1}"
        elif month <= 2:
            return f"Winter {year-1}-{year}"
        return None

    aoti_data['winter_period'] = aoti_data.apply(get_winter_label, axis=1)
    aoti_winter_clean = aoti_data.dropna(subset=['winter_period'])

    if not aoti_winter_clean.empty:
        winter_avg = aoti_winter_clean.groupby('winter_period')['PM2.5'].mean().reset_index()
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(data=winter_avg, x='winter_period', y='PM2.5', palette='coolwarm', ax=ax)
        for p in ax.patches:
            ax.annotate(f'{p.get_height():.2f}', (p.get_x() + p.get_width() / 2., p.get_height()), ha='center')
        st.pyplot(fig)
        st.caption("> **Info:** Periode Winter dihitung dari November sampai Februari tahun berikutnya.")
    else:
        st.info("Pilih rentang waktu yang mencakup bulan November-Februari untuk melihat analisis musim dingin.")

# --- INSIGHT DINAMIS AOTIZHONGXIN ---
    if len(winter_avg) >= 2:
        # Mengambil dua periode terakhir untuk dibandingkan
        last_two = winter_avg.tail(2)
        p1_name, p2_name = last_two['winter_period'].values
        p1_val, p2_val = last_two['PM2.5'].values
        
        # Hitung selisih persen
        diff_pct = ((p2_val - p1_val) / p1_val) * 100
        status = "peningkatan" if diff_pct > 0 else "penurunan"
            
        st.markdown(f"""
        **Insight Aotizhongxin:**
        * **Perbandingan Periode:** Rata-rata konsentrasi PM2.5 berubah dari **{p1_val:.2f} µg/m³** pada {p1_name} menjadi **{p2_val:.2f} µg/m³** pada {p2_name}.
        * **Analisis Tren:** Terjadi **{status}** konsentrasi sebesar **{abs(diff_pct):.1f}%** jika dibandingkan dengan periode musim dingin sebelumnya. 
        * **Catatan Musiman:** Tingginya angka di musim dingin biasanya berkaitan dengan fenomena inversi suhu atau peningkatan aktivitas pemanas ruangan di wilayah utara.
        """)
    else:
        st.markdown(f"""
        **Insight Aotizhongxin:**
        * Saat ini hanya tersedia data untuk periode **{winter_avg.iloc[0]['winter_period']}** dengan rata-rata **{winter_avg.iloc[0]['PM2.5']:.2f} µg/m³**. 
        * Tambah rentang tahun pada filter untuk melihat perbandingan antar musim dingin.
        """)

# --- BAGIAN 2: ANALISIS WANLIU ---
if "Wanliu" in selected_stations:
    st.header("2. Analisis Kualitas Udara di Stasiun Wanliu")
    wanliu_df = main_df[main_df['station'] == 'Wanliu'].copy()

    if not wanliu_df.empty:
        # Variabel bantuan untuk teks periode
        periode_text = f"Periode: {start_date} s/d {end_date}"
        
        tabs = st.tabs(["Matriks Korelasi", "Distribusi PM2.5", "Korelasi Angin", "Kategori"])

        with tabs[0]:
            st.subheader("Matriks Korelasi Faktor Meteorologi")
            st.caption(f"📊 {periode_text}")
            
            # Hitung korelasi
            cols = ['PM2.5', 'TEMP', 'PRES', 'DEWP', 'RAIN', 'WSPM']
            corr_matrix = wanliu_df[cols].corr()
            
            # Plot Heatmap
            fig_corr, ax_corr = plt.subplots(figsize=(8, 6))
            sns.heatmap(corr_matrix, annot=True, fmt=".2f", cmap='RdYlGn', ax=ax_corr)
            ax_corr.set_title(f"Korelasi PM2.5 di Wanliu\n({periode_text})", fontsize=12)
            st.pyplot(fig_corr)
            
            # Perhitungan Insight Dinamis
            top_f = corr_matrix['PM2.5'].drop('PM2.5').abs().idxmax()
            top_corr_val = corr_matrix.loc['PM2.5', top_f]
            
            st.markdown(f"""
            **Insight Korelasi:**
            * Faktor meteorologi yang memiliki hubungan paling signifikan dengan PM2.5 adalah **{top_f}** dengan koefisien sebesar **{top_corr_val:.2f}**.
            * Nilai ini menunjukkan seberapa kuat perubahan faktor cuaca tersebut memengaruhi fluktuasi konsentrasi polutan di Wanliu pada rentang waktu terpilih.
            """)

        with tabs[1]:
            st.subheader("Distribusi PM2.5 per Bulan")
            st.caption(f"📅 {periode_text}")
            
            # Plot Boxplot
            fig_box, ax_box = plt.subplots(figsize=(10, 5))
            sns.boxplot(x='month', y='PM2.5', data=wanliu_df, palette='viridis', ax=ax_box)
            ax_box.axhline(150, color='red', linestyle='--', label='Ambang Batas Unhealthy')
            ax_box.set_title(f"Variabilitas Bulanan PM2.5\n{periode_text}")
            st.pyplot(fig_box)
            
            # Perhitungan Insight Dinamis
            highest_median_month = wanliu_df.groupby('month')['PM2.5'].median().idxmax()
            max_val_wanliu = wanliu_df['PM2.5'].max()
            
            st.markdown(f"""
            **Insight Distribusi:**
            * **Bulan Terpolusi:** Secara median, kualitas udara terburuk di stasiun Wanliu tercatat pada bulan ke-**{int(highest_median_month)}**.
            * **Nilai Ekstrem:** Terdeteksi lonjakan polusi (outlier) hingga **{max_val_wanliu:.2f} µg/m³**, yang mengindikasikan adanya anomali cuaca atau polusi lokal sesaat.
            """)

        with tabs[2]:
            st.subheader("Tren PM2.5 vs Kecepatan Angin (WSPM)")
            st.caption(f"📈 {periode_text}")
            
            # Agregasi data untuk tren
            trend = wanliu_df.groupby('month').agg({'PM2.5':'mean', 'WSPM':'mean'}).reset_index()
            
            # Plot Line Chart (Dual Axis)
            fig_t, ax1 = plt.subplots(figsize=(10, 5))
            ax2 = ax1.twinx()
            sns.lineplot(data=trend, x='month', y='PM2.5', color='red', marker='o', label='PM2.5', ax=ax1)
            sns.lineplot(data=trend, x='month', y='WSPM', color='blue', marker='s', label='Angin (WSPM)', ax=ax2)
            plt.title(f"Hubungan PM2.5 dan Kecepatan Angin\n{periode_text}")
            st.pyplot(fig_t)

            # Perhitungan Insight Dinamis
            wspm_pm_corr = wanliu_df[['PM2.5', 'WSPM']].corr().iloc[0,1]
            
            st.markdown(f"""
            **Insight Hubungan Angin:**
            * Koefisien korelasi antara kecepatan angin dan PM2.5 adalah **{wspm_pm_corr:.2f}**.
            * Korelasi negatif menunjukkan bahwa angin yang lebih kencang cenderung membantu menyebarkan polutan, sehingga menurunkan konsentrasi PM2.5 di permukaan.
            """)

        with tabs[3]:
            st.subheader("Kategori Kualitas Udara")
            st.caption(f"📊 Analisis Proporsi: {periode_text}")
            
            def cat_epa(v):
                if v <= 35: return 'Baik'
                elif v <= 75: return 'Sedang'
                elif v <= 150: return 'Tidak Sehat'
                else: return 'Sangat Berbahaya'
            
            wanliu_df['cat'] = wanliu_df['PM2.5'].apply(cat_epa)
            counts = wanliu_df['cat'].value_counts().reindex(['Baik', 'Sedang', 'Tidak Sehat', 'Sangat Berbahaya']).fillna(0)
            
            col1, col2 = st.columns(2)
            with col1:
                fig_p, ax_p = plt.subplots()
                ax_p.pie(counts, labels=counts.index, autopct='%1.1f%%', colors=['#4CAF50','#FFEB3B','#FF9800','#F44336'])
                ax_p.set_title(f"Proporsi Kategori PM2.5\nWanliu ({periode_text})")
                st.pyplot(fig_p)
            with col2:
                st.write("**Data Observasi:**")
                st.table(counts)
            
            # Perhitungan Insight 
            dom_cat = counts.idxmax()
            dom_pct = (counts.max() / counts.sum()) * 100
            
            st.markdown(f"""
            **Insight Kategori:**
            * Mayoritas kualitas udara di Wanliu berada pada kategori **{dom_cat}** (**{dom_pct:.1f}%**).
            * Ringkasan ini memberikan gambaran tingkat risiko kesehatan bagi penduduk di sekitar stasiun Wanliu selama periode observasi.
            """)
    else:
        st.info("Data Wanliu tidak tersedia dalam filter rentang waktu atau stasiun yang dipilih.")

st.divider()
st.caption(f"Copyright © 2026 | Nurul Ainil Fitri")
