"""Pembersihan dataset 'Kompilasi Data Perkembangan Harga Pangan di Provinsi Jawa Barat' (Open Data Jabar)."""
import re
import pandas as pd

KOLOM = ["kode_bulan", "nama_komoditas", "harga_terendah", "harga_tertinggi",
         "harga_rata_rata", "satuan", "tahun"]
# Produk yang sama, namanya berubah antar tahun di dataset sumber -> disatukan.
ALIAS = {"SUSU BALITA (SGM) 400 GRAM": "SUSU BALITA (SGM)"}
SATUAN_BAKU = {"SUSU BALITA (SGM)": "RUPIAH/400GRAM"}


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", str(text).strip().lower()).strip("_")


def load_clean_csv(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    df.columns = [c.strip().lower() for c in df.columns]
    miss = [c for c in KOLOM if c not in df.columns]
    if miss:
        raise SystemExit(f"Kolom wajib hilang: {miss}")
    df["nama_komoditas"] = df["nama_komoditas"].str.strip().str.upper().replace(ALIAS)
    df["satuan"] = df["satuan"].str.strip().str.upper()
    for nama, sat in SATUAN_BAKU.items():
        df.loc[df["nama_komoditas"] == nama, "satuan"] = sat
    for c in ["harga_terendah", "harga_tertinggi", "harga_rata_rata"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df.dropna(subset=["harga_terendah", "harga_tertinggi", "harga_rata_rata"])
    # Nilai 0 di sumber berarti "tidak tercatat" (mis. Minyak Kita Jan-Feb 2024), bukan harga nol.
    df = df[(df[["harga_terendah", "harga_tertinggi", "harga_rata_rata"]] > 0).all(axis=1)]
    df["periode"] = pd.to_datetime(dict(year=df["tahun"], month=df["kode_bulan"], day=1)).dt.date
    df["kode_komoditas"] = df["nama_komoditas"].map(slugify)
    return df.drop_duplicates(["kode_komoditas", "tahun", "kode_bulan"]).reset_index(drop=True)
