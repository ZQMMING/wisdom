# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在最后增加保存不匹配案例到JSON文件
old = """for d in details[:10]:
    print('%s %s: 引擎=%s, 原文=%s' % (d['chart'], d['dayun'], d['engine'], d['text']))
    print('  原文: %s' % d['text_snippet'][:80])"""

new = """for d in details[:10]:
    print('%s %s: 引擎=%s, 原文=%s' % (d['chart'], d['dayun'], d['engine'], d['text']))
    print('  原文: %s' % d['text_snippet'][:80])

# 保存所有不匹配案例到JSON文件
import json as _json
with open(r'D:\shuntian-ziping-p0\scripts\dayun_mismatch_all.json', 'w', encoding='utf-8') as _f:
    _json.dump(details, _f, ensure_ascii=False, indent=2)
print()
print('所有不匹配案例已保存到: scripts\\dayun_mismatch_all.json (共%d个)' % len(details))"""

c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('评估脚本修改完成: 保存所有不匹配案例到JSON')
