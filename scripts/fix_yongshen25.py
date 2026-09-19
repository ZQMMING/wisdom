# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 在身旺扶抑路径最前面增加比劫成势+食伤透干优先食伤泄秀(辛未辛丑戊辰壬戌: 土比劫极旺+辛金双透, 用金泄秀)
old = """        if primary is None and tier in WANG_TIER:
            _zhuan_shi=False
            _gy=dm in '甲丙戊庚壬'; _yg='甲丙戊庚壬' if _gy else '乙丁己辛癸'
            _py_tou=any(_ganwx.get(g)==t['yin'] for g in other_gan if g in _yg)  # 偏印(生我同阴阳)透干
            _xiao_duo_shi=_py_tou and stem(t['shi'])>=1 and ben(t['shi'])==0  # 偏印透、食伤透无本气根=枭神夺食, 食伤被夺不可用
            # 印绶格护印:"""
new = """        if primary is None and tier in WANG_TIER:
            _zhuan_shi=False
            _gy=dm in '甲丙戊庚壬'; _yg='甲丙戊庚壬' if _gy else '乙丁己辛癸'
            _py_tou=any(_ganwx.get(g)==t['yin'] for g in other_gan if g in _yg)  # 偏印(生我同阴阳)透干
            _xiao_duo_shi=_py_tou and stem(t['shi'])>=1 and ben(t['shi'])==0  # 偏印透、食伤透无本气根=枭神夺食, 食伤被夺不可用
            # 比劫成势+食伤透干优先食伤泄秀(辛未辛丑戊辰壬戌: 土比劫极旺四库全+辛金双透, 用金泄秀吐精英)
            _bijie_chengshi = (cs(t['bi']) or ben(t['bi'])>=3 or (ben(t['bi'])>=2 and stem(t['bi'])>=1))
            if _bijie_chengshi and stem(t['shi'])>=1 and not _xiao_duo_shi and stem(t['guan'])==0:
                P(t['shi'],'ZHUANWANG','比劫成势食伤透干，顺泄吐秀为用(辛金吐秀泄其精英)'); S(t['cai'],'食伤生财')
            # 印绶格护印:"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('比劫成势食伤泄秀修复完成')
