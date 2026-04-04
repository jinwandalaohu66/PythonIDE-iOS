# 网吧模拟器 优化版 - 修复点击无反馈和逻辑问题
import ui
import random
import json
import hashlib
import time
import dialogs
import threading

class 网吧大亨优化版:
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
        self.天气 = ["☀️晴天", "🌧️小雨", "⛈️大雨", "❄️雪天"][random.randint(0, 3)]

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
        
        # UI 引用
        self.view = None
        self.status_labels = {}
        self.feedback_label = None

    # ====================== 反馈系统 ======================
    def 显示反馈(self, message):
        """显示操作反馈消息"""
        print(f"[反馈] {message}")  # 控制台输出
        
        # 如果UI已创建，在界面上显示反馈
        if self.view and self.feedback_label:
            self.feedback_label.text = message
            # 3秒后清除反馈
            def 清除反馈():
                time.sleep(3)
                if self.feedback_label:
                    self.feedback_label.text = ""
            threading.Thread(target=清除反馈).start()

    # ====================== 时间系统 ======================
    def 时间流逝(self, sender=None):
        # 电脑计时
        下机 = 0
        for i in range(self.电脑使用中):
            self.顾客上机时长[i] += 1
            if self.顾客上机时长[i] >= 24:
                下机 += 1
        
        if 下机 > 0:
            self.显示反馈(f"⏰ {下机}人满24小时强制下机")
            # 移除已下机的顾客
            new_时长 = []
            for i in range(self.电脑使用中):
                if self.顾客上机时长[i] < 24:
                    new_时长.append(self.顾客上机时长[i])
            self.电脑使用中 -= 下机
            self.顾客上机时长 = new_时长 + [0] * 下机

        # 街机计时（街机每小时自动下机）
        if self.街机使用中 > 0:
            self.街机使用中 = max(0, self.街机使用中 - 1)

        # 时间推进
        self.小时 += 1
        if self.小时 >= 24:
            self.小时 = 9
            self.天数 += 1
            self.今日营收 = 0
            self.天气 = random.choice(["☀️晴天", "🌧️小雨", "⛈️大雨", "❄️雪天"])
            self.显示反馈(f"📅 新的一天开始！今天是{self.天气}")

        # 顾客上限40
        来客 = random.randint(1, 4)
        if self.天气 == "☀️晴天": 
            来客 += 2
        if self.口碑 > 120: 
            来客 += 2
        self.排队顾客 = min(self.排队顾客 + max(来客, 0), 40)
        
        self.显示反馈(f"⏰ 时间流逝1小时，来了{来客}位顾客")
        self.更新界面()

    def 快进2h(self, sender=None):
        self.显示反馈("⏩ 快进2小时…")
        for _ in range(2):
            self.时间流逝()

    def 快进3h(self, sender=None):
        self.显示反馈("⏩ 快进3小时…")
        for _ in range(3):
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

    # ====================== 商城 ======================
    def 打开商城(self, sender=None):
        # 创建商城窗口
        shop_view = ui.View(frame=(0, 0, 400, 600))
        shop_view.name = "网吧商城"
        shop_view.background_color = '#f5f5f5'
        
        # 标题
        title_label = ui.Label(frame=(0, 20, 400, 40))
        title_label.text = "🏬 超级商城"
        title_label.font = ('<system-bold>', 24)
        title_label.alignment = ui.ALIGN_CENTER
        shop_view.add_subview(title_label)
        
        # 金钱显示
        money_label = ui.Label(frame=(0, 70, 400, 30))
        money_label.text = f"💰 当前金钱：{self.钱}"
        money_label.font = ('<system>', 18)
        money_label.alignment = ui.ALIGN_CENTER
        shop_view.add_subview(money_label)
        
        # 商品列表
        shop_items = [
            ("🖥️ 买电脑", f"价格：{200 + self.电脑数量*50}", "买电脑"),
            ("⬆️ 电脑等级", f"等级：{self.电脑等级} 价格：{300 * self.电脑等级}", "升电脑"),
            ("🪑 电脑桌", f"等级：{self.电脑桌等级} 价格：{100*self.电脑桌等级}", "升电脑桌"),
            ("🖥️ 主机", f"等级：{self.主机等级} 价格：{150*self.主机等级}", "升主机"),
            ("🖥️ 显示器", f"等级：{self.显示器等级} 价格：{120*self.显示器等级}", "升显示器"),
            ("🪑 椅子", f"等级：{self.椅子等级} 价格：{80*self.椅子等级}", "升椅子"),
            ("🖱️ 鼠标", f"等级：{self.鼠标等级} 价格：{50*self.鼠标等级}", "升鼠标"),
            ("⌨️ 键盘", f"等级：{self.键盘等级} 价格：{50*self.键盘等级}", "升键盘"),
            ("🎮 买街机", f"数量：{self.街机数量} 价格：{400 + self.街机数量*100}", "买街机"),
            ("⬆️ 街机等级", f"等级：{self.街机等级} 价格：{250*self.街机等级}", "升街机"),
        ]
        
        y_offset = 120
        for i, (title, desc, action) in enumerate(shop_items):
            item_view = ui.View(frame=(20, y_offset, 360, 44))
            item_view.background_color = '#ffffff'
            item_view.corner_radius = 10
            item_view.border_width = 1
            item_view.border_color = '#dddddd'
            
            title_label = ui.Label(frame=(10, 5, 200, 34))
            title_label.text = title
            title_label.font = ('<system>', 16)
            item_view.add_subview(title_label)
            
            desc_label = ui.Label(frame=(210, 5, 100, 34))
            desc_label.text = desc
            desc_label.font = ('<system>', 12)
            desc_label.text_color = '#666666'
            item_view.add_subview(desc_label)
            
            buy_btn = ui.Button(frame=(320, 5, 30, 34))
            buy_btn.title = "✅"
            buy_btn.font = ('<system>', 16)
            buy_btn.action = self.创建购买动作(action)
            item_view.add_subview(buy_btn)
            
            shop_view.add_subview(item_view)
            y_offset += 50
            
        # 返回按钮
        back_btn = ui.Button(frame=(120, y_offset+20, 160, 44))
        back_btn.title = "返回主菜单"
        back_btn.background_color = '#007AFF'
        back_btn.title_color = 'white'
        back_btn.corner_radius = 10
        back_btn.action = lambda s: shop_view.close()
        shop_view.add_subview(back_btn)
        
        shop_view.present('sheet')
        
    def 创建购买动作(self, action_type):
        def 购买操作(sender):
            success = False
            message = ""
            
            if action_type == "买电脑":
                价 = 200 + self.电脑数量 * 50
                if self.钱 >= 价:
                    self.钱 -= 价
                    self.电脑数量 += 1
                    self.顾客上机时长.append(0)
                    message = f"✅ 购买成功！花费{价}元"
                    success = True
                else:
                    message = "❌ 钱不够"
                    
            elif action_type == "升电脑":
                价 = 300 * self.电脑等级
                if self.钱 >= 价:
                    self.钱 -= 价
                    self.电脑等级 += 1
                    message = f"✅ 电脑升到{self.电脑等级}级！"
                    success = True
                else:
                    message = "❌ 钱不够"
                    
            elif action_type == "升电脑桌":
                价 = 100 * self.电脑桌等级
                if self.钱 >= 价:
                    self.钱 -= 价
                    self.电脑桌等级 += 1
                    message = "✅ 电脑桌升级成功！"
                    success = True
                else:
                    message = "❌ 钱不够"
                    
            elif action_type == "升主机":
                价 = 150 * self.主机等级
                if self.钱 >= 价:
                    self.钱 -= 价
                    self.主机等级 += 1
                    message = "✅ 主机升级成功！"
                    success = True
                else:
                    message = "❌ 钱不够"
                    
            elif action_type == "升显示器":
                价 = 120 * self.显示器等级
                if self.钱 >= 价:
                    self.钱 -= 价
                    self.显示器等级 += 1
                    message = "✅ 显示器升级成功！"
                    success = True
                else:
                    message = "❌ 钱不够"
                    
            elif action_type == "升椅子":
                价 = 80 * self.椅子等级
                if self.钱 >= 价:
                    self.钱 -= 价
                    self.椅子等级 += 1
                    message = "✅ 椅子升级成功！"
                    success = True
                else:
                    message = "❌ 钱不够"
                    
            elif action_type == "升鼠标":
                价 = 50 * self.鼠标等级
                if self.钱 >= 价:
                    self.钱 -= 价
                    self.鼠标等级 += 1
                    message = "✅ 鼠标升级成功！"
                    success = True
                else:
                    message = "❌ 钱不够"
                    
            elif action_type == "升键盘":
                价 = 50 * self.键盘等级
                if self.钱 >= 价:
                    self.钱 -= 价
                    self.键盘等级 += 1
                    message = "✅ 键盘升级成功！"
                    success = True
                else:
                    message = "❌ 钱不够"
                    
            elif action_type == "买街机":
                价 = 400 + self.街机数量 * 100
                if self.钱 >= 价:
                    self.钱 -= 价
                    self.街机数量 += 1
                    message = "✅ 街机+1"
                    success = True
                else:
                    message = "❌ 钱不够"
                    
            elif action_type == "升街机":
                价 = 250 * self.街机等级
                if self.钱 >= 价:
                    self.钱 -= 价
                    self.街机等级 += 1
                    message = f"✅ 街机升到{self.街机等级}级"
                    success = True
                else:
                    message = "❌ 钱不够"
            
            # 显示反馈
            self.显示反馈(message)
            
            # 更新界面并关闭商城
            self.更新界面()
            if success:
                sender.superview.superview.close()  # 关闭商城窗口
            
        return 购买操作

    # ====================== 接待 ======================
    def 接待电脑(self, sender=None):
        可用 = self.电脑数量 - self.电脑使用中
        if 可用 <= 0:
            self.显示反馈("❌ 没有空闲电脑")
            return
        if self.排队顾客 <= 0:
            self.显示反馈("❌ 没有排队顾客")
            return
            
        接 = min(可用, self.排队顾客)
        单台 = self.每台电脑每小时收益()
        收入 = 接 * 单台
        self.钱 += 收入
        self.今日营收 += 收入
        
        # 为新顾客设置上机时长
        for i in range(self.电脑使用中, self.电脑使用中 + 接):
            if i < len(self.顾客上机时长):
                self.顾客上机时长[i] = 0
            else:
                self.顾客上机时长.append(0)
                
        self.电脑使用中 += 接
        self.排队顾客 -= 接
        self.口碑 = min(self.口碑 + 2, 150)
        self.显示反馈(f"✅ 接待{接}位顾客，收入{收入}元")
        self.更新界面()

    def 接待街机(self, sender=None):
        可用 = self.街机数量 - self.街机使用中
        if 可用 <= 0:
            self.显示反馈("❌ 街机已满")
            return
        if self.排队顾客 <= 0:
            self.显示反馈("❌ 没有排队顾客")
            return
            
        接 = min(可用, min(3, self.排队顾客))  # 最多3人，且不能超过排队人数
        单台 = self.每台街机每小时收益()
        收入 = 接 * 单台
        self.钱 += 收入
        self.今日营收 += 收入
        self.街机使用中 += 接
        self.排队顾客 -= 接
        self.显示反馈(f"✅ 街机接待{接}人，收入{收入}元")
        self.更新界面()

    # ====================== 存档系统 ======================
    def 生成存档码(self, sender=None):
        数据 = self.__dict__.copy()
        # 移除UI引用
        if 'view' in 数据:
            del 数据['view']
        if 'status_labels' in 数据:
            del 数据['status_labels']
        if 'feedback_label' in 数据:
            del 数据['feedback_label']
            
        字符串 = json.dumps(数据, ensure_ascii=False)
        唯一码 = hashlib.sha256((字符串 + str(time.time())).encode()).hexdigest()[:16]
        
        dialogs.alert("🏪 存档信息", f"✅ 存档码：{唯一码}\n\n存档数据已复制到剪贴板", "确定")
        import clipboard
        clipboard.set(字符串)
        self.显示反馈("✅ 存档成功！")
        
    def 读取存档码(self, sender=None):
        import clipboard
        存档数据 = clipboard.get()
        if not 存档数据:
            dialogs.alert("❌ 错误", "剪贴板中没有存档数据", "确定")
            return
            
        try:
            data = json.loads(存档数据)
            self.__dict__.update(data)
            # 重新初始化UI引用
            self.view = None
            self.status_labels = {}
            self.feedback_label = None
            
            dialogs.alert("✅ 成功", "读档成功！", "确定")
            self.显示反馈("✅ 读档成功！")
            self.更新界面()
        except Exception as e:
            dialogs.alert("❌ 失败", f"读取存档失败：{str(e)}", "确定")
            self.显示反馈("❌ 读档失败")

    # ====================== UI界面 ======================
    def 创建界面(self):
        # 主视图
        self.view = ui.View(frame=(0, 0, 400, 750))
        self.view.name = "🏪 网吧大亨·优化版"
        self.view.background_color = '#1a1a2e'
        
        # 顶部标题
        title_label = ui.Label(frame=(0, 40, 400, 50))
        title_label.text = "🏪 网吧大亨·优化版"
        title_label.font = ('<system-bold>', 24)
        title_label.text_color = '#ffffff'
        title_label.alignment = ui.ALIGN_CENTER
        self.view.add_subview(title_label)
        
        # 反馈标签
        self.feedback_label = ui.Label(frame=(20, 90, 360, 30))
        self.feedback_label.text = "欢迎来到网吧大亨！"
        self.feedback_label.font = ('<system>', 14)
        self.feedback_label.text_color = '#FFD700'  # 金色
        self.feedback_label.alignment = ui.ALIGN_CENTER
        self.view.add_subview(self.feedback_label)
        
        # 状态显示区域
        status_y = 130
        status_items = [
            ("电脑状态", f"🖥️电脑：{self.电脑使用中}/{self.电脑数量} Lv.{self.电脑等级}", "电脑状态"),
            ("街机状态", f"🎮街机：{self.街机使用中}/{self.街机数量} Lv.{self.街机等级}", "街机状态"),
            ("排队顾客", f"👥排队：{self.排队顾客}/40", "排队顾客"),
            ("资金", f"💰钱：{self.钱}", "资金"),
            ("口碑天气", f"🌟口碑：{self.口碑}  {self.天气}", "口碑天气"),
            ("今日营收", f"📊今日营收：{self.今日营收}", "今日营收"),
            ("电脑单价", f"💸电脑单价：{self.每台电脑每小时收益()}元/时", "电脑单价"),
            ("街机单价", f"🎮街机单价：{self.每台街机每小时收益()}元/时", "街机单价"),
            ("配件等级", f"配件：桌{self.电脑桌等级} 主机{self.主机等级} 显示器{self.显示器等级} 椅{self.椅子等级} 鼠{self.鼠标等级} 键{self.键盘等级}", "配件等级"),
            ("时间", f"📅第{self.天数}天 ⏰{self.小时}:00", "时间"),
        ]
        
        self.status_labels = {}
        for i, (title, text, key) in enumerate(status_items):
            label = ui.Label(frame=(20, status_y + i*30, 360, 30))
            label.text = text
            label.font = ('<system>', 14)
            label.text_color = '#e0e0e0'
            label.alignment = ui.ALIGN_LEFT
            self.view.add_subview(label)
            self.status_labels[key] = label
        
        # 操作按钮区域
        buttons_y = status_y + len(status_items)*30 + 20
        
        # 第一行按钮
        btn1 = ui.Button(frame=(20, buttons_y, 160, 44))
        btn1.title = "🖥️ 接待电脑"
        btn1.background_color = '#4CAF50'
        btn1.title_color = 'white'
        btn1.corner_radius = 10
        btn1.action = self.接待电脑
        self.view.add_subview(btn1)
        
        btn2 = ui.Button(frame=(220, buttons_y, 160, 44))
        btn2.title = "🎮 接待街机"
        btn2.background_color = '#2196F3'
        btn2.title_color = 'white'
        btn2.corner_radius = 10
        btn2.action = self.接待街机
        self.view.add_subview(btn2)
        
        # 第二行按钮
        btn3 = ui.Button(frame=(20, buttons_y + 54, 160, 44))
        btn3.title = "🏬 商城"
        btn3.background_color = '#FF9800'
        btn3.title_color = 'white'
        btn3.corner_radius = 10
        btn3.action = self.打开商城
        self.view.add_subview(btn3)
        
        btn4 = ui.Button(frame=(220, buttons_y + 54, 160, 44))
        btn4.title = "⏰ 快进1h"
        btn4.background_color = '#9C27B0'
        btn4.title_color = 'white'
        btn4.corner_radius = 10
        btn4.action = self.时间流逝
        self.view.add_subview(btn4)
        
        # 第三行按钮
        btn5 = ui.Button(frame=(20, buttons_y + 108, 160, 44))
        btn5.title = "⏩ 快进2h"
        btn5.background_color = '#673AB7'
        btn5.title_color = 'white'
        btn5.corner_radius = 10
        btn5.action = self.快进2h
        self.view.add_subview(btn5)
        
        btn6 = ui.Button(frame=(220, buttons_y + 108, 160, 44))
        btn6.title = "⏩ 快进3h"
        btn6.background_color = '#3F51B5'
        btn6.title_color = 'white'
        btn6.corner_radius = 10
        btn6.action = self.快进3h
        self.view.add_subview(btn6)
        
        # 第四行按钮（存档/读档）
        btn7 = ui.Button(frame=(20, buttons_y + 162, 160, 44))
        btn7.title = "💾 存档"
        btn7.background_color = '#009688'
        btn7.title_color = 'white'
        btn7.corner_radius = 10
        btn7.action = self.生成存档码
        self.view.add_subview(btn7)
        
        btn8 = ui.Button(frame=(220, buttons_y + 162, 160, 44))
        btn8.title = "📂 读档"
        btn8.background_color = '#795548'
        btn8.title_color = 'white'
        btn8.corner_radius = 10
        btn8.action = self.读取存档码
        self.view.add_subview(btn8)
        
        # 说明标签
        info_label = ui.Label(frame=(20, buttons_y + 216, 360, 40))
        info_label.text = "💡 提示：所有操作都有反馈显示在上方"
        info_label.font = ('<system>', 12)
        info_label.text_color = '#888888'
        info_label.alignment = ui.ALIGN_CENTER
        self.view.add_subview(info_label)
        
        return self.view
    
    def 更新界面(self):
        if not self.view:
            return
            
        # 更新所有状态标签
        self.status_labels["电脑状态"].text = f"🖥️电脑：{self.电脑使用中}/{self.电脑数量} Lv.{self.电脑等级}"
        self.status_labels["街机状态"].text = f"🎮街机：{self.街机使用中}/{self.街机数量} Lv.{self.街机等级}"
        self.status_labels["排队顾客"].text = f"👥排队：{self.排队顾客}/40"
        self.status_labels["资金"].text = f"💰钱：{self.钱}"
        self.status_labels["口碑天气"].text = f"🌟口碑：{self.口碑}  {self.天气}"
        self.status_labels["今日营收"].text = f"📊今日营收：{self.今日营收}"
        self.status_labels["电脑单价"].text = f"💸电脑单价：{self.每台电脑每小时收益()}元/时"
        self.status_labels["街机单价"].text = f"🎮街机单价：{self.每台街机每小时收益()}元/时"
        self.status_labels["配件等级"].text = f"配件：桌{self.电脑桌等级} 主机{self.主机等级} 显示器{self.显示器等级} 椅{self.椅子等级} 鼠{self.鼠标等级} 键{self.键盘等级}"
        self.status_labels["时间"].text = f"📅第{self.天数}天 ⏰{self.小时}:00"
        
        # 强制重绘
        self.view.set_needs_display()
    
    def 开始游戏(self):
        view = self.创建界面()
        view.present('sheet')

# 启动游戏
if __name__ == "__main__":
    游戏 = 网吧大亨优化版()
    游戏.开始游戏()