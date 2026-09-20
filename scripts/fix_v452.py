# -*- coding: utf-8 -*-
"""V4.52: 完善调候路径avoid列表，增加生扶调候忌神的五行"""
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

old = """            # V4.36: 调候路径同步设置忌神(克调候用神的五行为忌), 避免avoid为空导致大运喜忌误判
            _ke_of_hou = KE_ME.get(hou[0])
            if _ke_of_hou:
                A(_ke_of_hou,'克调候用神为忌')"""

new = """            # V4.36: 调候路径同步设置忌神(克调候用神的五行为忌), 避免avoid为空导致大运喜忌误判
            _ke_of_hou = KE_ME.get(hou[0])
            if _ke_of_hou:
                A(_ke_of_hou,'克调候用神为忌')
            # V4.52: 增加生扶调候忌神的五行为忌(原典: 生忌神者亦为忌)
            if _ke_of_hou:
                _sheng_of_ji = SHENG_ME.get(_ke_of_hou)
                if _sheng_of_ji and _sheng_of_ji != hou[0]:
                    A(_sheng_of_ji,'生扶调候忌神为忌')"""

if old in c:
    c = c.replace(old, new)
    print('V4.52修改成功')
else:
    print('未找到目标字符串')
    # 调试：看看实际内容
    import re
    match = re.search(r'V4\.36.*?A\(_ke_of_hou.*?\)', c, re.DOTALL)
    if match:
        print('找到匹配:', repr(match.group()[:100]))

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
