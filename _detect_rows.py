# -*- coding: utf-8 -*-
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from PIL import Image
LOC = r'C:\Users\ming\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.sessions\38441318361371138\agents\o_0001WbT8w2b\loc'
n = int(sys.argv[1]) if len(sys.argv)>1 else 26
im = Image.open(os.path.join(LOC, f'p447_{n:03d}.png')).convert('L')
W0,H0 = im.size
# downscale width to 900 for scanning
tw = 900
th = int(H0 * tw / W0)
small = im.resize((tw, th))
px = small.load()
def darkcount_row(y):
    c=0
    for x in range(tw):
        if px[x,y] < 128: c+=1
    return c
print('orig',W0,H0,'small',tw,th,'scale y=',H0/th)
# find long horizontal rules (rows where >55% ink)
print('--- long horizontal rules (ink frac>0.5) ---')
for y in range(th):
    c = darkcount_row(y)
    if c > 0.5*tw:
        print('  small-y=%d  full-y=%.0f  ink=%d'%(y, y*H0/th, c))
# ink bands in top third
print('--- ink bands in top 40% (small y) ---')
run_start=None
for y in range(int(th*0.42)):
    c = darkcount_row(y)
    has = c > 15
    if has and run_start is None: run_start=y
    if (not has or y==int(th*0.42)-1) and run_start is not None:
        print('  band small-y %d..%d  full-y %.0f..%.0f'%(run_start,y, run_start*H0/th, y*H0/th))
        run_start=None
