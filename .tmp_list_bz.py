# -*- coding: utf-8 -*-
import io, sys, os, glob
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
# 找盲派中级/讲义文件
for p in glob.glob("D:/顺天系统资料/**/*.md", recursive=True) + glob.glob("D:/顺天系统资料/**/*.txt", recursive=True):
    b = os.path.basename(p)
    if any(k in b for k in ["盲派", "段建业", "讲义", "中级", "高级", "生产规则"]):
        print(p)
