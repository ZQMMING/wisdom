# -*- coding: utf-8 -*-
"""地支关系事实层 (D1/D2).
原典依据:
  D1 六合: 子丑/寅亥/卯戌/辰酉/巳申/午未 (子平真诠/三命通会)
  D1 暗会: 子巳/午亥/卯申/酉寅/辰巳/未申 (滴天髓秘传体系, WEAK级)
  D2 位置距离: adjacent(相邻)/span_one(隔一位)/remote(遥隔)
  D2-B 阻隔: 中间支为化神克星或冲神

本层只记录结构事实: 关系对/类型/位置距离/阻隔.
不判吉凶, 不判合力大小(只记录距离事实).
"""
from typing import Any, Dict, List

# D1 六合六组
LIUHE_PAIRS = {
    frozenset(('子', '丑')): '土',
    frozenset(('寅', '亥')): '木',
    frozenset(('卯', '戌')): '火',
    frozenset(('辰', '酉')): '金',
    frozenset(('巳', '申')): '水',
    frozenset(('午', '未')): '土',  # 午未合土/火, 取土为主
}

# D1 暗会六局 (滴天髓秘传体系, WEAK级)
# 暗会形态: 两支贴近, 中间隔一支为引(如: 子巳←丑)
ANHUI_PAIRS = {
    frozenset(('子', '巳')): '庚',  # 子巳暗会庚局
    frozenset(('午', '亥')): '甲',  # 午亥暗会甲局
    frozenset(('卯', '申')): '乙',  # 卯申暗会乙局
    frozenset(('酉', '寅')): '丙',  # 酉寅暗会丙局
    frozenset(('辰', '巳')): '丑',  # 辰巳暗会丑局
    frozenset(('未', '申')): '辰',  # 未申暗会辰局
}

# D2 位置距离 (与天干M2-A同构, 但地支定义稍不同)
POSITION_DISTANCE = {
    frozenset(('year', 'month')): 'adjacent',      # 相邻
    frozenset(('month', 'day')): 'adjacent',       # 相邻
    frozenset(('day', 'hour')): 'adjacent',        # 相邻
    frozenset(('year', 'day')): 'span_one',        # 隔一位
    frozenset(('month', 'hour')): 'span_one',      # 隔一位
    frozenset(('year', 'hour')): 'remote',          # 遥隔
}

# 地支位置顺序
POS_ORDER = {'year': 0, 'month': 1, 'day': 2, 'hour': 3}


def build_branch_relations(pillars: Dict[str, Any], facts: Dict[str, Any]) -> Dict[str, Any]:
    """构建地支关系事实层.
    
    输入:
      pillars: {year:[干,支], month:[干,支], day:[干,支], hour:[干,支]}
      facts: l0_fact_builder的输出
    
    输出:
      {
        'zhi_relations': [
          {
            'branches': ['子', '丑'],
            'type': 'liuhe',  # liuhe/anhui
            'huashen': '土',  # 化神五行(六合)
            'position': 'adjacent',  # adjacent/span_one/remote
            'positions': ['year', 'day'],
            'intervening_branches': ['寅'],  # 中间支
            'blocking_branches': [],  # 阻隔支(化神克星或冲神)
            'has_blocking': False,
          },
        ],
      }
    """
    relations = []
    
    # 提取四支
    branches = {k: pillars[k][1] for k in ('year', 'month', 'day', 'hour')}
    keys = list(branches.keys())
    
    # 遍历所有地支对
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            a, b = branches[keys[i]], branches[keys[j]]
            pair = frozenset((a, b))
            
            # D1 六合检测
            if pair in LIUHE_PAIRS:
                huashen = LIUHE_PAIRS[pair]
                # D2 位置距离
                pos_key = frozenset((keys[i], keys[j]))
                distance = POSITION_DISTANCE.get(pos_key, 'unknown')
                # D2-B 中间支检测
                pi, pj = POS_ORDER.get(keys[i], -1), POS_ORDER.get(keys[j], -1)
                intervening = []
                if pi >= 0 and pj >= 0:
                    for k in range(min(pi, pj) + 1, max(pi, pj)):
                        pos_name = {0: 'year', 1: 'month', 2: 'day', 3: 'hour'}[k]
                        intervening.append(branches[pos_name])
                # D2-B 阻隔检测: 中间支为化神克星或冲神
                # 化神克星: 克化神五行的地支
                WUXING_KE_ME = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
                KE_ME_TO_WUXING = {'金': '木', '水': '火', '木': '土', '火': '金', '土': '水'}
                ke_wx = WUXING_KE_ME.get(huashen, '')
                # 冲神: 六冲
                LIUCHONG = {'子': '午', '丑': '未', '寅': '申', '卯': '酉', '辰': '戌', '巳': '亥',
                           '午': '子', '未': '丑', '申': '寅', '酉': '卯', '戌': '辰', '亥': '巳'}
                blocking = []
                for ib in intervening:
                    # 中间支是化神克星的本气支
                    BENQI_WUXING = {'子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土', 
                                   '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金', 
                                   '戌': '土', '亥': '水'}
                    if BENQI_WUXING.get(ib) == ke_wx:
                        blocking.append(ib)
                    # 中间支是冲神
                    if LIUCHONG.get(ib) in (a, b):
                        if ib not in blocking:
                            blocking.append(ib)
                
                relations.append({
                    'branches': [a, b],
                    'type': 'liuhe',
                    'huashen': huashen,
                    'position': distance,
                    'positions': [keys[i], keys[j]],
                    'intervening_branches': intervening,
                    'blocking_branches': blocking,
                    'has_blocking': len(blocking) > 0,
                })
            
            # D1 暗会检测
            if pair in ANHUI_PAIRS:
                # 暗会成败条件: ①两支贴近(adjacent) ②不混杂(无刑冲)
                pos_key = frozenset((keys[i], keys[j]))
                distance = POSITION_DISTANCE.get(pos_key, 'unknown')
                # 暗会只在adjacent时成立
                if distance == 'adjacent':
                    relations.append({
                        'branches': [a, b],
                        'type': 'anhui',
                        'anhui_shen': ANHUI_PAIRS[pair],
                        'position': distance,
                        'positions': [keys[i], keys[j]],
                        'evidence_grade': 'WEAK',  # 滴天髓秘传体系
                        'note': '暗会: 表面虚而实增强, 喜增吉忌添凶',
                    })
    
    return {'zhi_relations': relations}
