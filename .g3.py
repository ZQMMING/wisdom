# -*- coding: utf-8 -*-
import sys, io, inspect
sys.path.insert(0, r"D:\shuntian")
# blind_themes 公开接口
th = io.open(r"src/tongshu/engines/blind_themes.py", encoding="utf-8").read()
import re
print("== blind_themes 类/函数 ==")
for m in re.finditer(r"^class (\w+)|^def (\w+)", th, re.M):
    print(" ", m.group(1) or m.group(2))
