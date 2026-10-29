import os

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st

st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")
sns.set_theme(style="white")

# Palet warna: biru tua = nilai tertinggi, biru muda = kategori lainnya, oranye hanya untuk membedakan garis
BASE, HIGHLIGHT, ACCENT = "#9DC3E6", "#1F4E79", "#E07B00"
SEASON_ORDER = ["Winter", "Spring", "Summer", "Fall"]
WEATHER_ORDER = ["Cerah", "Berkabut", "Hujan Ringan", "Hujan Lebat"]
DAY_TYPES = ["Hari Kerja", "Akhir Pekan/Libur"]
MONTHS = ["Jan", "Feb", "Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des"]
TEMP_LABELS = ["Dingin (<10°C)", "Sejuk (10–20°C)", "Hangat (20–30°C)", "Panas (≥30°C)"]


# --------------------------------------------------------------------------- Data
@st.cache_data
def load_data():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_data.csv")
    df = pd.read_csv(path, parse_dates=["date"])
    df["season"] = pd.Categorical(df["season"], categories=SEASON_ORDER, ordered=True)
    df["weather_day"] = pd.Categorical(df["weather_day"], categories=WEATHER_ORDER, ordered=True)
    return df


def build_daily(df):
    """Agregasi data per jam menjadi data per hari."""
    daily = (
        df.groupby("date")
        .agg(
            year=("year", "first"),
            month=("month", "first"),
            season=("season", "first"),
            day_type=("day_type", "first"),
            weather=("weather_day", "first"),
            temp_c=("temp_c", "mean"),
            casual=("casual", "sum"),
            registered=("registered", "sum"),
            cnt=("cnt", "sum"),
        )
        .reset_index()
    )
    daily["temp_group"] = pd.cut(daily["temp_c"], bins=[-np.inf, 10, 20, 30, np.inf], labels=TEMP_LABELS, right=False)
    return daily


def style_axes(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x:,.0f}"))


def bar_highlight(ax, labels, values, ylabel, title):
    """Bar chart: biru tua = tertinggi, biru muda = lainnya, sumbu y dimulai dari 0."""
    values = np.asarray(values, dtype=float)
    colors = [HIGHLIGHT if v == values.max() else BASE for v in values]
    bars = ax.bar(labels, values, color=colors, width=0.62)
    ax.bar_label(bars, labels=[f"{v:,.0f}" for v in values], padding=4, fontsize=10, fontweight="bold")
    ax.set_ylim(0, values.max() * 1.15)
    ax.set_ylabel(ylabel)
    ax.set_title(title, loc="left", fontsize=12, fontweight="bold")
    style_axes(ax)


# --------------------------------------------------------------------------- Sidebar (filter)
raw_df = load_data()

