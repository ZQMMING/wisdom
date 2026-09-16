# -*- coding: utf-8 -*-
import os
from PIL import Image
SRC = r'D:\顺天系统资料\河洛理数_藏书阁K3-448_1632_OCR\K3-448_008_png'
DST = r'C:\Users\ming\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.sessions\38441318361371138\agents\m_0cwEjCaaqOA\loc'
os.makedirs(DST, exist_ok=True)
for p in range(0, 20):
    src = os.path.join(SRC, f'p{p:04d}.png')
    if not os.path.exists(src):
        print('缺', src); continue
    im = Image.open(src); w, h = im.size
    s = 2200 / max(w, h)
    if s < 1: im = im.resize((int(w*s), int(h*s)), Image.LANCZOS)
    im.convert('RGB').save(os.path.join(DST, f'v8_p{p:04d}.png'), quality=85)
print('done')
