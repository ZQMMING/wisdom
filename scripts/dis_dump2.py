# -*- coding: utf-8 -*-
import io, csv
src=io.open(r'D:\shuntian-ziping-p0\scripts\dayun_align.py',encoding='utf-8').read()
g={'__name__':'__main__'}
exec(compile(src,'dayun_align','exec'),g)
dis=g['dislist']
out=r'D:\shuntian-ziping-p0\scripts\dis_v5.csv'
with io.open(out,'w',encoding='utf-8-sig',newline='') as f:
    w=csv.writer(f); w.writerow(['line','chart','gz','lc','ganwx','zhiwx','ju','v','primary','fav','av','blob','clash'])
    for row in dis: w.writerow(row)
print('dis count',len(dis),'->',out)
