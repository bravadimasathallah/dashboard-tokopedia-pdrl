"""
Dashboard Analisis Kesiapan Teknologi Pengguna Aplikasi Tokopedia
Kelompok 5 - Tema 10: Kesiapan Teknologi Pengguna
Mata Kuliah: Pemrograman dan Data Raya Lanjutan - FEB UNJ
Sumber data : database_tokopedia_pdrl.db (tabel_kuesioner & tabel_ulasan)
"""

import sqlite3
import base64
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# 1. KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(
    page_title="Dashboard Kesiapan Teknologi Pengguna - Tokopedia",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

DB_PATH = "database_tokopedia_pdrl.db"

# Palet warna brand Tokopedia (hijau) + warna pendukung
BRAND = "#03AC0E"
BRAND_DARK = "#027A0A"
ACCENT = "#2E86DE"
NEUTRAL_BG = "#0A3A20"
PLOT_COLORWAY = ["#03AC0E", "#2E86DE", "#F5A623", "#DD5555"]

# =========================================================
# 2. CUSTOM CSS - INI YANG BIKIN TAMPILAN "NAIK KELAS"
# =========================================================
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Poppins', sans-serif;
    }}

    /* Mengubah warna background utama menjadi gradasi hijau gelap */
    .stApp {{
        background: radial-gradient(circle at top, #0A3A20 0%, #051A0E 100%) !important;
    }}

    /* Membuat warna teks bawaan Streamlit menjadi terang agar kontras */
    .stApp p, .stApp span, .stApp label, .stApp h2, .stApp h3, .stApp caption {{
        color: #f0f0f0 !important;
    }}

    /* 3. Membuat BATANG HEADER TRANSPARAN (Menghilangkan kotak abu-abu headbar) */
    header {{
        background-color: transparent !important;
        background: transparent !important;
        box-shadow: none !important;
        border: none !important;
    }}

    /* 4. Memastikan semua ikon & tombol di header (Deploy, Menu, Panah) berwarna putih terang */
    header svg, header button, header p, [data-testid="stAppDeploy"] {{
        color: #ffffff !important;
    }}

    /* Menghilangkan garis hiasan warna-warni tipis di paling atas layar */
    [data-testid="stDecoration"] {{
        display: none !important;
    }}

    /* KPI CARD ABU-ABU ELEGAN */
    .metric-card {{
        background: #3A433F !important; /* Abu-abu gelap tona hijau forest */
        border-radius: 16px;
        padding: 1.1rem 1.3rem;
        border: 1px solid #505C57;      /* Border tipis agar berdimensi */
        box-shadow: 0 6px 24px rgba(0,0,0,0.4);
        height: 100%;
    }}
    .metric-card .icon {{
        font-size: 1.4rem;
        margin-bottom: 0.3rem;
    }}
    .metric-card .label {{
        font-size: 0.76rem;
        color: #CBD1CB !important;       /* Teks label abu-abu muda */
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}
    .metric-card .value {{
        font-size: 1.7rem;
        font-weight: 700;
        color: #ffffff !important;       /* Angka/Nilai menjadi putih terang */
        margin-top: 0.15rem;
    }}
    .metric-card div {{
        color: #f0f0f0 !important;
    }}

    .block-container {{
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1300px;
    }}

    /* Hero banner header */
    .hero {{
        background: linear-gradient(135deg, {BRAND} 0%, {BRAND_DARK} 100%);
        padding: 1.8rem 2.2rem;
        border-radius: 18px;
        color: white;
        margin-bottom: 1.6rem;
        box-shadow: 0 8px 24px rgba(3,172,14,0.25);
    }}
    .hero h1 {{
        margin: 0;
        font-size: 1.65rem;
        font-weight: 700;
        color: white !important;
    }}
    .hero p {{
        margin: 0.35rem 0 0 0;
        opacity: 0.92;
        font-size: 0.92rem;
        color: white !important;
    }}
    .hero-content {{
        display: flex;
        align-items: center;
        gap: 0.9rem;
    }}
    .hero-logo {{
        width: 46px;
        height: 46px;
        object-fit: contain;
        filter: drop-shadow(0 2px 6px rgba(0,0,0,0.3));
        flex-shrink: 0;
    }}
    
    /* Section title dengan garis aksen */
    .section-title {{
        font-size: 1.05rem;
        font-weight: 600;
        color: #ffffff;
        border-left: 5px solid {BRAND};
        padding-left: 0.6rem;
        margin: 0.4rem 0 0.8rem 0;
    }}

    /* Rapikan tab */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 6px;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: #0A3A20;
        border-radius: 10px 10px 0 0;
        padding: 8px 18px;
        font-weight: 500;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {BRAND} !important;
        color: white !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #041E10 !important;
    }}

    /* Mengubah warna background chip pilihan di sidebar */
    section[data-testid="stSidebar"] span[data-baseweb="tag"] {{
        background-color: #03AC0E !important;
        color: #ffffff !important;
    }}

    /* Memastikan teks input dropdown tetap putih terang */
    section[data-testid="stSidebar"] div[data-baseweb="select"] div {{
        color: #ffffff !important;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


def metric_card(col, icon, label, value, color="#ffffff"):
    """Render KPI card custom (pengganti st.metric bawaan)."""
    col.markdown(
        f"""
        <div class="metric-card">
            <div class="icon">{icon}</div>
            <div class="label">{label}</div>
            <div class="value" style="color:{color}">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_title(text):
    st.markdown(f'<div class="section-title">{text}</div>', unsafe_allow_html=True)


@st.cache_data
def get_base64_image(path):
    """Baca file gambar lalu ubah jadi base64 supaya bisa ditempel di tag <img> HTML."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


LOGO_BASE64 = get_base64_image("assets/tokopedia_logo.png")


PLOT_TEMPLATE = "plotly_dark"


def style_fig(fig, height=380):
    fig.update_layout(
        template=PLOT_TEMPLATE,
        font_family="Poppins, sans-serif",
        title_font_size=15,
        margin=dict(l=10, r=10, t=50, b=10),
        height=height,
        legend=dict(orientation="h", yanchor="bottom", y=-0.25),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
    )
    return fig


# =========================================================
# 3. LOAD DATA
# =========================================================
@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df_kuesioner = pd.read_sql_query("SELECT * FROM tabel_kuesioner", conn)
    df_ulasan = pd.read_sql_query("SELECT * FROM tabel_ulasan", conn)
    conn.close()
    return df_kuesioner, df_ulasan


df_kuesioner, df_ulasan = load_data()

# =========================================================
# 4. TRANSFORMASI: TEKS LIKERT -> ANGKA 1-5
# =========================================================
LIKERT_MAP = {
    "Sangat Tidak Setuju": 1,
    "Tidak Setuju": 2,
    "Netral": 3,
    "Setuju": 4,
    "Sangat Setuju": 5,
}

# Tema 10: Kesiapan Teknologi Pengguna
# X1 = Optimisme, X2 = Inovatif, M = Kemudahan, Y = Efektivitas
VARIABEL_ITEMS = {
    "X1": ["x1_1", "x1_2", "x1_3", "x1_4", "x1_5"],
    "X2": ["x2_1", "x2_2", "x2_3", "x2_4", "x2_5"],
    "M":  ["m_1", "m_2", "m_3", "m_4", "m_5"],
    "Y":  ["y_1", "y_2", "y_3", "y_4", "y_5"],
}
VARIABEL_LABEL = {
    "X1": "Optimisme",
    "X2": "Inovatif",
    "M": "Kemudahan",
    "Y": "Efektivitas",
}

df_num = df_kuesioner.copy()
for cols in VARIABEL_ITEMS.values():
    for c in cols:
        df_num[c] = df_num[c].map(LIKERT_MAP)

df_num["usia_singkat"] = df_num["usia"].str.extract(r"^([^\(]+)")[0].str.strip()

# =========================================================
# 5. SIDEBAR - FILTER
# =========================================================
st.sidebar.markdown("### 🔍 Filter Data")

pilihan_gender = st.sidebar.multiselect(
    "Jenis Kelamin",
    options=sorted(df_num["jenis_kelamin"].unique()),
    default=sorted(df_num["jenis_kelamin"].unique()),
)
pilihan_usia = st.sidebar.multiselect(
    "Kategori Usia",
    options=sorted(df_num["usia_singkat"].unique()),
    default=sorted(df_num["usia_singkat"].unique()),
)
pilihan_frekuensi = st.sidebar.multiselect(
    "Frekuensi Pemakaian",
    options=sorted(df_num["frekuensi_pakai"].unique()),
    default=sorted(df_num["frekuensi_pakai"].unique()),
)

df_filtered = df_num[
    df_num["jenis_kelamin"].isin(pilihan_gender)
    & df_num["usia_singkat"].isin(pilihan_usia)
    & df_num["frekuensi_pakai"].isin(pilihan_frekuensi)
]

st.sidebar.markdown("---")
st.sidebar.caption(f"Menampilkan **{len(df_filtered)}** dari {len(df_num)} responden")

# =========================================================
# 6. HERO HEADER
# =========================================================
st.markdown(
    f"""
    <div class="hero">
        <div class="hero-content">
            <img src="data:image/png;base64,{LOGO_BASE64}" class="hero-logo" />
            <div>
                <h1>Dashboard Kesiapan Teknologi Pengguna Aplikasi Tokopedia</h1>
                <p>Kelompok 5 · Tema 10: Kesiapan Teknologi Pengguna</p>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if df_filtered.empty:
    st.warning("Tidak ada data yang cocok dengan filter yang dipilih.")
    st.stop()

# =========================================================
# 7. KPI CARDS (layout asimetris: 1 kartu besar + 3 kartu kecil)
# =========================================================
col_big, col1, col2, col3 = st.columns([1.4, 1, 1, 1])

metric_card(col_big, "👥", "Total Responden", f"{len(df_filtered)} orang", BRAND_DARK)
metric_card(col1, "💬", "Total Ulasan Scraping", f"{len(df_ulasan)}")
metric_card(
    col2,
    "🎯",
    "Rata-rata Skor Keseluruhan",
    f"{sum(df_filtered[cols].mean().mean() for cols in VARIABEL_ITEMS.values()) / len(VARIABEL_ITEMS):.2f} / 5",
)
metric_card(col3, "⭐", "Rata-rata Rating Ulasan", f"{df_ulasan['score'].mean():.2f} / 5")

st.write("")

# =========================================================
# 8. TAB LAYOUT
# =========================================================
tab1, tab2, tab3 = st.tabs(
    ["👥  Profil Responden", "📊  Hasil Kuesioner", "💬  Analisis Ulasan"]
)

# ---------- TAB 1: PROFIL RESPONDEN ----------
with tab1:
    section_title("Demografi Responden")

    # Layout asimetris: pie lebih besar, histogram di sisi kanan lebih kecil
    c1, c2 = st.columns([1, 1])

    with c1:
        fig_gender = px.pie(
            df_filtered,
            names="jenis_kelamin",
            title="Berdasarkan Jenis Kelamin",
            color_discrete_sequence=[BRAND, ACCENT],
            hole=0.55,
        )
        fig_gender.update_traces(textinfo="percent+label", textfont_size=13)
        st.plotly_chart(style_fig(fig_gender, 340), use_container_width=True)

    with c2:
        fig_usia = px.pie(
            df_filtered,
            names="usia_singkat",
            title="Berdasarkan Usia",
            color_discrete_sequence=PLOT_COLORWAY,
            hole=0.55,
        )
        fig_usia.update_traces(textinfo="percent+label", textfont_size=13)
        st.plotly_chart(style_fig(fig_usia, 340), use_container_width=True)

    section_title("Frekuensi Penggunaan Aplikasi")
    freq_counts = (
        df_filtered["frekuensi_pakai"].value_counts().reset_index()
    )
    freq_counts.columns = ["Frekuensi", "Jumlah"]
    fig_freq = px.bar(
        freq_counts,
        title="Jumlah Frekuensi",
        x="Jumlah",
        y="Frekuensi",
        orientation="h",
        text="Jumlah",
        color="Frekuensi",
        color_discrete_sequence=PLOT_COLORWAY,
    )
    fig_freq.update_layout(showlegend=False, yaxis_title="", xaxis_title="Jumlah Responden")
    st.plotly_chart(style_fig(fig_freq, 320), use_container_width=True)

# ---------- TAB 2: HASIL KUESIONER ----------
with tab2:
    ringkasan = []
    for var, cols in VARIABEL_ITEMS.items():
        mean_skor = df_filtered[cols].mean().mean()
        tcr = (mean_skor / 5) * 100
        ringkasan.append(
            {
                "Variabel": f"{var} ({VARIABEL_LABEL[var]})",
                "Rata-rata Skor": round(mean_skor, 2),
                "TCR (%)": round(tcr, 1),
            }
        )
    df_ringkasan = pd.DataFrame(ringkasan)

    section_title("Rata-Rata Skor & Tingkat Capaian Responden (TCR)")
    c1, c2 = st.columns(2)

    with c1:
        fig_mean = px.bar(
            df_ringkasan,
            x="Variabel",
            y="Rata-rata Skor",
            text="Rata-rata Skor",
            title="Rata-Rata Jawaban Responden",
            color="Variabel",
            color_discrete_sequence=PLOT_COLORWAY,
            range_y=[0, 5],
        )
        fig_mean.update_traces(textposition="outside")
        fig_mean.update_layout(showlegend=False, xaxis_title="")
        st.plotly_chart(style_fig(fig_mean), use_container_width=True)

    with c2:
        fig_tcr = px.bar(
            df_ringkasan,
            x="Variabel",
            y="TCR (%)",
            text="TCR (%)",
            title="Tingkat Capaian Responden (TCR)",
            color="Variabel",
            color_discrete_sequence=PLOT_COLORWAY,
            range_y=[0, 100],
        )
        fig_tcr.update_traces(textposition="outside")
        fig_tcr.update_layout(showlegend=False, xaxis_title="")
        st.plotly_chart(style_fig(fig_tcr), use_container_width=True)

    section_title("Keterangan Variabel")
    k1, k2, k3, k4 = st.columns(4)
    keterangan = {
        "X1": ("Optimisme", "Persepsi bahwa teknologi membuat urusan lebih fleksibel."),
        "X2": ("Inovatif", "Kesiapan perangkat pengguna menjalankan aplikasi dengan lancar."),
        "M": ("Kemudahan", "Kemudahan memahami fitur baru tanpa banyak bertanya."),
        "Y": ("Efektivitas", "Keberhasilan menggunakan seluruh fungsi aplikasi secara efektif."),
    }
    for col, (var, (label, desc)) in zip([k1, k2, k3, k4], keterangan.items()):
        col.markdown(
            f"""
            <div class="metric-card">
                <div class="label">{var} — {label}</div>
                <div style="font-size:0.85rem;color:#555;margin-top:0.4rem;line-height:1.4;">{desc}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with st.expander("📄 Lihat Data Mentah (setelah filter)"):
        st.dataframe(df_filtered, use_container_width=True)

# ---------- TAB 3: ANALISIS ULASAN ----------
with tab3:
    section_title("Ulasan Pengguna dari Play Store / App Store")
    c1, c2 = st.columns([1.3, 1])

    with c1:
        score_counts = df_ulasan["score"].value_counts().sort_index().reset_index()
        score_counts.columns = ["Rating", "Jumlah"]
        fig_score = px.bar(
            score_counts,
            x="Rating",
            y="Jumlah",
            text="Jumlah",
            title="Distribusi Rating Ulasan",
            color="Rating",
            color_continuous_scale=["#DD5555", "#F5A623", BRAND],
        )
        fig_score.update_traces(textposition="outside")
        fig_score.update_layout(xaxis=dict(dtick=1), coloraxis_showscale=False)
        st.plotly_chart(style_fig(fig_score), use_container_width=True)

    with c2:
        df_ulasan["Panjang Kata"] = (
            df_ulasan["content"].astype(str).str.split().apply(len)
        )
        fig_len = px.box(
            df_ulasan,
            y="Panjang Kata",
            title="Panjang Ulasan (jumlah kata)",
            color_discrete_sequence=[ACCENT],
        )
        st.plotly_chart(style_fig(fig_len), use_container_width=True)

    section_title("Jelajahi Ulasan")
    filter_rating = st.select_slider(
        "Filter berdasarkan rating", options=[1, 2, 3, 4, 5], value=(1, 5)
    )
    df_ulasan_filtered = df_ulasan[
        (df_ulasan["score"] >= filter_rating[0]) & (df_ulasan["score"] <= filter_rating[1])
    ]
    st.dataframe(
        df_ulasan_filtered[["userName", "score", "at", "content"]],
        use_container_width=True,
        height=380,
    )

# =========================================================
# 9. FOOTER
# =========================================================
st.markdown(
    """
    <div style="text-align:center; color:#999; font-size:0.8rem; margin-top:2rem;">
        Dibuat untuk Ujian Akhir Semester (PBL) · Pemrograman dan Data Raya Lanjutan · FEB UNJ
    </div>
    """,
    unsafe_allow_html=True,
)
