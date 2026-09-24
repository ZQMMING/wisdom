# -*- coding: utf-8 -*-
"""wuxing_power兼容层——P0浮点体系已废, 本模块仅保留接口签名兼容,
内部实现指向transit_power纯规则计数. 所有输出为布尔计数, 非浮点加权."""
from typing import Any, Dict


def build_wuxing_power(pillars: Dict, facts: Dict, th=None, extra_pillars=None) -> Dict[str, Any]:
    """兼容旧接口: 三参数(pillars, facts, th) → 内部调纯规则计数."""
    from engines.common.transit_power import _build_pure_power
    cfc = facts.get('combination_facts', {}) or {}
    return _build_pure_power(pillars, facts, cfc, extra_pillars or [])


def build_spectrum_topology(network: Dict[str, Any], wp: Dict[str, Any]) -> Dict[str, str]:
    """兼容旧接口: 七档spectrum → 四档布尔枚举(强/旺/平/衰)."""
    from engines.common.transit_power import element_power_tier
    dm_wx = network.get('facts', {}).get('daymaster_element', '')
    if not dm_wx:
        dm_wx = wp.get('daymaster_element', '')
    tier = element_power_tier(wp, dm_wx)
    return {'spectrum': tier['name']}


def build_spectrum_from_power(wp: Dict[str, Any], pillars: Dict = None) -> Dict[str, str]:
    """兼容旧接口: 从wp直接取四档."""
    from engines.common.transit_power import element_power_tier
    dm_wx = wp.get('daymaster_element', '')
    if not dm_wx and pillars:
        dm = pillars.get('day', [''])[0]
        from engines.common.l0_fact_builder import WUXING
        dm_wx = WUXING.get(dm, '')
    if not dm_wx:
        return {'spectrum': '平'}
    tier = element_power_tier(wp, dm_wx)
    return {'spectrum': tier['name']}
