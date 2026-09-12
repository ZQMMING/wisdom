# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = r"D:\顺天系统资料\盲派命理-案例资料集.md"
src = io.open(p, encoding="utf-8").read()
# 打印案例1-9 + 应期案例10 全文
import re
lines = src.splitlines()
cur = None
buf = {}
for i, l in enumerate(lines):
    if l.startswith("### 案例"):
        cur = l.strip()
        buf[cur] = []
    elif cur:
        buf[cur].append(l)
for k in ["### 案例2：仕途坎坷与\"穿害\"的杀伤力","### 案例3：从\"禄\"看身体与福报","### 案例4：婚姻中的\"宾主\"倒置","### 案例7：财制印格（金融巨头·反传统做功）","### 案例8：做功无效的反例（仓库保管员）","### 案例9：复合做功（身弱变强）","### 案例10：戊申 壬戌 甲子 丙寅（坤造·婚期）"]:
    if k in buf:
        print("="*50)
        print(k)
        print("\n".join(buf[k])[:1500])
