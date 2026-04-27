# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
# ==============================================
#  MINDOS Novus 2.3
#  代号：Novus | 现代Windows风格 · 全Emoji图形化
#  默认离线模式 · 可手动联网 · 完善系统逻辑
#  纯字符UI + 图标美化 · 全功能文件/网络/工具
# ==============================================
import os
import time
import platform
import random
import datetime
import shutil

# 联网库兼容适配
try:
    import requests
    NET_AVAILABLE = True
except ImportError:
    NET_AVAILABLE = False

# ========== 全局系统变量 ==========
INTERNET_ONLINE = False  # 默认离线🔴

# ========== 安全清屏（双兼容） ==========
def ui_clear():
    try:
        if hasattr(os, "system"):
            os.system("cls" if os.name == "nt" else "clear")
        else:
            print("\n" * 40)
    except:
        print("\n" * 40)

# 分割线
def ui_line():
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

# ===================== 🔧 离线基础软件 =====================
def app_calculator():
    ui_clear()
    ui_line()
    print("      🧮 MINDOS 计算器")
    ui_line()
    try:
        exp = input("⌨️ 输入运算表达式：")
        res = eval(exp)
        print(f"✅ 运算结果：{res}")
    except Exception:
        print("❌ 表达式格式错误，计算失败")
    input("\n🔙 按下回车返回桌面...")

def app_notepad():
    ui_clear()
    ui_line()
    print("      📝 MINDOS 记事本")
    ui_line()
    filename = input("📄 输入文件名称：")
    content = ""
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        print("\n📃 原有文档内容：")
        print(content)
    print("\n✏️ 输入新编辑内容：")
    new_text = input()
    with open(filename, "w", encoding="utf-8") as f:
        f.write(new_text)
    print("💾 ✅ 文档保存完成")
    input("\n🔙 按下回车返回桌面...")

def app_sysinfo():
    ui_clear()
    ui_line()
    print("      💻 本机硬件信息")
    ui_line()
    print(f"🖥️  运行平台：{platform.system()}")
    print(f"📦 系统版本：{platform.release()}")
    print(f"🐍 Python环境：{platform.python_version()}")
    print(f"📂 当前目录：{os.getcwd()}")
    ui_line()
    input("🔙 按下回车返回桌面...")

def app_clock():
    ui_clear()
    ui_line()
    print("      🕒 本地日历时钟")
    ui_line()
    now = datetime.datetime.now()
    week_arr = ["星期一","星期二","星期三","星期四","星期五","星期六","星期日"]
    print(f"📅 当前日期：{now.year}-{now.month}-{now.day}")
    print(f"⌚ 当前时间：{now.hour}:{now.minute}:{now.second}")
    print(f"📆 今日星期：{week_arr[now.weekday()]}")
    ui_line()
    input("🔙 按下回车返回桌面...")

def app_pwdgen():
    ui_clear()
    ui_line()
    print("      🔐 随机密码生成器")
    ui_line()
    char_pool = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#$&_"
    try:
        length = int(input("📏 设置密码长度："))
        password = "".join(random.sample(char_pool, length))
        print(f"🔑 生成密码：{password}")
    except:
        print("❌ 请输入合法数字")
    input("\n🔙 按下回车返回桌面...")

def app_wordcount():
    ui_clear()
    ui_line()
    print("      📊 文本字数统计")
    ui_line()
    text = input("📝 粘贴或输入文本：")
    all_len = len(text)
    clean_len = len(text.replace(" ",""))
    print(f"📜 含空格字符：{all_len}")
    print(f"📖 无空格字符：{clean_len}")
    input("\n🔙 按下回车返回桌面...")

# ===================== 📁 文件管理系统 =====================
def file_list():
    ui_clear()
    ui_line()
    print("      📂 文件资源管理器")
    ui_line()
    item_list = os.listdir()
    for item in item_list:
        if os.path.isdir(item):
            print(f"📁 {item}")
        else:
            print(f"📄 {item}")
    ui_line()
    input("🔙 按下回车返回...")

def file_create():
    ui_clear()
    ui_line()
    name = input("📄 输入新建文件名：")
    if not os.path.exists(name):
        with open(name, "w", encoding="utf-8") as f:
            f.write("")
        print("✅ 📄 文件创建成功")
    else:
        print("❌ 文件已存在")
    input("🔙 按下回车返回...")

