# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
import time
def show(text,s=0.1):
    for i in list(text):
        print(i,end="")
        time.sleep(s)
    print("")
def text(text):
    if text.startswith("/i"):
        show(text[2:])
        return input()
    else:
        show(text)
L=["你好","欢迎来到这里","/i你的名字？"]
for k in L:
    i=text(k)
    print(i if i else "",end="\n" if i else "")