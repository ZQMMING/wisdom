# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
p = "docs/v2/盲派9例对齐验证_V3.4.3.md"
src = io.open(p, encoding="utf-8").read()
# 找测试段实际文本
idx = src.find("## 测试")
print(repr(src[idx:idx+400]))
