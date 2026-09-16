# -*- coding: utf-8 -*-
# 用法: python _hdr_zoom.py <page> [page...]
# 自动检测每页表头横格线(首条长横线), 裁其上方字带, 按宽度切5列(最右=c0), 放大输出 z_p{pg}_phy{k}.png
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image
LOC = r'C:\Users\ming\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.sessions\38441318361371138\agents\o_0001WbT8w2b\loc'

def find_rule_y(im):
    W0,H0 = im.size
    tw=700; th=int(H0*tw/W0)
    sm = im.convert('L').resize((tw,th))
    px=sm.load()
    best=None
    for y in range(0, int(th*0.30)):
        c=sum(1 for x in range(tw) if px[x,y]<128)
        if c>0.45*tw:
            best=y; break
    if best is None: return int(H0*0.17)
    return int(best*H0/th)

for arg in sys.argv[1:]:
    n=int(arg)
    im=Image.open(os.path.join(LOC,f'p447_{n:03d}.png'))
    W,H=im.size
    rule=find_rule_y(im)
    Y0=max(0, rule-430); Y1=rule+40
    band=im.crop((0,Y0,W,Y1))
    bw=W//5
    for i in range(5):
        x0=i*bw
        strip=band.crop((x0,0,x0+bw,Y1-Y0))
        s=1700/strip.width
        strip=strip.resize((int(strip.width*s),int(strip.height*s)),Image.LANCZOS)
        phy=5-i   # phy1=最右=c0; phy5=最左=c4
        strip.save(os.path.join(LOC,f'z_p{n:03d}_phy{phy}.png'))
    print('p',n,'rule_y',rule,'band',(Y0,Y1))
