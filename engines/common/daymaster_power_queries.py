# -*- coding: utf-8 -*-
"""PATCH-160-C Query Interface v0
经典命题各自查询多维网络, 不汇总成总分.
分层: state(命题是否成立) vs match_type(结构是否匹配).
DESHI_BUWANG/SHISHI_BURUO 只输出结构匹配, 不声明"不旺/不弱"最终命题.
不做 Strength Resolver / STRONG/WEAK / score / weight / threshold / count / winner / aggregate.
evidence_refs 沿用现有 Evidence ID, 不在 Query 层重新造证据.
"""
from typing import Any, Dict, List


def _party_present(group: Dict) -> bool:
    """「成党」结构骨架: 该组内某十神 透干且通根(stem_present AND root_present)。
    原典「于庚辛而支酉丑」「干甲乙而支寅卯」= 天干透出 + 地支有根。
    纯布尔结构, 不计数、不判「太重/重叠」程度。"""
    return any(v.get('stem_present') and v.get('root_present') for v in group.values())


def _has_drain_party(dim: Dict) -> bool:
    return _party_present(dim.get('DRAIN', {}))


def _has_control_party(dim: Dict) -> bool:
    return _party_present(dim.get('CONTROL', {}))


def _has_support_party(dim: Dict) -> bool:
    return _party_present(dim.get('SUPPORT', {}))


def _has_cai_party(dim: Dict) -> bool:
    cai = dim.get('DRAIN', {}).get('CAI', {})
    return bool(cai.get('stem_present') and cai.get('root_present'))


def _has_shishang_party(dim: Dict) -> bool:
    sh = dim.get('DRAIN', {}).get('SHISHANG', {})
    return bool(sh.get('stem_present') and sh.get('root_present'))


def _has_guansha_party(dim: Dict) -> bool:
    g = dim.get('CONTROL', {}).get('GUANSHA', {})
    return bool(g.get('stem_present') and g.get('root_present'))


def _has_yin_party(dim: Dict) -> bool:
    y = dim.get('SUPPORT', {}).get('YIN', {})
    return bool(y.get('stem_present') and y.get('root_present'))


def _has_bijie_party(dim: Dict) -> bool:
    b = dim.get('SUPPORT', {}).get('BIJIE', {})
    return bool(b.get('stem_present') and b.get('root_present'))


def _result(query_id: str, name: str, classic: str,
            state: str, match_type: str,
            matched_nodes: List[str], matched_edges: List[str],
            evidence_refs: List[str], boundary_note: str) -> Dict:
    return {
        'query_id': query_id,
        'name': name,
        'classic': classic,
        'state': state,          # SUPPORTED / NOT_SUPPORTED / UNKNOWN
        'match_type': match_type,  # STRUCTURE_MATCH / NO_MATCH / UNKNOWN
        'matched_nodes': matched_nodes,
        'matched_edges': matched_edges,
        'evidence_refs': evidence_refs,
        'boundary_note': boundary_note,
    }


def query_can_ren_caiguan(network: Dict[str, Any]) -> Dict:
    """原著: 只要四柱有根, 便能受财官食神而当伤官七煞.
    纯结构: ROOT.has_root == true.
    此 Query 原著直接授权, 可输出 SUPPORTED/NOT_SUPPORTED."""
    has_root = network['dimensions']['ROOT'].get('has_root', False)
    return _result(
        query_id='ZP-160-QUERY-REN-CAIGUAN',
        name='能任财官',
        classic='子平真诠',
        state='SUPPORTED' if has_root else 'NOT_SUPPORTED',
        match_type='STRUCTURE_MATCH' if has_root else 'NO_MATCH',
        matched_nodes=['ROOT_BRANCH'] if has_root else [],
        matched_edges=['ROOT_RELATION'] if has_root else [],
        evidence_refs=['PZZQ-005-005'],  # 論干支: 只要四柱有根, 便能受財官食神而當傷官七煞
        boundary_note='有根=能任, 无根普通格不能任; 从化从杀等特殊路径未授权, 不推',
    )


