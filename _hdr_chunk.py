# -*- coding: utf-8 -*-
# 用法: python _hdr_chunk.py <page>
# 自动找表头线, 把表头横带切成3段宽幅重叠图(左/中/右), 放大输出 hc_p{pg}_{L,M,R}.png
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image
LOC = r'C:\Users\ming\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.sessions\38441318361371138\agents\o_0001WbT8w2b\loc'

def find_rule_y(im):
    W0,H0=im.size; tw=700; th=int(H0*tw/W0)
    sm=im.convert('L').resize((tw,th)); px=sm.load()
    for y in range(0,int(th*0.30)):
        c=sum(1 for x in range(tw) if px[x,y]<128)
        if c>0.45*tw: return int(y*H0/th)
    return int(H0*0.17)

for n in [int(a) for a in sys.argv[1:]]:
    im=Image.open(os.path.join(LOC,f'p447_{n:03d}.png'))
    W,H=im.size
    rule=find_rule_y(im)
    Y0=max(0,rule-470); Y1=rule+30
    band=im.crop((0,Y0,W,Y1))
    w3=W//3
    ov=360
    segs={'L':(0,w3+ov),'M':(w3-ov,2*w3+ov),'R':(2*w3-ov,W)}
    for tag,(a,b) in segs.items():
        strip=band.crop((a,0,b,Y1-Y0))
        s=2200/strip.width
        strip=strip.resize((int(strip.width*s),int(strip.height*s)),Image.LANCZOS)
        strip.save(os.path.join(LOC,f'hc_p{n:03d}_{tag}.png'))
    print('p',n,'rule',rule,'band',(Y0,Y1))
