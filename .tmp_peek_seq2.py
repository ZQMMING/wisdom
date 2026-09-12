# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = io.open("src/tongshu/engines/blind_bazi_engine.py", encoding="utf-8").read()
import re
# compute 主流程调用
i = src.find("def compute")
j = src.find("def _resolve_work_efficiency")
print(src[i:i+3000])
