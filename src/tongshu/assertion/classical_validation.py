# -*- coding: utf-8 -*-
"""古籍引用交叉验证模块 (Classical Citation Cross-Validation).

核心理念(借鉴 chinese-fortune 八字解读纪律):
- 凡古籍无据者不妄断
- 断言必须有古籍依据支撑, 无据则置信度下调

功能:
1. validate_assertion_refs: 校验单个断言的classical_refs是否非空/有据
2. cross_validate_systems: 对多体系断言做古籍交叉验证, 判定"有据可查"程度
3. 无古籍依据的断言 → 置信度降级提示
"""
from __future__ import annotations

from dataclasses import dataclass

from tongshu.assertion.contract import Assertion, Confidence
from tongshu.assertion.classical_citations import CLASSICS


@dataclass
class CitationValidationResult:
    """古籍引用验证结果."""
    system: str
    has_refs: bool                 # 是否有古籍引用
    ref_count: int                 # 引用数量
    cited_classics: list[str]      # 引用的古籍
    all_valid: bool                # 引用是否均为有效古籍
    validity_score: float          # 有效性评分(0.0-1.0)


# 古籍识别关键词: 显示名 → 匹配关键词(用书名主体, 兼容"《滴天髓·篇》"带篇名格式)
# 覆盖: 五大子平古籍 + 紫微/盲派/河洛/易经来源
BOOK_KEYWORDS = {
    "《子平真诠》": ["子平真诠"],
    "《滴天髓》": ["滴天髓"],
    "《穷通宝鉴》": ["穷通宝鉴"],
    "《三命通会》": ["三命通会"],
    "《渊海子平》": ["渊海子平"],
    "《河洛理数》": ["河洛理数"],
    "《周易》": ["周易", "卦辞", "爻辞", "象传", "彖传", "文言传"],
    "《紫微斗数全书》": ["紫微斗数全书"],
    "倪海厦《天纪》": ["天纪"],
    "盲派口诀": ["盲派"],
}


def _cited_classics(refs: tuple) -> list[str]:
    """从古籍引用文本中提取引用的古籍名(用书名主体关键词匹配)."""
    cited = []
    for ref in refs:
        for display, keywords in BOOK_KEYWORDS.items():
            if any(kw in ref for kw in keywords):
                cited.append(display)
                break
    return cited


def validate_assertion_refs(assertion: Assertion) -> CitationValidationResult:
    """校验单个断言的古籍引用.

    Args:
        assertion: 断言对象

    Returns:
        CitationValidationResult 验证结果.
    """
    refs = assertion.classical_refs or ()
    has_refs = len(refs) > 0
    cited = _cited_classics(refs)
    all_valid = len(cited) == len(refs) if refs else False

    # 有效性评分: 有引用且全部有效=1.0; 有引用部分有效=0.5; 无引用=0
    if not refs:
        validity = 0.0
    elif all_valid:
        validity = 1.0
    else:
        validity = 0.5

    return CitationValidationResult(
        system=assertion.subject,
        has_refs=has_refs,
        ref_count=len(refs),
        cited_classics=cited,
        all_valid=all_valid,
        validity_score=validity,
    )


def cross_validate_systems(assertions: list[Assertion]) -> dict:
    """对多体系断言做古籍交叉验证.

    统计:
    - 每个体系的古籍引用情况
    - 覆盖的古籍种类(越多体系有据→交叉验证越强)
    - 无据体系的警告列表

    Returns:
        {
            "per_system": [CitationValidationResult],
            "cited_classics": [...],       # 所有被引用的古籍
            "systems_with_refs": int,
            "systems_total": int,
            "ref_coverage": float,          # 引用覆盖率(0.0-1.0)
            "unreferenced_systems": [...],  # 无古籍引用的体系
            "verdict": str,                 # 综合判定
        }
    """
    results = []
    cited_all = set()
    systems_with_refs = 0
    unreferenced = []

    for a in assertions:
        r = validate_assertion_refs(a)
        results.append(r)
        cited_all.update(r.cited_classics)
        if r.has_refs:
            systems_with_refs += 1
        else:
            unreferenced.append(a.subject)

    total = len(assertions)
    coverage = systems_with_refs / total if total > 0 else 0.0

    if total == 0:
        verdict = "no systems"
    elif coverage == 1.0:
        verdict = "所有体系均有古籍依据, 交叉验证充分"
    elif coverage >= 0.5:
        verdict = f"部分体系({systems_with_refs}/{total})有古籍依据, 建议补全无据体系"
    else:
        verdict = f"多数体系({systems_with_refs}/{total})缺乏古籍依据, 断言可信度受限"

    return {
        "per_system": results,
        "cited_classics": sorted(cited_all),
        "systems_with_refs": systems_with_refs,
        "systems_total": total,
        "ref_coverage": round(coverage, 3),
        "unreferenced_systems": unreferenced,
        "verdict": verdict,
    }


def adjust_confidence_for_refs(assertion: Assertion) -> Assertion:
    """根据古籍引用调整置信度.

    规则:
    - 有古籍依据且断言非拒断 → 置信度可提升/保持
    - 无古籍依据 → 若当前为LIKELY, 提示降级风险(不强制改, 返回原对象)
    - 返回(原断言, 是否有据)
    """
    r = validate_assertion_refs(assertion)
    return assertion, r.has_refs


__all__ = [
    "CitationValidationResult",
    "validate_assertion_refs",
    "cross_validate_systems",
    "adjust_confidence_for_refs",
]
