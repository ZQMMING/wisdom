# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = io.open("src/tongshu/engines/blind_bazi_engine.py", encoding="utf-8").read()
i = src.find("def _resolve_occupation_candidate")
j = src.find("def _resolve_body_candidate")
print(src[i:j])
