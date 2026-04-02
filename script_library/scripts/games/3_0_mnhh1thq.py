# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
import random
import json
import hashlib
import time

def clear():
    print("\033c", end="")

class 网吧大亨终极版:
    def __init__(self):
        # 基础
        self.钱 = 800
        self.天数 = 1
        self.小时 = 10
        self.排队顾客 = 0
        self.上网价格 = 6
        self.口碑 = 100
        self.会员数 = 0
        self.今日营收 = 0
        self.天气 = ["☀️晴天", "🌧️小雨", "⛈️大雨", "❄️雪天"][random.randint(0,3)]

        # 电脑（现在有等级）
        self.电脑数量 = 6
        self.电脑等级 = 1
        self.电脑使用中 = 0

        # 电脑必须配件（都有等级）
        self.电脑桌等级 = 1
        self.主机等级 = 1
        self.显示器等级 = 1
        self.椅子等级 = 1
        self.鼠标等级 = 1
        self.键盘等级 = 1

        # 街机
        self.街机数量 = 0
        self.街机等级 = 1
        self.街机使用中 = 0

        # 饮料
        self.饮料库存 = 20
        self.饮料成本 = 2
        self.饮料售价 = 5

        # 网管
        self.网管列表 = []
        self.最大网管数 = 5

        # 顾客计时（24小时强制下机）
        self.顾客上机时长 = [0] * self.电脑数量

    # ====================== 存档 ======================
    def 生成存档码(self):
        clear()
        数据 = self.__dict__.copy()
        字符串 = json.dumps(数据, ensure_ascii=False)
        唯一码 = hashlib.sha256((字符串 + str(time.time())).encode()).hexdigest()[:16]
        print("🏪 存档信息".center(50, "="))
        print(f"✅ 存档码：{唯一码}")
        print("💾 存档数据：")
        print(字符串)
        input("\n回车返回…")

    def 读取存档码(self):
        clear()
        try:
            s = input("请粘贴存档数据：\n")
            data = json.loads(s)
            self.__dict__.update(data)
            print("✅ 读档成功！")
        except:
            print("❌ 失败")
        input("回车…")

    # ====================== 时间系统 ======================
    def 时间流逝(self):
        # 电脑计时
        for i in range(self.电脑使用中):
            self.顾客上机时长[i] += 1
        下机 = 0
        for i in range(self.电脑使用中):
            if self.顾客上机时长[i] >= 24:
                下机 += 1
        if 下机 > 0:
            print(f"\n⏰ {下机}人满24小时强制下机")
        self.电脑使用中 -= 下机
        self.顾客上机时长 = self.顾客上机时长[下机:] + [0]*下机

        # 时间推进
        self.小时 += 1
        if self.小时 >= 24:
            self.小时 = 9
            self.天数 += 1
            self.今日营收 = 0
            self.天气 = random.choice(["☀️晴天","🌧️小雨","⛈️大雨","❄️雪天"])

        # 顾客上限40
        来客 = random.randint(1,4)
        if self.天气 == "☀️晴天": 来客 +=2
        if self.口碑>120:来客+=2
        self.排队顾客 = min(self.排队顾客 + max(来客,0), 40)

    def 快进2h(self):
        print("\n⏩快进2小时…")
        self.时间流逝()
        self.时间流逝()
    def 快进3h(self):
        print("\n⏩快进3小时…")
        self.时间流逝()
        self.时间流逝()
        self.时间流逝()

    # ====================== 核心收益 ======================
    def 每台电脑每小时收益(self):
        倍率 = (
            self.电脑等级 * 0.2
            + self.电脑桌等级 * 0.05
            + self.主机等级 * 0.1
            + self.显示器等级 * 0.08
            + self.椅子等级 * 0.05
            + self.鼠标等级 * 0.03
            + self.键盘等级 * 0.03
            + 1
        )
        return round(self.上网价格 * 倍率, 1)

    def 每台街机每小时收益(self):
        return round(8 + self.街机等级 * 3, 1)

    # ====================== 商城（你要的全部在这里） ======================
    def 商城(self):
        while True:
            clear()
            print("🏬【超级商城】".center(50,"="))
            print(f"💰当前金钱：{self.钱}")
            print("1.🖥️买电脑        2.⬆️电脑等级 Lv.{self.电脑等级}")
            print("3.🪑电脑桌 Lv.{self.电脑桌等级}    4.🖥️主机 Lv.{self.主机等级}")
            print("5.🖥️显示器 Lv.{self.显示器等级}  6.🪑椅子 Lv.{self.椅子等级}")
            print("7.🖱️鼠标 Lv.{self.鼠标等级}      8.⌨️键盘 Lv.{self.键盘等级}")
            print("9.🎮买街机        10.⬆️街机等级 Lv.{self.街机等级}")
            print("0.返回主菜单")
            print("="*50)
            c = input("选择：").strip()

            if c == "1":
                价 = 200 + self.电脑数量*50
                if self.钱 >= 价:
                    self.钱 -= 价
                    self.电脑数量 +=1
                    self.顾客上机时长.append(0)
                    print(f"✅ 购买成功！花{价}")
                else:print("❌钱不够")
            elif c == "2":
                价 = 300 * self.电脑等级
                if self.钱 >= 价:
                    self.钱 -=价
                    self.电脑等级 +=1
                    print(f"✅ 电脑升到{self.电脑等级}级！")
                else:print("❌钱不够")
            elif c == "3":
                价 = 100*self.电脑桌等级
                if self.钱>=价:self.钱-=价;self.电脑桌等级+=1;print("✅升级")
                else:print("❌钱不够")
            elif c == "4":
                价 = 150*self.主机等级
                if self.钱>=价:self.钱-=价;self.主机等级+=1;print("✅升级")
                else:print("❌钱不够")
            elif c == "5":
                价 = 120*self.显示器等级
                if self.钱>=价:self.钱-=价;self.显示器等级+=1;print("✅升级")
                else:print("❌钱不够")
            elif c == "6":
                价 = 80*self.椅子等级
                if self.钱>=价:self.钱-=价;self.椅子等级+=1;print("✅升级")
                else:print("❌钱不够")
            elif c == "7":
                价 = 50*self.鼠标等级
                if self.钱>=价:self.钱-=价;self.鼠标等级+=1;print("✅升级")
                else:print("❌钱不够")
            elif c == "8":
                价 = 50*self.键盘等级
                if self.钱>=价:self.钱-=价;self.键盘等级+=1;print("✅升级")
                else:print("❌钱不够")
            elif c == "9":
                价 = 400 + self.街机数量*100
                if self.钱>=价:self.钱-=价;self.街机数量+=1;print("✅街机+1")
                else:print("❌钱不够")
            elif c == "10":
                价 = 250*self.街机等级
                if self.钱>=价:self.钱-=价;self.街机等级+=1;print(f"✅街机{self.街机等级}级")
                else:print("❌钱不够")
            elif c == "0":
                break
            input("\n回车继续…")

    # ====================== 接待 ======================
    def 接待电脑(self):
        可用 = self.电脑数量 - self.电脑使用中
        if 可用 <=0 or self.排队顾客<=0:
            print("❌没电脑/没人")
            return
        接 = min(可用, self.排队顾客)
        单台 = self.每台电脑每小时收益()
        self.钱 += 接*单台
        self.今日营收 += 接*单台
        for i in range(self.电脑使用中, self.电脑使用中+接):
            self.顾客上机时长[i] = 0
        self.电脑使用中 +=接
        self.排队顾客 -=接
        self.口碑 = min(self.口碑+2,150)
        print(f"✅接待{接}人，每台{单台}元/时")

    def 接待街机(self):
        可用 = self.街机数量 - self.街机使用中
        if 可用<=0:
            print("❌街机已满")
            return
        接 = min(可用, 3)
        单台 = self.每台街机每小时收益()
        self.钱 += 接*单台
        self.今日营收 += 接*单台
        self.街机使用中 +=接
        print(f"✅街机接待{接}人，每台{单台}元/时")

    # ====================== 地图 ======================
    def 画界面(self):
        clear()
        print("🏪【网吧大亨·终极完整版】".center(58,"="))
        print(f"🖥️电脑：{self.电脑使用中}/{self.电脑数量} Lv.{self.电脑等级}")
        print(f"🎮街机：{self.街机使用中}/{self.街机数量} Lv.{self.街机等级}")
        print(f"👥排队：{self.排队顾客}/40    💰钱：{self.钱}")
        print(f"🌟口碑：{self.口碑}  {self.天气}  📊今日：{self.今日营收}")
        print(f"💸电脑单价：{self.每台电脑每小时收益()}元/时")
        print(f"🎮街机单价：{self.每台街机每小时收益()}元/时")
        print("配件：桌{} 主机{} 显示器{} 椅{} 鼠{} 键{}".format(
            self.电脑桌等级,self.主机等级,self.显示器等级,
            self.椅子等级,self.鼠标等级,self.键盘等级))
        print("="*58)

    # ====================== 主菜单 ======================
    def 开始游戏(self):
        while True:
            self.画界面()
            print("\n【🎮主菜单】")
            print("1.🖥️接待电脑  2.🎮接待街机  3.🏬商城  4.🕒快进1h")
            print("5.⏩快进2h   6.⏩快进3h   7.💾存档  8.📂读档  0.退出")
            选 = input("\n请选择：").strip()

            clear()
            if 选=="1": self.接待电脑()
            elif 选=="2": self.接待街机()
            elif 选=="3": self.商城()
            elif 选=="4": self.时间流逝()
            elif 选=="5": self.快进2h()
            elif 选=="6": self.快进3h()
            elif 选=="7": self.生成存档码()
            elif 选=="8": self.读取存档码()
            elif 选=="0":
                clear()
                print("👋再见！")
                break
            input("\n回车继续…")

if __name__ == "__main__":
    游戏 = 网吧大亨终极版()
    游戏.开始游戏()