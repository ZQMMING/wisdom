# -*- coding: utf-8 -*-
import io, re
s = io.open(r"src/tongshu/engines/blind_bazi_engine.py", encoding="utf-8").read()
# work_level 相关
for m in re.finditer(r"work_level", s):
    i = m.start()
    ls = s.rfind("\n", 0, i)+1
    le = s.find("\n", i)
    print(f"@{i}: {s[ls:le].strip()[:120]}")
