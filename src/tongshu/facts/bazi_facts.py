"""tongshu.facts.bazi_facts — 八字基础事实表 (P0-FNDR-03)

设计原则:
- 本模块是「事实层」(facts layer), 无任何上层业务依赖
- 不 import tongshu.engines, tongshu.reasoning, tongshu.canonical 等
- 只定义原子事实常量 (天干→五行、天干→阴阳、地支→五行、五行生克、地支藏干)
- 上层模块 (bazi_ten_gods, bazi_engine, zi_ping_* 等) 均从此处导入事实

依赖方向 (User 第七轮审计要求):
  facts (本模块)
    ↓
  reasoning.bazi_ten_gods (canonical 十神引擎)
    ↓
  engines.bazi_engine (八字计算)

禁止反向依赖: bazi_engine / bazi_ten_gods 不得被本模块 import。

Evidence Sources:
- 《渊海子平·论五行所属》(E-YHZP-001~012) — 天干/地支五行
- 《子平真诠·论阴阳生克》(E-ZQ-051-001) — 五行生克
- 《子平真诠·论用神》(E-ZQ-052-001) — 十神命名（事实层只提供映射, 命名由 bazi_ten_gods 负责）
- 《渊海子平·论地支藏干》(E-YHZP-013~024) — 地支藏干主气/中气/余气
"""

from __future__ import annotations

# ============================================================================
# 天干基础事实
# ============================================================================

# 10 Heavenly Stems (天干)
HEAVENLY_STEMS = (
    "JIA", "YI", "BING", "DING", "WU", "JI", "GENG", "XIN", "REN", "GUI",
)

# 12 Earthly Branches (地支)
EARTHLY_BRANCHES = (
    "ZI", "CHOU", "YIN", "MAO", "CHEN", "SI",
    "WU", "WEI", "SHEN", "YOU", "XU", "HAI",
)

# Element of each stem (天干五行映射)
STEM_ELEMENT = {
    "JIA": "WOOD", "YI": "WOOD",
    "BING": "FIRE", "DING": "FIRE",
    "WU": "EARTH", "JI": "EARTH",
    "GENG": "METAL", "XIN": "METAL",
    "REN": "WATER", "GUI": "WATER",
}

# Yin/Yang of each stem (天干阴阳)
STEM_POLARITY = {
    "JIA": "YANG", "YI": "YIN",
    "BING": "YANG", "DING": "YIN",
    "WU": "YANG", "JI": "YIN",
    "GENG": "YANG", "XIN": "YIN",
    "REN": "YANG", "GUI": "YIN",
}


# ============================================================================
# 地支基础事实
# ============================================================================

# Element of each branch (地支五行映射)
BRANCH_ELEMENT = {
    # WATER 子亥
    "ZI":   "WATER",
    "HAI":  "WATER",
    # WOOD 寅卯
    "YIN":  "WOOD",
    "MAO":  "WOOD",
    # FIRE 巳午
    "SI":   "FIRE",
    "WU":   "FIRE",
    # METAL 申酉
    "SHEN": "METAL",
    "YOU":  "METAL",
    # EARTH 辰戌丑未 (四季土)
    "CHEN": "EARTH",
    "XU":   "EARTH",
    "CHOU": "EARTH",
    "WEI":  "EARTH",
}

# 地支藏干 (主气 first). Standard table.
# Each branch maps to ordered list of (stem, role) tuples.
# role ∈ {"main" (本气), "middle" (中气), "residual" (余气)}
BRANCH_HIDDEN_STEMS = {
    "ZI":   [("GUI", "main")],
    "CHOU": [("JI", "main"), ("GUI", "middle"), ("XIN", "residual")],
    "YIN":  [("JIA", "main"), ("BING", "middle"), ("WU", "residual")],
    "MAO":  [("YI", "main")],
    "CHEN": [("WU", "main"), ("YI", "middle"), ("GUI", "residual")],
    "SI":   [("BING", "main"), ("WU", "middle"), ("GENG", "residual")],
    "WU":   [("DING", "main"), ("JI", "middle")],
    "WEI":  [("JI", "main"), ("DING", "middle"), ("YI", "residual")],
    "SHEN": [("GENG", "main"), ("REN", "middle"), ("WU", "residual")],
    "YOU":  [("XIN", "main")],
    "XU":   [("WU", "main"), ("XIN", "middle"), ("DING", "residual")],
    "HAI":  [("REN", "main"), ("JIA", "middle")],
}

# Season by month-branch (季节 by 月支)
SEASON_BY_BRANCH = {
    "YIN": "SPRING", "MAO": "SPRING", "CHEN": "SPRING",
    "SI": "SUMMER", "WU": "SUMMER", "WEI": "SUMMER",
    "SHEN": "AUTUMN", "YOU": "AUTUMN", "XU": "AUTUMN",
    "HAI": "WINTER", "ZI": "WINTER", "CHOU": "WINTER",
}

# 杂气月 (辰戌丑未) — 《论杂气如何取用》专题处理
ZAGI_BRANCHES = {"CHEN", "XU", "CHOU", "WEI"}


# ============================================================================
# 五行关系事实
# ============================================================================

# 五行相生链 (X 生 GENERATES[X])
GENERATES = {
    "WOOD": "FIRE",
    "FIRE": "EARTH",
    "EARTH": "METAL",
    "METAL": "WATER",
    "WATER": "WOOD",
}

# 五行相克链 (X 克 CONTROLS[X])
CONTROLS = {
    "WOOD": "EARTH",
    "EARTH": "WATER",
    "WATER": "FIRE",
    "FIRE": "METAL",
    "METAL": "WOOD",
}


# ============================================================================
# Evidence Metadata
# ============================================================================

EVIDENCE_IDS = {
    "STEM_ELEMENT": "E-YHZP-001~010",          # 渊海子平·论天干五行所属
    "STEM_POLARITY": "E-YHZP-001~010",          # 渊海子平·论天干阴阳
    "BRANCH_ELEMENT": "E-YHZP-001~012",         # 渊海子平·论地支五行所属
    "BRANCH_HIDDEN_STEMS": "E-YHZP-013~024",    # 渊海子平·论地支藏干
    "GENERATES": "E-ZQ-051-001",                # 子平真诠·论阴阳生克
    "CONTROLS": "E-ZQ-051-001",                 # 子平真诠·论阴阳生克
    "SEASON_BY_BRANCH": "E-YHZP-025~028",       # 渊海子平·论四时月令
}


__all__ = [
    "HEAVENLY_STEMS",
    "EARTHLY_BRANCHES",
    "STEM_ELEMENT",
    "STEM_POLARITY",
    "BRANCH_ELEMENT",
    "BRANCH_HIDDEN_STEMS",
    "SEASON_BY_BRANCH",
    "ZAGI_BRANCHES",
    "GENERATES",
    "CONTROLS",
    "EVIDENCE_IDS",
]
