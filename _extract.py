# -*- coding: utf-8 -*-
import fitz, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
doc = fitz.open(r'D:\顺天系统资料\河洛正本\K3-447_009.pdf')
for n in [24, 26, 32, 37, 45, 52]:
    t = doc[n-1].get_text()
    print(f'=== p{n} 文字层 ===')
    print(t[:600])
    print()
