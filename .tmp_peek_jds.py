# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
for p in ["docs/v2/盲派遗留口诀_古籍核证决定书.md"]:
    t = io.open(p, encoding="utf-8").read()
    # 找职业相关段落
    for k in ["职业", "工作", "行业", "象法", "IMG"]:
        i = t.find(k)
        if i >= 0:
            print(f"### [{p}] 命中[{k}] @{i}")
            print(t[max(0,i-200):i+600])
            print()
