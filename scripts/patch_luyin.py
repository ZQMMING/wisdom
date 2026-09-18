# -*- coding: utf-8 -*-
import io
p=r'scripts/gen_topo.py'
s=io.open(p,encoding='utf-8').read()
old="""          or (L==2 and dm_ben>=1 and fin_rooted<=1 and int(ss.get('ben_n',0))<2 and int(ss.get('ju_n',0))<1 and ratio>=0.30)):
        spec='旺'   # 特例: 禄刃重根而官杀全无、食伤仅泄秀非过泄(壬午癸丑甲寅丁卯寅卯气旺丁火秀)"""
new="""          or (L==2 and dm_ben>=1 and fin_rooted<=1 and int(ss.get('ben_n',0))<2 and int(ss.get('ju_n',0))<1 and ratio>=0.30)):
        spec='旺'   # 特例: 禄刃重根而官杀全无、食伤仅泄秀非过泄(壬午癸丑甲寅丁卯寅卯气旺丁火秀)
    # ---- 禄刃硬根+独立本气印化、官杀虚浮不当令不成势: 身旺任财官(日主健旺足以用官) ----
    elif (dm_has_lu and yin_ben>=1 and (not gs_dangling) and (not gs_shi)
          and fin_rooted<=dm_ben+1 and ratio>=0.15):
        spec='旺'   # 己亥丁卯庚申庚辰(申禄辰本气戊印, 丁官虚, 足以用官科甲封疆); 己巳癸酉丙寅庚寅(巳禄寅印)"""
assert s.count(old)==1, s.count(old)
io.open(p,'w',encoding='utf-8',newline='').write(s.replace(old,new))
print('规则D: 禄刃+本气印+官杀虚 -> 身旺任财官')
