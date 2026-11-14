import streamlit as st
from src.queries import load_merged
from src import charts, ui

st.set_page_config(page_title="Harga Pangan Jawa Barat", page_icon="🌾", layout="wide")
st.markdown(ui.CSS, unsafe_allow_html=True)

try:
    df = load_merged()
except Exception as e:
    st.error("Gagal terhubung ke database. Periksa secrets/env dan Network Access di Atlas.")
    st.exception(e)
    st.stop()

# ---------- Filter ----------
st.sidebar.header("Filter data")
semua_kat = sorted(df["kategori"].unique())
kat = st.sidebar.multiselect("Kategori", semua_kat, default=semua_kat)
opsi_kom = sorted(df.loc[df["kategori"].isin(kat), "nama_komoditas"].unique())
kom = st.sidebar.multiselect("Komoditas", opsi_kom, default=opsi_kom[:4],
                             format_func=lambda x: x.title())
tahun = st.sidebar.multiselect("Tahun", sorted(df["tahun"].unique()), default=sorted(df["tahun"].unique()))
tampil_ev = st.sidebar.checkbox("Tandai peristiwa kalender di grafik tren", value=True)
st.sidebar.caption("Kategori dan kalender peristiwa dibaca dari MongoDB.")

f = df[df["nama_komoditas"].isin(kom) & df["tahun"].isin(tahun)]
if f.empty:
    st.markdown(ui.hero(0, df["periode"].min(), df["periode"].max()), unsafe_allow_html=True)
    st.warning("Pilih minimal satu komoditas dan satu tahun di panel kiri.")
    st.stop()

p_akhir = f["periode"].max()
latest = f[f["periode"] == p_akhir]

st.markdown(ui.hero(f["nama_komoditas"].nunique(), f["periode"].min(), p_akhir), unsafe_allow_html=True)

# ---------- KPI ----------
mom = latest["perubahan_mom_pct"].mean()
naik, turun = int((latest["perubahan_mom_pct"] > 0).sum()), int((latest["perubahan_mom_pct"] < 0).sum())
vol = f.groupby("nama_komoditas")["rentang_pct"].mean()
k1, k2, k3, k4 = st.columns(4)
if mom == mom:  # bukan NaN
    k1.markdown(ui.kpi(f"Perubahan rata-rata, {ui.periode_label(p_akhir)}", f"{mom:+.2f}%",
                       "dibanding bulan sebelumnya", "up" if mom > 0 else "down", lead=True), unsafe_allow_html=True)
else:
    k1.markdown(ui.kpi("Perubahan rata-rata", "n/a", "belum ada bulan pembanding", lead=True), unsafe_allow_html=True)
k2.markdown(ui.kpi("Komoditas naik / turun", f"{naik} / {turun}", f"pada {ui.periode_label(p_akhir)}"),
            unsafe_allow_html=True)
k3.markdown(ui.kpi("Paling berfluktuasi", vol.idxmax().title(),
                   f"rentang harga bulanan rata-rata {vol.max():.1f}%"), unsafe_allow_html=True)
k4.markdown(ui.kpi("Komoditas dipantau", str(f["nama_komoditas"].nunique()),
                   f"{len(f):,} pengamatan bulanan"), unsafe_allow_html=True)

# ---------- Tab ----------
tab1, tab2, tab3, tab4 = st.tabs(["Ringkasan", "Tren harga", "Volatilitas dan peristiwa", "Data"])

with tab1:
    st.markdown(ui.section(f"Pergerakan harga {ui.periode_label(p_akhir)}",
                           "Perubahan harga rata-rata dibanding bulan sebelumnya."), unsafe_allow_html=True)
    a, b = st.columns(2)
    a.markdown(ui.movers_html(latest, "naik"), unsafe_allow_html=True)
    b.markdown(ui.movers_html(latest, "turun"), unsafe_allow_html=True)
    st.markdown(ui.section("Harga terbaru per komoditas",
                           "Satuan berbeda-beda (kg, liter, item), jadi bandingkan tren, bukan nominal antar satuan."),
                unsafe_allow_html=True)
    tabel = latest[["nama_komoditas", "kategori", "harga_rata_rata", "satuan", "perubahan_mom_pct"]].copy()
    tabel["nama_komoditas"] = tabel["nama_komoditas"].str.title()
    st.dataframe(tabel.rename(columns={"nama_komoditas": "Komoditas", "kategori": "Kategori",
                                       "harga_rata_rata": "Harga rata-rata (Rp)", "satuan": "Satuan",
                                       "perubahan_mom_pct": "Perubahan (%)"}),
                 hide_index=True)

with tab2:
    st.markdown(ui.section("Tren harga rata-rata", "Bintang emas menandai bulan dengan peristiwa kalender."),
                unsafe_allow_html=True)
    st.plotly_chart(charts.trend_chart(f, tampil_ev))
    st.markdown(ui.section("Rentang harga satu komoditas",
                           "Area emas adalah selisih harga terendah dan tertinggi dalam sebulan."),
                unsafe_allow_html=True)
    pilih = st.selectbox("Komoditas", sorted(f["nama_komoditas"].unique()), format_func=lambda x: x.title())
    st.plotly_chart(charts.band_chart(f[f["nama_komoditas"] == pilih]))

with tab3:
    st.markdown(ui.section("Peta panas perubahan harga bulanan",
                           "Merah berarti naik, hijau kebiruan berarti turun."), unsafe_allow_html=True)
    st.plotly_chart(charts.heatmap_mom(f))
    c1, c2 = st.columns(2)
    c1.markdown(ui.section("Seberapa berfluktuasi tiap komoditas"), unsafe_allow_html=True)
    c1.plotly_chart(charts.volatility_bar(f))
    c2.markdown(ui.section("Bulan peristiwa dan bulan biasa",
                           "Gambaran deskriptif, bukan bukti sebab-akibat."), unsafe_allow_html=True)
    c2.plotly_chart(charts.event_compare(f.dropna(subset=["perubahan_mom_pct"])))
    st.markdown(ui.section("Sebaran harga per kategori"), unsafe_allow_html=True)
    st.plotly_chart(charts.category_box(f))

with tab4:
    st.markdown(ui.section("Data gabungan PostgreSQL dan MongoDB"), unsafe_allow_html=True)
    st.dataframe(f.sort_values(["periode", "nama_komoditas"]), hide_index=True)
    st.download_button("Unduh CSV", f.to_csv(index=False).encode("utf-8"),
                       "harga_pangan_gabungan.csv", "text/csv")

st.divider()
st.caption("Sumber data: Open Data Jabar, Biro Perekonomian Setda Provinsi Jawa Barat. Nama dan NIM: Haris Nugraha, 230660121074")