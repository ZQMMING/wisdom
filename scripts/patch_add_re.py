# -*- coding: utf-8 -*-
import io
fp=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(fp,encoding='utf-8').read()
old="""吉凶前端拦截, 本层只给真实取用结构; 不接 production_entry。
\"\"\"
WUXING='木火土金水'"""
assert s.count(old)==1, s.count(old)
new="""吉凶前端拦截, 本层只给真实取用结构; 不接 production_entry。
\"\"\"
import re
WUXING='木火土金水'"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('added import re')
