# -*- coding: utf-8 -*-
from PIL import Image
import os
D = r'C:\Users\ming\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.sessions\38441318361371138\agents\m_0cwEjCaaqOA\loc'
for n in [26,24,32,37,45,52]:
    im = Image.open(os.path.join(D, f'p447_{n:03d}.png'))
    w,h = im.size
    # 裁顶部 38%（表头区：干支行+表头+首几列诗）
    top = im.crop((0,0,w,int(h*0.40)))
    s = 3800/max(top.size)
    top = top.resize((int(top.width*s), int(top.height*s)), Image.LANCZOS)
    top.save(os.path.join(D, f'p447_{n:03d}_top.png'))
    print(n, top.size)
