# -*- coding: utf-8 -*-
import io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
# 搜盲派职业相关关键词
kws = ["武职", "军警", "文职", "司法", "公检法", "公职", "经商", "生意", "技术", "手艺", "教师", "律师", "医生", "当官", "掌权", "职业", "行业"]
roots = ["D:/顺天系统资料", "C:/Users/ming/Desktop"]
for r in roots:
    if not os.path.isdir(r): continue
    for root, dirs, files in os.walk(r):
        for f in files:
            if not f.endswith((".md", ".txt")): continue
            p = os.path.join(root, f)
            try:
                t = io.open(p, encoding="utf-8", errors="ignore").read()
            except: continue
            cnt = sum(t.count(k) for k in kws)
            if cnt >= 8:
                print(cnt, p)
