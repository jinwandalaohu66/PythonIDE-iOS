# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
import time
R = "\033[91m"   # 红
G = "\033[92m"   # 绿
Y = "\033[93m"   # 黄
X = "\033[0m"    # 重置
print("普通")
t='█'
for i in range(51):
	k=i*2
	print(f"\r|{i*'█'}{(50-i)*' '}|{k}%",end="")
	time.sleep(0.08)
#高级
print("\n高级")
def load():

    for i in range(51):
        if i*2<30:
            types=R
        elif i*2>30 and i*2<60:
            types=Y
        elif i*2>60:
            types=G
        print(f"\r|{types}{i * t}{X}|{(49 - i) * '-'}{i*2}%", end="\033[A")
        time.sleep(0.08)
load()