def query_deshi_buwang(network: Dict[str, Any]) -> Dict:
    """原著: 得时而不旺 = 得令, 而克方/泄方成党(于庚辛而支酉丑; 或丙丁透巳午成党)。
    结构匹配: in_season AND (CONTROL成党 OR DRAIN成党),
    其中「成党」= 该方某十神 透干且通根(stem_present AND root_present)。
    只输出 STRUCTURE_MATCH/NO_MATCH, 不声明"不旺", 不判断"太重/成局"程度。"""
    in_season = network['dimensions']['SEASONAL'].get('in_season', False)
    ctrl_party = _has_control_party(network['dimensions'])
    drain_party = _has_drain_party(network['dimensions'])
    match = in_season and (ctrl_party or drain_party)
    nodes = ['SEASON']
    edges = ['SEASONAL_RELATION']
    if ctrl_party:
        nodes.append('CONTROL_PARTY')
        edges.append('CONTROL_RELATION')
    if drain_party:
        nodes.append('DRAIN_PARTY')
        edges.append('DRAIN_RELATION')
    return _result(
        query_id='ZP-160-QUERY-DESHI-BUWANG',
        name='得时不旺',
        classic='子平真诠',
        state='UNKNOWN',  # 结构匹配≠命题成立, 不直接输出 SUPPORTED
        match_type='STRUCTURE_MATCH' if match else 'NO_MATCH',
        matched_nodes=nodes if match else [],
        matched_edges=edges if match else [],
        evidence_refs=['PZZQ-005-005'],
        boundary_note='只匹配得令+克/泄方成党(透干且通根); 不声明"太重/不旺", 不判成局强度; 命题成立待授权',
    )


def query_shishi_buruo(network: Dict[str, Any]) -> Dict:
    """原著: 失时而不弱 = 失令, 而比印通根成党(干甲乙而支寅卯)。
    结构匹配: NOT in_season AND SUPPORT成党(比劫/印 透干且通根)。
    只输出 STRUCTURE_MATCH/NO_MATCH, 不声明"不弱", 不判断"重叠"程度。"""
    in_season = network['dimensions']['SEASONAL'].get('in_season', False)
    support_party = _has_support_party(network['dimensions'])
    match = (not in_season) and support_party
    return _result(
        query_id='ZP-160-QUERY-SHISHI-BURUO',
        name='失时不弱',
        classic='子平真诠',
        state='UNKNOWN',  # 结构匹配≠命题成立, 不直接输出 SUPPORTED
        match_type='STRUCTURE_MATCH' if match else 'NO_MATCH',
        matched_nodes=['SEASON', 'SUPPORT_PARTY'] if match else [],
        matched_edges=['SEASONAL_RELATION', 'SUPPORT_RELATION'] if match else [],
        evidence_refs=['PZZQ-005-005'],
        boundary_note='只匹配失令+扶身成党(透干且通根); 不声明"重叠/不弱"; 命题成立待授权',
    )


def run_queries(network: Dict[str, Any]) -> List[Dict]:
    """跑全部已授权 Query, 各自独立输出, 不汇总."""
    return [
        query_can_ren_caiguan(network),
        query_deshi_buwang(network),
        query_shishi_buruo(network),
        query_cai_duo_shen_ruan(network),
        query_sha_zhong_shen_qing(network),
        query_xie_qi_tai_zhong(network),
        query_heavy_root(network),
        query_light_root(network),
        query_tengluo_xijia(network),
        query_juechu_fengsheng(network),
        query_yin_party(network),
        query_bijie_party(network),
        query_root_struck(network),
        query_root_gan_priority(network),
        query_wangzhe_chong_shuai(network),
        query_he_huashen_deshi(network),
    ]


