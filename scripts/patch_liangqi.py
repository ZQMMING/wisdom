# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(p,encoding='utf-8').read()
old=("    if lq:\n"
     "        if lq.get('xiu'): P(lq['xiu'],'LIANGQI','两气成象顺食伤秀神'); S(t['bi'],'成象顺本方')\n")
new=("    if lq and lq.get('relation')=='相生':\n"
     "        # 相生两气成象(w1->w2): 顺其势喜chain两神+w2顺泄(食伤); 忌克w2(官杀犯旺)、克w1(财断源)\n"
     "        ws=[w for w in (lq.get('wuxing') or []) if w]\n"
     "        w1=w2=None\n"
     "        for _a in ws:\n"
     "            for _b in ws:\n"
     "                if SHENG.get(_a)==_b: w1,w2=_a,_b\n"
     "        if lq.get('xiu'): P(lq['xiu'],'LIANGQI','两气成象顺其相生之势, 取秀神')\n"
     "        for _w in ws: S(_w,'成象顺神')\n"
     "        if w2:\n"
     "            S(SHENG.get(w2),'顺chain泄秀')\n"
     "            for _w in (KE_ME.get(w2),KE_ME.get(w1)):\n"
     "                if _w: A(_w,'逆chain犯旺/断源')\n"
     "    elif lq:\n"
     "        if lq.get('xiu'): P(lq['xiu'],'LIANGQI','两气成象顺秀神'); S(t['bi'],'成象顺本方')\n")
assert s.count(old)==1, ('lq',s.count(old))
s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('两气成象相生顺逆喜忌 done')
