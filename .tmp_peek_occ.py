# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
src = io.open("src/tongshu/engines/blind_judgment.py", encoding="utf-8").read()
i = src.find("EVT-OCCUPATION-001")
print(src[max(0,i-2500):i+1500])
