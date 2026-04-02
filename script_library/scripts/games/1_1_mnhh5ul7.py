import random

# 安全清屏（绝对不报错）
def clear():
    print("\n" * 80)

class 网吧大亨终极版:
    def __init__(self):
        # 基础资源
        self.钱 = 500
        self.天数 = 1
        self.小时 = 10
        self.电脑总数 = 6
        self.电脑使用中 = 0
        self.电脑损坏 = 0
        self.排队顾客 = 0
        self.上网价格 = 6
        
        # 🔥 新增系统
        self.口碑 = 100        # 口碑越高顾客越多
        self.会员数 = 0        # 会员会常来
        self.饮料库存 = 20    # 可乐/矿泉水
        self.饮料成本 = 2
        self.饮料售价 = 5
        self.雇佣网管 = False  # 网管自动修电脑
        self.装修等级 = 1      # 装修越高越吸引人
        self.天气 = ["☀️晴天", "🌧️小雨", "⛈️大雨", "❄️雪天"][random.randint(0,3)]
        self.今日营收 = 0

    # ======================
    # 🎨 表情图形化网吧地图
    # ======================
    def 画地图(self):
        clear()
        print("🏪【网吧大亨·终极版】🏪".center(58, "="))
        print()
        
        # 电脑区域表情地图
        print("  🖥️ 电脑区：可用🖥️  使用💻  损坏🔧")
        print("-"*58)
        电脑行 = "  "
        for i in range(self.电脑总数):
            if i < self.电脑使用中:
                电脑行 += "💻  "
            elif i < self.电脑使用中 + self.电脑损坏:
                电脑行 += "🔧  "
            else:
                电脑行 += "🖥️  "
        print(电脑行)
        print("-"*58)

        # 顾客排队
        顾客显示 = "👤" * min(self.排队顾客, 12)
        if self.排队顾客 >12: 顾客显示 += f"+{self.排队顾客-12}人"
        print(f"  👥排队：{顾客显示}")
        
        # 会员 & 网管 & 装修
        print(f"  👑会员：{self.会员数}  |  👨💻网管：{'已雇佣' if self.雇佣网管 else '未雇'}  |  🎨装修：{self.装修等级}级")
        print(f"  🌟口碑：{self.口碑}  |  {self.天气}  |  📊今日营收：{self.今日营收}元")
        print(f"  💰金钱：{self.钱}  |  🥤饮料库存：{self.饮料库存}  |  💸网费：{self.上网价格}元/时")
        print("="*58)

    # ======================
    # 🌏 核心系统：时间&天气&顾客
    # ======================
    def 时间流逝(self):
        self.小时 +=1
        if self.小时 >=24:
            self.小时 = 9
            self.天数 +=1
            self.今日营收 =0
            self.天气 = ["☀️晴天","🌧️小雨","⛈️大雨","❄️雪天"][random.randint(0,3)]
        
        # 天气+口碑影响顾客
        来客数 = random.randint(1,4)
        if self.天气 == "☀️晴天": 来客数 +=2
        if self.天气 == "⛈️大雨": 来客数 -=2
        if self.口碑 >120: 来客数 +=2
        if self.口碑 <60: 来客数 -=1
        self.排队顾客 += max(来客数,0)

        # 电脑损坏
        if random.randint(1,10) ==1 and self.电脑损坏 < self.电脑总数//2:
            self.电脑损坏 +=1
            print("\n⚠️ 一台电脑坏了！")
        
        # 网管自动维修
        if self.雇佣网管 and self.电脑损坏>0 and random.randint(1,2)==1:
            self.电脑损坏 -=1
            print("\n✅ 网管自动修好一台电脑！")

    # ======================
    # 🎮 超多新功能
    # ======================
    def 接待顾客(self):
        可用 = self.电脑总数 - self.电脑使用中 - self.电脑损坏
        if 可用<=0 or self.排队顾客<=0:
            print("\n❌ 没电脑/没顾客！")
            input("回车继续...")
            return
        接待 = min(可用, self.排队顾客)
        收入 = 接待 * self.上网价格
        self.钱 +=收入
        self.今日营收 +=收入
        self.电脑使用中 +=接待
        self.排队顾客 -=接待
        self.口碑 = min(self.口碑+2,150)
        print(f"\n✅ 接待{接待}人！赚{收入}元 🌟口碑+2")
        input("回车继续...")

    def 卖饮料(self):
        if self.电脑使用中 ==0:
            print("\n❌ 没人上网，卖不出去！")
            input("回车继续...")
            return
        if self.饮料库存 <=0:
            print("\n❌ 饮料卖完了！")
            input("回车继续...")
            return
        卖出 = min(random.randint(1, self.电脑使用中), self.饮料库存)
        利润 = 卖出*(self.饮料售价 - self.饮料成本)
        self.钱 +=利润
        self.今日营收 +=利润
        self.饮料库存 -=卖出
        print(f"\n🥤 卖出{卖出}瓶饮料！赚{利润}元")
        input("回车继续...")

    def 进货饮料(self):
        进价 = self.饮料成本 *10
        if self.钱 <进价:
            print("\n❌ 钱不够进货！")
            input("回车继续...")
            return
        self.钱 -=进价
        self.饮料库存 +=10
        print(f"\n📦 饮料进货+10瓶！花费{进价}元")
        input("回车继续...")

    def 雇佣解雇网管(self):
        if not self.雇佣网管:
            if self.钱 <200:
                print("\n❌ 雇佣网管需要200元！")
                input("回车继续...")
                return
            self.钱 -=200
            self.雇佣网管 = True
            print("\n👨💻 网管已雇佣！自动帮你修电脑～")
        else:
            self.雇佣网管 = False
            print("\n👋 已解雇网管")
        input("回车继续...")

    def 升级装修(self):
        费用 = 150 * self.装修等级
        if self.钱 <费用:
            print(f"\n❌ 升级需要{费用}元！")
            input("回车继续...")
            return
        self.钱 -=费用
        self.装修等级 +=1
        self.口碑 +=10
        print(f"\n🎨 装修升到{self.装修等级}级！口碑+10")
        input("回车继续...")

    def 发展会员(self):
        费用 = 80
        if self.钱 <费用:
            print("\n❌ 发展会员需要80元！")
            input("回车继续...")
            return
        self.钱 -=费用
        self.会员数 += random.randint(3,8)
        self.口碑 +=5
        print(f"\n👑 会员+{random.randint(3,8)}人！口碑+5")
        input("回车继续...")

    def 突发事件(self):
        事件 = random.choice([
            "网红打卡🎉，顾客暴涨！",
            "突然停电⚡，所有顾客下机！",
            "消防检查👮，口碑小幅下降",
            "老顾客送礼🎁，直接给你100元！"
        ])
        if "网红" in 事件:
            self.排队顾客 +=10
            self.口碑 +=10
        elif "停电" in 事件:
            self.电脑使用中 =0
            self.口碑 = max(self.口碑-10, 30)
        elif "消防" in 事件:
            self.口碑 = max(self.口碑-8, 30)
        elif "送礼" in 事件:
            self.钱 +=100
        print(f"\n🚨 突发事件：{事件}")
        input("回车继续...")

    def 买电脑(self):
        价格 = 180
        if self.钱 <价格:
            print(f"\n❌ 买电脑需要{价格}元！")
            input("回车继续...")
            return
        self.钱 -=价格
        self.电脑总数 +=1
        print("\n🆕 新增电脑一台！")
        input("回车继续...")

    def 每日打卡(self):
        奖励 = random.randint(50,150)
        self.钱 +=奖励
        print(f"\n🎁 打卡成功！获得{奖励}元")
        input("回车继续...")

    # ======================
    # 🎯 主菜单
    # ======================
    def 开始游戏(self):
        while True:
            self.画地图()
            print("\n【🎮 超级操作菜单】")
            print(" 1.👥接待顾客   2.🥤卖饮料    3.📦进货饮料   4.🆕买电脑")
            print(" 5.👨💻雇/解雇网管 6.🎨升级装修 7.👑发展会员  8.💰每日打卡")
            print(" 9.🚨突发事件  10.💸改网价  11.🕒时间快进  0.🚪退出游戏")
            
            选择 = input("\n请输入操作(1-11或0)：").strip()
            if 选择 == "1": self.接待顾客()
            elif 选择 == "2": self.卖饮料()
            elif 选择 == "3": self.进货饮料()
            elif 选择 == "4": self.买电脑()
            elif 选择 == "5": self.雇佣解雇网管()
            elif 选择 == "6": self.升级装修()
            elif 选择 == "7": self.发展会员()
            elif 选择 == "8": self.每日打卡()
            elif 选择 == "9": self.突发事件()
            elif 选择 == "10":
                try:
                    新价 = int(input("输入新价格(1-40)："))
                    if 1<=新价<=40:
                        self.上网价格 = 新价
                        print("✅ 价格已改！")
                except: pass
                input("回车继续...")
            elif 选择 == "11": self.时间流逝()
            elif 选择 == "0":
                clear()
                print("👋 感谢玩《网吧大亨·终极版》！")
                break
            else:
                input("❌ 输入错误，回车重试...")

if __name__ == "__main__":
    游戏 = 网吧大亨终极版()
    游戏.开始游戏()