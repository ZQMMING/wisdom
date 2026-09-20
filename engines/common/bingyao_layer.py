# -*- coding: utf-8 -*-
"""病药/作用子层 (bingyao_layer)
命局病机药神枚举 + 应期去病添病.
只输出结构事实, 不判吉凶/成败/轻重.
原典依据: SFTK-008-001 病藥說, SFTK-009-002 雕枯旺弱四病.

设计原则:
- 病 = 对日主或格局有害的结构因素 (只识别存在, 不判轻重)
- 药 = 可以去病的结构因素 (只识别存在, 不判有效性)
- 病药配对 = 原典明确的对应关系 (不自行综合)
- 矛盾共存不裁, 多病多药并列保留
- 不判吉凶/成败/用神/身强弱
"""
from typing import Any, Dict, List, Optional


# 十神中文名称映射
TENGOD_CN = {
    'BIJIAN': '比肩', 'JIECAI': '劫财',
    'SHISHANG': '食神', 'SHANGGUAN': '伤官',
    'PIANCAI': '偏财', 'ZHENGCAI': '正财',
    'QISHA': '七杀', 'ZHENGGUAN': '正官',
    'PIANYIN': '偏印', 'ZHENGYIN': '正印',
}

# 五行生克: 日主五行→所克(财)→所生(食伤)→克我(官杀)→生我(印)
KE = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}
SHENG = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
KE_WO = {'木': '金', '火': '水', '土': '木', '金': '火', '水': '土'}
SHENG_WO = {'木': '水', '火': '木', '土': '火', '金': '土', '水': '金'}


# 病类型定义 (原典依据)
BING_TYPES = {
    'CAI_DUO_SHEN_RUO': {
        'name': '财多身弱',
        'classic': 'SFTK-008-001',
        'desc': '财星当令或成党, 日主失令无根/根轻',
    },
    'SHA_ZHONG_SHEN_QING': {
        'name': '杀重身轻',
        'classic': 'SFTK-008-001',
        'desc': '官杀当令或成党, 日主无根/根轻',
    },
    'XIE_QI_TAI_ZHONG': {
        'name': '泄气太重',
        'classic': 'PZZQ 食神本属泄气',
        'desc': '食伤当令或成党, 日主泄气太过',
    },
    'SHANGGUAN_JIAN_GUAN': {
        'name': '伤官见官',
        'classic': 'YHZP 伤官见官为祸百端',
        'desc': '伤官与官杀同时透干/出现',
    },
    'XIAO_DUO_SHI': {
        'name': '枭神夺食',
        'classic': 'YHZP 枭神夺食',
        'desc': '偏印(枭)与食神同时出现, 枭克食',
    },
    'BIJIE_DUO_CAI': {
        'name': '比劫夺财',
        'classic': 'SFTK-008-001 用财见比肩为病',
        'desc': '比劫透干成党, 财星被夺',
    },
    'BIJIE_CHENG_DANG': {
        'name': '比劫成党',
        'classic': 'DTS 水多以水为病 / SFTK 比劫成党',
        'desc': '比劫数量达到3个或以上, 日主同类成势, 无论是否有财',
    },
    'YIN_DUO_MAI_ZI': {
        'name': '印多埋子(母多灭子)',
        'classic': 'DTS 母多灭子 / 土多金埋水多木浮',
        'desc': '印星成党且力量远大于日主, 印多反埋日主, 需财星疏印',
    },
}

# 药类型定义 (原典依据)
YAO_TYPES = {
    'YIN_BI_BANG_SHEN': {
        'name': '印比帮身',
        'classic': 'SFTK-009-002 日主太弱宜行身旺之地',
        'desc': '印星生身 + 比劫帮身',
    },
    'SHI_SHANG_ZHI_SHA': {
        'name': '食伤制杀',
        'classic': 'YHZP 食神制杀',
        'desc': '食神/伤官克制七杀',
    },
    'CAI_PO_YIN': {
        'name': '财破印',
        'classic': 'YHZP 财破印',
        'desc': '财星克制印星',
    },
    'GUAN_SHA_ZHI_BIJIE': {
        'name': '官杀制比劫',
        'classic': 'YHZP 官杀制比劫',
        'desc': '官杀克制比劫',
    },
    'YIN_HUA_SHA': {
        'name': '印化杀',
        'classic': 'YHZP 杀印相生',
        'desc': '印星化泄七杀',
    },
}

