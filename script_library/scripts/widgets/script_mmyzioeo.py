# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～

# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
from widget import Widget
from datetime import datetime, date

w = Widget()  # 原生背景，系统自动深浅模式

now = datetime.now()
today = date.today()
current_year = today.year


year_start = date(current_year, 1, 1)
days_in_year = (date(current_year + 1, 1, 1) - year_start).days
days_passed = (today - year_start).days
progress = days_passed / days_in_year if days_in_year > 0 else 0

festivals = [
    (1, 1, "元旦", "新年快乐！今年继续摆烂吗？"),
    (2, 14, "情人节", "单身狗别哭，晚上要深深惹哦～"),
    (4, 5, "清明节", "扫完墓记得踏青啊,别只顾着emo"),
    (5, 1, "劳动节", "放假了！该卷的卷,该摸的摸"),
    (6, 10, "端午节", "粽子管够！赛龙舟我在岸上吃瓜"),
    (8, 20, "七夕", "中国版情人节，脱单的冲！单身的养神兽"),
    (9, 25, "中秋节", "月饼别吃太多,赏月许愿发财"),
    (10, 1, "国庆节", "黄金周！堵高速上思考人生？"),
    (10, 15, "重阳节", "老人节！爬山？我家喝茶敬老"),
    (2, 10, "春节", "过年好！红包拿来！今年发大财！")
]

next_fests = []
for month, day, name, egg in festivals:
    fest_date = datetime(today.year, month, day)
    if fest_date < now:
        fest_date = datetime(today.year + 1, month, day)
    next_fests.append((fest_date, name, egg))

next_fest = min(next_fests, key=lambda x: x[0])
days_to_fest = (next_fest[0] - now).days
name = next_fest[1]
egg = next_fest[2]
fest_date_str = f"{next_fest[0].month}月{next_fest[0].day}日"


quotes = [
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
quote = quotes[(today.month * 31 + today.day) % len(quotes)]

with w.vstack(spacing=6, padding=10, align="leading"):
    w.icon("escape", size=22, color="#ff9500")
    
    w.text(f"下个节日：{fest_date_str} {name}", size=17, weight="bold", color="#1f2937")
    
    with w.hstack(spacing=15, align="top"):  
        with w.vstack(spacing=15.5, align="leading"):
            w.text(f"倒计时 {days_to_fest} 天", size=28, weight="heavy", color="#e63946")
            w.text(egg, size=13.5, color="#4b5563")
            w.text(quote, size=13.5, weight="bold", color="#666666")
        
        
        with w.vstack(spacing=2, align="center"):
            w.gauge(progress, size=60, color="#10b981", track_color="#e5e7eb")
            w.text(f"{int(progress*100)}%", size=20, weight="bold", color="#10b981")  
            w.text(f"{current_year} 已过", size=12, color="#4b5563")  

w.render()