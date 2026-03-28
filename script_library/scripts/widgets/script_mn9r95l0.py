from widget import Widget, family, SMALL, MEDIUM, LARGE
import requests

def safe_text(val, default=""):
    return val if val and val.strip() else default

try:
    headers = {"Content-Type": "application/x-www-form-urlencoded;charset:utf-8"}
    resp = requests.post(
        "https://api.taolale.com/api/hot_rankings/get",
        data={"key": "DoG1KYTwfGhcTACTpgAk4eFiDf"},
        headers=headers,
        timeout=10
    )
    data = resp.json()
    movies = data.get("data", [])[:5] if data.get("code") == 200 else []
except:
    movies = []

bg = ("#F8FAFC", "#0F172A")
title_color = ("#0F172A", "#F8FAFC")
subtitle_color = ("#647B94", "#94A3B8")
accent = "#EF4444"

w = Widget(background=bg, padding=14)

if family == SMALL:
    top = movies[0] if movies else None
    with w.vstack(spacing=0, align="leading"):
        w.spacer(24)
        if top:
            w.icon("film.fill", size=18, color=accent)
            w.spacer(8)
            w.text(top["title"], size=17, weight="bold", color=title_color, max_lines=1)
            w.spacer(6)
            w.text(top["sumBoxDesc"], size=24, weight="bold", design="rounded", color=title_color)
            release_info = safe_text(top.get("releaseInfo"))
            if release_info:
                w.spacer(6)
                w.text(release_info, size=12, color=subtitle_color)
        else:
            w.text("暂无数据", size=16, color=subtitle_color)
        w.spacer()

elif family == MEDIUM:
    with w.hstack(spacing=0):
        w.icon("film.fill", size=15, color=accent)
        w.spacer(6)
        w.text("实时票房前三", size=14, weight="semibold", color=title_color)
        w.spacer()
        #w.text(f"共{len(movies)}部", size=12, color=subtitle_color)
    w.spacer()
    for movie in movies[:3]:
        rank = movie["index"]
        rc = "#F59E0B" if rank == 1 else "#94A3B8" if rank == 2 else "#CD7F32"
        with w.hstack(spacing=0, align="center"):
            w.text(f"#{rank}", size=13, weight="bold", color=rc)
            w.spacer(6)
            w.text(movie["title"], size=13, weight="medium", color=title_color)
            w.spacer()
            w.text(movie["sumBoxDesc"], size=13, weight="bold", design="rounded", color=title_color)
        w.spacer(4)
    w.spacer()

else:
    with w.hstack(spacing=0):
        w.icon("film.fill", size=17, color=accent)
        w.spacer(8)
        w.text("实时票房榜", size=17, weight="bold", color=title_color)
        w.spacer()
        w.text(f"共{len(movies)}部", size=13, color=subtitle_color)
    w.spacer(12)
    for movie in movies:
        rank = movie["index"]
        rc = "#F59E0B" if rank == 1 else "#94A3B8" if rank == 2 else "#CD7F32"
        release_info = safe_text(movie.get("releaseInfo"))
        with w.hstack(spacing=0, align="center"):
            w.text(f"#{rank}", size=15, weight="bold", color=rc)
            w.spacer(8)
            w.text(movie["title"], size=15, weight="semibold", color=title_color)
            if release_info:
                w.text(f" · {release_info}", size=12, color=subtitle_color)
            w.spacer()
            w.text(movie["sumBoxDesc"], size=16, weight="bold", design="rounded", color=title_color)
        w.spacer(6)

w.render()