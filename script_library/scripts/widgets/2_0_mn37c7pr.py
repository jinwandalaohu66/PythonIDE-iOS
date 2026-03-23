# 2026-3-23 by.Silence 测试设备16.2 14pm 
import requests
from widget import Widget, family
from widget import SMALL, MEDIUM, LARGE, CIRCULAR, RECTANGULAR
from datetime import datetime


def get_unicom_data():
    url = '自行填写'
    headers = {
        'Host': 'm.client.10010.com',
        'User-Agent': '自行填写',
        'Cookie': '自行填写'
    }
    try:
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            flow = data.get('flowResource', {}).get('flowPersent', '0')
            fee = data.get('feeResource', {}).get('feePersent', '0')
            voice = data.get('voiceResource', {}).get('voicePersent', '0')
            t = data.get("flush_date_time", "").split(" ")[-1] if " " in data.get("flush_date_time", "") else "刚刚"
            return True, flow, fee, voice, t
    except:
        pass
    return False, "0", "0", "0", "--"


def get_date_tip():
    now = datetime.now()
    week_list = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    week_day = week_list[now.weekday()]
    month_day = now.strftime("%m月%d日")
    
    year_start = datetime(now.year, 1, 1)
    year_end = datetime(now.year+1, 1, 1)
    year_pass = (now - year_start).total_seconds()
    year_total = (year_end - year_start).total_seconds()
    year_percent = int((year_pass / year_total) * 100)
    return f"{week_day} {month_day} · 今年已过{year_percent}%"


success, flow, fee, voice, update_time = get_unicom_data()
date_tip = get_date_tip()

w = Widget(
    background=("#FFFFFF", "#0B0F1A"),
    padding=16
)

if family == MEDIUM:
    with w.hstack(spacing=0):
        
        
        with w.vstack(align="leading", spacing=0):
            with w.hstack(spacing=6, align="center"):
                w.icon("antenna.radiowaves.left.and.right", size=16, color="#E63946")
                w.text("中国联通", size=14, weight="bold", color=("#111", "#EEE"), max_lines=1)
            
            w.spacer(14)
            w.text("剩余通用流量", size=12, color=("#64748B", "#94A3B8"), max_lines=1)
            w.spacer(4)
            
            with w.hstack(spacing=4, align="bottom"):
                w.text(flow, size=36, weight="bold", design="rounded", color=("#000", "#FFF"), max_lines=1)
                w.text("GB", size=14, weight="bold", color="#E63946", max_lines=1)
            
            
            w.spacer(8)
            w.text(date_tip, size=11, color=("#94A3B8", "#64748B"), max_lines=1)

        w.spacer()

        
        with w.vstack(align="leading", spacing=10):
            w.spacer(6)
            
            with w.hstack(spacing=8, align="center"):
                w.icon("yensign.circle.fill", size=14, color="#F59E0B")
                w.text(f"{fee} 元", size=11, weight="semibold", color="#F59E0B", max_lines=1)
            
            with w.hstack(spacing=8, align="center"):
                w.icon("phone.fill", size=14, color="#10B981")
                w.text(f"{voice} 分钟", size=11, weight="semibold", color="#10B981", max_lines=1)
            
            with w.hstack(spacing=8, align="center"):
                w.icon("clock", size=14, color=("#94A3B8", "#64748B"))
                w.text(update_time, size=11, color=("#94A3B8", "#64748B"), max_lines=1)


if not success:
    w = Widget(background=("#FFFFFF", "#0B0F1A"), padding=16)
    with w.vstack(align="center", spacing=8):
        w.spacer()
        w.icon("wifi.exclamationmark", size=30, color=("#64748B", "#94A3B8"))
        w.text("数据获取失败", size=14, weight="semibold", color=("#111", "#EEE"), max_lines=1)
        w.text("请更新Cookie", size=12, color=("#64748B", "#94A3B8"), max_lines=1)
        w.spacer()

w.render(url="pythonide://")