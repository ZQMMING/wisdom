# -*- coding: utf-8 -*-
import io
p=r'scripts/gen_topo.py'
s=io.open(p,encoding='utf-8').read()
def rep(old,new,n=1):
    global s
    c=s.count(old); assert c==n, f'{c}!={n}: {old[:60]}'
    s=s.replace(old,new)

# 1) lu_yin_ok 定义
rep("    # ---- 衰极(ratio 主轴 + 无根/当令成势结构) ----\n    if ratio < 0.07:",
    "    # 禄刃硬根+独立本气印、官杀虚浮不当令不成势: 身旺任财官(虽ratio被死绝月令系数压低)\n"
    "    lu_yin_ok = (dm_has_lu and yin_ben>=1 and (not gs_dangling) and (not gs_shi))\n"
    "    # ---- 衰极(ratio 主轴 + 无根/当令成势结构) ----\n    if ratio < 0.07:")

# 2) 128 豁免
rep("    elif ratio < 0.18 or (R==0 and (fin_shi>=1 or (ss_shi and L==0))):\n        spec='太衰'",
    "    elif (ratio < 0.18 and not lu_yin_ok) or (R==0 and (fin_shi>=1 or (ss_shi and L==0))):\n        spec='太衰'   # 禄刃+本气印+官杀虚者豁免(申禄辰印, 绝令系数压低ratio而实任财官)")

# 3) 删除旧 D 块(201-204, 含拼入的B尾注)
old_d=("    # ---- 禄刃硬根+独立本气印化、官杀虚浮不当令不成势: 身旺任财官(日主健旺足以用官) ----\n"
"    elif (dm_has_lu and yin_ben>=1 and (not gs_dangling) and (not gs_shi)\n"
"          and fin_rooted<=dm_ben+1 and ratio>=0.15):\n"
"        spec='旺'   # 己亥丁卯庚申庚辰(申禄辰本气戊印, 丁官虚, 足以用官科甲封疆); 己巳癸酉丙寅庚寅(巳禄寅印)   # 己卯庚午甲寅丁卯日元强(寅禄两卯任丁泄); 壬午甲辰丁巳己酉日主临旺; 辛丑戊申旺而逢生\n")
rep(old_d,"")

# 4) 前移到 168 块后
rep("""    elif S>=2 and (yin_zhong_sheng or dang_you_gen) and ratio>=0.25:
        spec='旺'
""",
"""    elif S>=2 and (yin_zhong_sheng or dang_you_gen) and ratio>=0.25:
        spec='旺'
    # ---- 禄刃硬根+独立本气印、官杀虚浮不当令不成势: 身旺任财官(先于得时不旺降级; 日主健旺足以用官) ----
    elif lu_yin_ok and fin_rooted<=dm_ben+1 and ratio>=0.15:
        spec='旺'   # 己亥丁卯庚申庚辰(申禄辰本气戊印丁官虚, 足以用官科甲封疆); 己巳癸酉丙寅庚寅(巳禄寅印)
""")
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('lu_yin_ok 定义+128豁免+D前移完成')
