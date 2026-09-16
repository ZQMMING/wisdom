# -*- coding: utf-8 -*-
import json, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
p = r'D:\shuntian\data\heluo\canping\canping_jingyi_full.json'
fix = {
 'p26-c4':'子卯',
 # p35
 'p35-c0':'寅亥','p35-c1':'子戌','p35-c4':'子子',
 # p36
 'p36-c1':'寅寅','p36-c2':'卯卯','p36-c4':'巳巳',
 # p41 (纠正上轮错改:秋月照空山在丑亥列)
 'p41-c1':'丑亥',
 # p45
 'p45-c0':'丑酉','p45-c3':'午戌',
 # p49 (秋色来天上在辰亥列,纠正)
 'p49-c0':'寅酉','p49-c1':'卯戌','p49-c2':'辰亥','p49-c4':'丑酉',
 # p52
 'p52-c1':'卯卯','p52-c3':'巳巳',
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
