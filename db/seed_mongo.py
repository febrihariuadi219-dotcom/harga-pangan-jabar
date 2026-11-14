"""Seed MongoDB. Jalankan: python -m db.seed_mongo"""
import os
import sys
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from db.common import load_clean_csv
from db.mongo_docs import metadata_komoditas, kalender_docs

load_dotenv()


def main(csv_path: str):
    df = load_clean_csv(csv_path)
    db = MongoClient(os.environ["MONGO_URI"])[os.environ.get("MONGO_DB_NAME", "pangan_jabar")]
    meta = metadata_komoditas(df)
    db["metadata_komoditas"].bulk_write(
        [UpdateOne({"kode_komoditas": d["kode_komoditas"]}, {"$set": d}, upsert=True) for d in meta])
    kal = kalender_docs(df)
    db["kalender_peristiwa"].bulk_write(
        [UpdateOne({"tahun": d["tahun"], "kode_bulan": d["kode_bulan"]}, {"$set": d}, upsert=True) for d in kal])
    print(f"MongoDB: {len(meta)} metadata_komoditas, {len(kal)} kalender_peristiwa.")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/raw/harga_pangan_jabar.csv")