def query_cai_duo_shen_ruan(network: Dict[str, Any]) -> Dict:
    """原著结构(渊海子平): 财多身弱 = 财成党(透干且通根) 而日主无根.
    结构匹配: CAI成党 AND NOT has_root.
    只输出结构匹配; 不声明"财多/身弱"程度, 命题恒 UNKNOWN."""
    no_root = not network['dimensions']['ROOT'].get('has_root', False)
    cai_party = _has_cai_party(network['dimensions'])
    match = no_root and cai_party
    return _result(
        query_id='ZP-160-QUERY-CAIDUO-SHENRUAN',
        name='财党无根结构',
        classic='渊海子平',
        state='UNKNOWN',
        match_type='STRUCTURE_MATCH' if match else 'NO_MATCH',
        matched_nodes=['CAI_PARTY', 'NO_ROOT'] if match else [],
        matched_edges=['CAI_RELATION', 'ROOT_ABSENT'] if match else [],
        evidence_refs=['YHZP-078-024'],  # 继善篇: 财多生官须要身健, 财多盗气本身自柔
        boundary_note='只匹配财成党+日主无根; 不判财多程度, 不下旺衰结论; 命题成立待授权',
    )


def query_sha_zhong_shen_qing(network: Dict[str, Any]) -> Dict:
    """原著结构(渊海子平): 煞重身轻 = 官杀成党(透干且通根) 而日主无根.
    结构匹配: GUANSHA成党 AND NOT has_root.
    只输出结构匹配; 不声明"煞重/身轻"程度, 命题恒 UNKNOWN."""
    no_root = not network['dimensions']['ROOT'].get('has_root', False)
    sha_party = _has_guansha_party(network['dimensions'])
    match = no_root and sha_party
    return _result(
        query_id='ZP-160-QUERY-SHAZHONG-SHENQING',
        name='杀党无根结构',
        classic='渊海子平',
        state='UNKNOWN',
        match_type='STRUCTURE_MATCH' if match else 'NO_MATCH',
        matched_nodes=['GUANSHA_PARTY', 'NO_ROOT'] if match else [],
        matched_edges=['CONTROL_RELATION', 'ROOT_ABSENT'] if match else [],
        evidence_refs=['YHZP-079-031'],  # 正气官星(继善篇注): 杀重身轻, 移身有损
        boundary_note='只匹配官杀成党+日主无根; 不判煞重程度, 不下旺衰结论; 命题成立待授权',
    )


def query_heavy_root(network: Dict[str, Any]) -> Dict:
    """原著: 长生禄刃, 根之重者.
    纯结构: ROOT.root_weight_class == HEAVY (含长生/禄/刃重根).
    此为事实判断, 可输出 SUPPORTED/NOT_SUPPORTED; 但不升"身强". """
    rc = network['dimensions']['ROOT'].get('root_weight_class')
    return _result(
        query_id='ZP-160-QUERY-HEAVY-ROOT',
        name='重根结构',
        classic='子平真诠',
        state='SUPPORTED' if rc == 'HEAVY' else 'NOT_SUPPORTED',
        match_type='STRUCTURE_MATCH' if rc == 'HEAVY' else 'NO_MATCH',
        matched_nodes=['ROOT_BRANCH'] if rc == 'HEAVY' else [],
        matched_edges=['ROOT_RELATION'] if rc == 'HEAVY' else [],
        evidence_refs=['PZZQ-005-005'],  # 长生禄刃, 根之重者也
        boundary_note='只报有无长生禄刃重根; 不下旺衰结论, 不计根数/不叠加轻根',
    )


def query_light_root(network: Dict[str, Any]) -> Dict:
    """原著: 墓库余气, 根之轻者.
    纯结构: ROOT.root_weight_class == LIGHT (仅墓库/余气轻根, 无重根).
    此为事实判断, 可输出 SUPPORTED/NOT_SUPPORTED; 不下旺衰结论."""
    rc = network['dimensions']['ROOT'].get('root_weight_class')
    return _result(
        query_id='ZP-160-QUERY-LIGHT-ROOT',
        name='轻根结构',
        classic='子平真诠',
        state='SUPPORTED' if rc == 'LIGHT' else 'NOT_SUPPORTED',
        match_type='STRUCTURE_MATCH' if rc == 'LIGHT' else 'NO_MATCH',
        matched_nodes=['ROOT_BRANCH'] if rc == 'LIGHT' else [],
        matched_edges=['ROOT_RELATION'] if rc == 'LIGHT' else [],
        evidence_refs=['PZZQ-005-005'],  # 墓库余气, 根之轻者也
        boundary_note='只报有无墓库余气轻根; 不下旺衰结论, 不计根数/不与重根叠加',
    )


