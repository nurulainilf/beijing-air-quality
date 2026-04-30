# Beijing Air Quality Analysis Dashboard 📊

## Deskripsi
ashboard ini dikembangkan untuk melakukan analisis mendalam mengenai karakteristik kualitas udara di dua stasiun pemantauan strategis di Beijing, yaitu **Aotizhongxin** dan **Wanliu**. Proyek ini mengevaluasi tren polusi musiman serta mengidentifikasi faktor meteorologi dominan yang memengaruhi fluktuasi konsentrasi PM2.5 menggunakan pendekatan data-driven.

## Struktur Direktori
- **dashboard/**: Berisi file utama aplikasi Streamlit (dashboard.py) dan dataset yang telah dibersihkan (main_data.csv).
- **data/**: Berisi dataset mentah (raw data) dalam format .csv.
- **notebook.ipynb**: File Jupyter Notebook untuk proses data wrangling, EDA, hingga visualisasi.
- **requirements.txt**: Daftar library Python yang dibutuhkan.
- **url.txt**: Link dashboard yang telah di-deploy ke Streamlit Cloud.

## Instalasi
1. Clone repository ini atau download folder submission.
2. Pastikan Python sudah terinstal di sistem Anda.
3. Instal library yang dibutuhkan dengan menjalankan perintah berikut di terminal:

pip install -r requirements.txt

## Menjalankan Dashboard
Untuk menjalankan dashboard secara lokal, silakan jalankan perintah berikut di terminal:

streamlit run dashboard/dashboard.py

## Analisis yang Tersedia
1. **Analisis Karakteristik Aotizhongxin**: Mengevaluasi perbandingan karakteristik kualitas udara pada periode musim dingin (2014/2015 vs 2015/2016) untuk melihat tren peningkatan konsentrasi dan variabilitas polutan PM2.5.
2. **Korelasi Meteorologi Wanliu**: Mengidentifikasi pengaruh variabel cuaca, terutama Kecepatan Angin (WSPM), terhadap pola penumpukan polutan di wilayah Wanliu menggunakan matriks korelasi dan analisis tren temporal.
3. **Kategori Kualitas Udara**: Visualisasi distribusi bulanan menggunakan box plot serta pengelompokkan status kualitas udara berdasarkan standar internasional US-EPA Air Quality Index.

---
**Author:** Nurul Ainil Fitri
**Email:** nurulainilf@gmail.com
**ID Dicoding:** nurulainilf