def file_read():
    ui_clear()
    ui_line()
    name = input("📖 输入需要读取的文件：")
    if os.path.isfile(name):
        with open(name, "r", encoding="utf-8") as f:
            print("\n📃 文件内容：\n", f.read())
    else:
        print("❌ 文件不存在")
    input("\n🔙 按下回车返回...")

def file_delete():
    ui_clear()
    ui_line()
    name = input("🗑️ 输入需要删除的文件：")
    if os.path.isfile(name):
        os.remove(name)
        print("✅ 🗑️ 文件已永久删除")
    else:
        print("❌ 文件不存在")
    input("🔙 按下回车返回...")

def file_rename():
    ui_clear()
    ui_line()
    old_name = input("📛 原名称：")
    new_name = input("📛 新名称：")
    if os.path.exists(old_name):
        os.rename(old_name, new_name)
        print("✅ 📛 重命名完成")
    else:
        print("❌ 目标不存在")
    input("🔙 按下回车返回...")

def dir_create():
    ui_clear()
    ui_line()
    folder = input("📁 输入文件夹名称：")
    if not os.path.exists(folder):
        os.mkdir(folder)
        print("✅ 📁 文件夹创建成功")
    else:
        print("❌ 文件夹已存在")
    input("🔙 按下回车返回...")

def dir_delete():
    ui_clear()
    ui_line()
    folder = input("🗑️ 输入要删除的文件夹：")
    if os.path.isdir(folder):
        shutil.rmtree(folder)
        print("✅ 🗑️ 文件夹已彻底清除")
    else:
        print("❌ 文件夹不存在")
    input("🔙 按下回车返回...")

# ===================== ⚙️ 系统设置 & 关于本机 =====================
def app_about():
    ui_clear()
    ui_line()
    print("          ℹ️ 关于 MINDOS")
    ui_line()
    print("💻 系统名称：MINDOS")
    print("📌 版本代号：Novus 2.3")
    print("🌐 运行模式：默认离线 | 可手动联机")
    print("⚙️ 内核环境：Python 原生轻量构建")
    print("🎨 界面风格：现代Windows视觉布局 + Emoji图标")
    print("📁 核心能力：完整文件管理 + 多工具 + 网络服务")
    print("📝 开发定位：轻量化自制桌面操作系统")
    ui_line()
    input("🔙 按下回车返回桌面...")

def app_settings():
    while True:
        ui_clear()
        ui_line()
        print("      ⚙️ MINDOS 系统设置")
        ui_line()
        print("1. 📂 查看当前工作目录")
        print("2. ⬆️ 返回上级根目录")
        print("3. 🧩 查看系统架构信息")
        print("0. 🔙 退出设置面板")
        ui_line()
        sel = input("⌨️ 请选择设置项：")
        if sel == "1":
            print(f"\n📂 当前目录：{os.getcwd()}")
            input("🔄 回车继续...")
        elif sel == "2":
            os.chdir("../")
            print("✅ 已返回上级目录")
            input("🔄 回车继续...")
        elif sel == "3":
            print(f"🧬 系统架构：{platform.machine()}")
            print(f"⚡ 处理器：{platform.processor()}")
            input("🔄 回车继续...")
        elif sel == "0":
            break
        else:
            print("❌ 无效选项，请重新选择")
            time.sleep(1)

# ===================== 🌐 网络核心控制 =====================
def net_connect():
    global INTERNET_ONLINE
    ui_clear()
    ui_line()
    print("      🌐 网络连接中心")
    ui_line()
    if not NET_AVAILABLE:
        print("❌ 缺少网络依赖库，无法联网")
        print("💡 请执行：pip install requests")
        input("\n🔙 回车返回...")
        return
    try:
        requests.get("https://httpbin.org/text", timeout=5)
        INTERNET_ONLINE = True
        print("✅ 🌐 互联网连接成功")
        print("🟢 系统已切换至【联机模式】")
    except Exception:
        INTERNET_ONLINE = False
        print("❌ 网络连接失败，请检查设备网络")
    input("\n🔙 回车返回...")

def net_disconnect():
    global INTERNET_ONLINE
    INTERNET_ONLINE = False
    ui_clear()
    ui_line()
    print("❌ 已断开互联网连接")
    print("🔴 系统切回【离线默认模式】")
    ui_line()
    input("🔙 回车返回...")

