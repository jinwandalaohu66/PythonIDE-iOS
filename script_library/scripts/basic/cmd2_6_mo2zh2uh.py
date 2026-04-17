# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
# cmd简练版
R = ""   # 红
G = ""   # 绿
Y = ""   # 黄
B = ""   # 蓝
C = ""   # 青
M = ""   # 紫
X = ""

copy=""
import os
import dialogs
import time
def load():
    t="█"
    for i in range(51):
        if i*2<30:
            types=R
        elif i*2>30 and i*2<60:
            types=Y
        elif i*2>60:
            types=G
        print(f"\r|{types}{i * t}{X}|{(49 - i) * '-'}{i*2}%", end="\033[A")
        time.sleep(0.01)
new_l = "\n"
import json
cmd = ""
show = ">"
file={"command.com":"bin,can't see",
    "io.sys":"bin,can't see",
    "msdos.sys":"bin,can't see",
    "ms.txt":"hello user!",
    "sys.txt":"看到这个的人我祝福他幸福快乐每一天",
    "thank.xz":"敢看嘛，其实是感谢使用"
}
print("DOS改版")
print("输入help以了解命令")
while True:
    
    cmd = input(show).strip()  #del " "
    if not cmd == new_l:
        # help
        if cmd.startswith("help"):
            print("echo 打印文字，如echo hello")
            print("echo on 开启提示符，echo off 关闭提示符")
            print("dir显示文件")
            print("type显示文件内容")
            print("del可以删除文件，无需路径")
            print("我自定义了文件的写入方式")
            print("add file-text")
            print("new file name")
            print("exit 退出程序")
            print("alert text")
            print("（del如果显示文件名就是删除成功）")
        #echo
        elif cmd.startswith("echo"):
            input_str = cmd[4:].lstrip()
            if input_str.startswith("on"):
                show = ">"
            elif input_str.startswith("off"):
                show = ""
            else:
                print(input_str)
        # exit
        elif cmd == "exit":
            exit()
        elif cmd=="dir":
            print("file:")
            
            for i in list(file):
                B=float('%.2f'%(len(str(file[i]))/1024))
                leng=32-len(str(i))
                print(f"- {i}"+f'%{leng}s'%(f'{B}KB'))
            print("file number:"+str(len(file)))
        elif cmd == "oaoa":
            print("91*10086=917826")
        # 在命令判断里加一段
        elif cmd.startswith("cls"):
            for I in range(1):
                print("\a")
        elif cmd.startswith("type"):
            print(file.get(cmd[5:],"无法找到此文件"))
        elif cmd.startswith("del "):
            if not cmd.endswith(".sys"):
                if file.pop(cmd[4:],False):
                    kakimi="jsjsjjzzkafjzlyrzkxyf"
                    #上面这个string是猫踩的
                #处理误删文件
                    bool=True
            else:
                bool=False
            print("try del file:"+cmd[4:] if bool else "cannot find or del this file")
        elif cmd.startswith("add"):
            try:
                file[cmd[4:]]+=input("text>")
            except:
                file[cmd[4:]]=input("text>")
        elif cmd.startswith("new"):
            name=cmd[4:]
            text=input("text>")
            file[name]=text
        elif cmd.startswith("format"):
            file={}
            exit()
        # read 命令
        elif cmd.startswith('load'):
            print("loading...")
            load()
            print("\n")
            with open("dosfile.json", "r", encoding="utf-8") as f:
                file = json.load(f)
        elif cmd.startswith("save"):
            print("saving...")
            load()
            print("\n")
            with open("dosfile.json", "w", encoding="utf-8") as f:
                json.dump(file, f, ensure_ascii=False, indent=2)
        elif cmd.startswith("ui"):
            if dialogs.list_dialog("选择一个操作",["continue"])=="continue":
                continue
            else:
                continue
        elif cmd.startswith("delt"):
            inp=input("此操作可能会影响到你的文件，是否继续(n/y)")
            if inp=="y":
                try:
                    os.remove(cmd[5:])
                    print("成功")
                except:
                    print("失败")
                    continue
        elif cmd.startswith("alert"):
            dialogs.alert(cmd[6:])
        elif cmd.startswith("input"):
            copy=dialogs.input_alert(cmd[6:])
        elif cmd=="copy":
            print(copy)
        elif cmd=="others":
    
            print("呜呜呜要期中了下载一下吧")
        else:  
            dialogs.alert(f"'{cmd}' 不是内部或外部命令，也不是可运行的程序")
				