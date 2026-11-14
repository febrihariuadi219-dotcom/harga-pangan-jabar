import pandas as pd
import streamlit as st
from .connections import pg_engine, mongo_db
from .transform import build_merged

SQL = """
SELECT h.periode, h.tahun, h.kode_bulan, h.kode_komoditas, k.nama_komoditas, k.satuan,
       h.harga_terendah, h.harga_tertinggi, h.harga_rata_rata
FROM harga_bulanan h JOIN komoditas k USING (kode_komoditas)
"""


@st.cache_data(ttl=600, show_spinner="Mengambil data dari PostgreSQL & MongoDB...")
def load_merged() -> pd.DataFrame:
    df_harga = pd.read_sql(SQL, pg_engine())                                   # DBMS 1
    db = mongo_db()                                                             # DBMS 2
    df_meta = pd.DataFrame(list(db["metadata_komoditas"].find({}, {"_id": 0})))
    df_kal = pd.DataFrame(list(db["kalender_peristiwa"].find({}, {"_id": 0})))
    return build_merged(df_harga, df_meta, df_kal)
