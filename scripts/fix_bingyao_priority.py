# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# V4.31: B0调候路径前增加"明显病药结构识别" - 枭印夺食
old = """    # ---------- B0 通用调候(QTBJ穷通宝鉴覆盖所有月份，正格适用) ----------
    # 有明确调候候选hou时直接用第一优先(QTBJ调候是月令核心需求，优先级最高)
    # 排除: 从格(cong or cong_shun)不走通用调候，应该走从格路径
    # V4.27: B0调候路径只排除真从(CONFIRMED)和cong_shun，不排除假从(CANDIDATE)
    _cong_confirmed = bool(cong) and (cong_state or '') == 'CONFIRMED'
    if primary is None and hou and hou[0] and not (_cong_confirmed or cong_shun):
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')"""

new = """    # ---------- B-1 明显病药结构识别(优先于调候，SFTK"有病方为贵") ----------
    # V4.31: 枭印夺食: 印星成势(ben>=2或成局)且食伤当令(月令本气)被印克，病药用食伤泄秀
    if primary is None and (ben(t['yin'])>=2 or cs(t['yin'])) \
            and BRANCH_WX.get(mz)==t['shi'] and ben(t['shi'])>=1:
        P(t['shi'],'BINGYAO','枭印夺食: 印星成势克当令食伤，病在印、药在食，用食伤泄秀卫食')
        S(t['cai'],'食伤生财'); A(t['yin'],'印旺克食为病')

    # ---------- B0 通用调候(QTBJ穷通宝鉴覆盖所有月份，正格适用) ----------
    # 有明确调候候选hou时直接用第一优先(QTBJ调候是月令核心需求，优先级最高)
    # 排除: 从格(cong or cong_shun)不走通用调候，应该走从格路径
    # V4.27: B0调候路径只排除真从(CONFIRMED)和cong_shun，不排除假从(CANDIDATE)
    _cong_confirmed = bool(cong) and (cong_state or '') == 'CONFIRMED'
    if primary is None and hou and hou[0] and not (_cong_confirmed or cong_shun):
        P(hou[0],'QIHOU','通用调候候神(《穷通宝鉴》月令调候第一优先)')"""
c = c.replace(old, new)

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('yongshen_engine.py V4.31完成(枭印夺食病药结构优先于调候)')
