# -*- coding: utf-8 -*-
"""ZIPING V3.1 气候 / 清浊 / 通关 / 病药 / 气势 / 用神分方法 域 (辨层扩展).

全部 确定性结构判定, 无数量阈值 (§2/§50), 无 LLM 入判断层 (ARCH-011).
事实缺失 → fail-closed (UNDETERMINED + 分因 §77), 绝不臆测.

Bazi 十神标签为中文 (正官/七杀/正财/偏财/食神/伤官/比肩/劫财/正印/偏印),
子平直接消费, 不重算 (ARCH-003~006).
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Set

from .constants import BRANCH_ELEMENT, STEM_ELEMENT, GENERATES, CONTROLS
from .engine import EngineContext, JudgmentBuilder, Rule
from .types import (
    FrozenBaziFact, MethodScope, UndeterminedReason,
    ZiPingDerivedFact, ZiPingJudgment,
)

# 中文十神 → 结构类
_SHENG = {"正印", "偏印"}          # 生我 (印)
_TONG  = {"比肩", "劫财"}          # 同我 (比劫)
_XIE   = {"食神", "伤官"}          # 我生 (食伤泄)
_HAO   = {"正财", "偏财"}          # 我克 (财耗)
_KE    = {"正官", "七杀"}          # 克我 (官杀)
_DAYMASTER = "DAY_MASTER"


def _stem_tengods(ctx: EngineContext) -> Set[str]:
    """四柱透干 十神集合 (中文, Bazi 冻结)."""
    out: Set[str] = set()
    for pos in ("YEAR", "MONTH", "DAY", "HOUR"):
        tg = (ctx.fact.stem_ten_gods or {}).get(pos, "")
        if tg and tg != _DAYMASTER:
            out.add(tg)
    return out


def _hidden_tengods(ctx: EngineContext) -> Set[str]:
    out: Set[str] = set()
    for pos, info in (ctx.fact.branch_ten_gods or {}).items():
        if isinstance(info, dict):
            out.update(s for s in info.get("all", []) if s and s != _DAYMASTER)
    return out


# ---------------------------------------------------------------------------
# §19/§38 气候 (CLIMATE-FACT + 调候)
# ---------------------------------------------------------------------------

def judge_climate(ctx: EngineContext, derived: ZiPingDerivedFact,
                  climate_table: Optional[Dict] = None) -> ZiPingJudgment:
    """§38 CLIMATEFACT + §19 调候: 月令寒暖燥湿 结构态 + 调候需求.

    寒暖 (月令季): 冬(亥子丑)=COLD / 夏(巳午未)=HOT (CLIMATEFACT-002/003).
    燥湿 (全局): 水结构主导=WET / 火土燥旺=DRY (CLIMATEFACT-004/005).
    调候用神 (YONG-CLIMATE-001): 需 climate_table (pluggable, 缺→fail-closed).
    """
    from .constants import SEASON_OF_MONTH
    month_el = ctx.element_of_branch(ctx.fact.month_branch)
    season = SEASON_OF_MONTH.get(ctx.fact.month_branch, "")

    # 寒暖态 (结构)
    cold_hot: Optional[str]
    if season == "WINTER":
        cold_hot = "COLD"        # CLIMATEFACT-002
        rid, ev = "CLIMATEFACT-002", "E-DT-CLIMATEFACT-002"
    elif season == "SUMMER":
        cold_hot = "HOT"         # CLIMATEFACT-003
        rid, ev = "CLIMATEFACT-003", "E-DT-CLIMATEFACT-003"
    else:
        cold_hot = None          # 春/秋 非寒非暖极端 → 不臆测
        rid, ev = None, None

    # 燥湿态: 全局 水/火土 干 是否出现 (纯结构, 非数量)
    water_present = any(ctx.element_of_stem(s) == "WATER" for s in _stem_tengods(ctx))
    fire_dry_present = any(ctx.element_of_stem(s) in ("FIRE", "EARTH")
                           for s in _stem_tengods(ctx))
    dry_wet: Optional[str]
    if water_present and not fire_dry_present:
        dry_wet = "WET"          # CLIMATEFACT-004
    elif fire_dry_present and not water_present:
        dry_wet = "DRY"         # CLIMATEFACT-005
    else:
        dry_wet = None

    # 无寒暖结构 且 无调候表 → fail-closed
    if cold_hot is None and not climate_table:
        return JudgmentBuilder.undetermined("CLIMATE", UndeterminedReason.FACT_MISSING,
                                            "春/秋 月令非寒暖极端 且 无调候表")

    # 调候需求 (需表, pluggable)
    if climate_table and cold_hot in ("COLD", "HOT"):
        need = climate_table.get(cold_hot)
        if need:
            _r = Rule(rule_id="YONG-CLIMATE-001", domain="CLIMATE",
                      result_state=cold_hot)
            _r.evidence_refs = ["E-QTBJ-YONG-003"]
            _r.method_scope = [MethodScope.QIONG_TONG_BAO_JIAN]
            return JudgmentBuilder.from_hits("CLIMATE", cold_hot, _r)
        return JudgmentBuilder.undetermined("CLIMATE", UndeterminedReason.RULE_MISSING,
                                            f"调候表缺 {cold_hot} 需求格 (fail-closed)")

    if rid:
        _r = Rule(rule_id=rid, domain="CLIMATE", result_state=cold_hot)
        _r.evidence_refs = [ev]
        _r.method_scope = [MethodScope.DI_TIAN_SUI]
        return JudgmentBuilder.from_hits("CLIMATE", cold_hot, _r)

    # 仅燥湿 (无寒暖) → 结构事实
    if dry_wet:
        _r = Rule(rule_id="CLIMATEFACT-004" if dry_wet == "WET" else "CLIMATEFACT-005",
                  domain="CLIMATE", result_state=dry_wet)
        _r.evidence_refs = ["E-DT-CLIMATEFACT-004"]
        _r.method_scope = [MethodScope.DI_TIAN_SUI]
        return JudgmentBuilder.from_hits("CLIMATE", dry_wet, _r)

    return JudgmentBuilder.undetermined("CLIMATE", UndeterminedReason.FACT_MISSING,
                                        "寒暖燥湿 结构 均未消解")


# ---------------------------------------------------------------------------
# §17 清浊 (QING)
# ---------------------------------------------------------------------------

def judge_qing(ctx: EngineContext, derived: ZiPingDerivedFact) -> ZiPingJudgment:
    """清浊: 结构是否 主导清晰 vs 多主竞争/混杂.

    QING-005~007 混杂源 (正偏 同透 即 混杂, 结构存在性判定):
      官杀混杂 (正官+七杀 同透) / 印星混杂 (正印+偏印) / 财星混杂 (正财+偏财).
    有混杂源 → TURBID; 否则 主结构清晰 → CLEAR.
    """
    tg = _stem_tengods(ctx)

    # QING-005~007: 正偏 同透 混杂源
    if {"正官", "七杀"} <= tg:
        return _judge_rule("QING", "TURBID", "QING-005", "E-ZQ-QING-005",
                            "官杀混杂无制")
    if {"正印", "偏印"} <= tg:
        return _judge_rule("QING", "TURBID", "QING-006", "E-ZQ-QING-006",
                            "印星混杂")
    if {"正财", "偏财"} <= tg:
        return _judge_rule("QING", "TURBID", "QING-007", "E-ZQ-QING-007",
                            "财星混杂")

    # 无混杂源 → 结构主导清晰
    return _judge_rule("QING", "CLEAR", "QING-001", "E-DT-QING-001",
                        "主结构连贯, 无决定性问题混杂")


# ---------------------------------------------------------------------------
# §21 通关 (TONGGUAN)
# ---------------------------------------------------------------------------

def judge_tongguan(ctx: EngineContext, derived: ZiPingDerivedFact) -> ZiPingJudgment:
    """通关: 对立结构 是否 有 桥 (通关用神).

    结构逻辑 (TONGGUAN-001~006):
      对立存在 (A克B) → 找 桥 C (C 受 A 且 C 生 B) → 桥有效/被阻/缺失.
      食神制杀 (TONGGUAN-006) → 对立已解, 无需通关.
    纯存在性判定, 非数量.
    """
    tg = _stem_tengods(ctx)
    day_el = ctx.element_of_stem(ctx.fact.day_master)

    # 对立结构: 官杀克我 (对立源)
    officer_present = bool(tg & _KE)
    # 食神制杀 (TONGGUAN-006): 食神 与 七杀 同现 且 食神 制住 杀 → 对立已解
    if "食神" in tg and "七杀" in tg:
        return _judge_rule("TONGGUAN", "OPPOSITION_RESOLVED", "TONGGUAN-006",
                           "E-ZQ-TONGGUAN-006", "食神制杀, 制而不战, 无需通关")

    if not officer_present:
        # 无 克我 对立 → 无对立可通 (TONGGUAN-005 无对立 = 无需桥)
        return JudgmentBuilder.undetermined("TONGGUAN", UndeterminedReason.RULE_MISSING,
                                            "无对立结构, 通关不适用")

    # 对立存在 → 需 通关用神 桥 (pluggable, 缺表 fail-closed)
    bridge = _bridge_candidate(ctx, derived)
    if bridge:
        return _judge_rule("TONGGUAN", "TONGGUAN_EFFECTIVE", "TONGGUAN-003",
                           "E-DT-TONGGUAN-003", f"桥用神 {bridge} 有根/未被阻")
    return _judge_rule("TONGGUAN", "TONGGUAN_ABSENT", "TONGGUAN-005",
                       "E-DT-TONGGUAN-005", "对立存在但无有效通关桥")


def _bridge_candidate(ctx: EngineContext, derived: ZiPingDerivedFact) -> Optional[str]:
    """通关桥: 日主 与 对立(官杀) 之间 的生链 中干 (结构, 非数量).

    官杀 克日主: 用 印 (生日主, 官杀生印) 或 食伤 (日主生食伤, 食伤制官杀).
    返回 首个 出现于 四柱透干 的 桥干 (中文十神). 纯存在性.
    """
    tg = _stem_tengods(ctx)
    # 印 通关 (官杀 → 生印 → 生日主)
    if tg & _SHENG:
        return next(iter(tg & _SHENG))
    # 食伤 通关 (日主 → 生食伤 → 制官杀)
    if tg & _XIE:
        return next(iter(tg & _XIE))
    return None


# ---------------------------------------------------------------------------
# §20 病药 (DISEASE / MEDICINE)
# ---------------------------------------------------------------------------

def judge_disease(ctx: EngineContext, derived: ZiPingDerivedFact,
                  pattern_judgment: Optional[ZiPingJudgment] = None
                  ) -> ZiPingJudgment:
    """病药: 主格局 是否 被 对立结构 实质阻碍 (DISEASE), 药 是否 解病 (MEDICINE).

    五件套 (§61 REV-DISEASE): DISEASE_PRESENT/ABSENT +
    MEDICINE_EFFECTIVE/BLOCKED/UNRESOLVED. 禁 "病重药轻" 量化比较.
    需 pattern_judgment (主格); 缺 → fail-closed.
    """
    if pattern_judgment is None or pattern_judgment.state in ("UNDETERMINED",
                                                              "NOT_APPLICABLE"):
        return JudgmentBuilder.undetermined("DISEASE", UndeterminedReason.DEPENDENCY_UNRESOLVED,
                                            "主格未定 (病药 需 主格局, fail-closed)")

    tg = _stem_tengods(ctx)
    opposition = bool(tg & (_KE | _XIE | _HAO))

    # DISEASE-004: 无结构失衡 → 无病
    if not opposition:
        return _judge_rule("DISEASE", "DISEASE_ABSENT", "MEDICINE-004",
                           "E-DT-MEDICINE-004", "无结构失衡, 无病")
    # DISEASE-001: 对立结构实质阻碍主格 → 有病
    bridge = _bridge_candidate(ctx, derived)
    if bridge:
        return _judge_rule("DISEASE", "DISEASE_PRESENT", "DISEASE-001",
                           "E-DT-DISEASE-001", "有对立结构, 药(桥)可解")
    return _judge_rule("DISEASE", "DISEASE_UNRESOLVED", "MEDICINE-003",
                       "E-DT-MEDICINE-003", "有病但无有效药")


# ---------------------------------------------------------------------------
# §12 气势 (QI)
# ---------------------------------------------------------------------------

def judge_qi(ctx: EngineContext, derived: ZiPingDerivedFact,
             ling: Optional[ZiPingJudgment] = None,
             party: Optional[Dict[str, Any]] = None) -> ZiPingJudgment:
    """气势: 方向 定性 (非数量统计).

    依赖 上一步 月令 (DE_LING/SHI_LING) + 党众结构 (帮身/对立).
    QI-001 CONCENTRATED (得令+根同向) / QI-003 CONTESTED (帮身对立并存) /
    QI-005 DOMINANT (单一方向压倒) / QI-006 MIXED (无连贯方向).
    缺输入 → fail-closed.
    """
    if party is None:
        return JudgmentBuilder.undetermined("QI", UndeterminedReason.FACT_MISSING,
                                            "党众结构 未提供 (气势 需 党众输入)")
    support = set(party.get("SUPPORT_STRUCTURE", []))
    opposition = set(party.get("OPPOSITION_STRUCTURE", []))
    de_ling = bool(ling) and ling.state == "DE_LING"

    # QI-005 单一方向压倒: 仅对立 无帮身
    if opposition and not (support - {"月令"}):
        return _judge_rule("QI", "DOMINANT", "QI-005", "E-DT-QI-005",
                            "对立方向 压倒全盘")
    # QI-001 得令+同向: 得令 且 帮身结构含 月令
    if de_ling and "月令" in support:
        return _judge_rule("QI", "CONCENTRATED", "QI-001", "E-DT-QI-001",
                            "得令 根同向 强化")
    # QI-003 帮身对立 并存 → 竞争
    if (support - {"月令"}) and opposition:
        return _judge_rule("QI", "CONTESTED", "QI-003", "E-DT-QI-003",
                            "主要结构 相互对立")
    # QI-006 无连贯方向
    return _judge_rule("QI", "MIXED", "QI-006", "E-DT-QI-006",
                        "无连贯方向可立")


# ---------------------------------------------------------------------------
# §23 用神分方法 (YONG) — 分方法, 不合并
# ---------------------------------------------------------------------------

def judge_yong(
    ctx: EngineContext,
    derived: ZiPingDerivedFact,
    pattern: Optional[ZiPingJudgment] = None,
    climate: Optional[ZiPingJudgment] = None,
    disease: Optional[ZiPingJudgment] = None,
    tongguan: Optional[ZiPingJudgment] = None,
    climate_table: Optional[Dict] = None,
) -> Dict[str, ZiPingJudgment]:
    """用神 分方法 (YONG-PATTERN/CLIMATE/DISEASE/BRIDGE, §57 REV-YONG 隔离).

    各方法独立出 用神候选, YONG-MULTI-001: 多方法冲突 → 全部输出并标注方法来源,
    不合并不裁决唯一. 缺方法输入 → 该方法 UNDETERMINED.
    """
    out: Dict[str, ZiPingJudgment] = {}

    # 格局用神 (YONG-PATTERN-001/002)
    if pattern is not None and pattern.state not in ("UNDETERMINED", "NOT_APPLICABLE"):
        _r = Rule("YONG-PATTERN-001", "YONG-PATTERN", "")
        _r.evidence_refs = ["E-ZQ-YONG-001"]
        _r.method_scope = [MethodScope.ZIPING_ZHENQUAN]
        out["pattern"] = JudgmentBuilder.from_hits("YONG-PATTERN", pattern.state, _r)
    else:
        out["pattern"] = JudgmentBuilder.undetermined("YONG-PATTERN",
                                                      UndeterminedReason.DEPENDENCY_UNRESOLVED,
                                                      "主格未定, 格局用神 无法取")

    # 调候用神 (YONG-CLIMATE-001): 需 气候态 + 调候表
    if climate is not None and climate.state in ("COLD", "HOT") and climate_table:
        out["climate"] = climate  # 气候判断 已含 调候需求
    else:
        out["climate"] = JudgmentBuilder.undetermined("YONG-CLIMATE",
                                                       UndeterminedReason.FACT_MISSING,
                                                       "气候 或 调候表 缺失")

    # 病药用神 (YONG-DISEASE-001)
    if disease is not None and disease.state == "DISEASE_PRESENT":
        out["disease"] = _judge_rule("YONG-DISEASE", "YONG_DISEASE_DEFINED",
                                     "YONG-DISEASE-001", "E-DT-YONG-004",
                                     "有病, 药 为 病药用神")
    else:
        out["disease"] = JudgmentBuilder.undetermined("YONG-DISEASE",
                                                       UndeterminedReason.DEPENDENCY_UNRESOLVED,
                                                       "无 有效病 结构, 病药用神 不适用")

    # 通关卡神 (YONG-BRIDGE-001)
    if tongguan is not None and tongguan.state == "TONGGUAN_EFFECTIVE":
        out["bridge"] = _judge_rule("YONG-BRIDGE", "YONG_BRIDGE_DEFINED",
                                     "YONG-BRIDGE-001", "E-DT-YONG-005",
                                     "有效对立+有效桥, 桥 为 通关卡神")
    else:
        out["bridge"] = JudgmentBuilder.undetermined("YONG-BRIDGE",
                                                      UndeterminedReason.DEPENDENCY_UNRESOLVED,
                                                      "无 有效通关桥, 通关卡神 不适用")

    # YONG-MULTI-001: 多方法冲突 → 全部输出 (本函数已分键输出, 不合并)
    return out


# ---------------------------------------------------------------------------
# helper
# ---------------------------------------------------------------------------

def _judge_rule(domain: str, state: str, rule_id: str, evidence: str,
                detail: str = "") -> ZiPingJudgment:
    _r = Rule(rule_id=rule_id, domain=domain, result_state=state)
    _r.evidence_refs = [evidence]
    _r.method_scope = [MethodScope.DI_TIAN_SUI]
    j = JudgmentBuilder.from_hits(domain, state, _r)
    # 附 detail (ZiPingJudgment.reason_detail) — 非 UNDETERMINED 也可携带说明
    j.reason_detail = detail or None
    return j
