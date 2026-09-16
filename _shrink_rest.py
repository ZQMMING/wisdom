# -*- coding: utf-8 -*-
import fitz, io, sys, os
from PIL import Image
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
PDF = r'D:\顺天系统资料\河洛正本\K3-447_009.pdf'
OUT = r'C:\Users\ming\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.sessions\38441318361371138\agents\m_0cwEjCaaqOA\loc'
os.makedirs(OUT, exist_ok=True)
pages = [27,29,30,31,33,34,38,43,46]
doc = fitz.open(PDF)
for N in pages:
    pg = doc[N-1]
    pix = pg.get_pixmap(matrix=fitz.Matrix(3,3))
    img = Image.frombytes('RGB',[pix.width,pix.height],pix.samples)
    w,h = img.size
    top = img.crop((0,0,w,int(h*0.42)))
    tw = 3800
    th = int(top.height*tw/top.width)
    top = top.resize((tw,th), Image.LANCZOS)
    fp = os.path.join(OUT, f'p447_{N:03d}_top.png')
    top.save(fp)
    print('saved', fp, top.size)
