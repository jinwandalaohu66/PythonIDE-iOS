import time
import random

class AutoCaller:
    def __init__(self, target_number):
        self.target = target_number
        self.call_count = 0
        self.is_running = True
    
    def make_call(self):
        """模拟拨打电话（实际需对接真实电话API）"""
        self.call_count += 1
        print(f"\n{'='*50}")
        print(f"📞 第 {self.call_count} 次拨打: {self.target}")
        print(f"⏰ 时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 拨号中
        print("📞 拨号中...")
        time.sleep(1)
        
        # 振铃中
        print("🔔 振铃中...")
        time.sleep(2)
        
        # 随机模拟对方行为（实际使用时替换为真实通话状态检测）
        # 这里用随机模拟，真实场景需要对接电话API
        actions = ['answer', 'hangup', 'busy', 'no_answer']
        weights = [0.2, 0.5, 0.2, 0.1]  # 20%接听, 50%挂断, 20%忙线, 10%无人接听
        result = random.choices(actions, weights=weights)[0]
        
        if result == 'answer':
            print("💬 对方接听！通话中...")
            duration = random.randint(5, 30)
            time.sleep(duration)
            print(f"✅ 通话结束 (通话时长: {duration}秒)")
            print("🎉 通话成功完成，停止重拨")
            self.is_running = False
            return 'answered'
        
        elif result == 'hangup':
            print("❌ 对方挂断")
            return 'hangup'
        
        elif result == 'busy':
            print("📵 对方忙线")
            return 'busy'
        
        else:
            print("⏰ 无人接听")
            return 'no_answer'
    
    def start(self, interval=30, max_attempts=None):
        """开始自动重拨"""
        print("="*50)
        print("🚀 自动重拨已启动")
        print(f"📱 目标号码: {self.target}")
        print(f"⏱️  重拨间隔: {interval}秒")
        print(f"🔁 最大次数: {'无限' if max_attempts is None else max_attempts}")
        print("="*50)
        
        while self.is_running:
            if max_attempts and self.call_count >= max_attempts:
                print(f"\n⚠️ 已达到最大重拨次数 ({max_attempts})，停止重拨")
                break
            
            result = self.make_call()
            
            if result == 'answered':
                break
            
            if self.is_running:
                print(f"\n⏳ 等待 {interval} 秒后自动重拨...")
                for i in range(interval, 0, -1):
                    print(f"  剩余 {i} 秒", end='\r')
                    time.sleep(1)
                print("\n" + " "*20 + "\n")

if __name__ == "__main__":
    print("="*40)
    print("📞 自动重拨系统")
    print("="*40)
    
    # 直接在这里填写要拨打的手机号
    phone = "17751377766"  # 👈 改成你要拨打的号码
    
    interval = 10  # 挂断后等待10秒重拨
    max_attempts = 5  # 最多重拨5次，None表示无限
    
    print(f"目标号码: {phone}")
    print(f"重拨间隔: {interval}秒")
    print(f"最大重拨: {max_attempts}次")
    print("-"*40)
    
    caller = AutoCaller(phone)
    try:
        caller.start(interval=interval, max_attempts=max_attempts)
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户手动停止")