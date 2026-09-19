# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()
old=("        # g类噪声: 《原注》假设泛论(“日主喜X则吉/喜Y则不吉”)非本命断语, 不入对齐分母\n"
     "        if blob and (('【原注】' in blob) or ('日主喜' in blob and '则' in blob and ('不吉' in blob or '则吉' in blob))):\n"
     "            v=None\n")
new=("        # g类噪声: 断语窗以《原注》标记开头=章末通用泛论(非本命任注断语), 不入对齐分母; 本命断语不以【原注】开头\n"
     "        if blob and blob.lstrip().startswith('【原注】'):\n"
     "            v=None\n")
assert s.count(old)==1,('g4',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('原注泛论收紧为开头标记 done')
