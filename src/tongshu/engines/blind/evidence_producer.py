# -*- coding: utf-8 -*-
"""P2-EVIDENCE-REFACTOR — 盲派证据重构

职责：
  - BlindFeatureState: 精简的特征状态（从 BlindBaziResult 派生）
  - EvidenceItem: 证据项（移除 direction/polarity/strength）
  - EvidenceList: 证据列表容器
  - BlindEvidenceProducer: 接收 BlindFeatureState，输出 EvidenceList
"""
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any, Dict, List, Optional


# ─── 相关性枚举 ────────────────────────────────────────────────────────────────

class Relevance(str):
    """证据相关性等级（高/中/低），替代原有的 direction/polarity/strength"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"

    @classmethod
    def values(cls) -> List[str]:
        return [cls.HIGH, cls.MEDIUM, cls.LOW]


# ─── BlindFeatureState ─────────────────────────────────────────────────────────

@dataclass(frozen=True)
class BlindFeatureState:
    """盲派特征状态 —— 从 BlindBaziResult 提取的纯事实特征集合

    设计原则：
    - 只保留客观结构事实（无方向/极性/强度评估）
    - 字段不可变（frozen）
    - 完整可追溯
    """
    # 宾主判定
    main_branches: frozenset = field(default_factory=frozenset)
    guest_branches: frozenset = field(default_factory=frozenset)

    # 体用分析
    ti_branches: frozenset = field(default_factory=frozenset)
    yong_branches: frozenset = field(default_factory=frozenset)
    ti_stems: tuple = ()
    yong_stems: tuple = ()

    # 做功判断
    zuo_gong: bool = False
    zuo_gong_type: str = ""
    zuo_gong_methods: tuple = ()
    zuo_gong_detail: tuple = ()

    # 透干十神
    transparent_ten_gods: tuple = ()  # ((pillar, ten_god), ...)

    def to_dict(self) -> dict:
        return {
            "main_branches": list(self.main_branches),
            "guest_branches": list(self.guest_branches),
            "ti_branches": list(self.ti_branches),
            "yong_branches": list(self.yong_branches),
            "ti_stems": list(self.ti_stems),
            "yong_stems": list(self.yong_stems),
            "zuo_gong": self.zuo_gong,
            "zuo_gong_type": self.zuo_gong_type,
            "zuo_gong_methods": list(self.zuo_gong_methods),
            "zuo_gong_detail": list(self.zuo_gong_detail),
            "transparent_ten_gods": list(self.transparent_ten_gods),
        }

    @classmethod
    def from_blind_result(cls, result) -> "BlindFeatureState":
        """从 BlindBaziResult 转换为 BlindFeatureState"""
        return cls(
            main_branches=frozenset(result.main_branches),
            guest_branches=frozenset(result.guest_branches),
            ti_branches=frozenset(result.ti_branches),
            yong_branches=frozenset(result.yong_branches),
            ti_stems=tuple(result.ti_stems),
            yong_stems=tuple(result.yong_stems),
            zuo_gong=result.zuo_gong,
            zuo_gong_type=result.zuo_gong_type,
            zuo_gong_methods=tuple(result.zuo_gong_methods),
            zuo_gong_detail=tuple(result.zuo_gong_detail),
            transparent_ten_gods=tuple(
                (k, v) for k, v in result.transparent_ten_gods.items()
            ),
        )


# ─── EvidenceItem ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class EvidenceItem:
    """单条证据 —— 移除 direction/polarity/strength，改用 relevance"""
    id: str
    source: str          # 可追溯来源（如 "《盲派八字技法》"）
    content: str         # 证据内容（原文引用或结构化描述）
    relevance: str       # "高"/"中"/"低"
    valid: bool = True
    verified_at: Optional[str] = None  # 验证时间（ISO格式字符串）

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source": self.source,
            "content": self.content,
            "relevance": self.relevance,
            "valid": self.valid,
            "verified_at": self.verified_at,
        }


# ─── EvidenceList ──────────────────────────────────────────────────────────────

@dataclass
class EvidenceList:
    """证据列表容器"""
    items: List[EvidenceItem] = field(default_factory=list)

    def add(self, item: EvidenceItem) -> None:
        self.items.append(item)

    def filter_by_relevance(self, relevance: str) -> "EvidenceList":
        return EvidenceList([it for it in self.items if it.relevance == relevance])

    def filter_valid(self) -> "EvidenceList":
        return EvidenceList([it for it in self.items if it.valid])

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self):
        return iter(self.items)

    def to_dict(self) -> dict:
        return {
            "total": len(self.items),
            "items": [item.to_dict() for item in self.items],
        }


# ─── BlindEvidenceProducer ─────────────────────────────────────────────────────

class BlindEvidenceProducer:
    """盲派证据生产者

    职责：
    - 接收 BlindFeatureState（而非原始 BaziChart/BlindBaziResult）
    - 输出 EvidenceList（包含 EvidenceItem 列表）
    - 不产生 direction/polarity/strength/confidence
    """

    RULE_PREFIX = "BL"
    CALC_VERSION = "2026.09"

    # 证据来源规范
    SOURCE_RULES = {
        "main_guest": "data/rules/blind_main_guest.json",
        "ti_yong": "data/rules/blind_ti_yong.json",
        "zuo_gong": "data/rules/blind_zuo_gong.json",
        "ten_gods": "data/rules/blind_ten_gods.json",
    }

    def produce(
        self,
        state: BlindFeatureState,
        verified_at: Optional[str] = None,
    ) -> EvidenceList:
        """从 BlindFeatureState 生成证据列表

        Args:
            state: BlindFeatureState 对象
            verified_at: 验证时间戳（可选，默认当前日期）

        Returns:
            EvidenceList
        """
        evidences = EvidenceList()

        # 1. 宾主判定证据
        evidences.add(
            EvidenceItem(
                id=f"{self.RULE_PREFIX}-MAIN-{uuid.uuid4().hex[:8]}",
                source=self.SOURCE_RULES["main_guest"],
                content=f"主位地支：{sorted(state.main_branches)}；宾位地支：{sorted(state.guest_branches)}",
                relevance=Relevance.HIGH if len(state.main_branches) > 0 else Relevance.LOW,
                valid=True,
                verified_at=verified_at or date.today().isoformat(),
            )
        )

        # 2. 体用分析证据
        evidences.add(
            EvidenceItem(
                id=f"{self.RULE_PREFIX}-TI-{uuid.uuid4().hex[:8]}",
                source=self.SOURCE_RULES["ti_yong"],
                content=(
                    f"体支：{sorted(state.ti_branches)}；"
                    f"用支：{sorted(state.yong_branches)}；"
                    f"体干：{list(state.ti_stems)}；"
                    f"用干：{list(state.yong_stems)}"
                ),
                relevance=Relevance.HIGH if len(state.ti_branches) > 0 else Relevance.MEDIUM,
                valid=True,
                verified_at=verified_at or date.today().isoformat(),
            )
        )

        # 3. 做功结构证据
        if state.zuo_gong:
            evidences.add(
                EvidenceItem(
                    id=f"{self.RULE_PREFIX}-ZG-{uuid.uuid4().hex[:8]}",
                    source=self.SOURCE_RULES["zuo_gong"],
                    content=(
                        f"做功类型：{state.zuo_gong_type}；"
                        f"方法：{list(state.zuo_gong_methods)}；"
                        f"细节：{list(state.zuo_gong_detail)}"
                    ),
                    relevance=Relevance.HIGH,
                    valid=True,
                    verified_at=verified_at or date.today().isoformat(),
                )
            )
        else:
            evidences.add(
                EvidenceItem(
                    id=f"{self.RULE_PREFIX}-ZG-{uuid.uuid4().hex[:8]}",
                    source=self.SOURCE_RULES["zuo_gong"],
                    content="未检测到有效做功结构",
                    relevance=Relevance.LOW,
                    valid=True,
                    verified_at=verified_at or date.today().isoformat(),
                )
            )

        # 4. 透干十神证据
        if state.transparent_ten_gods:
            for pillar, ten_god in state.transparent_ten_gods:
                evidences.add(
                    EvidenceItem(
                        id=f"{self.RULE_PREFIX}-TGTG-{pillar}-{uuid.uuid4().hex[:6]}",
                        source=self.SOURCE_RULES["ten_gods"],
                        content=f"{pillar}柱透干为{ten_god}",
                        relevance=Relevance.MEDIUM,
                        valid=True,
                        verified_at=verified_at or date.today().isoformat(),
                    )
                )

        return evidences
