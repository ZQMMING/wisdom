# -*- coding: utf-8 -*-
# 会而不化过滤: 新成三会/三合化神在原局月令处休囚死(不当令)、运支本气恰为"克化神者"、且运支本气为喜用
# (运支是制化神之药), 则该会局不主导喜忌, 还原本运干支(化神须得时乘令, 休囚被克会而不化)。
# L1855 戌月水死, 丁丑: 亥子丑会水方, 丑土克水(KE_ME[水]=土)、丑土P财喜用 -> 会水不化, 丁火S丑土P吉;
# L1322 寅月水休, 丁丑同理。真会局化神当令(旺/相)或运支生扶/比和化神不滤。
import io
fp=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(fp,encoding='utf-8').read()
old="""        new_hs=new_huashen(tp0,tp)
"""
assert s.count(old)==1, s.count(old)
new="""        new_hs=new_huashen(tp0,tp)
        if new_hs:
            _zwx=BRANCH_WX[z]; _KEME={vv:kk for kk,vv in KE.items()}
            new_hs=[w for w in new_hs if not (
                tp0['wuxing_power']['wuxing_power'][w].get('ling_state') in ('休','囚','死')
                and _KEME.get(w)==_zwx and _zwx in fav)]
"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched ju hui-er-bu-hua (KE_ME direction)')
