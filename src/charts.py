import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

TEXT, GRID, GOLD = "#E6ECF5", "#1F2E4A", "#E2B65C"
COLORWAY = ["#E2B65C", "#5CC5B2", "#F08A7C", "#8E9BEA", "#6FB1E8", "#C9A27A", "#9BD48A", "#E58FC0"]
DIVERGING = [[0, "#5CC5B2"], [0.5, "#1B2A44"], [1, "#F08A7C"]]


def style(fig, height=400):
    fig.update_layout(
        template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color=TEXT, size=13), colorway=COLORWAY,
        height=height, margin=dict(l=8, r=8, t=24, b=8),
        hoverlabel=dict(bgcolor="#1B2A44", bordercolor=GOLD, font_size=13),
        legend=dict(orientation="h", y=-0.22, title_text=""))
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID, title_standoff=10)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, title_standoff=10)
    return fig


def trend_chart(df, tampil_peristiwa=True):
    fig = px.line(df, x="periode", y="harga_rata_rata", color="nama_komoditas", markers=True,
                  labels={"periode": "", "harga_rata_rata": "Harga rata-rata (Rp)", "nama_komoditas": ""},
                  hover_data={"peristiwa_teks": True, "satuan": True})
    fig.update_traces(line=dict(width=2.6), marker=dict(size=6))
    if tampil_peristiwa:
        ev = df.loc[df["jumlah_peristiwa"] > 0, ["periode", "peristiwa_teks"]].drop_duplicates("periode")
        for r in ev.itertuples():
            fig.add_vline(x=r.periode.timestamp() * 1000, line_dash="dot", line_color="#3A4C6E", opacity=0.9)
        if len(ev):
            fig.add_trace(go.Scatter(x=ev["periode"], y=[df["harga_rata_rata"].max()] * len(ev),
                                     mode="markers", marker=dict(symbol="star", size=12, color=GOLD),
                                     text=ev["peristiwa_teks"], hoverinfo="text+x", name="Peristiwa kalender"))
    fig.update_layout(hovermode="x unified")
    return style(fig, 430)


def band_chart(df_one):
    """Rentang harga terendah-tertinggi + rata-rata untuk satu komoditas."""
    d = df_one.sort_values("periode")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d["periode"], y=d["harga_tertinggi"], line=dict(width=0),
                             showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=d["periode"], y=d["harga_terendah"], fill="tonexty", line=dict(width=0),
                             fillcolor="rgba(226,182,92,0.20)", name="Rentang terendah sampai tertinggi"))
    fig.add_trace(go.Scatter(x=d["periode"], y=d["harga_rata_rata"], mode="lines+markers",
                             name="Rata-rata", line=dict(color=GOLD, width=2.6)))
    fig.update_layout(yaxis_title="Harga (Rp)", hovermode="x unified")
    return style(fig, 360)


def heatmap_mom(df):
    p = df.pivot_table(index="nama_komoditas", columns="periode", values="perubahan_mom_pct")
    p.index = [i.title() for i in p.index]
    p.columns = [c.strftime("%b %y") for c in p.columns]
    fig = px.imshow(p, aspect="auto", color_continuous_scale=DIVERGING, color_continuous_midpoint=0,
                    labels=dict(color="Perubahan (%)", x="", y=""))
    fig.update_traces(xgap=2, ygap=2)
    fig.update_layout(coloraxis_colorbar=dict(thickness=10, len=0.8, title_text=""))
    return style(fig, 480)


def volatility_bar(df):
    g = (df.groupby(["nama_komoditas", "kategori"], as_index=False)["rentang_pct"].mean()
           .sort_values("rentang_pct"))
    g["nama_komoditas"] = g["nama_komoditas"].str.title()
    fig = px.bar(g, x="rentang_pct", y="nama_komoditas", color="kategori", orientation="h",
                 labels={"rentang_pct": "Rentang harga bulanan (% dari rata-rata)",
                         "nama_komoditas": "", "kategori": ""})
    fig.update_traces(marker_line_width=0)
    return style(fig, 480)


def event_compare(df):
    d = df.assign(kondisi=df["jumlah_peristiwa"].map(lambda n: "Bulan ada peristiwa" if n else "Bulan biasa"))
    g = d.groupby("kondisi", as_index=False)["perubahan_mom_pct"].mean()
    fig = px.bar(g, x="kondisi", y="perubahan_mom_pct", color="kondisi",
                 color_discrete_map={"Bulan ada peristiwa": GOLD, "Bulan biasa": "#3A4C6E"},
                 labels={"perubahan_mom_pct": "Rata-rata perubahan bulanan (%)", "kondisi": ""},
                 text_auto=".2f")
    fig.update_layout(showlegend=False)
    fig.update_traces(marker_line_width=0, textposition="outside")
    return style(fig, 340)


def category_box(df):
    d = df.assign(nama=df["nama_komoditas"].str.title())
    fig = px.box(d, x="kategori", y="harga_rata_rata", color="kategori", points="all",
                 labels={"kategori": "", "harga_rata_rata": "Harga rata-rata (Rp)"})
    fig.update_layout(showlegend=False)
    return style(fig, 380)