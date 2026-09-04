"""Bazi (八字) Engine.

Computes the Four Pillars (年月日时) from birth birth and data.
Uses sxtwl for solar-term-aware computation.
Per architecture_decisions_v1.md, output is deterministic for fixed inputs.

P2 (RULES-EXPANSION-001, 2026-08-26): extended BaziChart with 9 fields for
marriage/health断事 (spouse_star / day_branch_clash / peach_blossom /
branch_clash_map / five_element_imbalance ...). Computed deterministically
from the four pillars and gender — no new facts introduced.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Literal

# 10 Heavenly Stems
HEAVENLY_STEMS = ("JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI")

# 12 Earthly Branches
EARTHLY_BRANCHES = (
    "ZI", "CHOU", "YIN", "MAO", "CHEN", "SI", "WU", "WEI", "SHEN", "YOU", "XU", "HAI"
)

# Element of each stem
STEM_ELEMENT = {
    "JIA": "WOOD", "YI": "WOOD",
    "BING": "FIRE", "DING": "FIRE",
    "WU": "EARTH", "JI": "EARTH",
    "GENG": "METAL", "XIN": "METAL",
    "REN": "WATER", "GUI": "WATER",
}

# Yin/Yang of each stem
STEM_POLARITY = {
    "JIA": "YANG", "YI": "YIN",
    "BING": "YANG", "DING": "YIN",
    "WU": "YANG", "JI": "YIN",
    "GENG": "YANG", "XIN": "YIN",
    "REN": "YANG", "GUI": "YIN",
}

# 天干五合配对表 (five stem combinations) — standard 子平 fixed data.
# P0-1.3：只添加配对表（AUTHORIZED），不实现合化判定器（合化条件属于 PARTIAL，待 P0-2/P0-3 后续审计）。
# 甲己合、乙庚合、丙辛合、丁壬合、戊癸合。
# 依据：子平真诠《论十干配合性情》专章论述。
STEM_HE = {
    frozenset({"JIA", "JI"}),
    frozenset({"YI", "GENG"}),
    frozenset({"BING", "XIN"}),
    frozenset({"DING", "REN"}),
    frozenset({"WU", "GUI"}),
}
STEM_HE_evidence_id = "E-DTS-144-001"  # 滴天髓：十干之合，阴阳相配

# 地支六冲表 (six clashes) — standard 子平 fixed data.
BRANCH_CLASH = {
    "ZI": "WU", "WU": "ZI",
    "CHOU": "WEI", "WEI": "CHOU",
    "YIN": "SHEN", "SHEN": "YIN",
    "MAO": "YOU", "YOU": "MAO",
    "CHEN": "XU", "XU": "CHEN",
    "SI": "HAI", "HAI": "SI",
}
BRANCH_CLASH_evidence_id = "E-YHZP-002-001"  # 渊海子平：十二地支相冲

# 地支六害表 (six harms) — standard 子平 fixed data.
BRANCH_HARM = {
    "ZI": "WEI", "WEI": "ZI",
    "CHOU": "WU", "WU": "CHOU",
    "YIN": "SI", "SI": "YIN",
    "MAO": "CHEN", "CHEN": "MAO",
    "SHEN": "HAI", "HAI": "SHEN",
    "YOU": "XU", "XU": "YOU",
}
BRANCH_HARM_evidence_id = "E-YHZP-003-001"  # 渊海子平：十二地支相穿

# 桃花(咸池) — 标准查法以日支查桃花: 寅午戌→卯, 巳酉丑→午, 申子辰→酉, 亥卯未→子.
PEACH_BLOSSOM_BY_DAY = {
    # 寅午戌 → 卯
    "YIN": "MAO", "WU": "MAO", "XU": "MAO",
    # 巳酉丑 → 午
    "SI": "WU", "YOU": "WU", "CHOU": "WU",
    # 申子辰 → 酉
    "SHEN": "YOU", "ZI": "YOU", "CHEN": "YOU",
    # 亥卯未 → 子
    "HAI": "ZI", "MAO": "ZI", "WEI": "ZI",
}
PEACH_BLOSSOM_evidence_id = "E-YHZP-004-001"  # 渊海子平：桃花咸池查法

# 直接日支为桃花(子午卯酉本身)
PEACH_BLOSSOM_DIRECT = {"ZI", "WU", "MAO", "YOU"}

# 地支六合(六组) — 标准子平固定数据, 含化气五行
# 子丑合土, 寅亥合木, 卯戌合火, 辰酉合金, 巳申合水, 午未合土
BRANCH_HE = {
    frozenset({"ZI", "CHOU"}): "EARTH",
    frozenset({"YIN", "HAI"}): "WOOD",
    frozenset({"MAO", "XU"}): "FIRE",
    frozenset({"CHEN", "YOU"}): "METAL",
    frozenset({"SI", "SHEN"}): "WATER",
    frozenset({"WU", "WEI"}): "EARTH",
}
BRANCH_HE_evidence_id = "E-YHZP-005-001"  # 渊海子平：地支六合

# 地支三合局(四组) — 标准子平固定数据
# 申子辰合水, 亥卯未合木, 寅午戌合火, 巳酉丑合金
BRANCH_SANHE = {
    frozenset({"SHEN", "ZI", "CHEN"}): "WATER",
    frozenset({"HAI", "MAO", "WEI"}): "WOOD",
    frozenset({"YIN", "WU", "XU"}): "FIRE",
    frozenset({"SI", "YOU", "CHOU"}): "METAL",
}
BRANCH_SANHE_evidence_id = "E-YHZP-006-001"  # 渊海子平：地支三合

# 地支三会局(四组) — standard 子平 fixed data.
# P0-1.3：三会组成 + 五行属性（AUTHORIZED，基于滴天髓方位五行）。
# 寅卯辰东方木、巳午未南方火、申酉戌西方金、亥子丑北方水。
# 依据：子平真诠"三方为会"；滴天髓 DTS_0079"寅卯辰属东方木位""巳午未南方火位""亥子丑北方水位"。
# 注意：工程上用"五行属性"而非"化气"（"化气"说法待原典确认，P0-1.2.3 PARTIAL）。
BRANCH_SANHUI = {
    frozenset({"YIN", "MAO", "CHEN"}): "WOOD",
    frozenset({"SI", "WU", "WEI"}): "FIRE",
    frozenset({"SHEN", "YOU", "XU"}): "METAL",
    frozenset({"HAI", "ZI", "CHOU"}): "WATER",
}
BRANCH_SANHUI_evidence_id = "E-DTS-145-001"  # 滴天髓：三会局方位五行

# 地支三刑(四组) — 标准子平固定数据
# 寅巳申三刑(无恩之刑), 丑戌未三刑(恃势之刑), 子卯刑(无礼之刑), 辰午酉亥自刑
BRANCH_SANXING = {
    frozenset({"YIN", "SI", "SHEN"}): "无恩之刑",
    frozenset({"CHOU", "XU", "WEI"}): "恃势之刑",
    frozenset({"ZI", "MAO"}): "无礼之刑",
    # 自刑: 辰辰、午午、酉酉、亥亥 (同一地支出现两次以上)
    "self": {"CHEN", "WU", "YOU", "HAI"},
}
BRANCH_SANXING_evidence_id = "E-YHZP-007-001"  # 渊海子平：地支三刑

# 空亡(六甲旬) — 标准子平固定数据
# 每旬10个干支, 空亡是该旬没有出现的两个地支
# 甲子旬空戌亥, 甲戌旬空申酉, 甲申旬空午未, 甲午旬空辰巳, 甲辰旬空寅卯, 甲寅旬空子丑
KONG_WANG_BY_XUN = {
    0: ("XU", "HAI"),   # 甲子旬(序号0-9)
    1: ("SHEN", "YOU"), # 甲戌旬(序号10-19)
    2: ("WU", "WEI"),   # 甲申旬(序号20-29)
    3: ("CHEN", "SI"),  # 甲午旬(序号30-39)
    4: ("YIN", "MAO"),  # 甲辰旬(序号40-49)
    5: ("ZI", "CHOU"),  # 甲寅旬(序号50-59)
}
KONG_WANG_evidence_id = "E-YHZP-008-001"  # 渊海子平：空亡旬表


@dataclass(frozen=True)
class Pillar:
    """One of the four pillars (year/month/day/hour)."""
    heavenly_stem: str
    earthly_branch: str

    @property
    def stem_element(self) -> str:
        return STEM_ELEMENT[self.heavenly_stem]

    @property
    def branch_element(self) -> str:
        b = self.earthly_branch
        if b in ("YIN", "MAO"):
            return "WOOD"
        if b in ("SI", "WU"):
            return "FIRE"
        if b in ("CHEN", "XU", "CHOU", "WEI"):
            return "EARTH"
        if b in ("SHEN", "YOU"):
            return "METAL"
        return "WATER"

    def to_dict(self) -> dict:
        return {
            "heavenly_stem": self.heavenly_stem,
            "earthly_branch": self.earthly_branch,
            "stem_element": self.stem_element,
            "branch_element": self.branch_element,
        }


def pillar_to_chinese(p: Pillar) -> str:
    """Convert Pillar to Chinese format (e.g., '壬戌')."""
    stem_map = {
        "JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
        "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸"
    }
    branch_map = {
        "ZI": "子", "CHOU": "丑", "YIN": "寅", "MAO": "卯", "CHEN": "辰", "SI": "巳",
        "WU": "午", "WEI": "未", "SHEN": "申", "YOU": "酉", "XU": "戌", "HAI": "亥"
    }
    return f"{stem_map.get(p.heavenly_stem, p.heavenly_stem)}{branch_map.get(p.earthly_branch, p.earthly_branch)}"


def _branch_element(b: str) -> str:
    """Element of an earthly branch (extracted from Pillar.branch_element)."""
    if b in ("YIN", "MAO"):
        return "WOOD"
    if b in ("SI", "WU"):
        return "FIRE"
    if b in ("CHEN", "XU", "CHOU", "WEI"):
        return "EARTH"
    if b in ("SHEN", "YOU"):
        return "METAL"
    return "WATER"


@dataclass(frozen=True)
class BaziChart:
    """Complete 八字 chart for one person.

    P2 extension (RULES-EXPANSION-001): added 9 fields for marriage/health
    断事 evaluation. All fields are derived deterministically from the four
    pillars + gender — no new facts introduced.
    """
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar
    day_master: str
    luck_pillars: list  # Decade luck pillars (大运)

    # P4: 起运岁数(传统算法: 顺排=出生日到下一节气天数÷3, 逆排=出生日到上一节气天数÷3)
    start_age: float = 0.0

    # === P2 新增字段（婚姻/健康断事用） ===

    # 性别 (Profile Contract §1.2 必填)
    gender: str = "male"

    # 配偶星强度(男=财星, 女=官星)。{"正财": 0.x, "偏财": 0.x, ...}
    spouse_star: dict = field(default_factory=dict)

    # 配偶星受克状态: 'rob_wealth' / 'guan_sha_mixed' / 'none'
    spouse_star_attack: str = "none"

    # 官杀混杂(仅女命)
    officer_mixed: bool = False

    # 日支被冲(被其他三支冲)
    day_branch_clash: bool = False

    # 日支被害
    day_branch_harm: bool = False

    # 配偶星强度档位: 'strong' / 'weak' / 'rootless'
    spouse_star_strength: str = "weak"

    # 日支是否为桃花(子午卯酉)
    peach_blossom: bool = False

    # 四支冲关系图 (canonical key sorted alphabetically)
    branch_clash_map: dict = field(default_factory=dict)
    # 例: {"ZI-WU": ["ZI", "WU"]}

    # 四支害关系图
    branch_harm_map: dict = field(default_factory=dict)
    # 例: {"ZI-WEI": ["ZI", "WEI"]}

    # P4: 地支六合/三合/三刑关系图
    branch_he_map: dict = field(default_factory=dict)
    # 例: {"ZI-CHOU": ["ZI", "CHOU", "EARTH"]}
    branch_sanhe_map: dict = field(default_factory=dict)
    # 例: {"SHEN-ZI-CHEN": ["SHEN", "ZI", "CHEN", "WATER"]}
    branch_sanxing_map: dict = field(default_factory=dict)
    # 例: {"YIN-SI-SHEN": ["YIN", "SI", "SHEN", "无恩之刑"]}

    # P4: 空亡(根据日柱旬)
    kong_wang: tuple = field(default_factory=tuple)
    # 例: ("XU", "HAI")

    # 五行分布(归一化) + 失衡标记
    five_element_balance: dict = field(default_factory=dict)
    # 例: {"WOOD": 0.2, "FIRE": 0.2, "EARTH": 0.2, "METAL": 0.2, "WATER": 0.2}
    five_element_imbalance: bool = False

    # 日支主气藏干对日主的十神 (通根/得地判据, P3 addition)
    day_branch_main_ten_god: str = ""

    def to_dict(self) -> dict:
        return {
            "year_pillar": self.year_pillar.to_dict(),
            "month_pillar": self.month_pillar.to_dict(),
            "day_pillar": self.day_pillar.to_dict(),
            "hour_pillar": self.hour_pillar.to_dict(),
            "day_master": self.day_master,
            "day_master_element": STEM_ELEMENT[self.day_master],
            "gender": self.gender,
            "start_age": self.start_age,
            "luck_pillars": [p.to_dict() for p in self.luck_pillars],
            "spouse_star": dict(self.spouse_star),
            "spouse_star_attack": self.spouse_star_attack,
            "officer_mixed": self.officer_mixed,
            "day_branch_clash": self.day_branch_clash,
            "day_branch_harm": self.day_branch_harm,
            "spouse_star_strength": self.spouse_star_strength,
            "peach_blossom": self.peach_blossom,
            "branch_clash_map": {k: list(v) for k, v in self.branch_clash_map.items()},
            "branch_harm_map": {k: list(v) for k, v in self.branch_harm_map.items()},
            "branch_he_map": {k: list(v) for k, v in self.branch_he_map.items()},
            "branch_sanhe_map": {k: list(v) for k, v in self.branch_sanhe_map.items()},
            "branch_sanxing_map": {k: list(v) for k, v in self.branch_sanxing_map.items()},
            "kong_wang": list(self.kong_wang),
            "five_element_balance": dict(self.five_element_balance),
            "five_element_imbalance": self.five_element_imbalance,
            "day_branch_main_ten_god": self.day_branch_main_ten_god,
        }

    def get_pillars_chinese(self) -> dict:
        """Return pillars in Chinese format for external comparison."""
        return {
            "year": pillar_to_chinese(self.year_pillar),
            "month": pillar_to_chinese(self.month_pillar),
            "day": pillar_to_chinese(self.day_pillar),
            "hour": pillar_to_chinese(self.hour_pillar),
        }

    def four_branches(self) -> list[str]:
        """Return four earthly branches (year/month/day/hour)."""
        return [
            self.year_pillar.earthly_branch,
            self.month_pillar.earthly_branch,
            self.day_pillar.earthly_branch,
            self.hour_pillar.earthly_branch,
        ]

    def four_stems(self) -> list[str]:
        """Return four heavenly stems (year/month/day/hour)."""
        return [
            self.year_pillar.heavenly_stem,
            self.month_pillar.heavenly_stem,
            self.day_pillar.heavenly_stem,
            self.hour_pillar.heavenly_stem,
        ]


# --------------------------------------------------------------------------- #
# P2 新增字段计算函数
# --------------------------------------------------------------------------- #

def _ten_god(day_master: str, other: str) -> str:
    """十神(local copy, used by chart builders; canonical in bazi_ten_gods).

    Evidence: E-ZQ-051-001 (子平真诠·论阴阳生克 - 五行生克基础)
              E-ZQ-052-001 (子平真诠·论用神 - 十神命名体系)
    """
    dm_el = STEM_ELEMENT[day_master]
    ot_el = STEM_ELEMENT[other]
    same = (STEM_POLARITY[day_master] == STEM_POLARITY[other])
    if ot_el == dm_el:
        return "比肩" if same else "劫财"
    if _GENERATES.get(dm_el) == ot_el:
        return "食神" if same else "伤官"
    if _GENERATES.get(ot_el) == dm_el:
        return "偏印" if same else "正印"
    if _CONTROLS.get(ot_el) == dm_el:
        return "七杀" if same else "正官"
    if _CONTROLS.get(dm_el) == ot_el:
        return "偏财" if same else "正财"
    raise ValueError(f"cannot determine 十神 for dm={day_master} other={other}")


_ten_god_evidence_id = "E-ZQ-051-001,E-ZQ-052-001"  # 子平真诠：十神算法基础


_GENERATES = {"WOOD": "FIRE", "FIRE": "EARTH", "EARTH": "METAL", "METAL": "WATER", "WATER": "WOOD"}
_CONTROLS = {"WOOD": "EARTH", "EARTH": "WATER", "WATER": "FIRE", "FIRE": "METAL", "METAL": "WOOD"}

# 地支藏干主气 (simplified subset, full table in bazi_ten_gods.BRANCH_HIDDEN_STEMS)
_BRANCH_HIDDEN_MAIN = {
    "ZI": "GUI", "CHOU": "JI", "YIN": "JIA", "MAO": "YI",
    "CHEN": "WU", "SI": "BING", "WU": "DING", "WEI": "JI",
    "SHEN": "GENG", "YOU": "XIN", "XU": "WU", "HAI": "REN",
}


def calc_spouse_star(chart: BaziChart) -> dict:
    """配偶星强度。

    男命: 正财=正妻, 偏财=偏妻, 兼看日主所克之五行在地支的根气.
    女命: 正官=正夫, 七杀=偏夫, 兼看日主所克之五行在地支的根气.
    """
    dm = chart.day_master
    stems = chart.four_stems()
    branches = chart.four_branches()

    if chart.gender == "male":
        zheng_cai = sum(1 for s in stems if _ten_god(dm, s) == "正财")
        pian_cai = sum(1 for s in stems if _ten_god(dm, s) == "偏财")
        # 财星在地支的根(看主气藏干)
        cai_branch = sum(
            1 for b in branches
            if _ten_god(dm, _BRANCH_HIDDEN_MAIN[b]) in ("正财", "偏财")
        )
        return {
            "正财": zheng_cai * 0.5,
            "偏财": pian_cai * 0.5,
            "branch_root": cai_branch * 0.2,
        }
    else:  # female
        zheng_guan = sum(1 for s in stems if _ten_god(dm, s) == "正官")
        qi_sha = sum(1 for s in stems if _ten_god(dm, s) == "七杀")
        guan_branch = sum(
            1 for b in branches
            if _ten_god(dm, _BRANCH_HIDDEN_MAIN[b]) in ("正官", "七杀")
        )
        return {
            "正官": zheng_guan * 0.5,
            "七杀": qi_sha * 0.5,
            "branch_root": guan_branch * 0.2,
        }


def calc_spouse_star_attack(chart: BaziChart) -> str:
    """配偶星受克状态: 'rob_wealth' / 'guan_sha_mixed' / 'none'."""
    if chart.gender == "male":
        stems = chart.four_stems()
        dm = chart.day_master
        has_rob = any(_ten_god(dm, s) in ("比肩", "劫财") for s in stems)
        has_cai = any(_ten_god(dm, s) in ("正财", "偏财") for s in stems)
        if has_rob and has_cai:
            return "rob_wealth"
    elif chart.gender == "female":
        stems = chart.four_stems()
        dm = chart.day_master
        has_guan = any(_ten_god(dm, s) == "正官" for s in stems)
        has_sha = any(_ten_god(dm, s) == "七杀" for s in stems)
        if has_guan and has_sha:
            return "guan_sha_mixed"
    return "none"


def calc_officer_mixed(chart: BaziChart) -> bool:
    """女命官杀混杂 (正官+七杀 同现于天干)."""
    if chart.gender != "female":
        return False
    dm = chart.day_master
    stems = chart.four_stems()
    has_guan = any(_ten_god(dm, s) == "正官" for s in stems)
    has_sha = any(_ten_god(dm, s) == "七杀" for s in stems)
    return has_guan and has_sha


def calc_day_branch_clash(chart: BaziChart) -> bool:
    """日支是否被其他三支冲。

    按位置排除日柱（索引 2），而不是按值過濾——避免日支地支重複時漏判。
    例：四柱 [子, 子, 子, 午]，日支=子，年/月也是子，若按值過濾會把全部子排除，
    正確應只排除日柱位置的子，年/月支的子仍參與判斷。
    """
    day_b = chart.day_pillar.earthly_branch
    branches = chart.four_branches()
    # 年(0)、月(1)、時(3)，排除日(2)的位置
    other = [branches[0], branches[1], branches[3]]
    return any(BRANCH_CLASH[day_b] == b for b in other)


def calc_day_branch_harm(chart: BaziChart) -> bool:
    """日支是否被其他三支害。

    按位置排除日柱（索引 2），而不是按值過濾——見 calc_day_branch_clash。
    """
    day_b = chart.day_pillar.earthly_branch
    branches = chart.four_branches()
    other = [branches[0], branches[1], branches[3]]
    return any(BRANCH_HARM[day_b] == b for b in other)


def calc_spouse_star_strength(chart: BaziChart) -> str:
    """配偶星强度档位: 'strong' / 'weak' / 'rootless'."""
    ss = chart.spouse_star
    if chart.gender == "male":
        score = ss.get("正财", 0) + ss.get("偏财", 0) + ss.get("branch_root", 0)
    else:
        score = ss.get("正官", 0) + ss.get("七杀", 0) + ss.get("branch_root", 0)

    if score >= 1.0:
        return "strong"
    if score >= 0.3:
        return "weak"
    return "rootless"


def calc_peach_blossom(chart: BaziChart) -> bool:
    """日支是否为桃花(子午卯酉)."""
    return chart.day_pillar.earthly_branch in PEACH_BLOSSOM_DIRECT


def calc_branch_clash_map(chart: BaziChart) -> dict:
    """四支冲关系图. canonical key 为 sorted pair joined by '-'."""
    branches = chart.four_branches()
    pairs = []
    seen = set()
    for i, a in enumerate(branches):
        for b in branches[i + 1:]:
            if BRANCH_CLASH.get(a) == b:
                key = "-".join(sorted([a, b]))
                if key not in seen:
                    seen.add(key)
                    pairs.append((key, [a, b]))
    return dict(pairs)


def calc_branch_harm_map(chart: BaziChart) -> dict:
    """四支害关系图."""
    branches = chart.four_branches()
    pairs = []
    seen = set()
    for i, a in enumerate(branches):
        for b in branches[i + 1:]:
            if BRANCH_HARM.get(a) == b:
                key = "-".join(sorted([a, b]))
                if key not in seen:
                    seen.add(key)
                    pairs.append((key, [a, b]))
    return dict(pairs)


def calc_branch_he_map(chart: BaziChart) -> dict:
    """四支六合关系图. 返回 {pair_key: [branch1, branch2, 化气五行]}."""
    branches = chart.four_branches()
    pairs = []
    seen = set()
    for i, a in enumerate(branches):
        for b in branches[i + 1:]:
            key = frozenset({a, b})
            if key in BRANCH_HE:
                pair_key = "-".join(sorted([a, b]))
                if pair_key not in seen:
                    seen.add(pair_key)
                    pairs.append((pair_key, [a, b, BRANCH_HE[key]]))
    return dict(pairs)


def calc_branch_sanhe_map(chart: BaziChart) -> dict:
    """四支三合局关系图. 返回 {triple_key: [branches..., 合化五行]}.
    三合局需要三支齐全才算成局.
    """
    branches = set(chart.four_branches())
    result = {}
    for triple, element in BRANCH_SANHE.items():
        if triple.issubset(branches):
            key = "-".join(sorted(triple))
            result[key] = list(triple) + [element]
    return result


def calc_branch_sanxing_map(chart: BaziChart) -> dict:
    """四支三刑关系图. 返回 {xing_key: [branches..., 刑名]}.
    三刑需要三支齐全(寅巳申/丑戌未)或两支齐全(子卯)才算成刑.
    自刑: 辰午酉亥同一地支出现两次以上.
    """
    branches = chart.four_branches()
    branch_set = set(branches)
    result = {}

    # 三刑(三支齐全)和二刑(子卯)
    for xing, name in BRANCH_SANXING.items():
        if isinstance(xing, frozenset) and xing.issubset(branch_set):
            key = "-".join(sorted(xing))
            result[key] = list(xing) + [name]

    # 自刑: 同一地支出现两次以上
    self_xing = BRANCH_SANXING["self"]
    from collections import Counter
    counts = Counter(branches)
    for b, cnt in counts.items():
        if b in self_xing and cnt >= 2:
            key = f"{b}-{b}"
            result[key] = [b, b, "自刑"]

    return result


def _get_jiazi_index(stem: str, branch: str) -> int:
    """计算日柱在六十甲子中的序号(0-59). 用于空亡计算."""
    stem_idx = HEAVENLY_STEMS.index(stem)
    branch_idx = EARTHLY_BRANCHES.index(branch)
    for i in range(60):
        if i % 10 == stem_idx and i % 12 == branch_idx:
            return i
    return -1


def calc_kong_wang(chart: BaziChart) -> tuple:
    """计算空亡(根据日柱旬). 返回 (空亡地支1, 空亡地支2).
    P0-1.3：空亡作为 Relation Effect Modifier（关系有效性修正），不是 Strength Evidence（强弱证据）。
    原典未找到空亡直接修正五行力量的明确依据（P0-1.2.1 NOT_AUTHORIZED），禁止将空亡等同于力量折减。
    """
    day_stem = chart.day_pillar.heavenly_stem
    day_branch = chart.day_pillar.earthly_branch
    idx = _get_jiazi_index(day_stem, day_branch)
    if idx < 0:
        return (None, None)
    xun = idx // 10  # 0-5
    return KONG_WANG_BY_XUN.get(xun, (None, None))


def calc_five_element_balance(chart: BaziChart):
    """五行分布(归一化) + 失衡标记.

    【⚠️ 降级为辅助信号 · 非经典计算】

    理论基础 (概念层):
      - E-DTS-150-001 (滴天髓·五行生克): 五行生克哲学
      - E-QTBJ-001-001 (穷通宝鉴·五行总论): 旺衰概念

    工程自定义 (算法层 — ENGINEERING_HEURISTIC):
      - 归一化方法: 简单计数比例 v / total
      - 失衡阈值: max > 0.40 or min < 0.05
      - 上述阈值无任何经典出处，是工程约定。

    Authority Status:
      - AUTHORITY_STATUS = NOT_AUTHORIZED
      - CALCULATION_STATUS = ENGINEERING_HEURISTIC
      - ROLE = AUXILIARY_SIGNAL
      - PRODUCTION_ADMITTED = false

    Warning:
      - 此输出仅作为 Signal Layer 参考信号
      - 不得声称为由经典授权的计算结果
      - 不得直接进入 Judgment 判断链
      - 不参与 Calculation Freeze 的权威证明
    """
    counts = {"WOOD": 0, "FIRE": 0, "EARTH": 0, "METAL": 0, "WATER": 0}
    for s in chart.four_stems():
        counts[STEM_ELEMENT[s]] += 1
    for b in chart.four_branches():
        counts[_branch_element(b)] += 1
    total = sum(counts.values()) or 1
    balance = {k: v / total for k, v in counts.items()}
    imbalance = (max(balance.values()) > 0.40) or (min(balance.values()) < 0.05)
    return balance, imbalance


calc_five_element_balance_evidence_id = "E-DTS-150-001,E-QTBJ-001-001"  # 滴天髓+穷通宝鉴：五行理论概念（非算法授权）
calc_five_element_balance_authority_status = "NOT_AUTHORIZED"  # 辅助信号，非经典计算
calc_five_element_balance_role = "AUXILIARY_SIGNAL"


def attach_p2_fields(chart: BaziChart) -> BaziChart:
    """计算并附加 P2 9 字段到 BaziChart (返回新实例, frozen=True 兼容).

    BaziChart 是 frozen=True, 故用 dataclasses.replace 重建.
    """
    from dataclasses import replace

    spouse_star = calc_spouse_star(chart)
    spouse_star_attack = calc_spouse_star_attack(chart)
    officer_mixed = calc_officer_mixed(chart)
    day_branch_clash = calc_day_branch_clash(chart)
    day_branch_harm = calc_day_branch_harm(chart)

    # 计算 strength 需要先有 spouse_star
    chart_with_ss = replace(chart, spouse_star=spouse_star)
    spouse_star_strength = calc_spouse_star_strength(chart_with_ss)

    peach_blossom = calc_peach_blossom(chart)
    branch_clash_map = calc_branch_clash_map(chart)
    branch_harm_map = calc_branch_harm_map(chart)
    # P4: 六合/三合/三刑
    branch_he_map = calc_branch_he_map(chart)
    branch_sanhe_map = calc_branch_sanhe_map(chart)
    branch_sanxing_map = calc_branch_sanxing_map(chart)
    # P4: 空亡
    kong_wang = calc_kong_wang(chart)
    five_element_balance, five_element_imbalance = calc_five_element_balance(chart)
    day_branch_main_ten_god = _ten_god(chart.day_master, _BRANCH_HIDDEN_MAIN.get(chart.day_pillar.earthly_branch, ""))

    return replace(
        chart_with_ss,
        spouse_star_attack=spouse_star_attack,
        officer_mixed=officer_mixed,
        day_branch_clash=day_branch_clash,
        day_branch_harm=day_branch_harm,
        spouse_star_strength=spouse_star_strength,
        peach_blossom=peach_blossom,
        branch_clash_map=branch_clash_map,
        branch_harm_map=branch_harm_map,
        branch_he_map=branch_he_map,
        branch_sanhe_map=branch_sanhe_map,
        branch_sanxing_map=branch_sanxing_map,
        kong_wang=kong_wang,
        five_element_balance=five_element_balance,
        five_element_imbalance=five_element_imbalance,
        day_branch_main_ten_god=day_branch_main_ten_god,
    )


# Hour branch derivation: traditional 时辰 mapping
def hour_branch(hour: int) -> int:
    """Get earthly branch index from solar hour (24h).

    23-1 -> 子 (0), 1-3 -> 丑 (1), ..., 21-23 -> 亥 (11).
    Special case: 23:00 belongs to 子时 of NEXT day, but for our skeleton
    we treat it as 子时 of the same day.
    """
    if hour == 23:
        return 0  # 子时
    return ((hour + 1) // 2) % 12


def hour_stem_from_day_stem(day_stem_idx: int, hour_branch_idx: int) -> int:
    """Get hour pillar stem index using 五鼠遁 formula.

    甲己起甲子(0), 乙庚起丙子(2), 丙辛起戊子(4), 丁壬起庚子(6), 戊癸起壬子(8).
    """
    if day_stem_idx in [0, 5]:  # 甲己
        base = 0
    elif day_stem_idx in [1, 6]:  # 乙庚
        base = 2
    elif day_stem_idx in [2, 7]:  # 丙辛
        base = 4
    elif day_stem_idx in [3, 8]:  # 丁壬
        base = 6
    else:  # 戊癸 (4, 9)
        base = 8

    return (base + hour_branch_idx) % 10


class BaziEngine:
    """Deterministic Bazi computation engine.

    Uses sxtwl for accurate computation when available.

    P2 extension: compute() now attaches 9 marriage/health fields via
    attach_p2_fields(). Backward-compatible — all new fields default to
    inert values when accessed on a manually-constructed chart.
    """

    def __init__(self):
        self._has_sxtwl = False
        try:
            import sxtwl
            self._has_sxtwl = True
        except ImportError:
            self._has_sxtwl = False

    def compute(
        self,
        solar_date: tuple[int, int, int, int],
        gender: Literal["male", "female"] = "male",
        skip_late_zi: bool = False,
    ) -> BaziChart:
        """Compute the Four Pillars and luck pillars from solar date.

        Args:
            solar_date: (year, month, day, hour) in solar calendar.
            gender: 'male' or 'female'. Affects luck-pillar direction (per P1-D).
            skip_late_zi: True时跳过内部夜子时换日逻辑. 用于BaziAdapter等上游
                已完成23:00换日的场景, 避免双重换日. 默认False保持向后兼容.

        Returns:
            BaziChart with all four pillars, day_master, luck_pillars, and
            9 P2 marriage/health fields.
        """
        year, month, day, hour = solar_date

        if self._has_sxtwl:
            four_pillars = self._compute_with_sxtwl(year, month, day, hour)
        else:
            four_pillars = self._compute_simple(year, month, day, hour)

        # P4: 夜子时处理 — 23:00-00:00属于第二天子时, 日柱换为第二天, 时柱天干按新日柱重算
        # V2.6 fix: skip_late_zi=True时跳过, 避免与上游TimeResolver换日逻辑双重换日
        if hour == 23 and not skip_late_zi:
            from datetime import date, timedelta
            next_day = date(year, month, day) + timedelta(days=1)
            if self._has_sxtwl:
                import sxtwl
                day_obj = sxtwl.fromSolar(next_day.year, next_day.month, next_day.day)
                gz_day = day_obj.getDayGZ()
                new_day_stem = HEAVENLY_STEMS[gz_day.tg]
                new_day_branch = EARTHLY_BRANCHES[gz_day.dz]
            else:
                # simple模式: 用第二天重新计算日柱
                ref = date(1900, 1, 1)
                days_diff = (next_day - ref).days
                new_day_stem = HEAVENLY_STEMS[days_diff % 10]
                new_day_branch = EARTHLY_BRANCHES[(10 + days_diff) % 12]
            # 时柱: 子时(ZI), 天干按新日柱五鼠遁重算
            new_day_stem_idx = HEAVENLY_STEMS.index(new_day_stem)
            new_hour_stem_idx = hour_stem_from_day_stem(new_day_stem_idx, 0)  # 0=子时
            four_pillars["day"] = Pillar(new_day_stem, new_day_branch)
            four_pillars["hour"] = Pillar(HEAVENLY_STEMS[new_hour_stem_idx], "ZI")

        # Compute luck pillars (DECISION P1-D) + P4: start_age
        luck_pillars, start_age = self._compute_luck_pillars(four_pillars, gender, year, (year, month, day, hour))

        chart = BaziChart(
            year_pillar=four_pillars["year"],
            month_pillar=four_pillars["month"],
            day_pillar=four_pillars["day"],
            hour_pillar=four_pillars["hour"],
            day_master=four_pillars["day"].heavenly_stem,
            luck_pillars=luck_pillars,
            gender=gender,
            start_age=start_age,
        )

        # P2: attach 9 marriage/health fields (immutable copy)
        chart = attach_p2_fields(chart)

        return chart

    def _compute_with_sxtwl(
        self, year: int, month: int, day: int, hour: int
    ) -> dict:
        """Use sxtwl for accurate computation.

        P2.7-C fix: Properly handle solar term boundaries for month pillar.

        The bug was that sxtwl.getMonthGZ() only accepts date, not hour.
        We need to manually check if birth time is before/after solar term
        and adjust month pillar accordingly.
        """
        import sxtwl

        day_idx = sxtwl.fromSolar(year, month, day)

        gz_year = day_idx.getYearGZ()
        year_p = Pillar(HEAVENLY_STEMS[gz_year.tg], EARTHLY_BRANCHES[gz_year.dz])

        # P2.7-C: 月柱计算需考虑节气边界
        # 策略：比较出生时刻与节气时刻的儒略日数
        gz_month = day_idx.getMonthGZ()
        month_branch = EARTHLY_BRANCHES[gz_month.dz]

        # 检查当天是否有节气
        if day_idx.hasJieQi():
            jieqi_jd = day_idx.getJieQiJD()

            # 计算出生时刻的儒略日数（使用 sxtwl.Time 对象）
            t = sxtwl.Time()
            t.Y, t.M, t.D = year, month, day
            t.h, t.m, t.s = hour, 0, 0.0
            birth_jd = sxtwl.toJD(t)

            # 如果出生时刻在节气之前，使用前一个月的月柱
            if birth_jd < jieqi_jd:
                # 找到前一个地支
                prev_branch_idx = (EARTHLY_BRANCHES.index(month_branch) - 1) % 12
                prev_month_branch = EARTHLY_BRANCHES[prev_branch_idx]

                # 计算月干（根据年干和月支）
                year_stem_idx = gz_year.tg
                year_stem_5 = year_stem_idx % 5
                month_starts = (2, 4, 6, 8, 0)
                month_stem_idx = (month_starts[year_stem_5] + (EARTHLY_BRANCHES.index(prev_month_branch) - 2)) % 10
                prev_month_stem = HEAVENLY_STEMS[month_stem_idx]

                month_p = Pillar(prev_month_stem, prev_month_branch)
            else:
                # 节气之后，使用当前月柱
                month_stem = HEAVENLY_STEMS[gz_month.tg]
                month_p = Pillar(month_stem, month_branch)
        else:
            # 无节气，直接使用当前月柱
            month_stem = HEAVENLY_STEMS[gz_month.tg]
            month_p = Pillar(month_stem, month_branch)

        gz_day = day_idx.getDayGZ()
        day_p = Pillar(HEAVENLY_STEMS[gz_day.tg], EARTHLY_BRANCHES[gz_day.dz])

        hour_gz = day_idx.getHourGZ(hour, True)
        hour_p = Pillar(HEAVENLY_STEMS[hour_gz.tg], EARTHLY_BRANCHES[hour_gz.dz])

        return {"year": year_p, "month": month_p, "day": day_p, "hour": hour_p}

    def _compute_simple(
        self, year: int, month: int, day: int, hour: int
    ) -> dict:
        """Fallback that also uses sxtwl when available.

        Kept for graceful degradation if sxtwl fails to import.
        """
        try:
            import sxtwl
            return self._compute_with_sxtwl(year, month, day, hour)
        except ImportError:
            pass

        year_branch_idx = (year - 4) % 12
        year_stem_idx = (year - 4) % 10
        year_p = Pillar(HEAVENLY_STEMS[year_stem_idx], EARTHLY_BRANCHES[year_branch_idx])

        month_branch_idx = (month + 1) % 12
        year_stem_5 = year_stem_idx % 5
        month_starts = (2, 4, 6, 8, 0)
        month_stem_idx = (month_starts[year_stem_5] + (month_branch_idx - 2)) % 10
        month_p = Pillar(HEAVENLY_STEMS[month_stem_idx], EARTHLY_BRANCHES[month_branch_idx])

        from datetime import date
        ref = date(1900, 1, 1)
        cur = date(year, month, day)
        days_diff = (cur - ref).days
        day_stem_idx = days_diff % 10
        day_branch_idx = (10 + days_diff) % 12
        day_p = Pillar(HEAVENLY_STEMS[day_stem_idx], EARTHLY_BRANCHES[day_branch_idx])

        hb = hour_branch(hour)
        hs = hour_stem_from_day_stem(day_stem_idx, hb)
        hour_p = Pillar(HEAVENLY_STEMS[hs], EARTHLY_BRANCHES[hb])

        return {"year": year_p, "month": month_p, "day": day_p, "hour": hour_p}

    def _is_jie(self, day_obj) -> bool:
        """判断某一天是否是"节"(月令交接点, sxtwl中奇数索引为节, 偶数为气).
        节: 小寒(1),立春(3),惊蛰(5),清明(7),立夏(9),芒种(11),小暑(13),立秋(15),白露(17),寒露(19),立冬(21),大雪(23)
        气: 冬至(0),大寒(2),雨水(4),春分(6),谷雨(8),小满(10),夏至(12),大暑(14),处暑(16),秋分(18),霜降(20),小雪(22)
        """
        if not self._has_sxtwl:
            return False
        if day_obj.hasJieQi():
            return day_obj.getJieQi() % 2 == 1  # 奇数索引为节
        return False

    def _calc_start_age(self, year: int, month: int, day: int, hour: int, direction: int) -> float:
        """计算起运岁数（精确到小时）.

        传统算法:
        - 顺排(阳男阴女): 出生时刻到下一个"节"的精确时间差 ÷ 3
        - 逆排(阴男阳女): 出生时刻到上一个"节"的精确时间差 ÷ 3
        3天=1年, 1天=4个月, 1时辰=10天.

        实现: 使用 sxtwl.getJieQiJD() 获取节气精确时刻，
              计算与出生时刻的精确时间差，转换为天数后除以3.

        Args:
            year, month, day, hour: 出生时间（北京时间）
            direction: +1 顺排，-1 逆排

        Returns:
            起运年龄（岁），float 类型
        """
        if not self._has_sxtwl:
            return 0.0

        import sxtwl
        from datetime import datetime, timedelta
        from .time.jd_converter import jd_to_datetime

        birth_dt = datetime(year, month, day, hour, 0, 0)

        # 遍历出生日前后最多32天，找到最近的"节"
        nearest_jieqi_dt = None
        days_diff = 0

        for i in range(1, 33):
            if direction == +1:
                test_dt = birth_dt + timedelta(days=i)
            else:
                test_dt = birth_dt - timedelta(days=i)

            day_obj = sxtwl.fromSolar(test_dt.year, test_dt.month, test_dt.day)
            if day_obj.hasJieQi():
                jieqi_jd = day_obj.getJieQiJD()
                nearest_jieqi_dt = jd_to_datetime(jieqi_jd)
                days_diff = i
                break

        if nearest_jieqi_dt is None:
            return 0.0

        # 计算精确时间差（小时）
        delta = nearest_jieqi_dt - birth_dt
        delta_days = delta.total_seconds() / 86400.0

        # 3天=1岁
        start_age = abs(delta_days) / 3.0

        return start_age

    def _compute_luck_pillars(
        self, four_pillars: dict, gender: str, birth_year: int, birth_date: tuple
    ) -> tuple:
        """Compute 10 luck pillars (大运) and start age.

        P4 fix: 大运顺逆根据年干阴阳+性别判断(原代码错误地用了月干).
        P4 add: 计算起运岁数(顺排=出生日到下一节日数÷3, 逆排=出生日到上一节日数÷3).

        Returns:
            (luck_pillars, start_age)
        """
        # P4 fix: 用年干判断阴阳, 不是月干
        year_stem = four_pillars["year"].heavenly_stem
        year_stem_idx = HEAVENLY_STEMS.index(year_stem)
        is_yang_year = (year_stem_idx % 2 == 0)

        if (gender == "male" and is_yang_year) or (gender == "female" and not is_yang_year):
            direction = +1
        else:
            direction = -1

        # P4 add: 计算起运岁数
        year, month, day, hour = birth_date
        start_age = self._calc_start_age(year, month, day, hour, direction)

        # 大运从月柱开始顺/逆排
        month_stem = four_pillars["month"].heavenly_stem
        month_branch = four_pillars["month"].earthly_branch
        start_stem_idx = HEAVENLY_STEMS.index(month_stem)
        start_branch_idx = EARTHLY_BRANCHES.index(month_branch)

        luck_pillars = []
        for decade in range(1, 4):
            new_stem_idx = (start_stem_idx + direction * decade) % 10
            new_branch_idx = (start_branch_idx + direction * decade) % 12
            lp = Pillar(HEAVENLY_STEMS[new_stem_idx], EARTHLY_BRANCHES[new_branch_idx])
            luck_pillars.append(lp)

        return luck_pillars, start_age
