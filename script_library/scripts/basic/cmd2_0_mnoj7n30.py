# 欢迎使用 PythonIDE！如果觉得好用，请给个好评哦～
import json
from pathlib import Path
import time
import random
Y = "\033[93m"
print("==========by ioo project==========")
time.sleep(1)
print("=         这是一个测试文件          =")
time.sleep(1)
print("=使用我的作品 模拟cmd可能会出现一些问题=")
time.sleep(1)
print("=       建议使用此工具进行测试       =")
for i in range(51):
    percent = i *2
    print(f"\r|{ '█' * i }{ ' ' * (50 - i) }|{ percent }%", end="")
    time.sleep(random.uniform(0.1, 0.3))
path=Path("dosfile.txt")
if path.exists():
	file=json.loads(path.read_text())
	print(file)
	print("=             测试成功4.1          =")
else:
	file={"command.com":"bin","io.sys":"sys"}
	print("\n=            错误，已修复           =")
	path.write_text(json.dumps(file))
k="#愚人节做的嘿嘿"
if input(">") == "Y":
	print(k)