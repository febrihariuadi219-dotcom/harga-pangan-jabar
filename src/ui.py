"""Komponen tampilan (HTML/CSS) - fungsi murni agar mudah diuji."""
import html
import pandas as pd

BULAN = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus",
         "September", "Oktober", "November", "Desember"]

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600&family=Fraunces:opsz,wght@9..144,500;9..144,600&display=swap');
html, body, [class*="css"], [data-testid="stAppViewContainer"] { font-family: 'DM Sans', sans-serif; }
[data-testid="stHeader"] { background: transparent; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 2.2rem; max-width: 1280px; }
[data-testid="stSidebar"] { border-right: 1px solid #1F2E4A; }
[data-testid="stSidebar"] h2 { font-family: 'Fraunces', serif; font-weight: 500; }

.hero { padding: 0.4rem 0 1.4rem 0; border-bottom: 1px solid #1F2E4A; margin-bottom: 1.4rem; }
.hero h1 { font-family: 'Fraunces', serif; font-weight: 600; font-size: 2.7rem; line-height: 1.1;
           letter-spacing: -0.02em; margin: 0 0 0.5rem 0; color: #F3F6FB; }
.hero p { color: #8FA0BC; font-size: 1.02rem; max-width: 62ch; margin: 0; line-height: 1.55; }
.hero .stamp { display: inline-block; margin-top: 0.9rem; padding: 0.22rem 0.7rem; border: 1px solid #E2B65C;
               color: #E2B65C; border-radius: 99px; font-size: 0.85rem; }

.kpi { background: #131E33; border: 1px solid #1F2E4A; border-radius: 10px; padding: 1rem 1.15rem; height: 100%; }
.kpi.lead { border-color: #E2B65C; }
.kpi-l { color: #8FA0BC; font-size: 0.9rem; margin-bottom: 0.35rem; }
.kpi-v { font-family: 'Fraunces', serif; font-weight: 600; font-size: 1.95rem; line-height: 1.15; color: #F3F6FB; }
.kpi-s { color: #8FA0BC; font-size: 0.85rem; margin-top: 0.35rem; line-height: 1.4; }
.up { color: #F08A7C; } .down { color: #5CC5B2; }

.sec { font-family: 'Fraunces', serif; font-weight: 500; font-size: 1.45rem; margin: 1.6rem 0 0.2rem 0; color: #F3F6FB; }
.sec-n { color: #8FA0BC; font-size: 0.92rem; margin: 0 0 0.9rem 0; }

.mv { background: #131E33; border: 1px solid #1F2E4A; border-radius: 10px; padding: 0.55rem 1.05rem; }
.mv-h { font-weight: 600; font-size: 1rem; padding: 0.5rem 0 0.4rem 0; }
.mv-r { display: grid; grid-template-columns: 1fr 1.3fr 4.2rem; align-items: center; gap: 0.8rem;
        padding: 0.5rem 0; border-top: 1px solid #1F2E4A; font-size: 0.93rem; }
.mv-bar { height: 8px; border-radius: 4px; background: #0C1424; overflow: hidden; }
.mv-bar > span { display: block; height: 100%; border-radius: 4px; }
.mv-p { text-align: right; font-weight: 600; font-variant-numeric: tabular-nums; }
.bg-up { background: #F08A7C; } .bg-down { background: #5CC5B2; }

button[data-baseweb="tab"] { font-size: 1rem; }
button[data-baseweb="tab"][aria-selected="true"] { color: #E2B65C; }
div[data-baseweb="tab-highlight"] { background-color: #E2B65C !important; }
</style>
"""


def periode_label(ts) -> str:
    ts = pd.Timestamp(ts)
    return f"{BULAN[ts.month]} {ts.year}"


def hero(n_komoditas: int, p_awal, p_akhir) -> str:
    return (
        '<div class="hero"><h1>Harga pangan Jawa Barat</h1>'
        f'<p>Pergerakan harga bulanan {n_komoditas} komoditas pangan strategis. '
        'Harga dibaca dari PostgreSQL, sedangkan kategori dan kalender peristiwa dari MongoDB, '
        'lalu digabung dengan Pandas.</p>'
        f'<span class="stamp">{periode_label(p_awal)} sampai {periode_label(p_akhir)}</span></div>'
    )


def kpi(label: str, value: str, sub: str = "", tone: str = "", lead: bool = False) -> str:
    return (f'<div class="kpi{" lead" if lead else ""}"><div class="kpi-l">{html.escape(label)}</div>'
            f'<div class="kpi-v">{html.escape(value)}</div>'
            f'<div class="kpi-s {tone}">{html.escape(sub)}</div></div>')


def section(judul: str, catatan: str = "") -> str:
    n = f'<p class="sec-n">{html.escape(catatan)}</p>' if catatan else ""
    return f'<div class="sec">{html.escape(judul)}</div>{n}'


def movers_html(latest: pd.DataFrame, arah: str, n: int = 5) -> str:
    """arah: 'naik' atau 'turun'. latest = baris periode terakhir."""
    d = latest.dropna(subset=["perubahan_mom_pct"])
    if d.empty:
        return '<div class="mv"><div class="mv-h">Belum ada data pembanding</div></div>'
    mx = max(d["perubahan_mom_pct"].abs().max(), 1e-9)
    if arah == "naik":
        pilih, judul, kelas = d[d["perubahan_mom_pct"] > 0].nlargest(n, "perubahan_mom_pct"), "Paling naik", "up"
    else:
        pilih, judul, kelas = d[d["perubahan_mom_pct"] < 0].nsmallest(n, "perubahan_mom_pct"), "Paling turun", "down"
    rows = ""
    for r in pilih.itertuples():
        w = abs(r.perubahan_mom_pct) / mx * 100
        rows += (f'<div class="mv-r"><div>{html.escape(r.nama_komoditas.title())}</div>'
                 f'<div class="mv-bar"><span class="bg-{kelas}" style="width:{w:.0f}%"></span></div>'
                 f'<div class="mv-p {kelas}">{r.perubahan_mom_pct:+.1f}%</div></div>')
    if not rows:
        rows = '<div class="mv-r"><div>Tidak ada komoditas pada kelompok ini</div><div></div><div></div></div>'
    return f'<div class="mv"><div class="mv-h">{judul}</div>{rows}</div>'