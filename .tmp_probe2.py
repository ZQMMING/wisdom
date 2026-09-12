# -*- coding: utf-8 -*-
import io, re
p = "src/tongshu/engines/blind_themes.py"
src = io.open(p, encoding="utf-8").read()
m = re.search(r"def aggregate_blind_themes\([^)]*\)", src)
print(m.group(0) if m else "NOT FOUND")
