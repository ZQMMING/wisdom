# -*- coding: utf-8 -*-
import io,sys,csv
sys.path.insert(0,r'D:\shuntian-ziping-p0')
base=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
src=io.open(base,encoding='utf-8').read()
src=src.replace('for x in dislist[:45]:','for x in dislist:')
out=r'D:\shuntian-ziping-p0\scripts\dis_v4.csv'
src+=("\nimport csv as _csv\n"
      "with open(r'%s','w',encoding='utf-8-sig',newline='') as _fh:\n"
      "    _w=_csv.writer(_fh); _w.writerow(['line','chart','gz','lc','ganwx','zhiwx','ju','v','primary','fav','av','blob','clash'])\n"
      "    for x in dislist: _w.writerow(x)\n"
      "print('DUMP',len(dislist))\n")%out
exec(compile(src,'dayun_align','exec'),{'__name__':'__main__'})
