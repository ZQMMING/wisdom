# -*- coding: utf-8 -*-
import io
p=r'scripts/gen_topo.py'
s=io.open(p,encoding='utf-8').read()
def rep(old,new,n=1):
    global s
    c=s.count(old); assert c==n, f'{c}!={n}: {old[:60]}'
    s=s.replace(old,new)

# 1) gs_ben 初始化
rep("    yin_cheng=False; guan_hua=False; cai_ben=0; bj_stem=0; yin_stem=0; month_wx=None; lu_chong=False",
    "    yin_cheng=False; guan_hua=False; cai_ben=0; gs_ben=0; bj_stem=0; yin_stem=0; month_wx=None; lu_chong=False")
# 2) gs_ben 计算
rep("        cai_ben = int(cai.get('ben_n',0))",
    "        cai_ben = int(cai.get('ben_n',0)); gs_ben = int(gs.get('ben_n',0))")
# 3) lu_chong 扩展众冲寡
old_lc=("        lu_chong = (L<2) and any(z in _chong0 and t=='BEN' and not (dm_wx=='土' and z in _ku0)\n"
        "                             for z,t in (dm.get('root_detail',{}) or {}).items())")
new_lc=("        _chong_ben = [z for z,t in (dm.get('root_detail',{}) or {}).items()\n"
        "                     if z in _chong0 and t=='BEN' and not (dm_wx=='土' and z in _ku0)]\n"
        "        # 禄刃本气根遭六冲: 我非当令(旺者冲衰衰者拔), 或财官党众冲克寡根(两卯冲酉+午克)\n"
        "        lu_chong = bool(_chong_ben) and (L<2 or (cai_ben+gs_ben > dm_ben))")
rep(old_lc,new_lc)
# 4) C: 财当令官印流通身旺(169 后)
old_c=("        spec='旺'\n    # ---- 食伤当令成势泄身+财透根耗身, 日主仅长生无禄刃(死月印止泄不力): 泄气太重/财多身弱 ----")
new_c=("        spec='旺'\n"
        "    elif (S>=3 and guan_hua and dm_has_lu and yin_ben>=1 and yin_stem>=1\n"
        "          and fin_rooted_eff<=1 and ratio>=0.20):\n"
        "        spec='旺'   # 财当令而财->官->印->身流通, 禄刃+本气印双透: 日元临旺逢生官印双清(乙卯丁亥戊午丙辰)\n"
        "    # ---- 食伤当令成势泄身+财透根耗身, 日主仅长生无禄刃(死月印止泄不力): 泄气太重/财多身弱 ----")
rep(old_c,new_c)
# 5) B: lu_chong 众冲寡衰(规则D后)
old_b=("        spec='旺'   # 己亥丁卯庚申庚辰(申禄辰本气戊印丁官虚, 足以用官科甲封疆); 己巳癸酉丙寅庚寅(巳禄寅印)\n")
new_b=old_b+("    # ---- 禄刃本气根遭六冲被拔(我非当令, 或财官党众冲克寡根): 根拔不任财官(T30 旺者冲衰衰者拔) ----\n"
        "    elif lu_chong and ratio<0.62 and (L<2 or (cai_ben+gs_ben > dm_ben)):\n"
        "        spec='衰'   # 乙卯乙酉庚寅壬午(酉刃当令被两卯冲+午火克, 财官党4>身1, 反弱不任财官)\n")
rep(old_b,new_b)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('官印流通身旺(C) + 禄刃众冲克折减(B) 接入')
