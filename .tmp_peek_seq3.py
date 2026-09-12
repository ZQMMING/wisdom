# -*- coding: utf-8 -*-
import io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = io.open("src/tongshu/engines/blind_bazi_engine.py", encoding="utf-8").read()
# 找所有 _resolve_xxx 的调用点（在 compute 内）
calls = [(m.start(), m.group()) for m in re.finditer(r"self\._resolve_\w+", src)]
for pos, name in calls:
    # 判断是否在 compute 函数体内（compute 定义后到下一个 def 前）
    print(pos, name)
