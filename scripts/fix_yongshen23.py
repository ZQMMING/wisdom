# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 在水专旺条件前添加调试print
old = """        _shui_zhuanwang = (ben(t['bi'])>=3 or (ben(t['bi'])>=2 and stem(t['bi'])>=1)) and stem(t['shi'])>=1 and dmw=='水'
        if primary is None and _shui_zhuanwang:"""
new = """        _shui_zhuanwang = (ben(t['bi'])>=3 or (ben(t['bi'])>=2 and stem(t['bi'])>=1)) and stem(t['shi'])>=1 and dmw=='水'
        if dm=='癸' and mz=='子': print(f'DEBUG shui_zhuanwang: ben_bi={ben(t["bi"])}, stem_bi={stem(t["bi"])}, stem_shi={stem(t["shi"])}, dmw={dmw}, cond={_shui_zhuanwang}, primary={primary}')
        if primary is None and _shui_zhuanwang:"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('调试print添加完成')
