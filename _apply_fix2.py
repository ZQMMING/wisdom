# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\shuntian\data\heluo\canping\canping_jingyi_full.json'
fix = {
 # p27
 'p27-c2':'子酉','p27-c3':'丑未','p27-c4':'寅亥',
 # p29
 'p29-c0':'申子','p29-c1':'酉丑','p29-c2':'寅戌','p29-c3':'卯亥','p29-c4':'午戌',
 # p30
 'p30-c0':'未亥','p30-c2':'子未','p30-c3':'丑申','p30-c4':'寅酉',
 # p31
 'p31-c0':'卯辰','p31-c1':'辰亥','p31-c3':'子午',
 # p33
 'p33-c0':'丑申','p33-c1':'寅酉','p33-c2':'卯戌','p33-c3':'辰亥','p33-c4':'子申',
 # p34
 'p34-c0':'酉丑','p34-c1':'寅戌','p34-c2':'卯亥','p34-c3':'子酉','p34-c4':'戌未',
 # p43
 'p43-c0':'巳寅','p43-c2':'丑戌','p43-c3':'寅亥',
 # p46
 'p46-c0':'子巳','p46-c2':'丑申','p46-c3':'寅酉','p46-c4':'卯戌',
}
d = json.load(open(p, encoding='utf-8'))
n=0
for it in d['items']:
    k=str(it.get('no'))
    if k in fix:
        old=it.get('header'); it['header']=fix[k]; n+=1
        print(f'{k} {it.get("part")}: {old!r} -> {fix[k]!r}')
print('changed',n)
json.dump(d,open(p,'w',encoding='utf-8'),ensure_ascii=False,indent=2)
print('saved')
