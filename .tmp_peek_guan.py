# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
# 读官运类断语 + 盲派生产规则里的职业部分
for p in ["D:/顺天系统资料/五部经典断语库/02_按类别分/官运类_断语.md"]:
    t = io.open(p, encoding="utf-8").read()
    print("===== 官运类断语 长度", len(t))
    # 输出前2500字
    print(t[:2500])