# 病药配对 (原典明确的对应关系)
BING_YAO_PAIRS = {
    'CAI_DUO_SHEN_RUO': ['YIN_BI_BANG_SHEN'],
    'SHA_ZHONG_SHEN_QING': ['SHI_SHANG_ZHI_SHA', 'YIN_HUA_SHA', 'YIN_BI_BANG_SHEN'],
    'XIE_QI_TAI_ZHONG': ['YIN_BI_BANG_SHEN'],
    'SHANGGUAN_JIAN_GUAN': ['YIN_HUA_SHA', 'CAI_PO_YIN'],
    'XIAO_DUO_SHI': ['CAI_PO_YIN'],
    'BIJIE_DUO_CAI': ['GUAN_SHA_ZHI_BIJIE'],
    'BIJIE_CHENG_DANG': ['GUAN_SHA_ZHI_BIJIE'],
    'YIN_DUO_MAI_ZI': ['CAI_PO_YIN'],
}


def _get_query_state(queries: List[Dict], query_id_suffix: str) -> Optional[str]:
    """从query列表中获取指定query的state (按后缀匹配)."""
    for q in queries:
        qid = q.get('query_id', '')
        if qid.endswith(query_id_suffix) or qid == query_id_suffix:
            return q.get('state')
    return None


def _has_tengod(ten_god_members: List[Dict], tengod_cn_list: List[str], position: str = None) -> bool:
    """检查十神成员中是否有指定中文十神.
    tengod_cn_list: 中文十神名称列表, 如['伤官']
    position: stem/hidden, None=全部
    """
    for m in ten_god_members:
        tg = m.get('ten_god', '')
        if tg in tengod_cn_list:
            if position is None or m.get('type') == position:
                return True
    return False


def _count_tengod(ten_god_members: List[Dict], tengod_cn_list: List[str], position: str = None) -> int:
    """统计指定十神的数量."""
    count = 0
    for m in ten_god_members:
        tg = m.get('ten_god', '')
        if tg in tengod_cn_list:
            if position is None or m.get('type') == position:
                count += 1
    return count


