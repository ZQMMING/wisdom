"""
Zhongzhou Evidence / Trace Resolver — 中州派证据绑定层（P0-4-A）

职责：
- 把每条 Rule → Source 绑定起来。
- 提供可审计的证据链：combo_id → source → 原文片段 → 证据等级。

证据等级：
- 1 = 王亭之原文
- 2 = 中州派讲义传承
- 3 = 后人整理（不进生产）
- 4 = 推演/现代解释（不进生产）

P0-4-A 严格只登记证据等级 1 的规则。
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ZhongzhouEvidence:
    """一条 Rule 的证据绑定。"""
    rule_id: str
    combo_id: str
    source: str           # 来源标识（如 "d48733", "谈星1107"）
    source_location: str  # 具体段落 / 句子位置
    original_text: str    # 原文片段（用于审计）
    evidence_grade: int   # 1 / 2 / 3 / 4


# P0-4-A Evidence 绑定表（10 条 + DRAFT 留 0 条）
EVIDENCE_TABLE: dict[str, ZhongzhouEvidence] = {
    "ZHZ-CMB-001": ZhongzhouEvidence(
        rule_id="R-COMBO-08",
        combo_id="ZHZ-CMB-001",
        source="d48733",
        source_location="中州派紫微斗数理论基础 / 60 星系表",
        original_text="机月同梁作吏人（命宫三方四正含 天机 + 天同 + 天梁 + 太阴）",
        evidence_grade=1,
    ),
    "ZHZ-CMB-003": ZhongzhouEvidence(
        rule_id="R-COMBO-09",
        combo_id="ZHZ-CMB-003",
        source="d48733",
        source_location="中州派紫微斗数理论基础 / 60 星系表",
        original_text="杀破廉贪四曜，性质刚烈，入庙会照主大富贵，否则主大凶暴",
        evidence_grade=1,
    ),
    "ZHZ-CMB-004": ZhongzhouEvidence(
        rule_id="R-COMBO-06",
        combo_id="ZHZ-CMB-004",
        source="谈星1108",
        source_location="王亭之谈星系列 / 1108 篇",
        original_text="天相 + 左右邻宫分别 巨门 + 天梁（巨门主财，天梁主荫）",
        evidence_grade=1,
    ),
    "ZHZ-CMB-006": ZhongzhouEvidence(
        rule_id="R-COMBO-06",
        combo_id="ZHZ-CMB-006",
        source="谈星1108",
        source_location="王亭之谈星系列 / 1108 篇",
        original_text="巨门 + 天梁 在天相左右邻宫，刑克主人，主官非",
        evidence_grade=1,
    ),
    "ZHZ-CMB-008": ZhongzhouEvidence(
        rule_id="R-DEF-02",
        combo_id="ZHZ-CMB-008",
        source="谈星1107",
        source_location="王亭之谈星系列 / 1107 篇",
        original_text="紫微在子午 / 辰戌 / 丑未 / 寅申，三方无左辅右弼者，为孤君",
        evidence_grade=1,
    ),
    "ZHZ-CMB-010": ZhongzhouEvidence(
        rule_id="R-COMBO-10",
        combo_id="ZHZ-CMB-010",
        source="谈星1113",
        source_location="王亭之谈星系列 / 1113 篇",
        original_text="明珠出海格指太阳/太阴 + 文昌/文曲 + 截空值日不在同宫",
        evidence_grade=1,
    ),
    "ZHZ-CMB-012": ZhongzhouEvidence(
        rule_id="R-JDG-12",
        combo_id="ZHZ-CMB-012",
        source="谈星1109",
        source_location="王亭之谈星系列 / 1109 篇",
        original_text="文曲化忌与杀破贪同宫，主暗损",
        evidence_grade=1,
    ),
    "ZHZ-CMB-016": ZhongzhouEvidence(
        rule_id="R-JDG-22",
        combo_id="ZHZ-CMB-016",
        source="谈星1117",
        source_location="王亭之谈星系列 / 1117 篇",
        original_text="七杀在卯/酉 + 武曲同度，主震兑方位凶险",
        evidence_grade=1,
    ),
    "ZHZ-CMB-017": ZhongzhouEvidence(
        rule_id="R-DEF-05",
        combo_id="ZHZ-CMB-017",
        source="谈星1126",
        source_location="王亭之谈星系列 / 1126 篇",
        original_text="禄存必为羊陀所夹",
        evidence_grade=1,
    ),
    "ZHZ-CMB-018": ZhongzhouEvidence(
        rule_id="R-JDG-18",
        combo_id="ZHZ-CMB-018",
        source="谈星1126",
        source_location="王亭之谈星系列 / 1126 篇",
        original_text="禄存 + 天马 同宫，主发财于远地",
        evidence_grade=1,
    ),
}


def get_evidence(combo_id: str) -> ZhongzhouEvidence | None:
    """fail-closed: 未知 combo_id 返回 None。"""
    return EVIDENCE_TABLE.get(combo_id)
