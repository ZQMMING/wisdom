# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
for p in ["D:/顺天系统资料/盲派命理-案例资料集.md", "D:/顺天系统资料/盲派命理-个人案例详解集.md"]:
    t = io.open(p, encoding="utf-8").read()
    print(f"===== {p} 长度{len(t)} =====")
    for k in ["职业", "工作", "行业", "从事", "银行", "教师", "律师", "医生", "当官", "公职", "军", "警", "仓库", "公务员", "经商", "生意", "技术", "手艺", "职工", "打工", "上班", "单位"]:
        for m in re.finditer(k, t):
            s = t[max(0,m.start()-60):m.start()+80].replace("\n", " ")
            if len(s) > 20:
                print(f"  [{k}] …{s}…")
