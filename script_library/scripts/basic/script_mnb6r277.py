#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ASCII 艺术示例：纯文本炫酷输出

在控制台用字符画出图案，无需图片即可做出视觉效果。
可配合 Rich 的彩色输出进一步美化。
"""

# Python IDE  Logo 风格
logo = r'''
  ____        _   _                    ____ ___  __  __ ____
 |  _ \ _   _| |_| |__   ___  _ __   |  _ \_ _|  \/  |  _ \
 | |_) | | | | __| '_ \ / _ \| '_ \  | | | | || |\/| | | | |
 |  __/| |_| | |_| | | | (_) | | | | | |_| | || |  | | |_| |
 |_|    \__, |\__|_| |_|\___/|_| |_| |____/___|_|  |_|____/
        |___/
'''

# 装饰边框
def box(text, width=40):
    lines = text.strip().split("\n")
    top = "+" + "-" * (width - 2) + "+"
    result = [top]
    for line in lines:
        result.append("| " + line[:width-4].ljust(width-4) + " |")
    result.append(top)
    return "\n".join(result)

print(logo)
print("PythonIDE - 移动端 Python 编程环境")
print()
print(box("支持 Python · JavaScript · HTML 预览\n内置 AI 助手 · 丰富扩展库"))