def identify_bing(facts: Dict[str, Any], queries: List[Dict]) -> List[Dict]:
    """识别命局中的病 (只识别存在, 不判轻重)."""
    bing_list = []
    ten_god_members = facts.get('ten_god_members', [])
    daymaster_element = facts.get('daymaster_element', '')
    month_qi_element = facts.get('month_qi_element', '')
    root_weight = facts.get('root_weight_class_facts', {})
    has_heavy_root = any(v.get('class') == 'HEAVY' for v in root_weight.values())
    has_light_root = any(v.get('class') == 'LIGHT' for v in root_weight.values())
    has_root = has_heavy_root or has_light_root

    # 1. 财多身弱 (query驱动 + 结构驱动)
    cai_duo_query = _get_query_state(queries, 'CAIDUO-SHENRUAN') == 'SUPPORTED'
    cai_dangling = (month_qi_element == KE.get(daymaster_element, ''))
    cai_count = _count_tengod(ten_god_members, ['正财', '偏财'])
    cai_cheng_dang = cai_count >= 3
    if cai_duo_query or (cai_dangling and not has_heavy_root) or (cai_cheng_dang and not has_heavy_root):
        b = BING_TYPES['CAI_DUO_SHEN_RUO']
        matched = []
        if cai_duo_query:
            matched.append('CAIDUO-SHENRUAN query=SUPPORTED')
        if cai_dangling:
            matched.append('财星当令')
        if cai_cheng_dang:
            matched.append('财星成党(%d个)' % cai_count)
        if not has_root:
            matched.append('日主无根')
        elif not has_heavy_root:
            matched.append('日主根轻')
        bing_list.append({
            'bing_id': 'CAI_DUO_SHEN_RUO',
            'name': b['name'],
            'desc': b['desc'],
            'classic': b['classic'],
            'evidence': [b['classic']],
            'matched_facts': matched,
        })

    # 2. 杀重身轻 (query驱动 + 结构驱动)
    sha_zhong_query = _get_query_state(queries, 'SHAZHONG-SHENQING') == 'SUPPORTED'
    sha_dangling = (month_qi_element == KE_WO.get(daymaster_element, ''))
    sha_count = _count_tengod(ten_god_members, ['七杀', '正官'])
    sha_cheng_dang = sha_count >= 3
    if sha_zhong_query or (sha_dangling and not has_heavy_root) or (sha_cheng_dang and not has_heavy_root):
        b = BING_TYPES['SHA_ZHONG_SHEN_QING']
        matched = []
        if sha_zhong_query:
            matched.append('SHAZHONG-SHENQING query=SUPPORTED')
        if sha_dangling:
            matched.append('官杀当令')
        if sha_cheng_dang:
            matched.append('官杀成党(%d个)' % sha_count)
        if not has_root:
            matched.append('日主无根')
        elif not has_heavy_root:
            matched.append('日主根轻')
        bing_list.append({
            'bing_id': 'SHA_ZHONG_SHEN_QING',
            'name': b['name'],
            'desc': b['desc'],
            'classic': b['classic'],
            'evidence': [b['classic']],
            'matched_facts': matched,
        })

    # 3. 泄气太重 (query驱动 + 结构驱动)
    xie_qi_query = _get_query_state(queries, 'XIEQI-TAIZHONG') == 'SUPPORTED'
    shishang_dangling = (month_qi_element == SHENG.get(daymaster_element, ''))
    shishang_count = _count_tengod(ten_god_members, ['食神', '伤官'])
    shishang_cheng_dang = shishang_count >= 3
    if xie_qi_query or (shishang_dangling and not has_heavy_root) or (shishang_cheng_dang and not has_heavy_root):
        b = BING_TYPES['XIE_QI_TAI_ZHONG']
        matched = []
        if xie_qi_query:
            matched.append('XIEQI-TAIZHONG query=SUPPORTED')
        if shishang_dangling:
            matched.append('食伤当令')
        if shishang_cheng_dang:
            matched.append('食伤成党(%d个)' % shishang_count)
        bing_list.append({
            'bing_id': 'XIE_QI_TAI_ZHONG',
            'name': b['name'],
            'desc': b['desc'],
            'classic': b['classic'],
            'evidence': [b['classic']],
            'matched_facts': matched,
        })

    # 4. 伤官见官 (结构驱动: 伤官+官杀同时出现)
    has_shangguan = _has_tengod(ten_god_members, ['伤官'])
    has_guansha = _has_tengod(ten_god_members, ['正官', '七杀'])
    if has_shangguan and has_guansha:
        b = BING_TYPES['SHANGGUAN_JIAN_GUAN']
        bing_list.append({
            'bing_id': 'SHANGGUAN_JIAN_GUAN',
            'name': b['name'],
            'desc': b['desc'],
            'classic': b['classic'],
            'evidence': [b['classic']],
            'matched_facts': ['伤官出现', '官杀出现'],
        })

    # 5. 枭神夺食 (结构驱动: 偏印+食神同时出现)
    has_pianyin = _has_tengod(ten_god_members, ['偏印'])
    has_shishen = _has_tengod(ten_god_members, ['食神'])
    if has_pianyin and has_shishen:
        b = BING_TYPES['XIAO_DUO_SHI']
        bing_list.append({
            'bing_id': 'XIAO_DUO_SHI',
            'name': b['name'],
            'desc': b['desc'],
            'classic': b['classic'],
            'evidence': [b['classic']],
            'matched_facts': ['偏印(枭)出现', '食神出现'],
        })

    # 6. 比劫夺财 (结构驱动: 比劫透干+财同时出现)
    has_bijie_tou = _has_tengod(ten_god_members, ['比肩', '劫财'], 'stem')
    has_cai = _has_tengod(ten_god_members, ['正财', '偏财'])
    if has_bijie_tou and has_cai:
        b = BING_TYPES['BIJIE_DUO_CAI']
        bing_list.append({
            'bing_id': 'BIJIE_DUO_CAI',
            'name': b['name'],
            'desc': b['desc'],
            'classic': b['classic'],
            'evidence': [b['classic']],
            'matched_facts': ['比劫透干', '财星出现'],
        })

    # 7. 比劫成党 (结构驱动: 比劫数量>=3, 无论是否有财)
    bijie_count = _count_tengod(ten_god_members, ['比肩', '劫财'])
    bijie_cheng_dang = bijie_count >= 3
    if bijie_cheng_dang:
        b = BING_TYPES['BIJIE_CHENG_DANG']
        bing_list.append({
            'bing_id': 'BIJIE_CHENG_DANG',
            'name': b['name'],
            'desc': b['desc'],
            'classic': b['classic'],
            'evidence': [b['classic']],
            'matched_facts': ['比劫成党(%d个)' % bijie_count],
        })

    # 8. 印多埋子/母多灭子 (结构驱动: 印星数量>=3 或 印力量>>日主力量)
    yin_count = _count_tengod(ten_god_members, ['正印', '偏印'])
    # 从wuxing_power获取印星和日主的力量对比
    wp = facts.get('wuxing_power', {})
    wp_data = wp.get('wuxing_power', wp) if isinstance(wp, dict) else {}
    daymaster_wx = facts.get('daymaster_element', '')
    yin_wx = SHENG_WO.get(daymaster_wx, '') if daymaster_wx else ''
    yin_power = wp_data.get(yin_wx, {}).get('total', 0) if yin_wx else 0
    dm_power = wp_data.get(daymaster_wx, {}).get('total', 0) if daymaster_wx else 0
    # 条件: 印星>=3个 或 (印力量>0 且 日主力量>0 且 印/日主>3) # PCT-MARK
    yin_duo = False
    matched = []
    if yin_count >= 3:
        yin_duo = True
        matched.append('印星成党(%d个)' % yin_count)
    if yin_power > 0 and dm_power > 0 and yin_power / dm_power > 3:  # PCT-MARK: 印/日主>3为印多埋子临界
        yin_duo = True
        matched.append('印力量%.1f/日主%.1f=%.1f倍' % (yin_power, dm_power, yin_power/dm_power))
    if yin_duo:
        b = BING_TYPES['YIN_DUO_MAI_ZI']
        bing_list.append({
            'bing_id': 'YIN_DUO_MAI_ZI',
            'name': b['name'],
            'desc': b['desc'],
            'classic': b['classic'],
            'evidence': [b['classic']],
            'matched_facts': matched,
        })

    return bing_list


