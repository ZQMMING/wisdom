# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'
s=io.open(p,encoding='utf-8').read()
old="    if not hua_name and dm_ben_eff >= 1:\n"
new=("    _dm_ben_pure = sum(1 for _k in ('year','month','day','hour') if BRANCH_WX.get(pillars[_k][1])==dm_wx) + dm_ju\n"
     "    # 印旺非专旺: 无比劫方局、比劫纯本气(不含寄于印官本位的长生根BEN_CS)<=1、而印本气成势(>=3)=母旺子相、印旺正格身旺任官,\n"
     "    # 非一行专旺(阳干长生在印母之宫, 如壬生申, 申本气庚金是印, 不作水比劫成方); DTS L2251 金印3/水纯根1, 任注喜土火官杀科甲, 非润下\n"
     "    _yin_wang_not_zw = (dm_ju == 0 and _dm_ben_pure <= 1 and yin_ben_eff >= 3)\n"
     "    if not hua_name and dm_ben_eff >= 1 and not _yin_wang_not_zw:\n")
assert s.count(old)==1,('yw',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('印旺非专旺排除 done')
