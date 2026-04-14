from widget import Widget, family, SMALL, MEDIUM, LARGE
from datetime import datetime, date

# 年薪（元），修改此數值
ANNUAL_SALARY = 1_000_000

# 台灣國定假日 2026
TW_HOLIDAYS_2026 = {
    date(2026, 1, 1),   # 元旦
    date(2026, 2, 16),  # 除夕
    date(2026, 2, 17),  # 春節
    date(2026, 2, 18),  # 春節
    date(2026, 2, 19),  # 春節
    date(2026, 2, 20),  # 春節
    date(2026, 2, 28),  # 和平紀念日
    date(2026, 4, 3),   # 兒童節
    date(2026, 4, 4),   # 清明節
    date(2026, 5, 1),   # 勞動節
    date(2026, 6, 19),  # 端午節
    date(2026, 9, 25),  # 中秋節
    date(2026, 10, 9),  # 國慶日補假
    date(2026, 10, 10), # 國慶日
}

TW_HOLIDAYS = TW_HOLIDAYS_2026


# 判斷是否為工作日，排除週六日與國定假日
def is_workday(d):
    if d.weekday() >= 5:  # 週六=5, 週日=6
        return False
    if d in TW_HOLIDAYS:
        return False
    return True


# 計算指定年份的總工作天數
def count_workdays_in_year(year):
    d = date(year, 1, 1)
    count = 0
    while d.year == year:
        if is_workday(d):
            count += 1
        d = date.fromordinal(d.toordinal() + 1)
    return count


# 計算今天已賺的金額與年度累積
def calc_earned_today(salary):
    now = datetime.now()
    today = now.date()
    year = today.year

    total_workdays = count_workdays_in_year(year)
    daily_salary = salary / total_workdays

    # 今年元旦到昨天的工作日數
    days_elapsed = (today - date(year, 1, 1)).days
    workdays_before_today = sum(
        1 for i in range(days_elapsed)
        if is_workday(date.fromordinal(date(year, 1, 1).toordinal() + i))
    )

    today_is_workday = is_workday(today)

    if today_is_workday:
        # 工作時間 08:20 ~ 17:45
        work_start = now.replace(hour=8, minute=20, second=0, microsecond=0)
        work_end = now.replace(hour=17, minute=45, second=0, microsecond=0)

        if now < work_start:
            fraction = 0.0
        elif now >= work_end:
            fraction = 1.0
        else:
            elapsed = (now - work_start).total_seconds()
            total = (work_end - work_start).total_seconds()
            fraction = elapsed / total

        today_earned = daily_salary * fraction
    else:
        fraction = 0.0
        today_earned = 0.0

    ytd_earned = (workdays_before_today + (fraction if today_is_workday else 0)) * daily_salary

    return {
        "today_earned": today_earned,
        "ytd_earned": ytd_earned,
        "daily_salary": daily_salary,
        "total_workdays": total_workdays,
        "today_is_workday": today_is_workday,
        "fraction": fraction,
        "now": now,
    }


# 執行計算
info = calc_earned_today(ANNUAL_SALARY)
now = info["now"]

fmt_today = f"${info['today_earned']:,.0f}"
fmt_ytd = f"${info['ytd_earned']:,.0f}"
fmt_daily = f"${info['daily_salary']:,.0f}"
progress_val = info["fraction"]

day_status = "工作日 💼" if info["today_is_workday"] else "假日 🎉"
time_str = now.strftime("%H:%M")
date_str = now.strftime("%m/%d")

# 工作日顯示綠色進度條，假日顯示灰色
bar_color = "#4ADE80" if info["today_is_workday"] else "#6B7280"

# 建立 Widget，深色背景
w = Widget(background=("#0F172A", "#0F172A"), padding=0)

if family == SMALL:
    with w.vstack(spacing=6, padding=12):
        w.text("今日薪資", size=11, color="#94A3B8", weight="medium")
        w.text(fmt_today, size=22, color="#4ADE80", weight="bold")
        w.spacer(length=2)
        w.progress(progress_val, color=bar_color, height=5, track_color="#1E293B")
        w.text(f"{date_str} {time_str}  {day_status}", size=10, color="#64748B")

elif family == LARGE:
    with w.vstack(spacing=10, padding=16):
        # 標題列
        with w.hstack(spacing=6):
            w.icon("dollarsign.circle.fill", size=16, color="#4ADE80")
            w.text("薪資追蹤器", size=14, color="#CBD5E1", weight="semibold")
            w.spacer()
            w.text(f"{date_str}  {time_str}", size=12, color="#64748B")

        w.divider(color="#1E293B")

        # 今日薪資
        w.text("今日已賺", size=12, color="#94A3B8")
        w.text(fmt_today, size=36, color="#4ADE80", weight="bold")
        w.text(day_status, size=12, color="#94A3B8")

        # 進度條與百分比
        w.progress(progress_val, color=bar_color, height=8, track_color="#1E293B")
        w.text(f"工作進度 {progress_val * 100:.0f}%", size=11, color="#64748B", align="trailing")

        w.spacer(length=4)
        w.divider(color="#1E293B")

        # 年度統計三欄
        with w.hstack(spacing=8):
            with w.card(background="#1E293B", corner_radius=10, padding=10):
                w.text("年薪", size=11, color="#94A3B8")
                w.text(f"${ANNUAL_SALARY:,}", size=14, color="white", weight="bold")
            with w.card(background="#1E293B", corner_radius=10, padding=10):
                w.text("日薪", size=11, color="#94A3B8")
                w.text(fmt_daily, size=14, color="white", weight="bold")
            with w.card(background="#1E293B", corner_radius=10, padding=10):
                w.text("年度累積", size=11, color="#94A3B8")
                w.text(fmt_ytd, size=14, color="#FCD34D", weight="bold")

else:
    # MEDIUM 尺寸（預設）
    with w.vstack(spacing=0, padding=6):
        # 上半：今日薪資 + 時間狀態
        with w.hstack():
            with w.vstack(spacing=2, align="leading"):
                w.text("今日薪資", size=15, color="#94A3B8", weight="medium")
                w.text(fmt_today, size=44, color="#4ADE80", weight="bold")
            w.spacer()
            with w.vstack(spacing=3, align="trailing"):
                w.text(date_str, size=16, color="#64748B", weight="medium")
                w.text(time_str, size=23, color="#CBD5E1", weight="semibold")
                w.text(day_status, size=15, color="#94A3B8")

        w.spacer()

        # 進度條
        w.progress(progress_val, color=bar_color, height=8, track_color="#1E293B")

        w.spacer(length=6)

        # 下半：日薪 + 年度累計
        with w.hstack(padding=2):
            with w.vstack(spacing=2, align="leading"):
                w.text("日薪", size=14, color="#64748B")
                w.text(fmt_daily, size=20, color="#CBD5E1", weight="semibold")
            w.spacer()
            with w.vstack(spacing=2, align="trailing"):
                w.text("年度累積", size=14, color="#64748B")
                w.text(fmt_ytd, size=20, color="#FCD34D", weight="semibold")

w.render()
