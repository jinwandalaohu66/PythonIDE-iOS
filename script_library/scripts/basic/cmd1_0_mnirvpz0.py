# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
# cmd简练版
R = "\033[91m"   # 红
G = "\033[92m"   # 绿
Y = "\033[93m"   # 黄
B = "\033[94m"   # 蓝
C = "\033[96m"   # 青
M = "\033[95m"   # 紫
X = "\033[0m"
new_l = "\n"
cmd = ""

show = ">"
file={"command.com":"bin,can't see",
    "io.sys":"bin,can't see",
    "msdos.sys":"bin,can't see",
    "ms.txt":"hello user!",
    "sys.txt":"看到这个的人我祝福他幸福快乐每一天",
    "thank.xz":"敢看嘛，其实是感谢使用",
    "format.bat":"format"
}
print("DOS改版")

print("输入help以了解命令")
while True:
    
    cmd = input(show).strip()  #del " "
    if not cmd == "\n":
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
            print(R+"file:")
            print(B)
            for i in list(file):
                print("    "+i)
            print(G+"file number:"+str(len(file)));print(X)
        elif cmd == "oaoa":
            print(G+"91*10086=917826");print(X)
        # 在命令判断里加一段
        elif cmd.startswith("cls"):
            for I in range(1145):
                print("\a")
        elif cmd.startswith("type"):
            print(file.get(cmd[5:],"无法找到此文件"))
        elif cmd.startswith("del"):
            if not cmd.endswith(".sys"):
                if file.pop(cmd[4:],False):
                
                    
                
                    bool=True
            else:
                bool=False
            print("try del file:"+cmd[4:] if bool else "cannot find or del this file")
        elif cmd.startswith("add"):
            try:
                file[cmd[4:]]+=input(">>text")
            except:
                file[cmd[4:]]=input(">>text")
        elif cmd.startswith("new"):
            name=cmd[4:]
            text=input(">>text")
            file[name]=text
        else:
            if cmd=="\n":
                continue
            else:
            
                print(f"'{cmd}' 不是内部或外部命令，也不是可运行的程序")
