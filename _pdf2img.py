# -*- coding: utf-8 -*-
import os, fitz
SRC = r'D:\顺天系统资料\河洛正本\K3-447_009.pdf'
DST = r'C:\Users\ming\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.sessions\38441318361371138\agents\m_0cwEjCaaqOA\loc'
os.makedirs(DST, exist_ok=True)
doc = fitz.open(SRC)
print('总页数', doc.page_count)
for n in [26, 24, 32, 37, 45, 52]:
    page = doc[n-1]  # 0-based
    pix = page.get_pixmap(matrix=fitz.Matrix(3, 3))
    out = os.path.join(DST, f'p447_{n:03d}.png')
    pix.save(out)
    print('saved', out, pix.width, pix.height)
