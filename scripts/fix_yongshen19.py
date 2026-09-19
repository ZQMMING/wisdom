# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 在身旺扶抑路径最前面增加印绶格护印条件(辛亥庚寅丙子乙未: 寅月印当令透干乙, 财虚透无根失令坏印, 用印护格)
old = """        if primary is None and tier in WANG_TIER:
            _zhuan_shi=False
            _gy=dm in '甲丙戊庚壬'; _yg='甲丙戊庚壬' if _gy else '乙丁己辛癸'
            _py_tou=any(_ganwx.get(g)==t['yin'] for g in other_gan if g in _yg)  # 偏印(生我同阴阳)透干
            _xiao_duo_shi=_py_tou and stem(t['shi'])>=1 and ben(t['shi'])==0  # 偏印透、食伤透无本气根=枭神夺食, 食伤被夺不可用
            if stem(t['guan'])>=2 and stem(t['shi'])>=1 and ben(t['guan'])==0 and ling(t['shi'])=='旺':"""
new = """        if primary is None and tier in WANG_TIER:
            _zhuan_shi=False
            _gy=dm in '甲丙戊庚壬'; _yg='甲丙戊庚壬' if _gy else '乙丁己辛癸'
            _py_tou=any(_ganwx.get(g)==t['yin'] for g in other_gan if g in _yg)  # 偏印(生我同阴阳)透干
            _xiao_duo_shi=_py_tou and stem(t['shi'])>=1 and ben(t['shi'])==0  # 偏印透、食伤透无本气根=枭神夺食, 食伤被夺不可用
            # 印绶格护印: 印当令透干、财虚透无根失令坏印为病, 用印护格(辛亥庚寅丙子乙未朱中堂造: 火虚木嫩用神在木忌神在金)
            if BRANCH_WX.get(mz)==t['yin'] and (stem(t['yin'])>=1 or ling(t['yin'])=='旺') \
                    and stem(t['cai'])>=1 and ben(t['cai'])==0 and ling(t['cai']) in ('休','囚','死') \
                    and ben(t['yin'])<=2 and stem(t['guan'])==0:
                P(t['yin'],'BINGYAO','印绶格印当令透干、财虚透无根失令坏印为病，用印护格(火虚木嫩用神在木)'); S(t['bi'],'比劫制财护印(药)'); A(t['cai'],'虚财坏印为病'); _zhuan_shi=True
            elif stem(t['guan'])>=2 and stem(t['shi'])>=1 and ben(t['guan'])==0 and ling(t['shi'])=='旺':"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('印绶格护印条件增加完成')
