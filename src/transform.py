"""Penggabungan data (federasi di tingkat aplikasi) - fungsi murni, tanpa Streamlit."""
import pandas as pd


def build_merged(df_harga: pd.DataFrame, df_meta: pd.DataFrame, df_kal: pd.DataFrame) -> pd.DataFrame:
    df_harga = df_harga.copy()
    df_harga["periode"] = pd.to_datetime(df_harga["periode"])
    for c in ["harga_terendah", "harga_tertinggi", "harga_rata_rata"]:
        df_harga[c] = df_harga[c].astype(float)

    # Integrasi PostgreSQL (fakta) + MongoDB (metadata & kalender)
    meta = df_meta[["kode_komoditas", "kategori"]]
    kal = df_kal.assign(
        peristiwa_teks=df_kal["peristiwa"].apply(lambda xs: "; ".join(x["nama"] for x in xs)),
        jumlah_peristiwa=df_kal["peristiwa"].apply(len),
    )[["tahun", "kode_bulan", "peristiwa_teks", "jumlah_peristiwa"]]
    m = (df_harga.merge(meta, on="kode_komoditas", how="left")
                 .merge(kal, on=["tahun", "kode_bulan"], how="left"))
    m["kategori"] = m["kategori"].fillna("Lainnya")
    m["peristiwa_teks"] = m["peristiwa_teks"].fillna("")
    m["jumlah_peristiwa"] = m["jumlah_peristiwa"].fillna(0).astype(int)

    # Metrik turunan
    m = m.sort_values(["kode_komoditas", "periode"])
    g = m.groupby("kode_komoditas")
    m["perubahan_mom_pct"] = g["harga_rata_rata"].pct_change() * 100
    # MoM hanya valid jika bulan sebelumnya benar-benar bulan berurutan (ada celah data -> kosong)
    selisih_bulan = (m["periode"].dt.year * 12 + m["periode"].dt.month) - \
                    (g["periode"].shift().dt.year * 12 + g["periode"].shift().dt.month)
    m.loc[selisih_bulan != 1, "perubahan_mom_pct"] = float("nan")
    m["rentang_pct"] = (m["harga_tertinggi"] - m["harga_terendah"]) / m["harga_rata_rata"] * 100
    return m.reset_index(drop=True)
