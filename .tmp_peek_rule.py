# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
for p in ["C:/Users/ming/Desktop/盲派生产规则.txt"]:
    t = io.open(p, encoding="utf-8").read()
    print("长度", len(t))
    # 找职业/工作相关
    for k in ["职业", "工作", "行业", "从事", "象"]:
        i = t.find(k)
        if i >= 0:
            print(f"\n### 命中[{k}] @{i}")
            print(t[max(0,i-300):i+500])
