# -*- coding: utf-8 -*-
"""PATCH-160-C Query Interface v0
经典命题各自查询多维网络, 不汇总成总分.
分层: state(命题是否成立) vs match_type(结构是否匹配).
DESHI_BUWANG/SHISHI_BURUO 只输出结构匹配, 不声明"不旺/不弱"最终命题.
不做 Strength Resolver / STRONG/WEAK / score / weight / threshold / count / winner / aggregate.
evidence_refs 沿用现有 Evidence ID, 不在 Query 层重新造证据.
"""
from typing import Any, Dict, List


def _has_drain(dim: Dict) -> bool:
    return any(v.get('stem_present') or v.get('root_present') for v in dim.get('DRAIN', {}).values())


def _has_support(dim: Dict) -> bool:
    return any(v.get('stem_present') or v.get('root_present') for v in dim.get('SUPPORT', {}).values())


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
        evidence_refs=[],  # TODO: 待绑 PZZQ 有根任财官 evidence_id
        boundary_note='有根=能任, 无根普通格不能任; 从化从杀等特殊路径未授权, 不推',
    )


def query_deshi_buwang(network: Dict[str, Any]) -> Dict:
    """原著: 得时而不旺 = 得令但泄太重.
    结构匹配: in_season AND has_drain.
    只输出 STRUCTURE_MATCH/NO_MATCH, 不声明"不旺", 不判断"泄太重"数量."""
    in_season = network['dimensions']['SEASONAL'].get('in_season', False)
    has_drain = _has_drain(network['dimensions'])
    match = in_season and has_drain
    return _result(
        query_id='ZP-160-QUERY-DESHI-BUWANG',
        name='得时不旺',
        classic='子平真诠',
        state='UNKNOWN',  # 结构匹配≠命题成立, 不直接输出 SUPPORTED
        match_type='STRUCTURE_MATCH' if match else 'NO_MATCH',
        matched_nodes=['SEASON', 'DRAIN_GROUP'] if match else [],
        matched_edges=['SEASONAL_RELATION', 'DRAIN_RELATION'] if match else [],
        evidence_refs=[],
        boundary_note='只匹配得令+有泄; 不声明"泄太重", 不直接输出"不旺"; 命题成立待授权',
    )


def query_shishi_buruo(network: Dict[str, Any]) -> Dict:
    """原著: 失时而不弱 = 失令但比印重叠.
    结构匹配: NOT in_season AND has_support.
    只输出 STRUCTURE_MATCH/NO_MATCH, 不声明"不弱", 不判断"比印重叠"数量."""
    in_season = network['dimensions']['SEASONAL'].get('in_season', False)
    has_support = _has_support(network['dimensions'])
    match = (not in_season) and has_support
    return _result(
        query_id='ZP-160-QUERY-SHISHI-BURUO',
        name='失时不弱',
        classic='子平真诠',
        state='UNKNOWN',  # 结构匹配≠命题成立, 不直接输出 SUPPORTED
        match_type='STRUCTURE_MATCH' if match else 'NO_MATCH',
        matched_nodes=['SEASON', 'SUPPORT_GROUP'] if match else [],
        matched_edges=['SEASONAL_RELATION', 'SUPPORT_RELATION'] if match else [],
        evidence_refs=[],
        boundary_note='只匹配失令+有扶; 不声明"比印重叠", 不直接输出"不弱"; 命题成立待授权',
    )


def run_queries(network: Dict[str, Any]) -> List[Dict]:
    """跑全部已授权 Query, 各自独立输出, 不汇总."""
    return [
        query_can_ren_caiguan(network),
        query_deshi_buwang(network),
        query_shishi_buruo(network),
    ]
