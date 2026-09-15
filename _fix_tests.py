# -*- coding: utf-8 -*-
"""修正 test_state.py 三态化断言"""
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

p = r'D:\shuntian-ziping-p0\engines\ditiansui\calculation\tests\test_state.py'
s = open(p, encoding='utf-8').read()

# 反例断言：不输出 → 恒输出反态
old_block = '''    v2 = res2.metadata["view"]
    assert "fire_state" not in v2.get("pending", {})
    assert "stimulus" not in v2.get("pending", {})
    assert "gold_meets" not in v2.get("pending", {})'''

new_block = '''    v2 = res2.metadata["view"]
    # 2026-09-16 三态化：单值枚举补反态，恒输出
    assert v2.get("pending", {}).get("fire_state") == "不烈"
    assert v2.get("pending", {}).get("stimulus") == "非激"
    assert v2.get("pending", {}).get("gold_meets") == "非水"'''

if old_block in s:
    s = s.replace(old_block, new_block)
    open(p, 'w', encoding='utf-8').write(s)
    print('FIXED: 反例断言')
else:
    print('!! old_block not found')

# 注释同步
old_cmt = '''    # 反例：无火当令（月支非火）→ 无 fire_state；无金水同现 → 无 stimulus/gold_meets'''
new_cmt = '''    # 反例：无火当令（月支非火）→ fire_state=不烈；无金水同现 → stimulus=非激/gold_meets=非水'''
if old_cmt in s:
    s = s.replace(old_cmt, new_cmt)
    open(p, 'w', encoding='utf-8').write(s)
    print('FIXED: 注释')
