# Bike Sharing Dashboard ✨

Proyek akhir kelas **Belajar Analisis Data dengan Python** (Dicoding).
Dashboard interaktif untuk menjelajahi pola penyewaan sepeda **Capital Bikeshare (Washington D.C.) tahun 2011–2012**.

## Pertanyaan Bisnis
1. Berapa rata-rata penyewaan sepeda per hari pada setiap musim dan kondisi cuaca (2011–2012), dan berapa persen selisih kondisi tertinggi vs terendah?
2. Pada jam berapa puncak penyewaan terjadi pada hari kerja dibandingkan akhir pekan/libur (2011–2012), dan berapa rata-ratanya?
3. Berapa pertumbuhan penyewaan 2012 dibanding 2011 (YoY), dan pada bulan apa pertumbuhan serta puncak terjadi?

## Struktur Proyek
```
submission
├───dashboard
│   ├───main_data.csv      # data per jam yang sudah dibersihkan (hasil notebook)
│   └───dashboard.py       # aplikasi Streamlit
├───data
│   ├───day.csv            # data mentah harian
│   ├───hour.csv           # data mentah per jam
│   └───Readme.txt         # keterangan dataset asli
├───notebook.ipynb         # proses analisis data lengkap
├───README.md
├───requirements.txt
└───url.txt                # tautan dashboard di Streamlit Cloud
```

## Setup Environment - Anaconda

```
conda create --name main-ds python=3.10
conda activate main-ds
pip install -r requirements.txt
```

## Setup Environment - Shell/Terminal

```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```

## Run Streamlit App

Dari folder utama proyek:

```
streamlit run dashboard/dashboard.py
```

atau masuk ke folder `dashboard` terlebih dahulu:

```
cd dashboard
streamlit run dashboard.py
```

Aplikasi akan terbuka di `http://localhost:8501`.

## Deploy ke Streamlit Community Cloud
1. Upload folder proyek ke repository GitHub (pastikan `requirements.txt`, `dashboard/dashboard.py`, dan `dashboard/main_data.csv` ikut ter-upload).
2. Buka [share.streamlit.io](https://share.streamlit.io), pilih repository, lalu isi *Main file path* dengan `dashboard/dashboard.py`.
3. Salin tautan aplikasi ke berkas `url.txt`.

## Fitur Dashboard
- Filter rentang tanggal, musim, dan tipe hari (hari kerja / akhir pekan-libur).
- Ringkasan KPI: total penyewaan, rata-rata per hari, persentase pengguna terdaftar, dan jam puncak.
- Tab visualisasi: pertumbuhan bulanan (YoY), musim & cuaca, pola per jam, analisis lanjutan (binning suhu dan segmentasi permintaan), serta kesimpulan & rekomendasi.

## Menjalankan Ulang Notebook
Buka `notebook.ipynb` dari **folder utama proyek** (agar path `data/day.csv` dan `dashboard/main_data.csv` terbaca), lalu pilih *Run All*. Sel terakhir pada bagian Cleaning Data akan membuat ulang `dashboard/main_data.csv`.

## Sumber Data
Fanaee-T, Hadi, and Gama, Joao, "Event labeling combining ensemble detectors and background knowledge", *Progress in Artificial Intelligence* (2013): pp. 1-15, Springer Berlin Heidelberg, doi:10.1007/s13748-013-0040-3.
