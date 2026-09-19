# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 在身旺扶抑路径增加提纲不照用印条件(庚申戊寅壬子甲辰: 寅月食伤当令不透, 透庚印为用, 提纲不照)
old = """            # 比劫成势+食伤透干优先食伤泄秀(辛未辛丑戊辰壬戌: 土比劫极旺四库全+辛金双透, 用金泄秀吐精英)
            _bijie_chengshi = (cs(t['bi']) or ben(t['bi'])>=3 or (ben(t['bi'])>=2 and stem(t['bi'])>=1))
            if _bijie_chengshi and stem(t['shi'])>=1 and not _xiao_duo_shi and stem(t['guan'])==0:
                P(t['shi'],'ZHUANWANG','比劫成势食伤透干，顺泄吐秀为用(辛金吐秀泄其精英)'); S(t['cai'],'食伤生财')
            # 印绶格护印:"""
new = """            # 比劫成势+食伤透干优先食伤泄秀(辛未辛丑戊辰壬戌: 土比劫极旺四库全+辛金双透, 用金泄秀吐精英)
            _bijie_chengshi = (cs(t['bi']) or ben(t['bi'])>=3 or (ben(t['bi'])>=2 and stem(t['bi'])>=1))
            if _bijie_chengshi and stem(t['shi'])>=1 and not _xiao_duo_shi and stem(t['guan'])==0:
                P(t['shi'],'ZHUANWANG','比劫成势食伤透干，顺泄吐秀为用(辛金吐秀泄其精英)'); S(t['cai'],'食伤生财')
            # 提纲不照用印: 月令食伤当令但不透干, 印星透干有根为用(庚申戊寅壬子甲辰: 寅月甲木不透, 庚金透干为用, 提纲不照)
            _tigang_buzhao = BRANCH_WX.get(mz)==t['shi'] and stem(t['shi'])==0 and stem(t['yin'])>=1 and (ben(t['yin'])>=1 or ling(t['yin']) in ('旺','相'))
            if _tigang_buzhao and not _bijie_chengshi:
                P(t['yin'],'BINGYAO','提纲不照：月令食伤当令不透，印星透干有根为用(透金为用神)'); S(t['bi'],'比劫帮身'); A(t['shi'],'提纲不照之食伤待运')
            # 印绶格护印:"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('提纲不照用印条件增加完成')
