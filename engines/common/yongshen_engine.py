# -*- coding: utf-8 -*-
"""160-D 用神多路径结构引擎(非单一裁决器)。
沿多维网络, 按原典并行给出取用路径候选(五行+路径+依据), 不输出唯一 final/selected, 不评分排序。
路径:
  CONG_SHUN  : 从格顺所从(从财/从官杀/从儿/从势)
  ZHUANWANG  : 专旺顺性(印/比)与泄秀(我生)
  HUA_QI     : 化气格扶化神/生化神
  FUYI      : 正格扶抑(旺类克泄耗=食伤财官杀; 衰类生扶=印比); 中和不强推
  QIHOU     : 《穷通宝鉴》调候(解冻/润燥), 寒暖为急
  (BINGYAO/TONGGUAN 病药通关第二版补)
候选中性并列, judgment_status=YONGSHEN_CANDIDATE_ONLY。
"""
from typing import Any, Dict, List
WUXING='木火土金水'
SHENG={'木':'火','火':'土','土':'金','金':'水','水':'木'}
KE={'木':'土','土':'水','水':'火','火':'金','金':'木'}
WX={'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
WANG_TIER=('旺极','太旺','旺'); SHUAI_TIER=('衰极','太衰','衰')

def _ten_wx(dm_wx):
    return {
        'bi': dm_wx,                                   # 比劫(同我)
        'yin': [x for x in WUXING if SHENG[x]==dm_wx][0],   # 印(生我)
        'shi': SHENG[dm_wx],                           # 食伤(我生)
        'cai': KE[dm_wx],                              # 财(我克)
        'guan': [x for x in WUXING if KE[x]==dm_wx][0],     # 官杀(克我)
    }

def build_yongshen_engine(pillars, facts, wuxing_power, spectrum, special, climate):
    dm = facts['day_stem']; dmw = WX[dm]
    t = _ten_wx(dmw)
    cands: List[Dict[str,str]] = []
    def add(w, path, note):
        if w and w in WUXING and not any(c['wuxing']==w and c['path']==path for c in cands):
            cands.append({'wuxing':w,'path':path,'note':note})
    cong = (special.get('cong_type') or '').strip()
    cong_state = (special.get('cong_state') or '').strip()
    zw = (special.get('zhuanwang') or '').strip()
    hua = (special.get('hua_qi') or '').strip()
    lq = special.get('liangqi') or None
    spec_name = cong or zw or hua or (lq.get('name') if lq else '')
    tier = spectrum.get('spectrum') if isinstance(spectrum, dict) else spectrum
    wpd = (wuxing_power or {}).get('wuxing_power', {})
    def cs(wx):  # 某五行成势/重: 当令旺相 或 本气根>=2 或 透干>=2 或 成局
        d = wpd.get(wx) or {}
        return d.get('ling_state') in ('旺','相') or d.get('ben_n',0)>=2 or d.get('stem_n',0)>=2 or d.get('ju_n',0)>=1
    zheng = (not zw) and (not lq) and (not cong or 'CANDIDATE' in cong_state)

    # 1) 化气: 化神 + 生化神
    if hua:
        for wx in WUXING:
            if ('化'+wx) in hua or wx in hua:
                add(wx,'HUA_QI','化神为用，顺化神之气')
                add(SHENG[wx],'HUA_QI','生扶化神')
                break
    # 1b) 两气成象: 相生成象顺流通(日主生他者顺食伤秀神; 他生日主顺印比)
    if lq:
        _xiu=lq.get('xiu')
        if _xiu:
            add(_xiu,'LIANGQI','两气成象相生，顺其流通(食伤秀神)')
        add(t['bi'],'LIANGQI','成象顺本方比劫')
        if not _xiu:
            add(t['yin'],'LIANGQI','他生日主成象，顺印')
    # 2) 从格顺所从(仅 CONFIRMED 直接顺; CANDIDATE 保留顺性候选但标注待辨, 正格路径亦并列)
    if cong:
        conf = 'CONFIRMED' in cong_state
        tag = 'CONG_SHUN' if conf else 'CONG_SHUN_CANDIDATE'
        if '从财' in cong:
            add(t['cai'],tag,'从财顺财，以财为用'); add(t['shi'],tag,'食伤吐秀生财')
        elif '从官' in cong or '从杀' in cong or '从煞' in cong:
            add(t['guan'],tag,'从官杀顺官杀'); add(t['cai'],tag,'财生官杀')
        elif '从儿' in cong:
            add(t['shi'],tag,'从儿顺食伤，吾儿又见儿'); add(t['cai'],tag,'食伤生财')
        elif '从势' in cong or '从强' in cong:
            add(t['cai'],tag,'从势顺财'); add(t['guan'],tag,'从势顺官杀'); add(t['shi'],tag,'从势顺食伤')
    # 3) 专旺顺性 + 泄秀
    if zw:
        add(t['shi'],'ZHUANWANG','专旺泄秀(我生)，导其气势')
        add(t['yin'],'ZHUANWANG','专旺顺性喜印')
        add(t['bi'],'ZHUANWANG','专旺顺性喜比劫')
        # 颠倒之理: 专旺而官杀叠透(>=2)为旺中伏克, 太旺者可克以修旺, 与顺泄并列待辨(候选非裁决)
        if (wpd.get(t['guan']) or {}).get('stem_n',0) >= 2:
            add(t['guan'],'WANG_KE','专旺而官杀叠透，太旺可克以修旺(《滴天髓》颠倒之理)，须得载有力，与顺泄并列待辨')
    # 4) 正格扶抑(非明确从/专旺时; CANDIDATE 从格亦给正格路径备辨)
    if zheng:
        if tier in WANG_TIER:
            add(t['shi'],'FUYI','身旺顺泄，食伤吐秀')
            add(t['cai'],'FUYI','身旺用财，我克为财')
            add(t['guan'],'FUYI','身旺用官杀，克身成权')
        elif tier in SHUAI_TIER:
            add(t['yin'],'FUYI','身弱用印，生我扶身')
            add(t['bi'],'FUYI','身弱用比劫，帮身任财官')
        # 中和: 不强推, 留待格局/调候/病药
    # 4b) 病药制化 + 通关(正格; 多路径并列, 身弱偏印化、身旺偏食制, 不唯一裁决)
    if zheng:
        if cs(t['guan']):  # 官杀重: 印化 / 食伤制
            add(t['yin'],'BINGYAO','杀重印化，杀生印、印生身(身弱优先)')
            add(t['shi'],'BINGYAO','杀重食伤制杀，我生克官杀(身旺可任)')
        if cs(t['yin']):   # 印重: 财破印
            add(t['cai'],'BINGYAO','印重财破印，去壅塞')
        if cs(t['shi']) and tier in SHUAI_TIER:  # 食伤泄太过: 印制
            add(t['yin'],'BINGYAO','食伤泄气太过，印制食伤扶身')
        if cs(t['cai']) and tier in SHUAI_TIER:  # 财多身弱: 比劫分财 / 印
            add(t['bi'],'BINGYAO','财重比劫分财')
            add(t['yin'],'BINGYAO','财多身弱用印')
        # 通关(两神皆成势相战, 以中间五行流通)
        if cs(t['guan']) and cs(t['bi']):
            add(t['yin'],'TONGGUAN','官杀与比劫相战，印通关(官生印生身)')
        if cs(t['cai']) and cs(t['yin']):
            add(t['guan'],'TONGGUAN','财印相战，官杀通关(财生官生印)')
        if cs(t['shi']) and cs(t['guan']):
            add(t['cai'],'TONGGUAN','食伤与官杀相战，财通关(食伤生财生官)')
    # 5) 调候(QTBJ 查表, 原文次序非评分)
    for cc in (climate.get('climate_candidates') or []):
        st=cc.get('stem')
        if st in WX:
            add(WX[st],'QIHOU',f"《穷通宝鉴》调候干{st}，寒暖燥湿为急")
    return {
        'module':'YONGSHEN_ENGINE_V1',
        'namespace':'daymaster_yongshen_engine',
        'day_master':dm,'daymaster_wuxing':dmw,
        'spectrum_tier':tier,'special':spec_name or '正格',
        'yongshen_candidates':cands,
        'candidate_wuxing':sorted({c['wuxing'] for c in cands}),
        'judgment_status':'YONGSHEN_CANDIDATE_ONLY',
        'boundary_note':'多路径取用候选并列(从性/专旺/化气/扶抑/调候), 非唯一用神裁决, 无score/winner; '
                       '病药通关制化待补; 假从/专旺不纯须先辨格局; 吉凶前端拦截, 本层只输出真实取用结构; 不接production_entry',
    }
