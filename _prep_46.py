# -*- coding: utf-8 -*-
import os, shutil, json, hashlib, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

JSON = r'D:\shuntian\data\heluo\canping\canping_jingyi_full.json'
BAK  = r'D:\shuntian\data\heluo\canping\canping_jingyi_full.json.bak_46fix'
SNAP = r'D:\shuntian\_snapshot_before.json'
SRC  = r'D:\顺天系统资料\河洛正本\K3-447_009.pdf'
LOC  = r'C:\Users\ming\AppData\Local\Doubao\User Data\Default\.doubao\agent_mode\workspace\.sessions\38441318361371138\agents\o_0001WbT8w2b\loc'

PAGES = [22,24,26,28,32,35,36,37,39,40,41,44,45,47,48,49,50,51,52,55,56]
PROT  = ['source_text','jingyi','modern_explanation','semantic_tags','evidence_basis']

# 1. backup
if not os.path.exists(BAK):
    shutil.copy2(JSON, BAK)
    print('backup ->', BAK)
else:
    print('backup already exists, skip:', BAK)

# 2. snapshot protected fields, keyed by no
lib = json.load(open(JSON, encoding='utf-8'))
items = lib['items']
snap = {}
for x in items:
    no = x['no']
    snap[no] = {k: x.get(k) for k in PROT}
json.dump(snap, open(SNAP,'w',encoding='utf-8'), ensure_ascii=False, indent=1, sort_keys=True)
h = hashlib.sha256(open(SNAP,'rb').read()).hexdigest()
print('snapshot items', len(snap), 'sha256', h[:16])

# 3. convert pages
import fitz
from PIL import Image
os.makedirs(LOC, exist_ok=True)
doc = fitz.open(SRC)
print('pdf pages', doc.page_count)
for n in PAGES:
    fp = os.path.join(LOC, f'p447_{n:03d}_top.png')
    if os.path.exists(fp):
        print('exists', fp); continue
    page = doc[n-1]
    pix = page.get_pixmap(matrix=fitz.Matrix(3,3))
    full = os.path.join(LOC, f'p447_{n:03d}.png')
    pix.save(full)
    im = Image.open(full)
    w,h = im.size
    top = im.crop((0,0,w,int(h*0.40)))
    s = 3800/max(top.size)
    top = top.resize((int(top.width*s), int(top.height*s)), Image.LANCZOS)
    top.save(fp)
    print('p', n, 'full', (w,h), 'top', top.size)
print('DONE')
