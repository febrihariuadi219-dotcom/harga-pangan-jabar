"""Dokumen yang disimpan di MongoDB (dipisah agar mudah diuji)."""
from db.common import slugify

# Pengelompokan editorial berdasarkan kata kunci nama komoditas (bukan dari dataset sumber).
KATEGORI = [
    ("beras", "Karbohidrat"), ("tepung", "Karbohidrat"), ("mie", "Karbohidrat"),
    ("gula", "Pemanis"), ("minyak", "Minyak & Lemak"),
    ("cabe", "Bumbu & Sayuran"), ("bawang", "Bumbu & Sayuran"),
    ("telur", "Protein Hewani"), ("daging", "Protein Hewani"), ("ikan", "Protein Hewani"),
    ("udang", "Protein Hewani"), ("susu", "Protein Hewani"),
    ("tahu", "Protein Nabati"), ("tempe", "Protein Nabati"),
    ("jeruk", "Buah"), ("pisang", "Buah"),
]


def kategori(nama: str) -> str:
    n = nama.lower()
    return next((k for kw, k in KATEGORI if kw in n), "Lainnya")


def metadata_komoditas(df):
    docs = []
    for r in df[["nama_komoditas", "satuan"]].drop_duplicates("nama_komoditas").itertuples():
        docs.append({
            "kode_komoditas": slugify(r.nama_komoditas),
            "nama": r.nama_komoditas.title(),
            "kategori": kategori(r.nama_komoditas),
            "satuan": r.satuan,
            "tags": sorted({w for w in r.nama_komoditas.lower().replace("(", " ").replace(")", " ").split() if len(w) > 2}),
        })
    return docs


# Peristiwa kalender nasional per bulan (dokumen fleksibel: jumlah peristiwa tiap bulan berbeda-beda).
# Tanggal mengacu pada kalender Indonesia / SKB 3 Menteri libur nasional 2024 & 2025.
KALENDER = {
    (2024, 2): [("Tahun Baru Imlek 2575", "Hari besar")],
    (2024, 3): [("Awal Ramadan 1445 H", "Hari besar keagamaan")],
    (2024, 4): [("Idul Fitri 1445 H (10 Apr)", "Hari besar keagamaan")],
    (2024, 6): [("Idul Adha 1445 H (17 Jun)", "Hari besar keagamaan")],
    (2024, 12): [("Natal", "Hari besar keagamaan"), ("Libur Akhir Tahun", "Libur nasional")],
    (2025, 1): [("Tahun Baru Imlek 2576 (29 Jan)", "Hari besar")],
    (2025, 3): [("Awal Ramadan 1446 H (1 Mar)", "Hari besar keagamaan"),
                ("Idul Fitri 1446 H (31 Mar)", "Hari besar keagamaan")],
    (2025, 6): [("Idul Adha 1446 H (6 Jun)", "Hari besar keagamaan")],
    (2025, 12): [("Natal", "Hari besar keagamaan"), ("Libur Akhir Tahun", "Libur nasional")],
}


def kalender_docs(df):
    docs = []
    for (th, bl) in sorted(df[["tahun", "kode_bulan"]].drop_duplicates().itertuples(index=False)):
        pe = [{"nama": n, "jenis": j} for n, j in KALENDER.get((int(th), int(bl)), [])]
        docs.append({"tahun": int(th), "kode_bulan": int(bl), "peristiwa": pe})
    return docs
