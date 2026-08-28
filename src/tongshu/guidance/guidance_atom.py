"""P5-A GuidanceAtom - 面向用户的行动解释原子.

这是Assertion与用户可见输出之间的中间层.
Assertion是事实层面的"判断", GuidanceAtom是面向用户的"行动解释".

硬契约(4条红线):
  1. Renderer不得重新计算 - GuidanceAtom已经包含所有用户可见信息
  2. Composer不得创造Evidence - 所有判断可追溯回source_assertion_ids
  3. 不允许从direction偷换成吉凶 - direction_label只能是"有利条件"/"需要注意"/"无明显方向性偏移"
  4. 不引入AI自由推理 - Mapping是deterministic的

禁止术语:
  - 传统吉凶: 吉/凶/大吉/大凶/上上/下下/好运/厄运
  - 确定性预测: 必然/一定/注定/肯定/绝对/一定会
  - 命定论: 命里注定/天意/劫数/报应

方向标签映射(不是吉凶):
  supportive -> "有利条件" / "可利用窗口"
  caution    -> "需要注意" / "结构性压力"
  neutral    -> "无明显方向性偏移" / "当前平稳"
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Any, Optional


# 禁止术语 - GuidanceAtom中不允许出现
FORBIDDEN_TERMS = frozenset({
    # 传统吉凶
    "大吉", "大凶", "上上", "下下", "好运", "厄运", "吉兆", "凶兆",
    "吉星", "凶星", "吉利", "凶险", "吉祥", "不祥", "福运", "祸运",
    # 确定性预测
    "必然", "一定", "注定", "肯定", "绝对", "一定会", "必然会", "注定会",
    # 命定论
    "命里注定", "天意", "劫数", "报应", "命该如此", "天数",
})

# 方向标签映射 - 不是吉凶
DIRECTION_LABELS = {
    "supportive": "有利条件",
    "caution": "需要注意",
    "neutral": "无明显方向性偏移",
}

# 方向描述映射 - 更具体的语境
DIRECTION_DESCRIPTIONS = {
    "supportive": "当前结构中存在可利用的有利条件, 适合主动推进相关事项",
    "caution": "当前结构中存在需要注意的压力或变化, 适合谨慎处理相关事项",
    "neutral": "当前没有明显的方向性偏移, 适合按常规节奏推进",
}


def make_guidance_id(case_id: str, domain: str, theme: str) -> str:
    """生成GuidanceAtom ID."""
    raw = f"{case_id}:{domain}:{theme}"
    return "GUID-" + hashlib.md5(raw.encode()).hexdigest()[:12]


@dataclass
class GuidanceAtom:
    """面向用户的行动解释原子.

    一个GuidanceAtom对应一个人生维度的一个主题, 包含:
    - 方向标签(不是吉凶)
    - 机会/注意事项/行动建议/避免事项
    - 可追溯的来源断言ID
    """
    guidance_id: str
    case_id: str
    domain: str  # 人生维度: CAREER/FINANCE/RELATIONSHIP/FAMILY/HEALTH/GROWTH/DECISION/MIGRATION
    theme: str  # 主题, 如"结构调整期"/"资源转化窗口"/"关系重新定位"
    direction_label: str  # 方向标签: 有利条件/需要注意/无明显方向性偏移
    direction_description: str  # 方向描述
    opportunities: list[str] = field(default_factory=list)  # 机会列表
    cautions: list[str] = field(default_factory=list)  # 注意事项列表
    actions: list[str] = field(default_factory=list)  # 行动建议列表
    avoid: list[str] = field(default_factory=list)  # 避免事项列表
    source_assertion_ids: list[str] = field(default_factory=list)  # 来源断言ID(可追溯)
    source_engines: list[str] = field(default_factory=list)  # 来源引擎(互补覆盖面)
    source_clusters: list[str] = field(default_factory=list)  # 来源cluster ID
    temporal_scope: str = "birth"  # 时间范围
    intensity: int = 50  # 强度(0-100, 不是概率/置信度)
    status: str = "P5_MAPPED"  # P5_MAPPED / P5_COMPOSED / P5_RENDERED

    def __post_init__(self):
        """验证GuidanceAtom契约."""
        # direction_label必须是合法值
        valid_labels = set(DIRECTION_LABELS.values())
        if self.direction_label not in valid_labels:
            raise ValueError(
                f"GuidanceAtom direction_label must be one of {valid_labels}, "
                f"got '{self.direction_label}'"
            )

        # intensity范围
        if not (0 <= self.intensity <= 100):
            raise ValueError(f"GuidanceAtom intensity must be 0-100, got {self.intensity}")

        # 检查禁止术语
        all_text = " ".join([
            self.theme, self.direction_label, self.direction_description,
            *self.opportunities, *self.cautions, *self.actions, *self.avoid,
        ])
        for term in FORBIDDEN_TERMS:
            if term in all_text:
                raise ValueError(
                    f"GuidanceAtom contains forbidden term: '{term}' "
                    f"(theme={self.theme}, domain={self.domain})"
                )

        # 必须有来源断言(可追溯)
        if not self.source_assertion_ids:
            raise ValueError(
                f"GuidanceAtom {self.guidance_id} must have source_assertion_ids (traceability)"
            )

    def to_dict(self) -> dict:
        return {
            "guidance_id": self.guidance_id,
            "case_id": self.case_id,
            "domain": self.domain,
            "theme": self.theme,
            "direction_label": self.direction_label,
            "direction_description": self.direction_description,
            "opportunities": self.opportunities,
            "cautions": self.cautions,
            "actions": self.actions,
            "avoid": self.avoid,
            "source_assertion_ids": self.source_assertion_ids,
            "source_engines": self.source_engines,
            "source_clusters": self.source_clusters,
            "temporal_scope": self.temporal_scope,
            "intensity": self.intensity,
            "status": self.status,
        }


def validate_guidance_contract(atoms: list[GuidanceAtom]) -> list[str]:
    """验证一组GuidanceAtom的契约."""
    errors = []
    for atom in atoms:
        try:
            pass  # __post_init__已经验证了大部分
        except ValueError as e:
            errors.append(f"GuidanceAtom {atom.guidance_id}: {e}")

        # 额外检查: opportunities/cautions/actions/avoid不应该全部为空
        if not any([atom.opportunities, atom.cautions, atom.actions, atom.avoid]):
            errors.append(
                f"GuidanceAtom {atom.guidance_id} has no content "
                f"(opportunities/cautions/actions/avoid all empty)"
            )

    return errors