def query_tengluo_xijia(network: Dict[str, Any]) -> Dict:
    """原著(滴天髓乙木章): 藤蘿系甲, 可春可秋.
    纯结构: 日干=乙 AND 天干见比肩甲透(BIANJIAN.stem_present).
    结构匹配 STRUCTURE_MATCH, 命题恒 UNKNOWN; 不升旺衰."""
    dm = network['nodes'][0]['attrs'].get('stem', '')
    jc = network['dimensions']['SUPPORT'].get('JIECAI', {}).get('stem_present', False)
    m = (dm == '乙') and bool(jc)
    return _result(
        query_id='ZP-160-QUERY-TENGLUO-XIJIA',
        name='藤萝系甲结构',
        classic='滴天髓',
        state='SUPPORTED' if m else 'UNKNOWN',
        match_type='STRUCTURE_MATCH' if m else 'NO_MATCH',
        matched_nodes=['DAYMASTER', 'JIECAI'] if m else [],
        matched_edges=['SUPPORT_RELATION'] if m else [],
        evidence_refs=['DTS-008-007'],  # 藤蘿系甲, 可春可秋
        boundary_note='只报乙日见甲透这一结构; 不升旺衰结论, 不解释"可春可秋"',
    )


def query_juechu_fengsheng(network: Dict[str, Any]) -> Dict:
    """原著(神峰通考): 水虽至巳为极弱, 然已有庚金为水根.
    纯结构: 月令绝地(JUECHU.month_jue) AND 月令藏干见印(month_hidden_yin).
    结构匹配 STRUCTURE_MATCH, 命题恒 UNKNOWN; 不升旺衰."""
    jc = network['dimensions'].get('JUECHU', {})
    m = bool(jc.get('month_jue')) and bool(jc.get('month_hidden_yin'))
    return _result(
        query_id='ZP-160-QUERY-JUECHU-FENGSHENG',
        name='绝处逢生结构',
        classic='神峰通考',
        state='SUPPORTED' if m else 'UNKNOWN',
        match_type='STRUCTURE_MATCH' if m else 'NO_MATCH',
        matched_nodes=['SEASON'] if m else [],
        matched_edges=['SUPPORT_RELATION'] if m else [],
        evidence_refs=['SFTK-009-002'],  # 水虽至巳为极弱, 然已有庚金为水根
        boundary_note='只报月令绝地+月令藏干见印这一结构; 不下旺衰结论',
    )


def query_xie_qi_tai_zhong(network: Dict[str, Any]) -> Dict:
    """原著结构(子平真诠): 泄气太重 = 食伤成党(透干且通根).
    结构匹配: SHISHANG成党.
    只输出结构匹配; 不声明"泄太重"程度, 命题恒 UNKNOWN."""
    xie_party = _has_shishang_party(network['dimensions'])
    return _result(
        query_id='ZP-160-QUERY-XIEQI-TAIZHONG',
        name='泄气太重结构',
        classic='子平真诠',
        state='UNKNOWN',
        match_type='STRUCTURE_MATCH' if xie_party else 'NO_MATCH',
        matched_nodes=['SHISHANG_PARTY'] if xie_party else [],
        matched_edges=['DRAIN_RELATION'] if xie_party else [],
        evidence_refs=['PZZQ-007-025'],  # 子平真诠: 食神本属泄气, 以其能生正财
        boundary_note='只匹配食伤成党(透干且通根); 不判"泄太重"程度; 命题成立待授权',
    )


