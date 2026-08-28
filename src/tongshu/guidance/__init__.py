"""P5 Guidance Layer - 指引层.

包含:
- guidance_atom: GuidanceAtom数据模型
- mapping: Assertion→Guidance确定性映射
- composer: Guidance Composer(组装多个GuidanceAtom为完整指引)
- renderer: Renderer(deterministic/template-first, 只负责语言表达)
"""
from .guidance_atom import (
    GuidanceAtom,
    DIRECTION_LABELS,
    DIRECTION_DESCRIPTIONS,
    FORBIDDEN_TERMS,
    make_guidance_id,
    validate_guidance_contract,
)
from .mapping import AssertionGuidanceMapper, MAPPING_TEMPLATES
from .composer import GuidanceComposer, ComposedGuidance, DomainGuidance
from .renderer import GuidanceRenderer

__all__ = [
    "GuidanceAtom",
    "DIRECTION_LABELS",
    "DIRECTION_DESCRIPTIONS",
    "FORBIDDEN_TERMS",
    "make_guidance_id",
    "validate_guidance_contract",
    "AssertionGuidanceMapper",
    "MAPPING_TEMPLATES",
    "GuidanceComposer",
    "ComposedGuidance",
    "DomainGuidance",
    "GuidanceRenderer",
]
