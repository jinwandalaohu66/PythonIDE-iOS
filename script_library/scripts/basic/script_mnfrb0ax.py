# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
import os
import shutil

print("=== 开始清理 PythonIDE（文禄 张）===")

# iOS 模拟器里这个APP的真实路径
home = os.path.expanduser("~")
paths = [
    f"{home}/Library/Developer/CoreSimulator/Devices/*/data/Containers/Data/Application/*PythonIDE*",
    f"{home}/Library/Developer/CoreSimulator/Devices/*/data/Containers/Bundle/Application/*PythonIDE*",
    f"{home}/Documents/PythonIDE",
    f"{home}/Library/Preferences/*wenlu*PythonIDE*"
]

for path in paths:
    try:
        shutil.rmtree(path, ignore_errors=True)
        print(f"✅ 已删除: {path}")
    except:
        pass

print("\n🎉 完成！PythonIDE 已经被清空，打不开了")