def query_root_struck(network: Dict[str, Any]) -> Dict:
    """原著: 日主根支参与冲/刑/自刑/害/破(对立类地支关系).
    纯结构: ROOT_RELATION.struck_root_pillars 非空.
    只报根支受对立关系这一结构; 不判根拔/根失效效果, 命题恒 UNKNOWN.
    注意: struck组聚合冲刑害破五类, 无单条原文全覆盖, refs留空不伪造.
    原典校准(DTS原文): 任氏明批"墓库逢冲必发"为后人之谬——库乃藏根之地,
    日主全赖辰戌丑未身库通根而逢冲, 反拔尽微根; 唯以土为喜神冲土方有益.
    故本 query 只报"根支受对立"事实, 不预设"冲开发福"."""
    rr = network['dimensions'].get('ROOT_RELATION', {})
    struck = rr.get('struck_root_pillars', []) or []
    m = bool(struck)
    return _result(
        query_id='ZP-160-QUERY-ROOT-STRUCK',
        name='根支受对立关系',
        classic='滴天髓',
        state='UNKNOWN',
        match_type='STRUCTURE_MATCH' if m else 'NO_MATCH',
        matched_nodes=['ROOT_BRANCH'] if m else [],
        matched_edges=['COMBINATION'] if m else [],
        evidence_refs=[],  # 冲刑害破混合组, 无单条原文全覆盖, 不伪造
        boundary_note='只报日主根支参与冲刑害破这一结构; 不判根是否被拔/失效. 原典批"墓库逢冲必发"为谬: 赖库根逢冲反拔微根, 不预设冲开发福',
    )


def query_he_huashen_deshi(network: Dict[str, Any]) -> Dict:
    """原著(渊海子平): 月令生旺养库临官之地方化, 逢龙即化.
    结构: 天干有合 且 化神五行==月令本气. 只记化神得令结构, 不判真化."""
    th = network['dimensions'].get('TIAN_HE', {})
    pairs = th.get('he_pairs', []) or []
    on_month = th.get('huashen_on_month_qi', False)
    has_chen = th.get('has_long_chen', False)
    if pairs and on_month:
        state, mt, nodes = 'SUPPORTED', 'STRUCTURE_MATCH', ['TIAN_HE']
    else:
        state, mt, nodes = 'UNKNOWN', 'NO_MATCH', []
    return _result(
        query_id='ZP-160-QUERY-HE-HUASHEN-DESHI',
        name='合化神得令结构',
        classic='渊海子平',
        state=state,
        match_type=mt,
        matched_nodes=nodes,
        matched_edges=['TIAN_HE_RELATION'] if pairs else [],
        evidence_refs=['YHZP-121-003'],  # 月令生旺养库临官之地方化
        boundary_note='仅记天干合+化神得月令结构; 不判真化假化, 不判化气格, 太过不及未量化',
    )


def query_wangzhe_chong_shuai(network: Dict[str, Any]) -> Dict:
    """原著(滴天髓): 旺者冲衰衰者拔, 衰神冲旺旺神发.
    冲两支按四阶(得月令+同党)比: 阶高者旺, 阶低者拔, 同阶两停.
    有序枚举比较, 无数值, 不输出日主综合强弱."""
    bt = network['dimensions'].get('BRANCH_TIER', {})
    clashes = bt.get('clash_results', []) or []
    decided = [c for c in clashes if c['tier_a'] != c['tier_b']]
    tie = [c for c in clashes if c['tier_a'] == c['tier_b']]
    if decided:
        state, mt, nodes = 'SUPPORTED', 'STRUCTURE_MATCH', ['ROOT_BRANCH']
    elif tie:
        state, mt, nodes = 'UNKNOWN', 'NO_MATCH', []
    else:
        state, mt, nodes = 'UNKNOWN', 'NO_MATCH', []
    return _result(
        query_id='ZP-160-QUERY-WANGCHONG-SHUAI',
        name='旺者冲衰结构',
        classic='滴天髓',
        state=state,
        match_type=mt,
        matched_nodes=nodes,
        matched_edges=['COMBINATION'] if decided else [],
        evidence_refs=['DTS-009-009'],  # 旺者冲衰衰者拔
        boundary_note='冲两支按四阶比谁拔谁发, 同阶两停; 不编七级旺衰, 不输出日主综合强弱',
    )