def identify_yao(facts: Dict[str, Any], queries: List[Dict]) -> List[Dict]:
    """识别命局中的药 (只识别存在, 不判有效性)."""
    yao_list = []
    ten_god_members = facts.get('ten_god_members', [])

    # 1. 印比帮身 (query驱动 + 结构驱动)
    yin_party = _get_query_state(queries, 'YIN-PARTY') == 'SUPPORTED'
    bijie_party = _get_query_state(queries, 'BIJIE-PARTY') == 'SUPPORTED'
    has_yin = _has_tengod(ten_god_members, ['正印', '偏印'])
    has_bijie = _has_tengod(ten_god_members, ['比肩', '劫财'])
    if yin_party or bijie_party or has_yin or has_bijie:
        y = YAO_TYPES['YIN_BI_BANG_SHEN']
        matched = []
        if yin_party:
            matched.append('印星成党')
        if bijie_party:
            matched.append('比劫成党')
        if has_yin and not yin_party:
            matched.append('印星出现')
        if has_bijie and not bijie_party:
            matched.append('比劫出现')
        yao_list.append({
            'yao_id': 'YIN_BI_BANG_SHEN',
            'name': y['name'],
            'desc': y['desc'],
            'classic': y['classic'],
            'evidence': [y['classic']],
            'matched_facts': matched,
        })

    # 2. 食伤制杀 (结构驱动: 食伤+七杀同时出现)
    has_shishang = _has_tengod(ten_god_members, ['食神', '伤官'])
    has_qisha = _has_tengod(ten_god_members, ['七杀'])
    if has_shishang and has_qisha:
        y = YAO_TYPES['SHI_SHANG_ZHI_SHA']
        yao_list.append({
            'yao_id': 'SHI_SHANG_ZHI_SHA',
            'name': y['name'],
            'desc': y['desc'],
            'classic': y['classic'],
            'evidence': [y['classic']],
            'matched_facts': ['食伤出现', '七杀出现'],
        })

    # 3. 财破印 (结构驱动: 财+印同时出现)
    has_cai = _has_tengod(ten_god_members, ['正财', '偏财'])
    has_yin = _has_tengod(ten_god_members, ['正印', '偏印'])
    if has_cai and has_yin:
        y = YAO_TYPES['CAI_PO_YIN']
        yao_list.append({
            'yao_id': 'CAI_PO_YIN',
            'name': y['name'],
            'desc': y['desc'],
            'classic': y['classic'],
            'evidence': [y['classic']],
            'matched_facts': ['财星出现', '印星出现'],
        })

    # 4. 官杀制比劫 (结构驱动: 官杀+比劫同时出现)
    has_guansha = _has_tengod(ten_god_members, ['正官', '七杀'])
    has_bijie = _has_tengod(ten_god_members, ['比肩', '劫财'])
    if has_guansha and has_bijie:
        y = YAO_TYPES['GUAN_SHA_ZHI_BIJIE']
        yao_list.append({
            'yao_id': 'GUAN_SHA_ZHI_BIJIE',
            'name': y['name'],
            'desc': y['desc'],
            'classic': y['classic'],
            'evidence': [y['classic']],
            'matched_facts': ['官杀出现', '比劫出现'],
        })

    # 5. 印化杀 (结构驱动: 印+七杀同时出现)
    if has_yin and has_qisha:
        y = YAO_TYPES['YIN_HUA_SHA']
        yao_list.append({
            'yao_id': 'YIN_HUA_SHA',
            'name': y['name'],
            'desc': y['desc'],
            'classic': y['classic'],
            'evidence': [y['classic']],
            'matched_facts': ['印星出现', '七杀出现'],
        })

    return yao_list


