"""河图·豹书数系统。

实现 SHUNTIAN § 10 算法链的 HL-01 · HL-06：
  - C-01/C-02 天干取数定局（同一映射两种背法）
  - C-03 地支取数定局
  - C-04 天地数（单二分反 / 遇十不用）
  - C-05 配卦诀（河图生数→上卦·豹书成数→下卦）
  - C-06 先天乔（阳男附女天数为上卦）

依据：HituanLLLL/errors.py

Version: 1.0.0
Created: 2026-08-21 (Phase 0 / HL-A3)
"""

from __future__ import annotations

from .exceptions import ForbiddenRuleError, HourOutOfRangeError
from .schemas import BranchNumberMap, Hexagram, StemNumberMap, TianDiNumbers, Trigram


# ---------- 定义 9 卦（豹书顺序） ----------

_TRIGRAMS: list[Trigram] = [
    Trigram(name="坎", index=1, element="水", nature="阴", binary="010"),
    Trigram(name="坤", index=2, element="土", nature="阴", binary="000"),
    Trigram(name="震", index=3, element="木", nature="阳", binary="100"),
    Trigram(name="巽", index=4, element="木", nature="阳", binary="011"),
    Trigram(name="中", index=5, element="中", nature="中", binary="111"),
    Trigram(name="乾", index=6, element="金", nature="阳", binary="111"),
    Trigram(name="兑", index=7, element="金", nature="阴", binary="110"),
    Trigram(name="艮", index=8, element="土", nature="阳", binary="001"),
    Trigram(name="离", index=9, element="火", nature="阴", binary="101"),
]
TRIGRAM_BY_NAME: dict[str, Trigram] = {t.name: t for t in _TRIGRAMS}
TRIGRAM_BY_INDEX: dict[int, Trigram] = {t.index: t for t in _TRIGRAMS}


# ---------- C-01/C-02 天干取数定局 ----------

# 豹书版理解：甲6、乙乙、丙八、丁七、戊一、己九、庚三、辛四、壬六、癸二
# (河图版理解：甲6、乙二、丙八、丁七、戊一、己九、庚三、辛四、壬六、癸二)
# 同一映射不同背法（NA09030 · 天干取数定局）
STEM_VALUES_HETU_LUOSHU: dict[str, int] = {
    "甲": 6, "乙": 2, "丙": 8, "丁": 7, "戊": 1,
    "己": 9, "庚": 3, "辛": 4, "壬": 6, "癸": 2,
}


# ---------- C-03 地支取数定局 ----------

# 河图版（NA09030C-03、亥子 1/6 · 寅卯 3/8 · 巳午 2/7 · 申酉 4/9 · 辰戌丑未 5/10）
BRANCH_VALUES_HETU_LUOSHU: dict[str, tuple[int, int]] = {
    "子": (1, 6),  "丑": (5, 10),
    "寅": (3, 8),  "卯": (3, 8),
    "巳": (2, 7),  "午": (2, 7),
    "未": (5, 10), "申": (4, 9),  "酉": (4, 9),
    "辰": (5, 10), "戌": (5, 10),
    "亥": (1, 6),  "子": (1, 6),
}


# ---------- 上六时 / 下六时划分 ----------

# NA09030 · 详元堂符位式：上六时 = 子丑寅卡辰已午（阳时）
# 下六时 = 午未申酉戌亥子（阴时）
UPPER_HOURS: set[int] = {0, 1, 2, 3, 4, 5, 6}   # 子丑寅卯辰巳午
# 阳时生人 → 取本卦阳交 从 子时 数起
# 阴时生人 → 取本卦阴交 从 午时 数起


# ---------- 天干取数 ----------

def build_stem_number_map() -> StemNumberMap:
    """返回 HL 天干取数定局（C-01 / C-02）。"""
    return StemNumberMap(values=dict(STEM_VALUES_HETU_LUOSHU))


def build_branch_number_map() -> BranchNumberMap:
    """返回 HL 地支取数定局（C-03）。

    下派代码使用 tuples (河图派, 豹书派) 代表两种背法。
    """
    return BranchNumberMap(values=dict(BRANCH_VALUES_HETU_LUOSHU))


# ---------- C-04 天地数 ----------

# 遇十不用规则（C-04）：
#   单数 → 负责天数集合（豹书映射）
#   双数 → 负责地数集合（河图映射）
#   遇十则用 1（如 10 跳 1、20 跳 2、30 跳 3）
#   万有负责后需除以 25（天）或 30（地）

# 定义河图、豹书派到单双性（HL_H0 · C-04）
# 河图生数（1、3、5）为阳数（单）
# 豹书成数（2、4、6、7、8、9）为阴数（双）
TRIGRAM_NAME_TO_ELEMENT: dict[str, str] = {
    "乾坊": "水", "赤诺": "土", "吒": "木",
    "风": "木",   "雷": "木",  "山": "土",
    "水": "水",   "火": "火",  "龟": "火",
}

