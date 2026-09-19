# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修改提纲不照条件: 用月干判断(月干不是月令本气), 不是整个天干无木
old = """            # 提纲不照用印: 月令食伤当令但不透干, 印星透干有根为用(庚申戊寅壬子甲辰: 寅月甲木不透, 庚金透干为用, 提纲不照)
            _tigang_buzhao = BRANCH_WX.get(mz)==t['shi'] and stem(t['shi'])==0 and stem(t['yin'])>=1 and (ben(t['yin'])>=1 or ling(t['yin']) in ('旺','相'))
            if _tigang_buzhao and not _bijie_chengshi:"""
new = """            # 提纲不照用印: 月干不是月令本气(提纲不照), 印星透干有根为用(庚申戊寅壬子甲辰: 寅月本气甲木不透(月干戊), 庚金透干为用, 提纲不照)
            _month_stem = pillars['month'][0]
            _month_benqi_wx = BRANCH_WX.get(mz)
            _tigang_buzhao = _month_benqi_wx and _ganwx.get(_month_stem)!=_month_benqi_wx and stem(t['yin'])>=1 and (ben(t['yin'])>=1 or ling(t['yin']) in ('旺','相'))
            if _tigang_buzhao and not _bijie_chengshi:"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('提纲不照条件改用月干判断完成')
