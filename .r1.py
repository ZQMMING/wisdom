# -*- coding: utf-8 -*-
import io, re
s = io.open(r"src/tongshu/engines/blind_bazi_engine.py", encoding="utf-8").read()
# 列所有 def _resolve_
for m in re.finditer(r"def (_resolve_\w+)", s):
    print(m.group(1))