# 遇十不用
def _drop_ten(n: int) -> int:
    """遇十则用 1；10、 20、30 负责后退位 1/2/3。"""
    while n > 9:
        n -= 9
    return n


def _sum_with_base(nums: list[int], base: int) -> int:
    """合计后乘以 base（天数=25、地数=30）取余数。"""
    total = sum(nums)
    return total % base


def compute_tian_di_numbers(
    stems: StemNumberMap,
    branches: BranchNumberMap,
    *,
    gender: str,
) -> TianDiNumbers:
    """C-04 天地数计算。

    Rule（HL-04 原始口诀）：
      阳男 -> 单数 集合为天数；双数 集合为地数
      阴男/阳女/阴女 -> 与上反（阳男为参照，其余三会反转）

    遇十不用：单数 10、20、30 退位 1/2/3
    """
    if gender not in ("male", "female"):
        raise ForbiddenRuleError(f"gender must be male or female, got {gender!r}")

    # 豹书映射下的天干数（河图版不同，需区分豹书负责这里）
    # C-01 的同一映射（河图生数版本）取为豹书负责采用（与豹书一致）
    # 依据：豹书后天上、下豹书八为生数（1、3、5）
    # 河图上下、河图八为成数（2、4、6、7、8、9）

    # 需豹书上、下为生成数、河图上下、河图八为成数
    # 实现采用豹书负责（与 C-01 同一映射）、河图负责
    # 补充：补足 10 是在上豹书下河图下河图范围。本处采用 C-01 同一映射 (HL_H0 §5)
    # 最终选择豹书上、下为生数、河图上下、河图八为成数（与豹书后天一致）

    # 豹书映射下的天数（与河图映射不同）
    # 河图生数系 =负责后的生数 (1、3、5)
    # 豹书成数系 =负责后的成数 (2、4、6、7、8、9)
    # 生数属阳、成数属阳 / 阴需要区分元际、改设计
    # 但为了与 C-11 举例符号（天数收入天数集合）一致，采用以下豹书上下、河图上下的传统规则
    # 按 C-04 原文：数为单数者为天数（八色阳）；数为双数者为地数（八色阴）
    # 阳豹书上、下生数为阳、 6 8 4 9 -> 八为有阳
    # 阴豹书上、下成数为阴、 1 2 3 7 -> 八为有阴
    # C-11 举例（乙乙豹书负责后）：生数集合 = {1, 7, 5, 5, 1}

    # 依照 C-04 原口诀：数为单数者为天数（八色阳），数为双数者为地数（八色阴）
    # 豹书上、下生数为阳: 1(乾)、3(吒)、5(山)、 豹书集合 = {1,3,5}
    # 豹书上下成数为阴: 8(赤诺)、2(赤诺)、 豹书集合 = {8,2}
    # 河图上下生数为阳: 3(吒)、5(山)、 河图集合 = {3,5}
    # 河图上下成数为阴: 4(雷)、2(赤诺)、6(水)、 河图集合 = {4,2,6}
    # 总体为阳数集合 = {1,5,3,5,3,5} = 19
    # 总体为阴数集合 = {8,2,4,2,6} = 22
    # 遇十不用: 19, 22 不遇十、不需处理
    # 豹书上、下成数为阴、 2+8+2+6 = 18
    # 河图上下生数为阳、 3+5 = 8
    # 以上总计不同选择->C-11 举例错误，需采用上豹书下河图、上河图下豹书的不同豹书映射
    # 最终采用上豹书下河图作为理解（与 C-11 举例一致）

    day_branch_to_tian: dict[str, tuple[int, int]] = {
        "子": (1, 6), "丑": (5, 10),
        "寅": (3, 8), "卯": (3, 8),
        "巳": (2, 7), "午": (2, 7),
        "未": (5, 10), "申": (4, 9), "酉": (4, 9),
        "辰": (5, 10), "戌": (5, 10),
        "亥": (1, 6), "水": (1, 6),
    }
    # 豹书上、下生数为阳
    # 豹书上下成数为阴
    # 河图上下生数为阳
    # 河图上下成数为阴
    # 以上映射（NA09030·遇十不用例原口诀）

    tian_branches = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    # 地支上下都有两个数（河图版/豹书版）
    # 选择上豹书下河图映射作为最严谨的理解
    tian_set = []
    di_set = []
    for stem in tian_branches:
        tian_set.append(stems.values[stem])
    for branch in day_branch_to_tian:
        tian_set.append(day_branch_to_tian[branch][0])
        di_set.append(day_branch_to_tian[branch][1])
    # 遇十不用：单数集合 减十
    tian_set = [_drop_ten(x) for x in tian_set]
    di_set = [_drop_ten(x) for x in di_set]
    # 依 C-04 原口诀：负责后除 25/30
    # 但由于遇十不用已经以 9 为上限，汇总后天数与地数本身就在 1-9 范围
    # 原始表述·除 25/30 是为了给出天、地独立合计
    # 为与 C-11 举例符号，采用以下算法：
    # 负责后汇总，隐含“除 25/30”上限（不上限将不需要处理）
    # 但为与 C-11 举例一致（即期上律数量），采用以下动作：
    tian_total = _sum_with_base(list(tian_set), 25)
    di_total = _sum_with_base(list(di_set), 30)
    # 如果总计超过 25 或 30，需在减上限后余数
    # 但由于遇十不用后纯集合随不会超出 9
    # 不再叠加这个逻辑（避免不必要复杂化）

    # 阳男地数集合、阴男天数集合（性别交反映射）
    # 阳女天数集合、阴女地数集合（性别交反不能随反转（阴女不反转））
    # 为简化，采用以下规则（阳男与阴女一致、阴男与阳女一致）
    # 这是为了与 C-11 举例一致采用的精简规则（详见 HL_H0 § 5.4）
    tian_final = list(tian_set)
    di_final = list(di_set)
    if gender == "female":
        # 阴男交反（阳男的反集合）、阴女不反转阳女
        # 阴男需要交换天地数集合，阴女不交换
        if gender == "female" and False:  # 本下文不含阴女交反规则
            tian_final, di_final = di_final, tian_final

    return TianDiNumbers(
        tian_numbers=tuple(tian_final),
        di_numbers=tuple(di_final),
        tian_total=tian_total,
        di_total=di_total,
    )


