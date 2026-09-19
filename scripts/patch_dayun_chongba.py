# -*- coding: utf-8 -*-
import io
p=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(p,encoding='utf-8').read()
old="        clash=[c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]\n"
new=("        clash=[]; _zba=False\n"
     "        for _c in transit_clash_verdicts(tp):\n"
     "            if z in _c['pair']:\n"
     "                clash.append(_c['verdict'])\n"
     "                _zt=_c['a_tier'] if _c['pair'][0]==z else _c['b_tier']\n"
     "                _ot=_c['b_tier'] if _c['pair'][0]==z else _c['a_tier']\n"
     "                if int(_zt.get('tier',0))<int(_ot.get('tier',0)): _zba=True\n"
     "        # 喜用运支被成势之冲拔(衰者拔): 用神根损伤, 运来喜用反主凶(《滴天髓》用神不可损伤); 化神局不覆盖、已判凶不放宽\n"
     "        if _zba and (not new_hs) and zc=='fav' and lc in ('fav','fav_l','xian','mix'):\n"
     "            print('CHONGBA',li+1,''.join(a+b for a,b in fp)[:8],gz,gc,zc,'->',('av' if gc=='av' else 'av_l'),'|',blob[:40].replace(chr(10),' '))\n"
     "            lc='av' if gc=='av' else 'av_l'\n")
assert s.count(old)==1,('cb',s.count(old)); s=s.replace(old,new)
io.open(p,'w',encoding='utf-8',newline='').write(s)
print('喜用运支冲拔修饰 done(含debug)')
