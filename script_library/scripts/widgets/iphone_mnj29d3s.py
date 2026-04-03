# 2026-4-3 Silence

import os
from widget import Widget, family, MEDIUM

def get_storage_info():
    statvfs = os.statvfs('/')
    block_size = statvfs.f_frsize
    total = statvfs.f_blocks * block_size
    free = statvfs.f_bavail * block_size
    used = total - free
    used_percent = (used / total) * 100 if total else 0
    
    total_gb = total / (1024**3)
    used_gb = used / (1024**3)
    free_gb = free / (1024**3)
    return total_gb, used_gb, free_gb, used_percent

def render_widget():
    total, used, free, percent = get_storage_info()
    
    bar_width = int(200 * (percent / 100))
    bar_width = min(200, max(0, bar_width))

    bg_color = ("#F1F5F9", "#0F172A")
    w = Widget(background=bg_color, padding=16)

    with w.vstack(spacing=12):
        
        with w.hstack():
            w.icon("internaldrive", size=18, color="#3B82F6")
            w.text("存储空间", size=14, weight="semibold", color=("#0F172A", "#F1F5F9"))
            w.spacer()
            w.text(f"{percent:.0f}%", size=12, weight="medium", color="#3B82F6")

        
        with w.hstack():
            w.spacer()
            with w.vstack():
                
                w.text("", size=1)  
                
                pass
        
        w.progress(percent / 100, color="#3B82F6", track_color=("#E2E8F0", "#334155"), height=8)

        
        with w.hstack():
            with w.vstack(align="leading", spacing=4):
                w.text("已用", size=11, color=("#64748B", "#94A3B8"))
                w.text(f"{used:.1f} GB", size=15, weight="bold", color=("#0F172A", "#F1F5F9"))
            w.spacer()
            with w.vstack(align="trailing", spacing=4):
                w.text("可用", size=11, color=("#64748B", "#94A3B8"))
                w.text(f"{free:.1f} GB", size=15, weight="bold", color=("#10B981", "#34D399"))
            w.spacer()
            with w.vstack(align="trailing", spacing=4):
                w.text("总计", size=11, color=("#64748B", "#94A3B8"))
                w.text(f"{total:.1f} GB", size=15, weight="bold", color=("#0F172A", "#F1F5F9"))

        
        if free < 5:
            w.text("⚠️剩余不足5G快去删点片吧⚠️", size=10, color="#EF4444", align="center")

    w.render()

if family == MEDIUM:
    render_widget()
else:
    w = Widget(background=("#FFFFFF", "#0B0F1A"), padding=16)
    with w.vstack(align="center", spacing=8):
        w.icon("internaldrive", size=30, color="#3B82F6")
        w.text("请使用中尺寸小组件", size=14, weight="semibold", color=("#111", "#EEE"))
    w.render()