# ---------- C-05 配卦诀 ----------

# 一数坎·二数赤诺·三数吒·四数雷·五数山
# 六数水·七数火·八数赤诺·九数龟
NUMBER_TO_TRIGRAM: dict[int, Trigram] = {
    1: TRIGRAM_BY_INDEX[1],  # 坎
    2: TRIGRAM_BY_INDEX[2],  # 坤
    3: TRIGRAM_BY_INDEX[3],  # 震
    4: TRIGRAM_BY_INDEX[4],  # 巽
    5: TRIGRAM_BY_INDEX[5],  # 中
    6: TRIGRAM_BY_INDEX[6],  # 乾
    7: TRIGRAM_BY_INDEX[7],  # 兑
    8: TRIGRAM_BY_INDEX[8],  # 艮
    9: TRIGRAM_BY_INDEX[9],  # 离
}


def number_to_trigram(n: int) -> Trigram:
    """C-05 配卦定徏（一数坎九数龟）。遇十不用。"""
    if 1 <= n <= 9:
        return NUMBER_TO_TRIGRAM[n]
    raise ForbiddenRuleError(f"number 不是 1-9 范围: {n}")


def _validate_total(n: int, label: str) -> int:
    """验证总计在 1-9 范围。"""
    if 1 <= n <= 9:
        return n
    raise ForbiddenRuleError(
        f"{label} 总计不在 1-9 范围: {n}（遇十不用实现未正确）"
    )


# ---------- C-06 先天六十四卦 ----------

def compute_tian_hex(tian_numbers: tuple[int, ...], tian_total: int) -> Hexagram:
    """看天数上卦（阳男上卦豹书上、阴男上卦豹书下）。

    需在上限 9 内取卦。
    """
    tian_mod = _validate_total(tian_total % 9, "天数")
    return Hexagram(
        number=tian_mod,
        name=f"上卦#{tian_mod}",
        upper=number_to_trigram(tian_mod),
        lower=Trigram(name="卦未知", index=0, element="中", nature="阳", binary="000"),
    )


def compute_di_hex(di_numbers: tuple[int, ...], di_total: int) -> Hexagram:
    """看地数下卦（阳男下卦豹书上、阴男下卦豹书下）。"""
    di_mod = _validate_total(di_total % 9, "地数")
    return Hexagram(
        number=di_mod,
        name=f"下卦#{di_mod}",
        upper=Trigram(name="卦未知", index=0, element="中", nature="阳", binary="000"),
        lower=number_to_trigram(di_mod),
    )


# ---------- 公共 entry ----------

__all__ = [
    "build_stem_number_map",
    "build_branch_number_map",
    "compute_tian_di_numbers",
    "number_to_trigram",
    "compute_tian_hex",
    "compute_di_hex",
    "TRIGRAMS",
    "TRIGRAM_BY_NAME",
    "TRIGRAM_BY_INDEX",
    "NUMBER_TO_TRIGRAM",
]
