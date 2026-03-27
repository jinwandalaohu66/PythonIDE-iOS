from widget import Widget, family, SMALL, MEDIUM, LARGE
import datetime
import ujson
import ssl

# 从网络获取古诗词名句
def get_quote():
    try:
        import urllib.request
        
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        opener = urllib.request.build_opener(
            urllib.request.HTTPSHandler(context=ctx)
        )
        
        req = urllib.request.Request(
            'https://v1.jinrishici.com/all.json',
            headers={
                'Accept': 'application/json',
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS like Mac OS X) AppleWebKit/605.1.15'
            }
        )
        
        response = opener.open(req, timeout=10)
        
        if response.status == 200:
            raw_data = response.read()
            data = ujson.loads(raw_data)
            content = data['content']
            origin = data['origin']
            author = data['author']
            category = data['category']
            return content, f"「{origin}」{author}", category
    except Exception as e:
        print(f"获取诗词失败: {e}")
    
    return None, None, None

quote, author, category = get_quote()

# 配色方案
bg = ("#F8FAFC", "#0F172A")
card_bg = ("#F1F5F9", "#1E293B")
primary = ("#0F172A", "#F8FAFC")
secondary = ("#475569", "#94A3B8")
weak = ("#94A3B8", "#64748B")
accent = ("#8B5CF6", "#A78BFA")

w = Widget(background=bg, padding=14)

if family == SMALL:
    with w.vstack(spacing=0, align="center"):
        w.spacer()
        w.icon("pencil.and.outline", size=20, color=accent)
        w.spacer(6)
        w.text(quote if quote else "加载中...", size=15, weight="medium", color=primary,
               max_lines=3, align="center")
        w.spacer(4)
        w.text(author if author else "", size=11, color=secondary, align="center")
        w.spacer()

elif family == MEDIUM:
    with w.vstack(spacing=0):
        w.spacer()
        with w.hstack(spacing=0):
            with w.vstack(spacing=0, align="center"):
                w.spacer()
                w.icon("pencil.and.outline", size=28, color=accent)
                w.spacer(6)
                w.text("古诗词", size=11, color=weak)
                w.spacer()
            w.spacer(12)
            with w.vstack(spacing=4, align="leading"):
                w.spacer()
                w.text(quote if quote else "网络不可用", size=16, weight="medium", color=primary,
                       max_lines=3)
                w.text(author if author else "", size=12, color=secondary)
                w.spacer()
        w.spacer(8)
        w.text(category if category else "", size=11, color=weak, align="trailing")
        w.spacer()

else:
    with w.vstack(spacing=0):
        w.spacer()
        with w.hstack(spacing=8):
            w.icon("pencil.and.outline", size=22, color=accent)
            w.text("每日诗词", size=18, weight="semibold",
                   color=("#334155", "#E2E8F0"))
            w.spacer()
            w.text(datetime.datetime.now().strftime("%Y/%m/%d"), size=13, color=weak)
        w.spacer(16)
        
        with w.card(background=card_bg, corner_radius=12, padding=16, spacing=0):
            w.text(quote if quote else "无法获取诗词，请检查网络连接", size=20, weight="medium", color=primary,
                   max_lines=4)
            w.spacer(10)
            w.text(author if author else "", size=14, color=secondary)
        
        w.spacer()
        
        with w.hstack(spacing=0):
            w.icon("leaf.fill", size=12, color="#10B981")
            w.spacer(6)
            w.text(category if category else "诗意的栖居", size=12, color=weak)
            w.spacer()
        
        w.spacer()

w.render()