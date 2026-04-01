from widget import Widget, family, MEDIUM
from datetime import datetime, date


BACKGROUND_COLOR = ("#F8F9FA", "#1C1C1E")
TITLE_COLOR = ("#2C3E50", "#FFFFFF")
DIVIDER_COLOR = ("#DEE2E6", "#3A3A3C")
NAME_COLOR = ("#212529", "#FFFFFF")
FUTURE_COLOR = ("#2ECC71", "#6EE7B7")
TODAY_COLOR = ("#F1C40F", "#FFD966")
PAST_COLOR = ("#E74C3C", "#FF6B6B")
AGE_COLOR = ("#E67E22", "#F39C12")

ICON_COLORS = {
    "birthday.cake.fill": ("#FF6B6B", "#FF9F4A"),
    "person.fill": ("#4A90E2", "#6AB0FF"),
    "heart.fill": ("#E8436E", "#FF6B8B"),
    "graduationcap.fill": ("#9B6DFF", "#B78CFF"),
    "star.fill": ("#FFC107", "#FFD966"),
    "gift.fill": ("#38B2AC", "#6EE7B7"),
    "default": ("#8E8E93", "#AEAEB2")
}

# 纪念日列表（直接在下面修改）
# 每个条目包含：name(名称), date(YYYY-MM-DD), icon(SF Symbol), type(类型)
# 类型说明：
#   - "yearly" : 每年重复（如生日、纪念日）
#   - "age"    : 累计天数（如“来到这个世界”）
#   - "once"   : 一次性固定日期（如某个活动截止日）
ANNIVERSARIES = [
    {
        "name": "生日",
        "date": "2000-01-01",
        "icon": "birthday.cake.fill",
        "type": "yearly"
    },
    {
        "name": "来到这个世界",
        "date": "2000-01-01",
        "icon": "person.fill",
        "type": "age"
    },
    {
        "name": "恋爱纪念日",
        "date": "2022-05-20",
        "icon": "heart.fill",
        "type": "yearly"
    },
    {
        "name": "毕业日",
        "date": "2024-07-01",
        "icon": "graduationcap.fill",
        "type": "yearly"
    }
]

ICON_SIZE = 20
TITLE_FONT_SIZE = 16
NAME_FONT_SIZE = 14
DAYS_FONT_SIZE = 12
SPACING = 10
PADDING = 12


def days_since_birth(birth_date):
    today = datetime.now().date()
    try:
        birth = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except:
        return None
    return (today - birth).days

def get_next_yearly(month, day):
    today = datetime.now().date()
    try:
        target_this_year = date(today.year, month, day)
    except ValueError:
        return None
    if target_this_year >= today:
        return target_this_year
    else:
        try:
            return date(today.year + 1, month, day)
        except ValueError:
            return None

def days_diff(item):
    if item['type'] == 'age':
        days = days_since_birth(item['date'])
        if days is None:
            return None, None
        return days, f" {days} 天"
    elif item['type'] == 'yearly':
        try:
            parts = item['date'].split('-')
            if len(parts) != 3:
                return None, None
            month, day = int(parts[1]), int(parts[2])
            next_date = get_next_yearly(month, day)
            if next_date is None:
                return None, None
            delta = (next_date - datetime.now().date()).days
            if delta == 0:
                text = "就是今天！"
            elif delta > 0:
                text = f"还有{delta} 天"
            else:
                text = f"已过 {-delta} 天"
            return delta, text
        except:
            return None, None
    else:
        try:
            target = datetime.strptime(item['date'], "%Y-%m-%d").date()
            delta = (target - datetime.now().date()).days
            if delta == 0:
                text = "就是今天！"
            elif delta > 0:
                text = f"还有 {delta} 天"
            else:
                text = f"已过 {-delta} 天"
            return delta, text
        except:
            return None, None

def get_icon_color(icon_name):
    return ICON_COLORS.get(icon_name, ICON_COLORS["default"])

def get_status_color(delta, item_type):
    if item_type == 'age':
        return AGE_COLOR
    if delta == 0:
        return TODAY_COLOR
    elif delta > 0:
        return FUTURE_COLOR
    else:
        return PAST_COLOR

def render_widget():
    items = []
    for a in ANNIVERSARIES:
        delta, text = days_diff(a)
        if delta is not None:
            items.append({
                'name': a['name'],
                'delta': delta,
                'text': text,
                'icon': a.get('icon', 'calendar'),
                'type': a['type']
            })

    items.sort(key=lambda x: (x['type'] == 'age', abs(x['delta'])))
    display_items = items[:4]

    w = Widget(background=BACKGROUND_COLOR)

    with w.vstack(spacing=8, padding=PADDING):
        with w.hstack(spacing=4):
            w.icon("calendar", size=ICON_SIZE-2, color=TITLE_COLOR, weight="medium")
            w.text("纪念日", size=TITLE_FONT_SIZE, weight="semibold", color=TITLE_COLOR)

        w.divider(color=DIVIDER_COLOR)

        if not display_items:
            with w.hstack():
                w.icon("info.circle", size=ICON_SIZE-2, color=("#6C757D", "#8E8E93"))
                w.text("暂无纪念日，请在脚本中添加", size=12, color=("#6C757D", "#8E8E93"), align="center")
        else:
            for item in display_items:
                with w.hstack(spacing=SPACING, align="center"):
                    icon_light, icon_dark = get_icon_color(item['icon'])
                    icon_color = (icon_light, icon_dark)
                    w.icon(item['icon'], size=ICON_SIZE, color=icon_color, weight="regular")

                    w.text(item['name'], size=NAME_FONT_SIZE, weight="medium", color=NAME_COLOR, max_lines=1)

                    w.spacer()

                    status_color = get_status_color(item['delta'], item['type'])
                    w.text(item['text'], size=DAYS_FONT_SIZE, color=status_color, weight="medium", max_lines=1)

    w.render(url="pythonide://")

if __name__ == '__main__':
    try:
        family
    except NameError:
        family = MEDIUM
    render_widget()