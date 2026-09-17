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
