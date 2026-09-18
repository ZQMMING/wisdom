# -*- coding: utf-8 -*-
import io
p=r'scripts/gen_topo.py'
s=io.open(p,encoding='utf-8').read()
def rep(old,new,n=1):
    global s
    c=s.count(old); assert c==n, f'{c}!={n}: {old[:60]}'
    s=s.replace(old,new)

# 1) 初始化 lu_chong
rep("    yin_cheng=False; guan_hua=False; cai_ben=0; bj_stem=0; yin_stem=0; month_wx=None",
    "    yin_cheng=False; guan_hua=False; cai_ben=0; bj_stem=0; yin_stem=0; month_wx=None; lu_chong=False")

# 2) if pw 块内 ss_ling 后计算 lu_chong
rep("        ss_ling = (month_wx==ss_wx)",
    "        ss_ling = (month_wx==ss_wx)\n"
    "        # T30 禄刃/本气硬根支遭六冲、我非当令(月令囚死): 旺者冲衰衰者拔, 禄根被冲伤; 四库土冲反旺除外\n"
    "        _cf0 = facts.get('combination_facts',{}) if isinstance(facts,dict) else {}\n"
    "        _chong0 = {b for pr in (_cf0.get('liuchong') or []) for b in pr}\n"
    "        _ku0=('辰','戌','丑','未')\n"
    "        lu_chong = (L<2) and any(z in _chong0 and t=='BEN' and not (dm_wx=='土' and z in _ku0)\n"
    "                             for z,t in (dm.get('root_detail',{}) or {}).items())")

# 3) lu_yin_ok 排除禄刃被冲
rep("    lu_yin_ok = (dm_has_lu and yin_ben>=1 and (not gs_dangling) and (not gs_shi))",
    "    lu_yin_ok = (dm_has_lu and yin_ben>=1 and (not gs_dangling) and (not gs_shi) and (not lu_chong))")
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('lu_chong 冲根折减接入 lu_yin_ok')