st.sidebar.title("🚲 Filter Data")
min_date, max_date = raw_df["date"].min().date(), raw_df["date"].max().date()
date_range = st.sidebar.date_input("Rentang tanggal", value=(min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(date_range, (tuple, list)):
    if len(date_range) != 2:
        st.sidebar.info("Pilih tanggal akhir untuk melengkapi rentang.")
        st.stop()
    start_date, end_date = date_range
else:
    start_date = end_date = date_range

seasons = st.sidebar.multiselect("Musim", SEASON_ORDER, default=SEASON_ORDER)
day_types = st.sidebar.multiselect("Tipe hari", DAY_TYPES, default=DAY_TYPES)
st.sidebar.caption("Data: Capital Bikeshare, Washington D.C. (2011–2012)")

main_df = raw_df[
    (raw_df["date"] >= pd.Timestamp(start_date))
    & (raw_df["date"] <= pd.Timestamp(end_date))
    & (raw_df["season"].isin(seasons))
    & (raw_df["day_type"].isin(day_types))
]
if main_df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih. Silakan ubah filter di sidebar.")
    st.stop()

daily_df = build_daily(main_df)

# --------------------------------------------------------------------------- Header & KPI
st.title("🚲 Bike Sharing Dashboard")
st.markdown(
    "Dashboard interaktif hasil analisis penyewaan sepeda **Capital Bikeshare (Washington D.C.)** tahun 2011–2012. "
    "Analisis ini membantu tim operator bike sharing menentukan **kapan armada harus ditambah, kapan promosi paling efektif, "
    "dan kapan pemeliharaan sebaiknya dilakukan**. Gunakan filter di sidebar untuk menjelajahi pola penyewaan."
)

hourly_all = main_df.groupby("hour")["cnt"].mean()
peak_hour = int(hourly_all.idxmax())
total_rent = int(daily_df["cnt"].sum())
registered_pct = daily_df["registered"].sum() / daily_df["cnt"].sum() * 100

k1, k2, k3, k4 = st.columns(4)
k1.metric("Total penyewaan", f"{total_rent:,}")
k2.metric("Rata-rata per hari", f"{daily_df['cnt'].mean():,.0f}")
k3.metric("Pengguna terdaftar", f"{registered_pct:.1f}%")
k4.metric("Jam puncak", f"{peak_hour:02d}:00", f"{hourly_all.max():,.0f} sewa/jam", delta_color="off")

tab_q1, tab_q2, tab_q3, tab_lanjutan, tab_kesimpulan = st.tabs(
    ["🌦️ Pertanyaan 1: Musim & Cuaca", "🕒 Pertanyaan 2: Pola per Jam", "📈 Pertanyaan 3: Pertumbuhan YoY",
     "🧭 Analisis Lanjutan", "💡 Kesimpulan & Rekomendasi"]
)

# --------------------------------------------------------------------------- Pertanyaan 1: musim & cuaca
with tab_q1:
    st.subheader("Pertanyaan 1")
    st.markdown("Berapa rata-rata jumlah penyewaan sepeda per hari pada setiap musim dan kondisi cuaca sepanjang tahun 2011–2012, serta berapa persen selisih antara kondisi dengan rata-rata tertinggi dan terendah?")
    season_mean = daily_df.groupby("season", observed=True)["cnt"].mean()
    weather_mean = daily_df.groupby("weather", observed=True)["cnt"].mean()
    weather_n = daily_df.groupby("weather", observed=True)["cnt"].size()

    fig, axes = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True, gridspec_kw={"width_ratios": [max(len(season_mean), 1), max(len(weather_mean), 1)]})
    bar_highlight(axes[0], season_mean.index.astype(str), season_mean.values, "Rata-rata penyewaan per hari", "Berdasarkan musim")
    bar_highlight(
        axes[1],
        [f"{w}\n(n = {n} hari)" for w, n in zip(weather_mean.index.astype(str), weather_n)],
        weather_mean.values, "", "Berdasarkan cuaca",
    )
    axes[0].set_ylim(0, max(season_mean.max(), weather_mean.max()) * 1.15)
    fig.text(0.01, -0.02, "Biru tua = tertinggi, biru muda = kategori lainnya. n = jumlah hari pengamatan.", fontsize=9, color="gray")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)

    if len(season_mean) > 1 and len(weather_mean) > 1:
        s_hi, s_lo = season_mean.idxmax(), season_mean.idxmin()
        w_hi, w_lo = weather_mean.idxmax(), weather_mean.idxmin()
        st.markdown(
            f"- **Musim:** {s_hi} tertinggi ({season_mean[s_hi]:,.0f}/hari), {s_lo} terendah ({season_mean[s_lo]:,.0f}/hari) "
            f"— selisih **{season_mean[s_hi] / season_mean[s_lo] - 1:.0%}**.\n"
            f"- **Cuaca:** {w_hi} tertinggi ({weather_mean[w_hi]:,.0f}/hari), {w_lo} terendah ({weather_mean[w_lo]:,.0f}/hari) "
            f"— {w_lo} **{1 - weather_mean[w_lo] / weather_mean[w_hi]:.0%} lebih rendah**."
        )
    st.caption("Catatan: kategori Hujan Ringan hanya terdiri dari sedikit hari, sehingga angkanya adalah indikasi, bukan nilai presisi.")