def build_bingyao_layer(facts: Dict[str, Any], queries: List[Dict]) -> Dict[str, Any]:
    """构建病药/作用子层.
    输入: L0 facts + L1 queries
    输出: 病药结构 (只识别存在, 不判吉凶/成败/轻重)
    """
    bing_list = identify_bing(facts, queries)
    yao_list = identify_yao(facts, queries)

    # 病药配对 (原典明确的对应关系)
    bing_yao_pairs = []
    for bing in bing_list:
        bing_id = bing['bing_id']
        if bing_id in BING_YAO_PAIRS:
            for yao_id in BING_YAO_PAIRS[bing_id]:
                yao_exists = any(y['yao_id'] == yao_id for y in yao_list)
                bing_yao_pairs.append({
                    'bing_id': bing_id,
                    'yao_id': yao_id,
                    'yao_present': yao_exists,
                    'classic': '原典病药对应',
                    'note': '药在局中存在' if yao_exists else '药不在局中, 宜行药运',
                })

    return {
        'layer': 'BINGYAO',
        'state': 'STRUCTURE_IDENTIFIED',
        'bing_count': len(bing_list),
        'yao_count': len(yao_list),
        'bing_list': bing_list,
        'yao_list': yao_list,
        'bing_yao_pairs': bing_yao_pairs,
        'boundary_note': '只识别病药结构存在, 不判吉凶/成败/轻重/有效性; 多病多药并列保留, 矛盾共存不裁',
    }



