# -*- coding: utf-8 -*-
"""习惯追踪器 — 7 habits, streak, progress ring."""

from widget import Widget, family, SMALL, MEDIUM, LARGE
import time, random

habits = [
    ("💧", "喝水",   True),
    ("📖", "阅读",   True),
    ("🏃", "运动",   False),
    ("🧘", "冥想",   True),
    ("🍎", "水果",   True),
    ("😴", "早睡",   False),
    ("📝", "日记",   True),
]

done   = sum(1 for *_, ok in habits if ok)
total  = len(habits)
streak = 12

bg       = {"gradient": ["#6366F1", "#8B5CF6"], "direction": "diagonal"}
card_bg  = ("#FFFFFF", "#1E1B4B")
txt_main = ("#1E1B4B", "#E0E7FF")
txt_sub  = ("#6366F1", "#A5B4FC")
done_clr = ("#22C55E", "#4ADE80")
miss_clr = ("#E5E7EB", "#312E81")

w = Widget(background=bg, padding=12)

if family in (SMALL, "small"):
    with w.vstack(spacing=6):
        with w.hstack(spacing=6, align="center"):
            w.icon("checkmark.circle.fill", size=16, color="#A5B4FC")
            w.text("习惯", size=15, weight="bold", color="#FFFFFF")
            w.spacer()
            w.text(f"🔥{streak}天", size=12, color="#FDE68A")
        w.gauge(done, total, label="", size=54, color="#34D399",
                track_color=("#C7D2FE", "#312E81"), line_width=6)
        w.text(f"{done}/{total} 已完成", size=12, weight="medium",
               color="#E0E7FF", align="center")

elif family in (MEDIUM, "medium"):
    with w.hstack(spacing=10):
        with w.vstack(spacing=4, padding=4):
            with w.hstack(spacing=4, align="center"):
                w.icon("checkmark.circle.fill", size=14, color="#A5B4FC")
                w.text("习惯追踪", size=14, weight="bold", color="#FFFFFF")
            w.spacer()
            w.gauge(done, total, label="", size=56, color="#34D399",
                    track_color=("#C7D2FE", "#312E81"), line_width=6)
            w.text(f"{done}/{total}", size=11, color="#E0E7FF", align="center")
        with w.vstack(spacing=3):
            with w.hstack(spacing=4, align="center"):
                w.text(f"🔥 连续 {streak} 天", size=11, weight="semibold",
                       color="#FDE68A")
                w.spacer()
            for emoji, name, ok in habits:
                with w.hstack(spacing=4, align="center"):
                    w.text(emoji, size=12)
                    w.text(name, size=11, color="#E0E7FF")
                    w.spacer()
                    w.icon("checkmark.circle.fill" if ok else "circle",
                           size=13,
                           color="#4ADE80" if ok else "#6366F1")

else:
    with w.vstack(spacing=6):
        with w.hstack(spacing=6, align="center"):
            w.icon("checkmark.circle.fill", size=18, color="#A5B4FC")
            w.text("习惯追踪器", size=17, weight="bold", color="#FFFFFF")
            w.spacer()
            w.text(f"🔥 连续 {streak} 天", size=13, weight="semibold",
                   color="#FDE68A")
        w.divider(color="#818CF8")
        with w.hstack(spacing=8, align="center"):
            w.gauge(done, total, label="", size=64, color="#34D399",
                    track_color=("#C7D2FE", "#312E81"), line_width=7)
            with w.vstack(spacing=2):
                w.text(f"{done}/{total} 已完成", size=13, weight="semibold",
                       color="#E0E7FF")
                pct = int(done / total * 100)
                w.progress(done, total, color="#34D399", height=6,
                           track_color=("#C7D2FE", "#312E81"))
                w.text(f"完成率 {pct}%", size=11, color="#A5B4FC")
        w.divider(color="#818CF8")
        with w.hstack(spacing=6):
            for emoji, name, ok in habits:
                with w.vstack(spacing=2, align="center"):
                    w.text(emoji, size=18)
                    w.icon("checkmark.circle.fill" if ok else "circle",
                           size=14,
                           color="#4ADE80" if ok else "#6366F1")

w.render()
