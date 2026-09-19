# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

old="    match = has_root and (yin_party or bijie_party) and not jiwang and not jishuai and not jiruo"
new="    match = (has_root or yin_party or bijie_party) and not jiwang and not jishuai and not jiruo"
content=content.replace(old,new)

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
