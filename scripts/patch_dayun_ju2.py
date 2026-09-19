# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()
old="_shun=any(x in ('ZHUANWANG','LIANGQI','CONG_SHUN') for x in (ye.get('yongshen_paths') or []))"
new="_shun=any(x in ('ZHUANWANG','LIANGQI') for x in (ye.get('yongshen_paths') or []))  # 从儿/从格会方顺神、干逆神坐化神多被顺化(吾儿又见儿), 不援虚干犯旺例"
assert s.count(old)==1,('shun',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('虚干犯旺收窄为专旺/两气 done')
