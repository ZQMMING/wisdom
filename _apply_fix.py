# -*- coding: utf-8 -*-
import json, shutil, io, sys, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\shuntian\data\heluo\canping\canping_jingyi_full.json'
bak = p + '.bak_46fix'
if not os.path.exists(bak):
    shutil.copy2(p, bak)
    print('backup ->', bak)
else:
    print('backup exists, skip')

fix = {
 # fire
 'p52-c0':'寅寅','p52-c4':'午午','p40-c4':'卯丑','p44-c4':'子申','p39-c2':'子亥',
 'p51-c2':'子亥','p41-c1':'卯巳','p48-c1':'辰戌','p52-c2':'辰辰','p49-c2':'卯戌',
 'p47-c0':'辰亥','p47-c1':'午亥','p45-c1':'戌寅','p50-c0':'寅戌',
 # water
 'p28-c4':'丑巳','p36-c0':'丑丑','p28-c0':'午酉','p37-c0':'午午','p24-c4':'子寅',
 'p28-c3':'子辰','p22-c1':'寅丑','p32-c4':'子未','p26-c3':'戌亥','p37-c4':'戌戌',
 'p24-c2':'酉戌','p24-c0':'未申','p28-c1':'未戌','p37-c1':'未未','p26-c1':'申酉',
 'p28-c2':'申亥','p32-c0':'申寅','p37-c2':'申申','p32-c2':'辰戌','p36-c3':'辰辰',
 'p26-c2':'酉戌','p32-c1':'酉卯','p37-c3':'酉酉','p26-c0':'午申',
 # wood
 'p56-c2':'子寅',
}
d = json.load(open(p, encoding='utf-8'))
items = d if isinstance(d, list) else d.get('items') or d.get('data')
changed=0
for it in items:
    k = str(it.get('no',''))
    if k in fix:
        old = it.get('header')
        it['header'] = fix[k]
        changed+=1
        print(f'{k} {it.get("part")}: {old!r} -> {fix[k]!r}')
print('changed', changed)
json.dump(d, open(p,'w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('saved')
