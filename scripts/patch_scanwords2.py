# -*- coding: utf-8 -*-
import io
p=r'scripts/direction_scan.py'
s=io.open(p,encoding='utf-8').read()
def rep(old,new,n=1):
    global s
    c=s.count(old); assert c==n, f'{c}!={n}: {old[:50]}'
    s=s.replace(old,new)
# 1) 删除歧义 X坚(木嫩金坚=杀坚非日主旺)
rep(",'木堅','木坚','金堅','金坚','水旺木堅','水旺木坚']","]")
# 2) QUOTE 增加五行数法则/何知章歌诀/运后印旺 拦截
rep("GEN=re.compile(r'(大凡|凡命|凡|假使|假如|设使|蓋|盖|所谓须要|所謂須要|须要|須要|必要|必先|俗以|人皆|皆曰|前造|前之|何以|何為|何为|安在|试看|試看)')",
    "GEN=re.compile(r'(大凡|凡命|凡|假使|假如|设使|蓋|盖|所谓须要|所謂須要|须要|須要|必要|必先|俗以|人皆|皆曰|前造|前之|何以|何為|何为|安在|试看|試看|当令者倍之|當令者倍之|休囚者减半|休囚者減半|木三金四|何知其人)')")
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('词表去歧义: 删X坚, 加五行数法则/何知章拦截')
