# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_dayun_xiji_accuracy.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 回退V3的明确喜忌运引导词匹配
old_start = "        # V3: 明确的喜忌运引导词匹配 (优先级最高)"
old_end = "        # 在上下文中判断喜忌"

# 找到V3部分并删除
idx_start = c.find(old_start)
idx_end = c.find(old_end)
if idx_start >= 0 and idx_end >= 0:
    c = c[:idx_start] + c[idx_end:]

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('回退到V2提取完成')
