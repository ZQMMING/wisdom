"""HL Engine - Phase 2 重构（8模块拆分）。

依据：SHUNTIAN §10 架构冻结 + Architecture Freeze V1.0 §2.3
"""

from .canonical import HeluoCanonical, HeluoResult, heluo_calculate
from .exceptions import (
    ForbiddenRuleError,
    HeluoEngineError,
    HourOutOfRangeError,
    YuanTangResolutionError,
)
from .hetu_luoshu import (
    build_branch_number_map,
    build_stem_number_map,
    compute_di_hex,
    compute_tian_di_numbers,
    compute_tian_hex,
    number_to_trigram,
)
from .input import HeluoInput, Location, prepare_heluo_input
from .numbers import get_hexagram_name, compute_tian_di_shu
from .prenatal import PrenatalHexagram, determine_prenatal_hexagram
from .postnatal import PostnatalHexagram, compute_postnatal
from .yuan_tang import YuanTang, find_yuantang, resolve_yuantang
from .hexagram import HexagramStructure, analyze_hexagram, compute_ti_yong
from .temporal import Timeline, compute_timeline
from .schemas import (
    Trigram,
    Hexagram,
    YuanTangResult,
    StemNumberMap,
    BranchNumberMap,
    TianDiNumbers,
)

HeluoBirthInput = HeluoInput

__all__ = [
    "HeluoCanonical",
    "heluo_calculate",
    "HeluoInput",
    "Location",
    "prepare_heluo_input",
    "HeluoBirthInput",
    "HeluoResult",
    "PrenatalHexagram",
    "YuanTang",
    "PostnatalHexagram",
    "Timeline",
    "HexagramStructure",
    "StemNumberMap",
    "BranchNumberMap",
    "TianDiNumbers",
    "Trigram",
    "Hexagram",
    "YuanTangResult",
    "analyze_hexagram",
    "compute_ti_yong",
    "compute_timeline",
    "number_to_trigram",
    "get_hexagram_name",
    "build_stem_number_map",
    "build_branch_number_map",
    "compute_tian_di_numbers",
    "compute_tian_hex",
    "compute_di_hex",
]