# --------------------------------------------------------------------------- Pertanyaan 2: pola jam
with tab_q2:
    st.subheader("Pertanyaan 2")
    st.markdown("Pada jam berapa puncak penyewaan sepeda terjadi pada hari kerja dibandingkan akhir pekan/hari libur sepanjang tahun 2011–2012, dan berapa rata-rata penyewaan per jam pada jam puncak tersebut?")
    hourly = main_df.groupby(["day_type", "hour"])["cnt"].mean().unstack(0)

    fig, ax = plt.subplots(figsize=(11, 4.8))
    line_colors = {"Hari Kerja": HIGHLIGHT, "Akhir Pekan/Libur": ACCENT}
    for tipe in hourly.columns:
        s = hourly[tipe].dropna()
        ax.plot(s.index, s.values, color=line_colors[tipe], lw=2.6, label=tipe)
        if tipe == "Hari Kerja" and s.index.min() < 12 <= s.index.max():
            peaks = [s[s.index < 12].idxmax(), s[s.index >= 12].idxmax()]
        else:
            peaks = [s.idxmax()]
        for h in peaks:
            ax.scatter(h, s[h], color=line_colors[tipe], s=60, zorder=3)
            ax.annotate(f"{h:02d}:00\n{s[h]:,.0f}", (h, s[h]), xytext=(0, 9), textcoords="offset points",
                        ha="center", fontsize=9, fontweight="bold", color=line_colors[tipe])
    ax.set_xticks(range(24))
    ax.set_xticklabels([f"{h:02d}" for h in range(24)], fontsize=9)
    ax.set_xlabel("Jam dalam sehari (00 = tengah malam)")
    ax.set_ylabel("Rata-rata penyewaan per jam")
    ax.set_ylim(0, np.nanmax(hourly.values) * 1.2)
    ax.legend(frameon=False, loc="upper left")
    ax.set_title("Rata-rata penyewaan per jam", loc="left", fontsize=12, fontweight="bold")
    style_axes(ax)
    st.pyplot(fig)
    plt.close(fig)

    user_mix = daily_df.groupby("day_type")[["casual", "registered", "cnt"]].mean()
    user_mix["casual_pct"] = user_mix["casual"] / user_mix["cnt"] * 100
    cols = st.columns(max(len(user_mix), 1))
    for col, (tipe, row) in zip(cols, user_mix.iterrows()):
        col.metric(f"Pengguna casual – {tipe}", f"{row['casual_pct']:.1f}%", f"{row['cnt']:,.0f} sewa/hari rata-rata", delta_color="off")
    st.caption("Hari kerja didominasi pengguna terdaftar (komuter); pengguna casual lebih banyak pada akhir pekan/libur.")

# --------------------------------------------------------------------------- Pertanyaan 3: pertumbuhan
with tab_q3:
    st.subheader("Pertanyaan 3")
    st.markdown("Berapa persen pertumbuhan total penyewaan sepeda tahun 2012 dibandingkan 2011 (Year-over-Year), dan pada bulan apa pertumbuhan tertinggi serta puncak penyewaan terjadi?")
    monthly = daily_df.groupby(["year", "month"])["cnt"].sum().unstack(0)

    fig, ax = plt.subplots(figsize=(10, 4.6))
    line_colors = {2011: BASE, 2012: HIGHLIGHT}
    for yr in monthly.columns:
        s = monthly[yr].dropna()
        ax.plot(s.index, s.values, color=line_colors.get(yr, BASE), lw=2.6, marker="o", label=str(yr))
        ax.text(s.index[-1] + 0.15, s.values[-1], str(yr), color=line_colors.get(yr, BASE),
                va="center", fontsize=11, fontweight="bold")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(MONTHS)
    ax.set_xlim(0.6, 12.9)
    ax.set_ylim(0, monthly.max().max() * 1.15)
    ax.yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f"{x / 1000:,.0f} rb"))
    ax.set_ylabel("Total penyewaan per bulan")
    ax.set_title("Total penyewaan per bulan", loc="left", fontsize=12, fontweight="bold")
    ax.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig)
    plt.close(fig)

    if {2011, 2012}.issubset(monthly.columns):
        common = monthly[[2011, 2012]].dropna()
        if len(common) > 0:
            growth = (common[2012] / common[2011] - 1) * 100
            total_growth = common[2012].sum() / common[2011].sum() - 1
            best = int(growth.idxmax())
            peak_m = int(monthly[2012].idxmax())
            c1, c2, c3 = st.columns(3)
            c1.metric("Pertumbuhan 2012 vs 2011", f"{total_growth:+.1%}", help="Dihitung pada bulan yang tersedia di kedua tahun.")
            c2.metric("Bulan pertumbuhan tertinggi", MONTHS[best - 1], f"{growth.max():+.0f}%")
            c3.metric("Bulan puncak 2012", MONTHS[peak_m - 1], f"{monthly[2012].max():,.0f} sewa", delta_color="off")
    else:
        st.info("Pilih rentang tanggal yang mencakup 2011 dan 2012 untuk melihat pertumbuhan year-over-year.")

