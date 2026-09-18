# -*- coding: utf-8 -*-
import io
p=r'scripts/gen_topo.py'
s=io.open(p,encoding='utf-8').read()
def rep(old,new,n=1):
    global s
    c=s.count(old); assert c==n, f'{c}!={n}: {old[:60]}'
    s=s.replace(old,new)

# 1) 定义 lu_yin_ok (衰极块前)
rep("    # ---- 衰极(ratio 主轴 + 无根/当令成势结构) ----\n    if ratio < 0.07:",
    "    # 禄刃硬根+独立本气印、官杀虚浮不当令不成势: 身旺任财官(即使ratio被死绝月令系数压低)\n"
    "    lu_yin_ok = (dm_has_lu and yin_ben>=1 and (not gs_dangling) and (not gs_shi))\n"
    "    # ---- 衰极(ratio 主轴 + 无根/当令成势结构) ----\n    if ratio < 0.07:")

# 2) 128 前置 ratio<0.18 衰块豁免 lu_yin_ok
rep("    elif ratio < 0.18 or (R==0 and (fin_shi>=1 or (ss_shi and L==0))):\n        spec='太衰'",
    "    elif (ratio < 0.18 and not lu_yin_ok) or (R==0 and (fin_shi>=1 or (ss_shi and L==0))):\n        spec='太衰'   # 禄刃+本气印+官杀虚者豁免(己亥丁卯庚申申禄辰印, 卯月绝令系数压低ratio而实任财官)")

# 3) 删除 B 后的 D 块
dblock="""    # ---- 禄刃硬根+独立本气印化、官杀虚浮不当令不成势: 身旺任财官(日主健旺足以用官) ----
    elif (dm_has_lu and yin_ben>=1 and (not gs_dangling) and (not gs_shi)
          and fin_rooted<=dm_ben+1 and ratio>=0.15):
        spec='旺'   # 己亥丁卯庚申庚辰(申禄辰本气戊印, 丁官虚, 足以用官科甲封疆); 己巳癸酉丙寅庚寅(巳禄寅印)
"""
rep(dblock,"")

# 4) 前移到 168 印重/比劫党块之后(降级块之前)
rep("""    elif S>=2 and (yin_zhong_sheng or dang_you_gen) and ratio>=0.25:
        spec='旺'
""",
"""    elif S>=2 and (yin_zhong_sheng or dang_you_gen) and ratio>=0.25:
        spec='旺'
    # ---- 禄刃硬根+独立本气印、官杀虚浮不当令不成势: 身旺任财官(日主健旺足以用官, 须先于得时不旺降级) ----
    elif lu_yin_ok and fin_rooted<=dm_ben+1 and ratio>=0.15:
        spec='旺'   # 己亥丁卯庚申庚辰(申禄辰本气戊印, 丁官虚, 足以用官科甲封疆); 己巳癸酉丙寅庚寅(巳禄寅印)
""")
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('lu_yin_ok: 前置衰块豁免 + 规则D前移降级前')