# ===================== 🛜 联网专属应用 =====================
def net_time_sync():
    if not INTERNET_ONLINE:
        ui_clear()
        ui_line()
        print("⚠️  当前为离线模式")
        print("💡 请先接入互联网再使用该功能")
        ui_line()
        input("🔙 回车返回...")
        return
    ui_clear()
    ui_line()
    print("      🕰️ 网络时间同步")
    ui_line()
    try:
        res = requests.get("https://time.163.com",timeout=5)
        print("✅ 网络时间获取成功，已完成校对")
    except:
        print("❌ 网络时间接口访问失败")
    ui_line()
    input("🔙 回车返回...")

def net_web_text():
    if not INTERNET_ONLINE:
        ui_clear()
        ui_line()
        print("⚠️  当前为离线模式")
        print("💡 请先接入互联网再使用该功能")
        ui_line()
        input("🔙 回车返回...")
        return
    ui_clear()
    ui_line()
    print("      🌍 简易网页文本浏览器")
    ui_line()
    print("💡 测试推荐：")
    print("1.一言短句：https://v1.hitokoto.cn/?encode=text")
    print("2.测试文本：https://httpbin.org/text")
    url = input("\n🔗 输入网址：")
    try:
        page = requests.get(url, timeout=10, headers={"User-Agent":"MINDOS/2.3"})
        print("\n📄 网页内容预览：")
        print(page.text[:600] + "...")
    except:
        print("❌ 无法访问该网址或链接失效")
    input("\n🔙 回车返回...")

def net_ip_info():
    if not INTERNET_ONLINE:
        ui_clear()
        ui_line()
        print("⚠️  当前为离线模式")
        print("💡 请先接入互联网再使用该功能")
        ui_line()
        input("🔙 回车返回...")
        return
    ui_clear()
    ui_line()
    print("      🌐 公网IP信息查询")
    ui_line()
    try:
        data = requests.get("https://httpbin.org/ip",timeout=5).json()
        print(f"🌍 本机公网IP：{data['origin']}")
    except:
        print("❌ IP信息获取失败")
    ui_line()
    input("🔙 回车返回...")

# ===================== 🖥️ MINDOS 主桌面（Windows布局） =====================
def mindos_main():
    while True:
        ui_clear()
        net_status = "🔴 离线模式" if not INTERNET_ONLINE else "🟢 联机模式"
        print("""
  __  __  ___  _   _  ____   ___
 |  \/  ||_ _|| \ | || __ ) / _ \\
 | |\/| | | | |  \| ||  _ \| | | |
 | |  | | | | | |\  || |_) | |_| |
 |_|  |_|___||_| \_||____/ \___/

      M I N D O S  Novus 2.3
        """)
        print(f"        📶 运行状态：{net_status}")
        ui_line()
        print("📁 【文件资源管理】")
        print("1.文件浏览  2.新建文件  3.读取文件")
        print("4.删除文件  5.重命名    6.新建文件夹")
        print("7.删除文件夹")
        ui_line()
        print("🧰 【常用离线工具】")
        print("8.记事本    9.计算器   10.本地时钟")
        print("11.密码生成 12.字数统计")
        ui_line()
        print("⚙️ 【系统管理】")
        print("13.关于本机 14.系统设置")
        ui_line()
        print("🌐 【网络控制中心】")
        print("15.接入互联网  16.断开互联网")
        ui_line()
        print("🛜 【联网专属应用】")
        print("17.网络时间校对 18.网页文本浏览 19.IP地址查询")
        ui_line()
        print("❌ 0. 关闭 MINDOS 系统")
        ui_line()

        choose = input("⌨️ 请输入功能编号：")
        if choose == "1":file_list()
        elif choose == "2":file_create()
        elif choose == "3":file_read()
        elif choose == "4":file_delete()
        elif choose == "5":file_rename()
        elif choose == "6":dir_create()
        elif choose == "7":dir_delete()
        elif choose == "8":app_notepad()
        elif choose == "9":app_calculator()
        elif choose == "10":app_clock()
        elif choose == "11":app_pwdgen()
        elif choose == "12":app_wordcount()
        elif choose == "13":app_about()
        elif choose == "14":app_settings()
        elif choose == "15":net_connect()
        elif choose == "16":net_disconnect()
        elif choose == "17":net_time_sync()
        elif choose == "18":net_web_text()
        elif choose == "19":net_ip_info()
        elif choose == "0":
            ui_clear()
            print("🛑 MINDOS Novus 2.3 正在关闭...")
            time.sleep(0.8)
            print("👋 感谢使用 MINDOS 自制操作系统")
            break
        else:
            print("❌ 输入编号无效，请重新操作")
            time.sleep(1)

if __name__ == "__main__":
    mindos_main()
	