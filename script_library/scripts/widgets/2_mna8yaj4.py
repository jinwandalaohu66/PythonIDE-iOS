from widget import Widget
from datetime import datetime, date, timedelta

LUNAR_FESTIVALS = {
    "春节": {2026: (2,17), 2027: (2,6), 2028: (1,26), 2029: (2,13), 2030: (2,3)},
    "端午节": {2026: (6,19), 2027: (6,9), 2028: (5,28), 2029: (6,16), 2030: (6,5)},
    "七夕节": {2026: (8,20), 2027: (8,9), 2028: (7,26), 2029: (8,15), 2030: (8,4)},
    "中秋节": {2026: (9,27), 2027: (9,15), 2028: (10,3), 2029: (9,22), 2030: (9,12)},
    "重阳节": {2026: (10,30), 2027: (10,9), 2028: (10,26), 2029: (10,16), 2030: (10,5)},
}

FESTIVAL_CONFIG = [
    {"name": "元旦", "slogan": "新岁伊始，万事可期", "icon": "sparkles", "color": ("#007aff", "#409cff"), "is_lunar": False, "month": 1, "day": 1},
    {"name": "春节", "slogan": "辞旧迎新，岁岁平安", "icon": "gift.fill", "color": ("#e63946", "#ff4757"), "is_lunar": True},
    {"name": "情人节", "slogan": "爱意随风起，浪漫不停歇", "icon": "heart.fill", "color": ("#ff6b81", "#ff85a1"), "is_lunar": False, "month": 2, "day": 14},
    {"name": "清明节", "slogan": "清明踏青，不负春光", "icon": "leaf.fill", "color": ("#2ecc71", "#34d399"), "is_lunar": False, "month": 4, "day": 5},
    {"name": "劳动节", "slogan": "劳逸结合，快乐放假", "icon": "hammer.fill", "color": ("#f39c12", "#fbbf24"), "is_lunar": False, "month": 5, "day": 1},
    {"name": "端午节", "slogan": "粽有安康，岁岁年年", "icon": "takeoutbag.and.cup.and.straw.fill", "color": ("#16a085", "#2dd4bf"), "is_lunar": True},
    {"name": "七夕节", "slogan": "星河万里，人间欢喜", "icon": "heart.circle.fill", "color": ("#e84393", "#f472b6"), "is_lunar": True},
    {"name": "中秋节", "slogan": "月圆人圆，事事圆满", "icon": "moon.stars.fill", "color": ("#f9ca24", "#fde047"), "is_lunar": True},
    {"name": "国庆节", "slogan": "山河锦绣，国泰民安", "icon": "flag.fill", "color": ("#dc2626", "#ef4444"), "is_lunar": False, "month": 10, "day": 1},
    {"name": "重阳节", "slogan": "登高望远，敬老安康", "icon": "figure.walk", "color": ("#78350f", "#92400e"), "is_lunar": True},
]

QUOTES = [
    "生活不止眼前的苟且,还有诗和远方.--海子",
    "天行健,君子以自强不息.«周易»",
    "路漫漫其修远兮,吾将上下而求索.--屈原",
    "不积跬步,无以至千里.--荀子",
    "静以修身,俭以养德.--诸葛亮",
    "三人行,必有我师焉.--孔子",
    "欲速则不达.--«论语»",
    "长风破浪会有时,直挂云帆济沧海.--李白",
    "海阔凭鱼跃,天高任鸟飞.--«增广贤文»",
    "胜不骄,败不馁.--俗语",
    "天生我材必有用.--李白",
    "莫愁前路无知己,天下谁人不识君.--高适",
    "千里之行,始于足下.--老子",
    "知足者常乐.--老子",
    "宠辱不惊,看庭前花开花落.--«菜根谭»",
    "是非成败转头空.--罗贯中",
    "人生得意须尽欢,莫使金樽空对月.--李白",
    "不以物喜,不以己悲.--范仲淹"
]

now = datetime.now()
today = date.today()
current_year = today.year

processed_festivals = []
for fest in FESTIVAL_CONFIG:
    if fest["is_lunar"]:
        fn = fest["name"]
        m, d = LUNAR_FESTIVALS[fn].get(current_year, LUNAR_FESTIVALS[fn][2026])
    else:
        m, d = fest["month"], fest["day"]
    fd = datetime(current_year, m, d)
    if fd < now:
        next_year = current_year + 1
        if fest["is_lunar"]:
            m, d = LUNAR_FESTIVALS[fn].get(next_year, LUNAR_FESTIVALS[fn][2026])
        fd = datetime(next_year, m, d)
    processed_festivals.append({**fest, "date": fd, "date_text": f"{fd.month}月{fd.day}日", "days_left": (fd - now).days})

processed_festivals.sort(key=lambda x: x["days_left"])
nearest_fest = processed_festivals[0]

daily_quote = QUOTES[(today.month * 31 + today.day) % len(QUOTES)]
daily_quote = daily_quote.replace("--", " —— ").replace("«", "《").replace("»", "》")

accent = nearest_fest["color"]

w = Widget(
    background=("#FFFFFF", "#0B0F1A"),
    padding=15
)

with w.hstack(spacing=0):
    
    with w.vstack(align="leading", spacing=0):
        with w.hstack(spacing=6, align="center"):
            w.icon(nearest_fest["icon"], size=23, color=accent)
            w.text(f"{nearest_fest['date_text']} {nearest_fest['name']}", 
                   size=15.5, weight="semibold", color=("#1f2937", "#f3f4f6"))
        
        w.spacer(14)
        
        with w.hstack(spacing=3, align="center"):
            w.spacer()
            w.text(str(nearest_fest["days_left"]), size=58, weight="black", color=accent)
            w.text("天", size=26, weight="semibold", color=accent)
            w.spacer()
        
        w.spacer(8)
        w.text(nearest_fest["slogan"], size=13.5, weight="medium", 
               color=("#475569", "#cbd5e1"), max_lines=1)
        
        w.spacer(12)
        w.text(daily_quote, size=11.5, color=("#64748b", "#94a3b8"), max_lines=2)

    w.spacer(16)

    with w.vstack(align="leading", spacing=7):
        w.text("即将到来", size=13, weight="semibold", color=("#64748b", "#94a3b8"))
        
        for fest in processed_festivals[1:4]:
            with w.hstack(spacing=9, align="center"):
                w.icon(fest["icon"], size=18, color=fest["color"])
                with w.vstack(spacing=0.5, align="leading"):
                    w.text(f"{fest['date'].month}月{fest['date'].day}日", size=10.5, color=("#64748b", "#94a3b8"))
                    w.text(f"还有 {fest['days_left']} 天 {fest['name'][:2]}", size=13, weight="semibold", color=fest["color"])

w.render(url="calshow://")