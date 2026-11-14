"""Seed PostgreSQL. Jalankan: python -m db.seed_postgres"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from db.common import load_clean_csv

load_dotenv()


def main(csv_path: str):
    engine = create_engine(os.environ["POSTGRES_URL"])
    df = load_clean_csv(csv_path)
    with engine.begin() as conn:
        with open("db/schema.sql", encoding="utf-8") as f:
            for stmt in f.read().split(";"):
                if stmt.strip():
                    conn.execute(text(stmt))
        kom = df[["kode_komoditas", "nama_komoditas", "satuan"]].drop_duplicates("kode_komoditas")
        conn.execute(text("INSERT INTO komoditas VALUES (:a,:b,:c) ON CONFLICT DO NOTHING"),
                     [dict(a=r.kode_komoditas, b=r.nama_komoditas, c=r.satuan) for r in kom.itertuples()])
        conn.execute(text(
            "INSERT INTO harga_bulanan (kode_komoditas,tahun,kode_bulan,periode,"
            "harga_terendah,harga_tertinggi,harga_rata_rata) "
            "VALUES (:k,:t,:b,:p,:lo,:hi,:av) ON CONFLICT DO NOTHING"),
            [dict(k=r.kode_komoditas, t=int(r.tahun), b=int(r.kode_bulan), p=r.periode,
                  lo=float(r.harga_terendah), hi=float(r.harga_tertinggi), av=float(r.harga_rata_rata))
             for r in df.itertuples()])
    print(f"PostgreSQL: {len(kom)} komoditas, {len(df)} baris harga.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/raw/harga_pangan_jabar.csv")
