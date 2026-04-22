import ui
import requests
import storage
import dialogs

# ===== 接口 =====
API = "http://api.yujn.cn/api/zzxjj.php"

# ===== 获取真实视频 =====
def get_real_url():
    try:
        r = requests.get(API, timeout=10)

        # 跳转地址
        if r.url != API:
            return r.url

        # 返回文本是URL
        if r.text.startswith("http"):
            return r.text.strip()

    except Exception as e:
        print("获取失败:", e)

    return None

# ===== HTML播放器 =====
def build_html(url):
    return f"""
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    </head>
    <body style="margin:0;background:black;">
    <video src="{url}" autoplay controls playsinline webkit-playsinline
    style="width:100%;height:100%;object-fit:cover;"></video>
    </body>
    </html>
    """

# ===== 主程序 =====
class VideoApp(ui.View):

    def __init__(self):
        super().__init__()

        self.background_color = "black"

        # 播放器
        self.web = ui.WebView(frame=self.bounds, flex="WH")
        self.add_subview(self.web)
        # 按钮
        self.button = ui.Button(title="切换视频", frame=(0, 0, 150, 50))  # 初始位置设为 (0, 0)
        self.button.action = self.play_video
        self.add_subview(self.button)

        # 首次运行显示使用说明
        
        dialogs.alert("使用说明", "欢迎使用本应用！\n刷新视频点击切换视频\n播放后找不到切换按钮点击右上X按钮\n换视频较慢!")

    # ===== 播放视频 =====
    def play_video(self, sender):
        url = get_real_url()
        if url:
            print("播放:", url)
            self.web.load_html(build_html(url))
        else:
            print("无法获取视频 URL")

# ===== 启动 =====
if __name__ == "__main__":
    
    v = VideoApp()
    w, h = ui.get_screen_size()
    v.frame = (0, 0, w, h)
    # 设置按钮位置为屏幕中心，并以模态形式显示
    v.present("sheet", animated=True, hide_title_bar=True)