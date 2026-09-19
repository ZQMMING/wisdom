# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'
s=io.open(p,encoding='utf-8').read()
old=("        if len(_pres)==2 and _cnt[_pres[0]]>=3 and _cnt[_pres[1]]>=3 \\\n"
     "                and (SHENG.get(_pres[0])==_pres[1] or SHENG.get(_pres[1])==_pres[0]):\n")
new=("        # 假两气排除(DTS L862癸亥甲寅): 月令食伤当令, 且日主本气根支被六合化为食伤(寅亥合木、水根化木),\n"
     "        # 食伤太重泄身(任注'寅亥化木,伤官太重'), 乃正格伤官用印(喜印官、逢克方反吉), 非两气成象(真两气逢克泄必凶)\n"
     "        _LIUHE_HS={('子','丑'):'土',('丑','子'):'土',('寅','亥'):'木',('亥','寅'):'木',('卯','戌'):'火',('戌','卯'):'火',\n"
     "                   ('辰','酉'):'金',('酉','辰'):'金',('巳','申'):'水',('申','巳'):'水',('午','未'):'土',('未','午'):'土'}\n"
     "        _ss_lin = BRANCH_WX.get(pillars['month'][1])==SHENG.get(dm_wx)\n"
     "        _gen_hua_ss = False\n"
     "        for _pr in (facts.get('combination_facts', {}) or {}).get('liuhe', []):\n"
     "            if _LIUHE_HS.get((_pr[0], _pr[1]))==SHENG.get(dm_wx) \\\n"
     "                    and (BRANCH_WX.get(_pr[0])==dm_wx or BRANCH_WX.get(_pr[1])==dm_wx):\n"
     "                _gen_hua_ss = True\n"
     "        _not_lq = _ss_lin and _gen_hua_ss\n"
     "        if len(_pres)==2 and _cnt[_pres[0]]>=3 and _cnt[_pres[1]]>=3 \\\n"
     "                and (SHENG.get(_pres[0])==_pres[1] or SHENG.get(_pres[1])==_pres[0]) and not _not_lq:\n")
assert s.count(old)==1,('lq',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('假两气排除(伤官太重根被合化) done')
