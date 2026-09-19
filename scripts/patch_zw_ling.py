# -*- coding: utf-8 -*-
# 专旺CANDIDATE门补排除(收窄版): 月令本气=财当令(cai_ling)、有本气财根、无完整本方局(dm_ju==0)、
# 且本方纯本气根(_dm_ben_pure, 按地支本气五行不含六合/会局归化)不足2 -> 月令财当权、身不成重党, 正格非专旺。
# L1855 甲戌月: 纯木本气仅寅1(亥系寅亥六合BEN_HE凑入, BRANCH_WX亥=水不计), 排除曲直;
# 己酉丙寅庚申庚辰: 金纯本气酉申2(酉刃申禄)三透成党, 失令不弱仍从革专旺用财木(GT木), 不排。
import io
fp=r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'
s=io.open(fp,encoding='utf-8').read()
old="""                and not (cai_ling and cai_stem >= 1) and not (gs_ling and (gs_stem >= 1 or cai_stem >= 1)):
            zw = ZHUANWANG_NAME.get(dm_wx)
            out['patterns'].append(_pat('ZP-SPECIAL-ZHUANWANG', zw, 'CANDIDATE', dm_wx,"""
assert s.count(old)==1, s.count(old)
new="""                and not (cai_ling and cai_stem >= 1) and not (gs_ling and (gs_stem >= 1 or cai_stem >= 1)) \
                and not (cai_ling and cai_ben_zw >= 1 and dm_ju == 0 and _dm_ben_pure < 2):
            zw = ZHUANWANG_NAME.get(dm_wx)
            out['patterns'].append(_pat('ZP-SPECIAL-ZHUANWANG', zw, 'CANDIDATE', dm_wx,"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched zhuanwang cai-ling exclude (pure_ben<2 narrow)')