def query_root_gan_priority(network: Dict[str, Any]) -> Dict:
    """原著: 通根如室家可住, 比肩如朋友相扶; 干多不如根重.
    这是层级优先级, 不是数量比较:
      有根(HEAVY/LIGHT) -> 室家可住, 根层成立
      无根但比劫干透    -> 朋友相扶, 无根借住
      无根无干          -> 两无
    纯布尔, 不数干个数, 不评分."""
    has_root = network['dimensions']['ROOT'].get('has_root', False)
    bijie_gan = network['dimensions']['SUPPORT'].get('BIJIE', {}).get('stem_present', False)
    if has_root:
        sub, nodes, edges, mt = '室家可住(根层成立)', ['ROOT_BRANCH'], ['ROOT_RELATION'], 'STRUCTURE_MATCH'
    elif bijie_gan:
        sub, nodes, edges, mt = '朋友相扶(无根有干)', ['ROOT_ABSENT', 'BIJIE'], ['SUPPORT_RELATION'], 'NO_MATCH'
    else:
        sub, nodes, edges, mt = '两无', [], [], 'NO_MATCH'
    return _result(
        query_id='ZP-160-QUERY-ROOT-GAN-PRIORITY',
        name='根干层级',
        classic='子平真诠',
        state='SUPPORTED' if has_root else 'UNKNOWN',
        match_type=mt,
        matched_nodes=nodes,
        matched_edges=edges,
        evidence_refs=['PZZQ-005-005'],  # 通根如室家可住, 朋友相扶; 干多不如根重
        boundary_note='根优先于干这一层级; 不数比肩个数, 不评分, 不下旺衰结论',
    )


def query_yin_party(network: Dict[str, Any]) -> Dict:
    """原著: 党众=比印; 印星成党(印透干且通根).
    纯结构: SUPPORT.YIN stem_present AND root_present.
    命题恒 UNKNOWN; 成党≠身强, 不判喜忌."""
    p = _has_yin_party(network['dimensions'])
    return _result(
        query_id='ZP-160-QUERY-YIN-PARTY',
        name='印星成党结构',
        classic='子平真诠',
        state='UNKNOWN',
        match_type='STRUCTURE_MATCH' if p else 'NO_MATCH',
        matched_nodes=['YIN_PARTY'] if p else [],
        matched_edges=['SUPPORT_RELATION'] if p else [],
        evidence_refs=['PZZQ-005-005'],  # 党众为强(比印通根扶助), 同章
        boundary_note='只匹配印星透干且通根; 不判成党程度, 不下旺衰/喜忌结论',
    )


def query_bijie_party(network: Dict[str, Any]) -> Dict:
    """原著: 党众=比劫; 比劫成党(比劫透干且通根).
    纯结构: SUPPORT.BIJIE stem_present AND root_present.
    命题恒 UNKNOWN; 成党≠身强, 不判喜忌."""
    p = _has_bijie_party(network['dimensions'])
    return _result(
        query_id='ZP-160-QUERY-BIJIE-PARTY',
        name='比劫成党结构',
        classic='子平真诠',
        state='UNKNOWN',
        match_type='STRUCTURE_MATCH' if p else 'NO_MATCH',
        matched_nodes=['BIJIE_PARTY'] if p else [],
        matched_edges=['SUPPORT_RELATION'] if p else [],
        evidence_refs=['PZZQ-005-005'],  # 党众为强(比劫), 同章
        boundary_note='只匹配比劫透干且通根; 不判成党程度, 不下旺衰/喜忌结论',
    )