# --------------------------------------------------------------------------- Analisis lanjutan
with tab_lanjutan:
    st.subheader("Clustering manual: kelompok suhu dan segmen permintaan")
    st.markdown(
        "- **Binning suhu** (`pd.cut`): mengelompokkan hari ke dalam 4 rentang suhu.\n"
        "- **Segmentasi permintaan** (`pd.qcut`): membagi seluruh hari (2011–2012) menjadi sepertiga *Rendah*, *Sedang*, *Tinggi*."
    )
    col_a, col_b = st.columns(2)

    with col_a:
        temp_stats = daily_df.groupby("temp_group", observed=True)["cnt"].agg(["mean", "size"])
        fig, ax = plt.subplots(figsize=(6, 4.6))
        bar_highlight(
            ax,
            [f"{k}\n(n = {n})" for k, n in zip(temp_stats.index.astype(str), temp_stats["size"])],
            temp_stats["mean"].values, "Rata-rata penyewaan per hari", "Penyewaan berdasarkan kelompok suhu",
        )
        ax.tick_params(axis="x", labelsize=8)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col_b:
        # Segmen dihitung dari seluruh hari agar batasnya tetap konsisten walau filter berubah
        full_daily = build_daily(raw_df)
        q1, q2 = full_daily["cnt"].quantile([1 / 3, 2 / 3])
        seg = pd.cut(daily_df["cnt"], bins=[-np.inf, q1, q2, np.inf], labels=["Rendah", "Sedang", "Tinggi"])
        komposisi = pd.crosstab(seg, daily_df["season"], normalize="index").reindex(
            index=["Rendah", "Sedang", "Tinggi"], columns=SEASON_ORDER).fillna(0) * 100
        fig, ax = plt.subplots(figsize=(6, 4.6))
        sns.heatmap(komposisi, annot=True, fmt=".0f", cmap="Blues", cbar=False, linewidths=1, linecolor="white",
                    annot_kws={"fontsize": 11, "fontweight": "bold"}, ax=ax, vmin=0, vmax=60)
        ax.set_xlabel("Musim")
        ax.set_ylabel("Segmen permintaan")
        ax.set_title("Komposisi musim tiap segmen (% hari)", loc="left", fontsize=12, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption(f"Batas segmen: Rendah < {q1:,.0f}; Sedang {q1:,.0f}–{q2:,.0f}; Tinggi > {q2:,.0f} penyewaan per hari.")

# --------------------------------------------------------------------------- Kesimpulan & rekomendasi
with tab_kesimpulan:
    st.subheader("Kesimpulan")
    st.markdown(
        "- **Kesimpulan Pertanyaan 1 (musim & cuaca):** penyewaan tertinggi saat **Summer (5.644/hari)** dan terendah saat **Winter (2.604/hari)**, "
        "selisih 117%. Hari **hujan ringan 63% lebih rendah** dibanding hari cerah, dan hari berkabut sekitar 17% lebih rendah.\n"
        "- **Kesimpulan Pertanyaan 2 (pola jam):** hari kerja punya dua puncak komuter pada **08:00 (473/jam)** dan **17:00 (524/jam)**; "
        "akhir pekan/libur satu puncak pada **13:00 (373/jam)**. Pengguna casual mencapai 31,7% pada akhir pekan/libur "
        "dibanding 13,2% pada hari kerja.\n"
        "- **Kesimpulan Pertanyaan 3 (pertumbuhan):** total penyewaan 2012 **tumbuh 64,9%** dibanding 2011, dengan puncak pada **September 2012 (218.573)**.\n"
        "- **Suhu:** penyewaan tertinggi pada suhu **20–30°C** (5.662/hari) dan paling rendah di bawah 10°C (1.678/hari)."
    )
    st.subheader("Rekomendasi Action Item")
    st.markdown(
        "1. **Redistribusi sepeda berbasis jam:** pastikan stok siap sebelum **07:00** dan **16:00** pada hari kerja.\n"
        "2. **Pemeliharaan terjadwal:** servis pada **00:00–05:00**, saat Winter, atau pada hari yang diprakirakan hujan.\n"
        "3. **Promo akhir pekan:** promo **11:00–17:00** dan paket konversi *casual → member*.\n"
        "4. **Promo musim sepi:** diskon atau langganan saat Winter dan hari berkabut.\n"
        "5. **Kapasitas armada:** tambah armada sebelum **Maret–Mei** dan siapkan kapasitas puncak **Mei–September**."
    )
    st.caption("Angka di atas adalah ringkasan seluruh periode 2011–2012 dan tidak berubah mengikuti filter di sidebar.")

st.divider()
st.caption("Sumber data: Fanaee-T & Gama (2013), Bike Sharing Dataset — Capital Bikeshare, Washington D.C. | Proyek Analisis Data Dicoding")
