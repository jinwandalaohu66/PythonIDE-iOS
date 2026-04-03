
# 2026-4-3 Silence

import requests
from widget import Widget, family, MEDIUM

BLACKLIST = ["死", "杀", "恨", "怨", "哭", "泪", "痛", "苦", "穷", 
             "失败", "绝望", "黑暗", "孤独", "放弃", "离开", "背叛", 
             "悲伤", "痛苦", "哭泣", "受伤", "残忍", "抑郁", "焦虑", "堕落"]

def is_good(text):
    for w in BLACKLIST:
        if w in text:
            return False
    return True

def get_motto():
    categories = ['d',  'i', 'k']
    for _ in range(8):
        try:
            import random
            cat = random.choice(categories)
            url = f"https://v1.hitokoto.cn/?c={cat}"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                text = data.get('hitokoto', '')
                if not text or len(text) < 8 or len(text) > 24:
                    continue
                if not is_good(text):
                    continue
                from_who = data.get('from_who', '')
                from_where = data.get('from', '')
                if from_who and from_where:
                    if from_who in from_where or from_where in from_who:
                        author = from_who if from_who else from_where
                    else:
                        author = f"{from_who} · {from_where}"
                elif from_who:
                    author = from_who
                elif from_where:
                    author = from_where
                else:
                    author = ""
                return text, author
        except:
            pass
    return "每天进步一点点，坚持带来大改变。", "佚名"

def render_widget():
    quote, author = get_motto()
    if len(quote) > 22:
        quote = quote[:20] + "…"
    
    bg_color = ("#FEFCE8", "#1E1A2F")
    w = Widget(background=bg_color, padding=16)
    
    with w.vstack(spacing=10):
        with w.hstack():
            w.icon("heart.text.square.fill", size=18, color="#E63946")
            w.text("每日名言", size=14, weight="semibold", color=("#1E293B", "#E2E8F0"))
            w.spacer()
            w.icon("leaf.fill", size=12, color="#A3E635")
        
        w.divider(color=("#E2E8F0", "#334155"))
        
        with w.hstack():
            w.icon("quote.opening", size=14, color=("#94A3B8", "#64748B"))
            w.spacer(4)
        w.spacer(4)
        
        w.text(f"「{quote}」", size=15, weight="medium", 
               color=("#0F172A", "#F1F5F9"), align="left", max_lines=3)
        
        w.spacer(4)
        
        if author:
            w.text(f"—— {author}", size=11, color=("#64748B", "#94A3B8"), 
                   align="right", max_lines=1)
        else:
            w.text(" 给今天一点力量 ", size=10, color=("#94A3B8", "#6B7280"), align="center")
    
    w.render()

if family == MEDIUM:
    render_widget()
else:
    w = Widget(background=("#FFFFFF", "#0B0F1A"), padding=16)
    with w.vstack(align="center", spacing=8):
        w.icon("heart.text.square", size=30, color="#E63946")
        w.text("请使用中尺寸小组件", size=14, weight="semibold", 
               color=("#111", "#EEE"), align="center")
    w.render()