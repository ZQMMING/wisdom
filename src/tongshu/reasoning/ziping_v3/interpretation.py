# -*- coding: utf-8 -*-
"""ZIPING 解层 (Interpretation) — C 版本: STRENGTH / QING / XIJI 三域断语触发.

架构:
    §28 辨层状态枚举
        ↓
    interpretation.py  (解层)
        ├── DomainResolver: 判断"这条断语是否适用当前命局"
        ├── DuanyuMatcher:  加载断语库条件钩子 → 命中候选集
        └── Interpretation: 每条触发断语输出 trigger/context/duanyu_text/evidence_ref

约束:
    1. 只读断语库 D:\顺天系统资料\五部经典断语库\03_综合索引\all_duanyu.json
    2. 不修改 §28 枚举，只追加 interpretations[] 字段
    3. 每条断语带 evidence_ref = classic + source + text[:40]
    4. 解层不得引入 LLM, score, weight, percentage
    5. 未实现的 X 域保持 UNDETERMINED (fail-closed)

C 阶段 (本 PR):
    - STRENGTH 三域断语 (旺衰类 ~1982 条 + 贫贱富贵类 ~340 条 + 部分用神喜忌类)
    - QING 两域断语 (清浊混杂相关类别)
    - XIJI 用神喜忌类 (4089 条全量接入, 但只输出可触发子集)

A 阶段 (后续):
    - 全部 16 类别断语接入
    - Semantic Bridge 连接现代概念 Registry
    - 完整 Chain: Judgment → Domain Resolver → Duanyu → Interpretation → Advice
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# 断语库路径 (资源库, 禁止硬编码本地开发机绝对路径)
DUANYU_DB = Path(__file__).parent.parent.parent.parent.parent.parent / "顺天系统资料" / "五部经典断语库" / "03_综合索引" / "all_duanyu.json"


@dataclass
class TriggeredDuanyu:
    """单条断语触发结果."""
    classic: str          # 经典名
    primary_category: str # 主类别
    text: str             # 断语原文 (逐字抄录)
    rule_match: str       # §28 域状态, 如 "STRENGTH=WANG_BUT_NOT_STRONG"
    evidence_ref: str     # 追溯引用: class+source+text[:40]
    confidence: str       # STRONG / MODERATE / WEAK (规则匹配可信度)


@dataclass
class InterpretationOutput:
    """解层输出契约."""
    strengths: List[TriggeredDuanyu] = field(default_factory=list)
    qings: List[TriggeredDuanyu] = field(default_factory=list)
    xijis: List[TriggeredDuanyu] = field(default_factory=list)
    undetermined_domains: List[str] = field(default_factory=list)


class DuanyuLoader:
    """断语库加载器 — 只做读取, 不修改 backend/."""

    def __init__(self, db_path: Path = DUANYU_DB):
        self._db_path = db_path
        self._cache: Optional[List[Dict[str, Any]]] = None

    @property
    def db_path(self) -> Path:
        return self._db_path

    def load(self) -> List[Dict[str, Any]]:
        """加载断语库, 带内存缓存."""
        if self._cache is not None:
            return self._cache
        if not self._db_path.exists():
            raise FileNotFoundError(f"断语库不存在: {self._db_path}")
        with open(self._db_path, encoding="utf-8") as f:
            self._cache = json.load(f)
        return self._cache

    def filter_by_categories(
        self,
        cats: List[str],
        exclude_prefixes: List[str] = None,
    ) -> List[Dict[str, Any]]:
        """按类别过滤, 排除散文原注."""
        all_data = self.load()
        if exclude_prefixes is None:
            exclude_prefixes = ["原注", "任氏曰", "书云", "目录"]
        results = []
        for item in all_data:
            if item.get("primary_category") not in cats and not any(
                c in item.get("categories", []) for c in cats
            ):
                continue
            text = item.get("text", "")
            if text and text.lstrip()[:2] in exclude_prefixes or text.lstrip()[:1] in ("序", "《"):
                continue
            results.append(item)
        return results


class DomainResolver:
    """解层核心: 判断当前 §28 状态是否满足断语条件."""

    # 命局状态 → 断语条件钩子 映射 (覆盖 C 阶段三域, 含古汉语原词)
    _STRENGTH_RULES: Dict[str, List[str]] = {
        "STRONG": ["身旺", "得令", "有根", "比劫多", "得地", "党众", "印比", "身强", "旺", "旺相", "气旺", "日干旺", "得时", "乘时"],
        "WANG_BUT_NOT_STRONG": ["得令但不旺", "旺而不足", "根旺透弱", "旺而不强", "失令但强", "身旺不专", "旺而受制", "旺而有制", "虽旺", "得令", "乘时", "得气但不专"],
        "SHUAI_BUT_NOT_WEAK": ["失令但不弱", "有根得助", "体用调和", "中和", "身衰不弱", "财多身弱", "气弱但帮", "衰而有根", "身弱有根", "虽有根"],
        "WEAK": ["身弱", "失令无根", "泄耗太过", "弱极", "身衰", "体弱", "无助", "气弱", "身弱无根", "日干弱", "失时"],
        "BALANCED": ["中和", "强弱适中", "无偏无倚", "平衡", "身不偏", "阴阳调和", "得中", "平", "不偏不倚"],
        "WANG_OVER": ["太旺", "亢旺", "过强", "身旺无依", "旺极", "旺之极", "太过", "偏旺"],
        "WEAK_OVER": ["极弱", "虚浮", "无根", "身弱无依", "弱极", "太弱", "不及", "偏枯"],
    }

    _QING_RULES: Dict[str, List[str]] = {
        "CLEAR": ["清纯", "不杂", "单一", "清透", "专", "清纯不杂", "不混", "清", "气清", "格局清纯", "无杂", "纯粹", "清顺"],
        "TURBID": ["混杂", "官杀混杂", "财印相战", "不清", "浊", "官杀混杂格", "正官七杀同透", "浊", "气浊", "格不清", "混浊", "偏枯", "杂", "驳"],
        "PARTIAL_CLEAR": ["略清", "微浊", "半清半浊", "清中带浊", "浊中带清", "清浊兼"],
    }

    _XIJI_RULES: Dict[str, List[str]] = {
        "STRONG": ["身旺宜克泄", "身旺忌印比", "用官杀", "用食伤", "用财", "喜财官", "宜财官", "旺宜泄", "旺喜", "旺忌", "喜克泄", "宜泄", "当克泄", "喜官杀", "喜食伤"],
        "WEAK": ["身弱宜生扶", "身弱忌克泄", "用印比", "用劫", "喜印比", "宜印比", "弱宜生扶", "弱喜", "弱忌", "喜生扶", "宜生", "当生扶", "喜印比"],
        "BALANCED": ["中和用通关", "视格局定喜忌", "中气调和", "当通关", "宜调和"],
        "HOT": ["火炎土燥喜水", "调候以癸", "润局为先", "金寒水冷喜火", "水多火熄喜土", "夏木虚焦调候以癸", "火旺", "炎上", "火燥", "喜润", "调候以水", "夏月调候"],
        "COLD": ["金寒水冷喜火", "调候以丙", "暖局为先", "冬水需火", "寒局喜暖", "冬金需火", "水冷", "寒金", "喜暖", "调候以火", "冬月调候", "寒气"],
        "DRY": ["燥土需水", "土燥喜润", "燥气需调", "土燥", "燥热", "喜润局", "宜润"],
        "WET": ["湿土需火", "水旺喜土", "湿局需暖", "水多", "湿土", "水泛", "宜燥", "宜暖"],
    }

    @classmethod
    def resolve_strength(
        cls, strength_state: str, party: Dict[str, List[str]] = None
    ) -> List[str]:
        """解析 STRENGTH 域, 返回断语条件钩子列表."""
        hooks = cls._STRENGTH_RULES.get(strength_state, [])
        if party:
            if "官杀" in party.get("对立", []):
                hooks.append("官杀克")
            if "印星" in party.get("帮身", []):
                hooks.append("印生")
        return hooks

    @classmethod
    def resolve_qing(cls, qing_state: str) -> List[str]:
        """解析 QING 域."""
        return cls._QING_RULES.get(qing_state, [])

    @classmethod
    def resolve_xiji(
        cls, strength_state: str, climate_state: str
    ) -> List[str]:
        """解析 XIJI 域 (身强弱 + 气候)."""
        hooks = list(cls._XIJI_RULES.get(strength_state, []))
        if climate_state in ("HOT", "COLD", "DRY", "WET"):
            hooks.extend(cls._XIJI_RULES.get(climate_state, []))
        return hooks


class DuanyuMatcher:
    """断语匹配器: 条件钩子 → 命局状态 → 断语文本."""

    def __init__(self, loader: DuanyuLoader):
        self._loader = loader

    def match(
        self,
        hooks: List[str],
        target_cats: List[str],
        limit: int = 20,
    ) -> List[TriggeredDuanyu]:
        """
        匹配断语.
        hooks: 命局条件钩子
        target_cats: 目标断语类别
        limit: 最多返回几条
        """
        candidates = self._loader.filter_by_categories(target_cats)
        matched = []
        for cand in candidates:
            text = cand.get("text", "")
            if not text:
                continue
            # 检查断语文本是否匹配至少一个钩子
            matched_hook = None
            for hook in hooks:
                if hook in text or hook.replace("(", "").replace(")", "") in text:
                    matched_hook = hook
                    break
            if matched_hook:
                matched.append(TriggeredDuanyu(
                    classic=cand.get("classic", ""),
                    primary_category=cand.get("primary_category", ""),
                    text=text,
                    rule_match=matched_hook,
                    evidence_ref=f"{cand.get('classic', '')}·{cand.get('source', '')}:{text[:40]}...",
                    confidence="STRONG" if len(matched_hook) >= 4 else "MODERATE",
                ))
                if len(matched) >= limit:
                    break
        return matched


def build_interpretation(
    strength_state: str,
    qing_state: str,
    climate_state: str,
    party: Dict[str, List[str]] = None,
) -> InterpretationOutput:
    """
    解层入口函数: §28 状态枚举 → 断语触发输出.
    C 阶段仅覆盖 STRENGTH / QING / XIJI 三域.
    """
    output = InterpretationOutput()

    # 1. STRENGTH 解层
    strength_hooks = DomainResolver.resolve_strength(strength_state, party)
    strength_cands = DuanyuMatcher(DuanyuLoader()).match(
        hooks=strength_hooks,
        target_cats=["旺衰类", "贫贱富贵类", "用神喜忌类"],
        limit=10,
    )
    output.strengths = strength_cands

    # 2. QING 解层
    qing_hooks = DomainResolver.resolve_qing(qing_state)
    qing_cands = DuanyuMatcher(DuanyuLoader()).match(
        hooks=qing_hooks,
        target_cats=["刑冲合害类", "用神喜忌类"],
        limit=5,
    )
    output.qings = qing_cands

    # 3. XIJI 解层
    xiji_hooks = DomainResolver.resolve_xiji(strength_state, climate_state)
    xiji_cands = DuanyuMatcher(DuanyuLoader()).match(
        hooks=xiji_hooks,
        target_cats=["用神喜忌类"],
        limit=15,
    )
    output.xijis = xiji_cands

    # 4. 未实现域的 fail-closed 登记
    all_states = {"STRENGTH": strength_state, "QING": qing_state, "CLIMATE": climate_state}
    for dom, state in all_states.items():
        if state == "UNDETERMINED":
            output.undetermined_domains.append(dom)

    return output
