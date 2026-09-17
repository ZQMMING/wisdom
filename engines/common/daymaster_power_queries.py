# -*- coding: utf-8 -*-
"""PATCH-160-B V2 Query Interface
经典命题各自查询多维网络, 不汇总成总分.
每个 Query 纯结构, 原著直接授权, 不评分不权重不阈值.
"""
from typing import Any, Dict


# ---- Query Registry ----
# 每个 Query 对应一条原著命题, 纯结构条件, 不判断"太重/重叠"数量语义.

def _has_drain(dim: Dict) -> bool:
    return any(v.get('stem_present') or v.get('root_present') for v in dim.get('DRAIN', {}).values())


def _has_support(dim: Dict) -> bool:
    return any(v.get('stem_present') or v.get('root_present') for v in dim.get('SUPPORT', {}).values())


def query_can_ren_caiguan(network: Dict[str, Any]) -> Dict[str, Any]:
    """原著: 只要四柱有根, 便能受财官食神而当伤官七煞.
    纯结构: ROOT.has_root == true."""
    has_root = network['dimensions']['ROOT'].get('has_root', False)
    return {
        'query_id': 'ZP-160-QUERY-REN-CAIGUAN',
        'name': '能任财官',
        'classic': '子平真诠',
        'condition': '有根',
        'result': 'SUPPORTED' if has_root else 'NOT_SUPPORTED',
        'boundary_note': '有根=能任, 无根普通格不能任; 从化从杀等特殊路径未授权, 不推',
    }


def query_deshi_buwang(network: Dict[str, Any]) -> Dict[str, Any]:
    """原著: 得时而不旺 = 得令但泄太重.
    纯结构: in_season AND 有泄 (不判断"太重"数量)."""
    in_season = network['dimensions']['SEASONAL'].get('in_season', False)
    has_drain = _has_drain(network['dimensions'])
    match = in_season and has_drain
    return {
        'query_id': 'ZP-160-QUERY-DESHI-BUWANG',
        'name': '得时不旺',
        'classic': '子平真诠',
        'condition': '得令 AND 有泄',
        'result': 'STRUCTURE_MATCH' if match else 'NO_MATCH',
        'boundary_note': '只判断得令+有泄, 不判断"泄太重"数量; 得时不旺命题保留',
    }


def query_shishi_buruo(network: Dict[str, Any]) -> Dict[str, Any]:
    """原著: 失时而不弱 = 失令但比印重叠.
    纯结构: NOT in_season AND 有扶 (不判断"重叠"数量)."""
    in_season = network['dimensions']['SEASONAL'].get('in_season', False)
    has_support = _has_support(network['dimensions'])
    match = (not in_season) and has_support
    return {
        'query_id': 'ZP-160-QUERY-SHISHI-BURUO',
        'name': '失时不弱',
        'classic': '子平真诠',
        'condition': '失令 AND 有扶身',
        'result': 'STRUCTURE_MATCH' if match else 'NO_MATCH',
        'boundary_note': '只判断失令+有扶, 不判断"比印重叠"数量; 失时不弱命题保留',
    }


def run_queries(network: Dict[str, Any]) -> list:
    """跑全部已授权 Query, 各自独立输出, 不汇总."""
    return [
        query_can_ren_caiguan(network),
        query_deshi_buwang(network),
        query_shishi_buruo(network),
    ]
