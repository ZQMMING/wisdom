# -*- coding: utf-8 -*-
import json
lines=open(r'D:\shuntian-ziping-lab\cases\all_cases.jsonl',encoding='utf-8').readlines()
kw_count={}
has_kw=0
for l in lines:
    d=json.loads(l)
    kw=d.get('wangshuai_kw',[])
    if kw:
        has_kw+=1
        if isinstance(kw,list):
            for k in kw:
                kw_count[k]=kw_count.get(k,0)+1
        else:
            kw_count[str(kw)]=kw_count.get(str(kw),0)+1
print(f'旺衰关键词分布:')
for k,v in sorted(kw_count.items(),key=lambda x:-x[1]):
    print(f'  {k}: {v}')
print(f'有旺衰关键词的案例: {has_kw}/{len(lines)}')