def check_qubing_level(original_bing_list: List[Dict], dayun_stems: List[str] = None,
                        liunian_stem: str = None) -> Dict[str, Any]:
    """去病程度结构化检查 (BINGYAO-DUIYING-002).

    只做: 检查大运/流年对原局病的去除程度
    不做: 吉凶/成败/最终裁决

    原典: 去尽病根, 位入台阁; 去病不净, 仍有后患.
    """
    if dayun_stems is None:
        dayun_stems = []
    if liunian_stem:
        all_stems = dayun_stems + [liunian_stem]
    else:
        all_stems = dayun_stems

    # 五行映射
    stem_to_wx = {'甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
                  '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水'}
    # 克关系: A克B
    ke_relation = {'木': '土', '火': '金', '土': '水', '金': '木', '水': '火'}
    # 生关系: A生B
    sheng_relation = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}

    dayun_wuxing = [stem_to_wx.get(s, '') for s in all_stems if stem_to_wx.get(s)]

    results = []
    total_bing = len(original_bing_list)
    fully_removed = 0
    partially_removed = 0
    not_removed = 0
    added_bing = 0

    for bing in original_bing_list:
        bing_id = bing.get('bing_id', '')
        bing_name = bing.get('name', '')
        matched_facts = bing.get('matched_facts', [])

        # 简化: 根据病的类型判断对应的药神五行
        bing_yao_map = {
            'CAI_DUO_SHEN_RUO': ['木', '水'],  # 财多身弱, 药=印比(水木)
            'SHA_ZHONG_SHEN_QING': ['火', '木', '水'],  # 煞重身轻, 药=食伤印(火木水)
            'XIE_QI_TAI_ZHONG': ['木', '水'],  # 泄气太重, 药=印比(水木)
            'SHANGGUAN_JIAN_GUAN': ['水', '土'],  # 伤官见官, 药=印财(水土)
            'XIAO_DUO_SHI': ['土'],  # 枭神夺食, 药=财(土)
            'BIJIE_DUO_CAI': ['金'],  # 比劫夺财, 药=官杀(金)
            'BIJIE_CHENG_DANG': ['金'],  # 比劫成党, 药=官杀(金)
        }

        yao_wuxing = bing_yao_map.get(bing_id, [])

        # 检查大运/流年是否包含药神五行
        yao_in_dayun = [wx for wx in yao_wuxing if wx in dayun_wuxing]
        has_yao = len(yao_in_dayun) > 0

        # 检查是否添病(大运/流年增加病的五行)
        # 简化: 比劫成党病, 大运再逢比劫(水)则添病
        bing_wuxing_map = {
            'BIJIE_CHENG_DANG': ['水'],  # 比劫=水(癸日主)
            'CAI_DUO_SHEN_RUO': ['土'],  # 财=土(癸日主)
        }
        bing_wx = bing_wuxing_map.get(bing_id, [])
        bing_added = any(wx in dayun_wuxing for wx in bing_wx)

        if has_yao and not bing_added:
            level = 'FULLY_REMOVED'
            fully_removed += 1
            level_note = '大运/流年含药神, 去病'
        elif has_yao and bing_added:
            level = 'PARTIALLY_REMOVED'
            partially_removed += 1
            level_note = '大运/流年含药神但也添病, 去病不净'
        elif not has_yao and bing_added:
            level = 'ADDED_BING'
            added_bing += 1
            level_note = '大运/流年添病'
        else:
            level = 'NOT_REMOVED'
            not_removed += 1
            level_note = '大运/流年不含药神, 病未去'

        results.append({
            'bing_id': bing_id,
            'bing_name': bing_name,
            'yao_wuxing': yao_wuxing,
            'yao_in_dayun': yao_in_dayun,
            'bing_added': bing_added,
            'qubing_level': level,
            'level_note': level_note,
        })

    if total_bing > 0:
        if fully_removed == total_bing:
            overall = 'ALL_FULLY_REMOVED'
            overall_note = '所有病均被去除, 去尽病根'
        elif fully_removed > 0 or partially_removed > 0:
            overall = 'PARTIALLY_REMOVED'
            overall_note = '部分病被去除, 去病不净'
        elif added_bing > 0:
            overall = 'ADDED_BING'
            overall_note = '大运/流年添病'
        else:
            overall = 'NOT_REMOVED'
            overall_note = '病未被去除'
    else:
        overall = 'NO_BING'
        overall_note = '原局无病'

    return {
        'module': 'BINGYAO_QUBING_LEVEL_CHECK',
        'namespace': 'bingyao.qubing_level',
        'total_bing': total_bing,
        'fully_removed': fully_removed,
        'partially_removed': partially_removed,
        'not_removed': not_removed,
        'added_bing': added_bing,
        'overall_level': overall,
        'overall_note': overall_note,
        'check_results': results,
        'boundary_note': (
            '去病程度仅为结构化检查; 只报告大运/流年对原局病的去除程度, '
            '不做吉凶/成败/最终裁决; 去尽病根≠大贵, 去病不净≠不吉'
        ),
        'evidence_refs': ['SFTK 去尽病根位入台阁', 'SFTK 有病方为贵'],
    }
