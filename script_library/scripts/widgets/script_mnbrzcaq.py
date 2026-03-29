import widget
import datetime
import calendar
import requests
import random

BG_COLOR = "#FFFFFF"
MAIN_TEXT_COLOR = "#1C1C1E"
SECONDARY_TEXT_COLOR = "#8E8E93"
ACCENT_COLOR = "#007AFF"
FESTIVAL_COLOR = "#34C759"
TODAY_COLOR = "#FF3B30"
DATE_TEXT_COLOR = "#3A3A3C"
QUOTE_MAX_LENGTH = 20
REQUEST_TIMEOUT = 1.5
SHOW_DATE_COUNT = 5

def get_festivals(month, day):
    festival_dict = {
        1: {1: "元旦节"}, 2: {14: "情人节"}, 3: {8: "妇女节", 12: "植树节", 21: "世界森林日"},
        4: {4: "清明节"}, 5: {1: "劳动节", 4: "青年节"}, 6: {1: "儿童节", 14: "端午节"},
        7: {1: "建党节"}, 8: {1: "建军节"}, 9: {10: "教师节", 17: "中秋节"},
        10: {1: "国庆节", 7: "重阳节"}, 12: {25: "圣诞节"}
    }
    month_fest = festival_dict.get(month, {})
    today_text = month_fest.get(day, "宜: 保持热爱")
    month_all = "·".join(list(month_fest.values())[:2]) if month_fest else "岁华寻常"
    return today_text, month_all

def get_hitokoto():
    default_quotes = [
        "代码敲累了，记得喝杯水...", "生活明朗，万物可爱。", "凡是过往，皆为序章。",
        "平安喜乐，得偿所愿。", "保持热爱，奔赴山海。", "慢慢来，谁还没有一个努力的过程。",
        "心有山海，静而无边。", "人间值得，未来可期。"
    ]
    try:
        headers = {"User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)"}
        r = requests.get("https://v1.hitokoto.cn/?c=i", headers=headers, timeout=REQUEST_TIMEOUT).json()
        return r.get("hitokoto", random.choice(default_quotes))
    except:
        return random.choice(default_quotes)

def build():
    w = widget.Widget(widget.LARGE)
    w._background = BG_COLOR
    w._color = MAIN_TEXT_COLOR
    
    now = datetime.datetime.now()
    y, m, d = now.year, now.month, now.day
    today_fest, month_all = get_festivals(m, d)
    total_days = 366 if calendar.isleap(y) else 365
    year_progress = now.timetuple().tm_yday / total_days
    today_week_idx = now.weekday()
    week_list = ["一", "二", "三", "四", "五", "六", "日"]

    date_list = [now + datetime.timedelta(days=i) for i in range(SHOW_DATE_COUNT)]
    date_rows = [date_list[i:i+5] for i in range(0, len(date_list), 5)]

    pre_week = " ".join(week_list[:today_week_idx]) + (" " if today_week_idx > 0 else "")
    today_week = week_list[today_week_idx]
    suf_week = (" " if today_week_idx < 6 else "") + " ".join(week_list[today_week_idx+1:])

    with w.vstack(spacing=12):
        with w.hstack():
            w.icon("calendar.badge.clock", size=24, color=ACCENT_COLOR)
            w.text(f"  {y} 年 {m} 月", size=24, weight="heavy")
            w.spacer()

        w.spacer()

        with w.hstack():
            with w.vstack(spacing=6):
                w.text(str(d), size=90, weight="heavy")
                w.text(f"{now.strftime('%B').upper()} ◈ {today_fest}", size=13, color=FESTIVAL_COLOR, weight="bold")
                w.text(f"本月: {month_all}", size=11, color=SECONDARY_TEXT_COLOR)
            
            w.spacer()

            with w.vstack(spacing=10):
                with w.hstack():
                    if pre_week.strip():
                        w.text(pre_week, size=12, color=SECONDARY_TEXT_COLOR, weight="bold")
                    w.text(today_week, size=12, color=TODAY_COLOR, weight="bold")
                    if suf_week.strip():
                        w.text(suf_week, size=12, color=SECONDARY_TEXT_COLOR, weight="bold")
                
                for row in date_rows:
                    row_days = [date.day for date in row]
                    has_today = d in row_days

                    if not has_today:
                        row_str = ""
                        for day_num in row_days:
                            row_str += f" {day_num:02d} "
                        w.text(row_str, size=17, color=DATE_TEXT_COLOR, weight="bold")
                    
                    else:
                        with w.hstack(spacing=0):
                            for date in row:
                                day_num = date.day
                                if day_num == d:
                                    w.text(f" {day_num:02d} ", size=13, color=TODAY_COLOR, weight="heavy")
                                else:
                                    w.text(f" {day_num:02d} ", size=13, color=DATE_TEXT_COLOR, weight="bold")

        w.spacer()
        w.divider()

        with w.hstack():
            try:
                w.progress(year_progress)._set_color(ACCENT_COLOR)
            except:
                pass
            w.text(f"  {int(year_progress*100)}%", size=13, color=SECONDARY_TEXT_COLOR, weight="bold")
        
        with w.hstack():
            w.icon("quote.bubble.fill", size=14, color=ACCENT_COLOR)
            quote = get_hitokoto()
            if len(quote) > QUOTE_MAX_LENGTH:
                short_quote = quote[:QUOTE_MAX_LENGTH].rsplit("，", 1)[0].rsplit("。", 1)[0]
                w.text(f" {short_quote}...", size=12, color=SECONDARY_TEXT_COLOR)
            else:
                w.text(f" {quote}", size=12, color=SECONDARY_TEXT_COLOR)
            w.spacer()

    w.render()
    widget.show(w)

if __name__ == "__main__":
    build()