"""P5 Guidance Layer - 指引层.

包含:
- guidance_atom: GuidanceAtom数据模型
- mapping: Assertion→Guidance确定性映射
- composer: Guidance Composer(后续P5-B)
- renderer: Renderer(后续P5-C)
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

__all__ = [
    "GuidanceAtom",
    "DIRECTION_LABELS",
    "DIRECTION_DESCRIPTIONS",
    "FORBIDDEN_TERMS",
    "make_guidance_id",
    "validate_guidance_contract",
    "AssertionGuidanceMapper",
    "MAPPING_TEMPLATES",
]
