# -*- coding: utf-8 -*-
"""state.py 全部 out 字段审计 + 与规则消费对照"""
import json, io, sys, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

src = open(r'D:\shuntian-ziping-p0\engines\ditiansui\calculation\state.py', encoding='utf-8').read()

# 提取 out["xxx"] 赋值点
outs = {}
for m in re.finditer(r'out\["([^"]+)"\]\s*=\s*(.+)', src):
    fld, val = m.group(1), m.group(2).strip()
    outs.setdefault(fld, []).append(val[:90])

print('=== state.py 输出字段（共 %d 个）===' % len(outs))
for fld in sorted(outs):
    vals = outs[fld]
    print('%-34s' % fld, '|', '; '.join(v[:60] for v in vals[:3]))
