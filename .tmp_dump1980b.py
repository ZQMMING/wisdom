# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
d = json.load(open("cases1980_both.json", encoding="utf-8"))["1980B"]
# 输出全部原始字段，供逐项翻译
print(json.dumps(d, ensure_ascii=False, indent=1, default=str)[:6000])
