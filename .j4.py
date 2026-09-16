# -*- coding: utf-8 -*-
import io
s = io.open(r"src/tongshu/engines/blind_interpretation.py", encoding="utf-8").read()
i = s.find("def interpret_blind(")
print(s[i+1500:i+4000])
