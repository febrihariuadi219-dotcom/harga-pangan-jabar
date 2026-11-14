-- DBMS 1: PostgreSQL (Neon / Supabase) - data master komoditas & fakta harga bulanan
CREATE TABLE IF NOT EXISTS komoditas (
    kode_komoditas VARCHAR(60) PRIMARY KEY,
    nama_komoditas VARCHAR(120) NOT NULL,
    satuan         VARCHAR(40)  NOT NULL
);

CREATE TABLE IF NOT EXISTS harga_bulanan (
    id             BIGSERIAL PRIMARY KEY,
    kode_komoditas VARCHAR(60) NOT NULL REFERENCES komoditas(kode_komoditas),
    tahun          SMALLINT NOT NULL,
    kode_bulan     SMALLINT NOT NULL CHECK (kode_bulan BETWEEN 1 AND 12),
    periode        DATE NOT NULL,
    harga_terendah NUMERIC(14,2) NOT NULL,
    harga_tertinggi NUMERIC(14,2) NOT NULL,
    harga_rata_rata NUMERIC(14,2) NOT NULL,
    CHECK (harga_terendah <= harga_rata_rata AND harga_rata_rata <= harga_tertinggi),
    UNIQUE (kode_komoditas, tahun, kode_bulan)
);

CREATE INDEX IF NOT EXISTS idx_harga_periode ON harga_bulanan(periode);
