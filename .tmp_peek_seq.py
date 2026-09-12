# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = io.open("src/tongshu/engines/blind_bazi_engine.py", encoding="utf-8").read()
import re
# 找 _resolve_occupation_candidate 调用顺序
for m in re.finditer(r"_resolve_(occupation|official)_candidate", src):
    print(m.group(1), "定义@", m.start())
# 找 compute 里调用序列
i = src.find("def compute")
seg = src[i:i+4000]
for m in re.finditer(r"_resolve_\w+", seg):
    print("调用:", m.group())
