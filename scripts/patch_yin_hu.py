# -*- coding: utf-8 -*-
# 印绶格护印分支(身旺WANG_TIER内, line430机械"身旺用财"之前):
# 月令印当令透干(格神印, 秋水通源/中和纯粹)、财透但无本气根且失令(休囚死)=虚财坏印为病,
# 当用印护格、比劫制财(药), 不以虚财为用; 财有根成势破印之壅塞归B4/母灭门, 不在此。
# L516 辛卯丙申癸卯壬戌: 癸生申月辛印透当令、丙火财透坐申无根火囚, 原文"以申金为用、丙火为病、壬水为药"。
import io
fp=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(fp,encoding='utf-8').read()
old="            elif qi(t['cai']): P(t['cai'],'FUYI','身旺用财，我克为财')"
assert s.count(old)==1, ('old',s.count(old))
new="""            elif BRANCH_WX.get(mz)==t['yin'] and (stem(t['yin'])>=1 or ling(t['yin'])=='旺') \\
                    and stem(t['cai'])>=1 and ben(t['cai'])==0 and ling(t['cai']) in ('休','囚','死') \\
                    and ben(t['yin'])<=2:
                # 印绶格印当令透干、财虚透无根失令反坏印为病, 用印护格、比劫制财护印(财有根破壅归B4不在此)
                P(t['yin'],'BINGYAO','印绶格印当令透干、财虚透无根失令坏印为病，用印护格'); S(t['bi'],'比劫制财护印(药)'); A(t['cai'],'虚财坏印为病'); _zhuan_shi=True
            elif qi(t['cai']): P(t['cai'],'FUYI','身旺用财，我克为财')"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched yinshou ge hu-yin (xu cai huai yin)')
