# -*- coding: utf-8 -*-
import sys, io, os, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 46条残缺列涉及的 raw page（去重）
pages = [24,26,28,32,35,36,37,39,40,41,44,45,47,48,49,50,51,52,55,56]
base = r'D:\顺天系统资料\河洛正本\ocr_output\K3-447_009'

for pg in pages:
    fp = os.path.join(base, f'p{pg:03d}.md')
    if not os.path.exists(fp):
        print(f'### raw p{pg} -> 447 p{pg:03d}  缺文件'); continue
    lines = open(fp, encoding='utf-8').read().splitlines()
    # 打印前6行（表头区：干支标注行 + 男/女/歲横看 + 首行诗）
    print(f'### raw p{pg} -> 447 p{pg:03d}')
    for i, ln in enumerate(lines[:7]):
        print(f'  L{i}: {ln}')
    print()
