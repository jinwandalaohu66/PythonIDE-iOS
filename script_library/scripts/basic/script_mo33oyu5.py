import random
import time

def slow_print(text, delay=0.04):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()

def start_game():
    slow_print("=== 新月之下 · 黑水之城 ===", 0.06)
    slow_print("你是韩雅诺。")
    slow_print("深夜，你站在阿卡普尔科的街头。")
    slow_print("海风带着血腥味，城市在毒枭的阴影里沉睡。")
    slow_print("你来找你的男朋友——陈海鸥。")
    slow_print("他失踪了。")
    print()

    slow_print("你面前有三条路：")
    slow_print("1. 走进黑暗的小巷（传闻海鸥最后出现的地方）")
    slow_print("2. 走向海边码头（海鸥常去的地方）")
    slow_print("3. 躲进废弃酒吧（你和海鸥曾一起待过的据点）")

    while True:
        choice = input("\n选择（1/2/3）：")
        if choice in ["1", "2", "3"]:
            break
        slow_print("请输入 1、2 或 3。")

    if choice == "1":
        alley_path()
    elif choice == "2":
        dock_path()
    else:
        bar_path()

def alley_path():
    slow_print("\n你走进小巷，黑暗中传来低沉的呼吸声。")
    slow_print("突然，四个黑影拦住了你。")
    slow_print("他们是黑水组织的人。")
    slow_print("其中一人冷笑：“韩雅诺，你在找陈海鸥？”")
    print()
    fight_or_flee()

def dock_path():
    slow_print("\n海风冰冷，海浪拍打着码头。")
    slow_print("你看到远处有一艘船，上面站着一个熟悉的身影——")
    slow_print("是陈海鸥！")
    slow_print("但他被人押着，动弹...