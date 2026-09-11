# -*- coding: utf-8 -*-
"""盲派八字引擎 — MangPai Bazi Engine (增强版 · 做功引擎)

基于段建业/杨清贫盲派方法论 + bonesyear/MangPai-Destiny 参考实现。
只实现确定性算法，不使用 LLM。

盲派核心概念（2026-08-27 互联网/典籍校对）：
- 宾主：日柱为「主」（我），其余为「宾」（外界）
- 体用：体（本钱）= 比肩/劫财/印/食神/伤官/禄；用（目标）= 财/官杀
- 做功：用「体」去取「用」，靠 合/冲/克/制/化/墓 等关系实现
- 五种做功：制用 / 化用 / 生用 / 合用 / 墓用
"""
from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from ..engines.bazi_engine import BaziEngine, BaziChart, STEM_ELEMENT, _branch_element, canonical_bazi_engine
from ..signal.canonical_signal import CanonicalSignal, SourceEngine, SignalLayer, SignalTemporalScope
from ..signal.adapters import BaseAdapter, AdapterContext
from ..spec.event_ontology_v1 import Domain, EventDirection
from ..reasoning.bazi_ten_gods import ten_god, BRANCH_HIDDEN_STEMS, GENERATES, CONTROLS
from ..reasoning.bazi_fixed_tables import road_branch, absolute_branch


# ─── 盲派核心常量 ─────────────────────────────────────────────────────────────

# 地支六合
BRANCH_LIUHE = {
    'ZI': 'CHOU', 'CHOU': 'ZI',
    'YIN': 'HAI', 'HAI': 'YIN',
    'MAO': 'XU', 'XU': 'MAO',
    'CHEN': 'YOU', 'YOU': 'CHEN',
    'SI': 'SHEN', 'SHEN': 'SI',
    'WU': 'WEI', 'WEI': 'WU',
}

# 地支三合
BRANCH_SANHE = {
    'SHEN-ZI-CHEN': {'SHEN', 'ZI', 'CHEN'},  # 水局
    'HAI-MAO-WEI': {'HAI', 'MAO', 'WEI'},    # 木局 (fix: 原SHEN-MAO-WEI错误)
    'YIN-WU-XU': {'YIN', 'WU', 'XU'},       # 火局
    'SI-YOU-CHOU': {'SI', 'YOU', 'CHOU'},   # 金局
}

# 地支六冲（盲派体用失衡判据：体支被冲 = 体受伤）
BRANCH_CHONG = {
    'ZI': 'WU', 'WU': 'ZI',
    'CHOU': 'WEI', 'WEI': 'CHOU',
    'YIN': 'SHEN', 'SHEN': 'YIN',
    'MAO': 'YOU', 'YOU': 'MAO',
    'CHEN': 'XU', 'XU': 'CHEN',
    'SI': 'HAI', 'HAI': 'SI',
}

# 地支六害(六穿) — V2.4: 盲派核心技法, 穿比冲更狠(背后偷袭、排斥破坏)
# 子未穿/丑午穿/寅巳穿/卯辰穿/申亥穿/酉戌穿
BRANCH_CHUAN = {
    'ZI': 'WEI', 'WEI': 'ZI',
    'CHOU': 'WU', 'WU': 'CHOU',
    'YIN': 'SI', 'SI': 'YIN',
    'MAO': 'CHEN', 'CHEN': 'MAO',
    'SHEN': 'HAI', 'HAI': 'SHEN',
    'YOU': 'XU', 'XU': 'YOU',
}

# 墓库 — V2.4: 辰=水墓, 戌=火墓, 丑=金墓, 未=木墓
# 墓库收放: 闭库收物=财富聚拢, 冲库开库=财官出来, 墓喜冲不冲不发
MU_KU = {
    'CHEN': 'WATER',   # 辰=水库(水墓)
    'XU': 'FIRE',      # 戌=火库(火墓)
    'CHOU': 'METAL',   # 丑=金库(金墓)
    'WEI': 'WOOD',     # 未=木库(木墓)
}

# 天干五合（盲派「合功」：日干合财/合官 → 得财/得权）
STEM_HE: Set[Tuple[str, str]] = {
    ('JIA', 'JI'), ('YI', 'GENG'), ('BING', 'XIN'),
    ('DING', 'REN'), ('WU', 'GUI'),
}

# 体用十神分类（段建业盲派）
TI_TEN_GODS = {'比肩', '劫财', '偏印', '正印', '食神', '伤官'}   # 体（本钱）
YONG_TEN_GODS = {'正财', '偏财', '正官', '七杀'}               # 用（目标）

# 财/官/食伤/印/比劫 分组
GROUP_CAI = {'正财', '偏财'}
GROUP_GUAN = {'正官', '七杀'}
GROUP_SHI = {'食神', '伤官'}
GROUP_YIN = {'正印', '偏印'}
GROUP_BI = {'比肩', '劫财'}


# ─── 盲派数据结构 ─────────────────────────────────────────────────────────────

# ── 新规则枚举（V1-FINAL：method_scope / 做功强弱 / 结构外显 / 功神角色）──

class MethodScope(str, enum.Enum):
    """盲派传承隔离（规则 §4/§90）。当前实现段建业主线。"""
    DUAN_JIANYE = "DUAN_JIANYE"
    XIA_ZHONGQI = "XIA_ZHONGQI"
    HAO_JINYANG = "HAO_JINYANG"


class WorkEfficiency(str, enum.Enum):
    """做功强弱四档（WK-EFFICIENCY-001，古籍：大/中/小/无效做功）。"""
    LARGE = "LARGE"          # 大效率
    MEDIUM = "MEDIUM"        # 中效率
    SMALL = "SMALL"          # 小效率
    NONE = "NONE"            # 无效做功
    UNDETERMINED = "UNDETERMINED"


class StructureClarity(str, enum.Enum):
    """结构外显四态（WK-EFFICIENCY-003，古籍：清晰/较清/有杂/混乱）。"""
    CLEAR = "CLEAR"
    PARTIALLY_CLEAR = "PARTIALLY_CLEAR"
    MIXED = "MIXED"
    CHAOTIC = "CHAOTIC"
    UNDETERMINED = "UNDETERMINED"


class GongShenRole(str, enum.Enum):
    """功神/废神角色（规则 GS-001~003 / §77）。"""
    WORKING = "WORKING"        # 功神（实际做功）
    SUPPORTING = "SUPPORTING"  # 辅神（辅助做功）
    TARGET = "TARGET"          # 目标（做功对象）
    BLOCKING = "BLOCKING"      # 阻神（阻断/干扰做功）
    IDLE = "IDLE"              # 闲神（method_scope 定义无作用）
    WASTE = "WASTE"            # 废神（明确规则定义为废）
    UNDETERMINED = "UNDETERMINED"


@dataclass
class BlindBaziResult:
    """盲派八字分析结果"""
    # 宾主判定
    main_branches: Set[str] = field(default_factory=set)
    guest_branches: Set[str] = field(default_factory=set)

    # 体用分析
    ti_branches: Set[str] = field(default_factory=set)
    yong_branches: Set[str] = field(default_factory=set)
    ti_stems: List[str] = field(default_factory=list)      # 体天干
    yong_stems: List[str] = field(default_factory=list)    # 用天干

    # 做功判断
    zuo_gong: bool = False
    zuo_gong_type: str = ""
    zuo_gong_methods: List[str] = field(default_factory=list)   # ['合财','食伤制杀',...]
    zuo_gong_detail: List[str] = field(default_factory=list)

    # 十神配置（透干十神）
    transparent_ten_gods: Dict[str, str] = field(default_factory=dict)  # {柱: 十神}

    # ── 新规则字段（V1-FINAL）──────────────────────────────────
    method_scope: str = MethodScope.DUAN_JIANYE.value      # 传承隔离
    # 做功强弱（WK-EFFICIENCY-001~005）
    work_efficiency: str = WorkEfficiency.UNDETERMINED.value   # 大/中/小/无效
    structure_clarity: str = StructureClarity.UNDETERMINED.value  # 结构外显四态
    eff_path_direct: bool = False        # 三判据① 做功路径是否直接
    eff_power_concentrated: bool = False # 三判据② 做功力量是否集中
    eff_target_effective: bool = False   # 三判据③ 做功对象是否得力
    work_level: str = "UNDETERMINED"     # 做功等级五档（理法-结果层）
    # 功神/废神角色（GS-001~003）
    gong_shen: Dict[str, List[str]] = field(default_factory=dict)  # {角色: [支/干]}
    # 制尽（规则 §37 CONTROL_COMPLETENESS）
    control_completeness: str = "UNDETERMINED"   # COMPLETE / PARTIAL / UNDETERMINED
    # ── 未核证规则域占位（VERIFY-BLIND 门禁）────────────────
    # 规则文档已列规则域但核证未通过（VERIFY-BLIND-015/017/022/023）：
    # 按"核证通过前不施工、不自行发明规则"原则，引擎只输出 UNDETERMINED 占位，
    # 不发明判定逻辑。核证完成并锁定规则后再落地。
    thief_capture: str = "UNDETERMINED"          # 贼神/捕神 §24（VERIFY-BLIND-015）
    ganzhi_transmission: str = "UNDETERMINED"    # 干支互通 §26（VERIFY-BLIND-017）
    image_substitution: str = "UNDETERMINED"     # 换象 §27（VERIFY-BLIND-022）
    kinship_chain: str = "UNDETERMINED"          # 六亲组合链 §30（VERIFY-BLIND-023）
    # 时间层/规则追踪
    undetermined_reasons: List[str] = field(default_factory=list)
    rules_triggered: List[str] = field(default_factory=list)

    # 盲派信号
    signals: List[CanonicalSignal] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'main_branches': list(self.main_branches),
            'guest_branches': list(self.guest_branches),
            'ti_branches': list(self.ti_branches),
            'yong_branches': list(self.yong_branches),
            'ti_stems': self.ti_stems,
            'yong_stems': self.yong_stems,
            'zuo_gong': self.zuo_gong,
            'zuo_gong_type': self.zuo_gong_type,
            'zuo_gong_methods': self.zuo_gong_methods,
            'zuo_gong_detail': self.zuo_gong_detail,
            'transparent_ten_gods': self.transparent_ten_gods,
            'method_scope': self.method_scope,
            'work_efficiency': self.work_efficiency,
            'structure_clarity': self.structure_clarity,
            'eff_path_direct': self.eff_path_direct,
            'eff_power_concentrated': self.eff_power_concentrated,
            'eff_target_effective': self.eff_target_effective,
            'work_level': self.work_level,
            'gong_shen': self.gong_shen,
            'control_completeness': self.control_completeness,
            'thief_capture': self.thief_capture,
            'ganzhi_transmission': self.ganzhi_transmission,
            'image_substitution': self.image_substitution,
            'kinship_chain': self.kinship_chain,
            'rules_triggered': self.rules_triggered,
            'undetermined_reasons': self.undetermined_reasons,
            'signals': [s.to_dict() for s in self.signals],
        }


# ─── 盲派引擎 ─────────────────────────────────────────────────────────────────

class BlindBaziEngine:
    """盲派八字引擎 - 宾主/体用/做功/断事分析"""

    def __init__(self, bazi_engine=None):
        self.bazi_engine = bazi_engine or canonical_bazi_engine

    # ── 主入口 ─────────────────────────────────────────────
    def compute(self, birth: Tuple[int, int, int, int], gender: str = "male") -> BlindBaziResult:
        chart = self.bazi_engine.compute(birth, gender=gender)
        result = BlindBaziResult()
        birth_year = birth[0]

        # 1. 宾主判定（日柱为主，年月为宾，时柱视为主位）
        result.main_branches.add(chart.day_pillar.earthly_branch)
        result.guest_branches.add(chart.year_pillar.earthly_branch)
        result.guest_branches.add(chart.month_pillar.earthly_branch)
        result.guest_branches.add(chart.hour_pillar.earthly_branch)

        # 日主(提前定义, 供体用分析和透干十神使用)
        day_master = chart.day_master

        # 2. 体用分析（V2.6: 遍历所有支含日支藏干, 原逻辑日支只进体不进用导致日支藏财官缺失）
        # 体（本钱）= 比肩/劫财/印/食神/伤官; 用（目标）= 财/官杀
        # 日支为日主之根, 天然属体; 同时按藏干十神分类, 一支可同时属体用
        result.ti_branches.add(chart.day_pillar.earthly_branch)
        all_branches = [
            chart.year_pillar.earthly_branch,
            chart.month_pillar.earthly_branch,
            chart.day_pillar.earthly_branch,
            chart.hour_pillar.earthly_branch,
        ]
        for b in all_branches:
            for hidden_stem, _pos in BRANCH_HIDDEN_STEMS.get(b, []):
                tg = ten_god(day_master, hidden_stem)
                if tg in TI_TEN_GODS:
                    result.ti_branches.add(b)
                elif tg in YONG_TEN_GODS:
                    result.yong_branches.add(b)

        # 3. 透干十神（年/月/时干相对日主）
        stems = {
            'year': (chart.year_pillar.heavenly_stem, ten_god(day_master, chart.year_pillar.heavenly_stem)),
            'month': (chart.month_pillar.heavenly_stem, ten_god(day_master, chart.month_pillar.heavenly_stem)),
            'hour': (chart.hour_pillar.heavenly_stem, ten_god(day_master, chart.hour_pillar.heavenly_stem)),
        }
        result.transparent_ten_gods = {k: v[1] for k, v in stems.items()}
        # 体用天干
        result.ti_stems = [st for _, (st, tg) in stems.items() if tg in TI_TEN_GODS]
        result.yong_stems = [st for _, (st, tg) in stems.items() if tg in YONG_TEN_GODS]

        # 4. 做功分析
        self._analyze_zuogong(chart, result, stems, day_master)

        # 4b. 做功强弱（WK-EFFICIENCY-001~005，古籍三判据 → 四档枚举）
        self._resolve_work_efficiency(result)

        # 4c. 功神/废神角色（GS-001~003）
        self._resolve_gong_shen(result)

        # 5. 生成盲派信号
        self._generate_signals(chart, result, birth_year, stems, day_master)

        # 5b. 制尽（规则 §37 CONTROL_COMPLETENESS-001/002）
        # COMPLETE = 做功链含制/穿/冲类控制路径 且 用支（目标）存在
        # PARTIAL  = 有做功但无控制路径（生合化路径），目标未受制
        # UNDETERMINED = 无做功
        if result.zuo_gong and result.yong_branches:
            control_methods = [
                m for m in result.zuo_gong_methods
                if ('制' in m or '穿' in m or '冲' in m)
            ]
            if control_methods:
                result.control_completeness = "COMPLETE"
                result.rules_triggered.append("CONTROL-COMPLETENESS-001")
            else:
                result.control_completeness = "PARTIAL"
                result.rules_triggered.append("CONTROL-COMPLETENESS-002")
        else:
            result.control_completeness = "UNDETERMINED"
            result.rules_triggered.append("CONTROL-COMPLETENESS-003")

        # 5c. 未核证规则域占位说明（只记一次）
        pending = {
            "贼神/捕神": "VERIFY-BLIND-015",
            "干支互通": "VERIFY-BLIND-017",
            "换象": "VERIFY-BLIND-022",
            "六亲组合链": "VERIFY-BLIND-023",
        }
        for domain, verify_id in pending.items():
            if not any(verify_id in r for r in result.undetermined_reasons):
                result.undetermined_reasons.append(
                    f"{domain}: {verify_id} 核证通过前不施工，输出 UNDETERMINED 占位"
                )

        return result

    # ── 做功分析 ───────────────────────────────────────────
    def _analyze_zuogong(self, chart, result, stems, day_master):
        """识别盲派做功方式：合用/制用/化用/生用 + 地支冲合。

        V2.2: 做功关系精确判定. 原逻辑"只要十神共存就触发"过于宽松(加入地支藏干后
        几乎所有做功方式都被触发). V2.2加入:
        1. 位置信息(柱索引0-3): 体用各自的位置
        2. 作用距离: 同柱(0)/相邻(1)/隔一位(2)/遥隔(3,不作用)
        3. 作用关系: 天干五合/地支六合/地支六冲/体克用(制)/体生用(生)/用生体(化)
        只有距离<=2且有明确作用关系的体用对才触发做功.
        """
        methods = []
        detail = []

        # ── 建立体用位置信息 ──
        # 格式: (stem, tg, pillar_idx, branch, is_hidden)
        ti_positions = []
        yong_positions = []
        pillars = [
            (0, chart.year_pillar.heavenly_stem, chart.year_pillar.earthly_branch),
            (1, chart.month_pillar.heavenly_stem, chart.month_pillar.earthly_branch),
            (2, day_master, chart.day_pillar.earthly_branch),
            (3, chart.hour_pillar.heavenly_stem, chart.hour_pillar.earthly_branch),
        ]
        for pillar_idx, stem, branch in pillars:
            # 天干
            if pillar_idx == 2:
                # 日主本身是体(比肩)
                ti_positions.append((stem, '比肩', pillar_idx, branch, False))
            else:
                tg = ten_god(day_master, stem)
                if tg in TI_TEN_GODS:
                    ti_positions.append((stem, tg, pillar_idx, branch, False))
                elif tg in YONG_TEN_GODS:
                    yong_positions.append((stem, tg, pillar_idx, branch, False))
            # 地支藏干
            for hidden_stem, _pos in BRANCH_HIDDEN_STEMS.get(branch, []):
                tg = ten_god(day_master, hidden_stem)
                if tg in TI_TEN_GODS:
                    ti_positions.append((hidden_stem, tg, pillar_idx, branch, True))
                elif tg in YONG_TEN_GODS:
                    yong_positions.append((hidden_stem, tg, pillar_idx, branch, True))

        # ── 作用关系判定 ──
        # 记录已触发的做功方式(避免重复)
        triggered = set()

        for ti in ti_positions:
            ti_stem, ti_tg, ti_idx, ti_branch, ti_hidden = ti
            for yong in yong_positions:
                yong_stem, yong_tg, yong_idx, yong_branch, yong_hidden = yong

                # 作用距离
                distance = abs(ti_idx - yong_idx)
                if distance > 2:
                    continue  # 遥隔不作用

                # 作用关系判定
                relation = None
                # 天干五合(仅天干之间)
                if not ti_hidden and not yong_hidden:
                    if (ti_stem, yong_stem) in STEM_HE or (yong_stem, ti_stem) in STEM_HE:
                        relation = "he"
                # 地支六合
                if relation is None and ti_branch != yong_branch:
                    if BRANCH_LIUHE.get(ti_branch) == yong_branch:
                        relation = "liuhe"
                # 地支六冲
                if relation is None and ti_branch != yong_branch:
                    if BRANCH_CHONG.get(ti_branch) == yong_branch:
                        relation = "chong"
                # V2.4: 地支六害(六穿) — 穿比冲更狠, 背后偷袭、排斥破坏
                # 穿可以做功(体穿用=制用), 也可以做负功(用穿体=体受伤)
                if relation is None and ti_branch != yong_branch:
                    if BRANCH_CHUAN.get(ti_branch) == yong_branch:
                        relation = "chuan"
                # 五行关系
                ti_el = STEM_ELEMENT[ti_stem]
                yong_el = STEM_ELEMENT[yong_stem]
                if relation is None and CONTROLS.get(ti_el) == yong_el:
                    relation = "ke_ti_yong"  # 体克用(制用)
                if relation is None and CONTROLS.get(yong_el) == ti_el:
                    relation = "ke_yong_ti"  # V2.3: 用克体(财制印、官杀制比劫)
                if relation is None and GENERATES.get(ti_el) == yong_el:
                    relation = "sheng_ti_yong"  # 体生用(生用)
                if relation is None and GENERATES.get(yong_el) == ti_el:
                    relation = "sheng_yong_ti"  # 用生体(化用)

                if relation is None:
                    continue

                # ── 根据十神类型+作用关系判定做功方式 ──
                method = None
                method_detail = None
                # V2.3: 做功主体判定 — 体在主位(日时,idx2-3)还是宾位(年月,idx0-1)
                # 盲派核心: 主位做功=为我所用, 宾位做功=非我所有(效力打折)
                ti_in_main = ti_idx >= 2  # 日时为主位
                yong_in_main = yong_idx >= 2
                # 主体获取宾位用(体在主、用在宾)=能获取外界财官, 做功效率高
                ti_gets_yong = ti_in_main and not yong_in_main

                # ① 合功: 合的对象是用(财/官) → 得财/得权
                if relation in ("he", "liuhe") and yong_tg in YONG_TEN_GODS:
                    method = f"合{yong_tg}"
                    method_detail = f"{'天干五合' if relation=='he' else '地支六合'}: {ti_stem}({ti_tg})合{yong_stem}({yong_tg}), 距{distance}{'[主取宾]' if ti_gets_yong else '[宾做功]' if not ti_in_main else ''}"
                # ①b V2.4: 穿害做功 — 体支穿用支=制用做功(穿比冲更狠)
                # 如卯辰穿: 卯(食伤)穿辰(官杀库)=食伤穿制官杀
                elif relation == "chuan" and ti_tg in TI_TEN_GODS and yong_tg in YONG_TEN_GODS:
                    method = f"穿制{yong_tg}"
                    method_detail = f"地支六穿: {ti_branch}({ti_tg})穿{yong_branch}({yong_tg}), 距{distance}{'[主取宾]' if ti_gets_yong else '[宾做功]' if not ti_in_main else ''}"
                # ② 食伤制杀: 体是食伤, 用是七杀, 体克用
                elif relation == "ke_ti_yong" and ti_tg in GROUP_SHI and yong_tg == "七杀":
                    method = "食伤制杀"
                    method_detail = f"{ti_stem}({ti_tg})制{yong_stem}({yong_tg}), 距{distance}{'[主取宾]' if ti_gets_yong else ''}"
                # ③ 伤官制官: 体是伤官, 用是正官, 体克用
                elif relation == "ke_ti_yong" and ti_tg == "伤官" and yong_tg == "正官":
                    method = "伤官制官"
                    method_detail = f"{ti_stem}({ti_tg})制{yong_stem}({yong_tg}), 距{distance}{'[主取宾]' if ti_gets_yong else ''}"
                # ④ 比劫制财: 体是比劫, 用是财, 体克用
                elif relation == "ke_ti_yong" and ti_tg in GROUP_BI and yong_tg in GROUP_CAI:
                    method = "比劫制财"
                    method_detail = f"{ti_stem}({ti_tg})制{yong_stem}({yong_tg}), 距{distance}{'[主取宾]' if ti_gets_yong else ''}"
                # ⑤ 财制印: V2.3 fix — 用是财, 体是印, 用克体(原写反为体克用,财属用不属体永不触发)
                # 盲派视"财制印"层次极高: 财星主动制合印星(资源/权力), 制得干净则大贵
                elif relation == "ke_yong_ti" and yong_tg in GROUP_CAI and ti_tg in GROUP_YIN:
                    method = "财制印"
                    method_detail = f"{yong_stem}({yong_tg})制{ti_stem}({ti_tg}), 距{distance}{'[用克体]' if not ti_in_main else ''}"
                # ⑤b 官杀制比劫: 用是官杀, 体是比劫, 用克体
                elif relation == "ke_yong_ti" and yong_tg in GROUP_GUAN and ti_tg in GROUP_BI:
                    method = "官杀制比劫"
                    method_detail = f"{yong_stem}({yong_tg})制{ti_stem}({ti_tg}), 距{distance}"
                # ⑥ 印化官杀: 体是印, 用是官杀, 用生体
                elif relation == "sheng_yong_ti" and ti_tg in GROUP_YIN and yong_tg in GROUP_GUAN:
                    method = "印化官杀"
                    method_detail = f"{yong_stem}({yong_tg})生{ti_stem}({ti_tg}), 距{distance}"
                # ⑦ 食伤生财: 体是食伤, 用是财, 体生用
                elif relation == "sheng_ti_yong" and ti_tg in GROUP_SHI and yong_tg in GROUP_CAI:
                    method = "食伤生财"
                    method_detail = f"{ti_stem}({ti_tg})生{yong_stem}({yong_tg}), 距{distance}{'[主取宾]' if ti_gets_yong else ''}"

                if method and method not in triggered:
                    triggered.add(method)
                    methods.append(method)
                    detail.append(method_detail)

        # ⑧ 地支三合(独立判定, 不依赖体用对)
        all_branch_set = {p[2] for p in pillars}
        for sanhe_key, sanhe_set in BRANCH_SANHE.items():
            if sanhe_set.issubset(all_branch_set):
                method = "地支三合"
                if method not in triggered:
                    triggered.add(method)
                    methods.append(method)
                    detail.append(f"地支三合: {sanhe_key}")

        # ⑨ V2.4: 墓库收放 — 辰戌丑未墓库, 闭库收物=财富聚拢, 冲库开库=财官出来
        # 墓喜冲: 库不开则财官无用, 一冲则发
        all_branches_list = [p[2] for p in pillars]
        muku_branches = [b for b in all_branches_list if b in MU_KU]
        for muku_b in muku_branches:
            muku_element = MU_KU[muku_b]
            muku_idx = all_branches_list.index(muku_b)
            muku_in_main = muku_idx >= 2
            # 检查墓库是否被冲(辰戌冲、丑未冲) — 冲则开库
            chong_target = BRANCH_CHONG.get(muku_b)
            is_chonged = chong_target in all_branches_list

            # 检查该五行是否在其他支中有根(被墓库收)
            element_stems = {"WOOD": ["JIA","YI"], "FIRE": ["BING","DING"],
                              "EARTH": ["WU","JI"], "METAL": ["GENG","XIN"], "WATER": ["REN","GUI"]}
            target_stems = element_stems.get(muku_element, [])
            has_root_elsewhere = False
            for b in all_branches_list:
                if b == muku_b:
                    continue
                for hidden_stem, _pos in BRANCH_HIDDEN_STEMS.get(b, []):
                    if hidden_stem in target_stems:
                        has_root_elsewhere = True
                        break
                if has_root_elsewhere:
                    break

            if is_chonged:
                # 冲库开库: 财官出来, 做功(墓喜冲不冲不发)
                method = "冲开墓库"
                if method not in triggered:
                    triggered.add(method)
                    methods.append(method)
                    detail.append(f"冲开{muku_b}({muku_element}墓): {muku_b}被{chong_target}冲, 开库出财官{'[主位]' if muku_in_main else '[宾位]'}")
            elif has_root_elsewhere:
                # 闭库收物: 墓库收该五行=财富聚拢, 做功
                method = "墓库收物"
                if method not in triggered:
                    triggered.add(method)
                    methods.append(method)
                    detail.append(f"闭库收{muku_element}: {muku_b}墓库收{muku_element}气=财富聚拢{'[主位]' if muku_in_main else '[宾位]'}")

        # ⑩ V2.5: 暗合 — 地支藏干之间的天干五合(如辰癸午丁暗合)
        # 盲派案例1: 辰中癸水与午中丁火暗合=财富靠整合资源收拢资本
        # 只在体用对之间, 且非天干/地支明合时判定
        hidden_he_triggered = set()
        for b1_idx, b1 in enumerate(all_branches_list):
            b1_in_main = b1_idx >= 2
            for b2_idx, b2 in enumerate(all_branches_list):
                if b1_idx >= b2_idx or b1 == b2:
                    continue
                # 检查两藏干之间是否有天干五合(跨支暗合)
                for h1, _p1 in BRANCH_HIDDEN_STEMS.get(b1, []):
                    for h2, _p2 in BRANCH_HIDDEN_STEMS.get(b2, []):
                        if (h1, h2) in STEM_HE or (h2, h1) in STEM_HE:
                            key = tuple(sorted([b1, b2]))
                            if key in hidden_he_triggered:
                                continue
                            hidden_he_triggered.add(key)
                            # 判定暗合的十神组合(以两藏干相对日主)
                            tg1 = ten_god(day_master, h1)
                            tg2 = ten_god(day_master, h2)
                            # 暗合取财/官为做功
                            if tg1 in YONG_TEN_GODS or tg2 in YONG_TEN_GODS:
                                in_main = b1_in_main or b2_idx >= 2
                                method = "暗合"
                                if method not in triggered:
                                    triggered.add(method)
                                    methods.append(method)
                                    detail.append(f"暗合: {b1}藏{h1}({tg1})合{b2}藏{h2}({tg2})={'资源整合' if in_main else '暗藏信息'}")
                            break
                    else:
                        continue
                    break

        # ⑪ V2.5: 包局 — 多支(2+)同气包围一支异气(如三寅包一子)
        # 盲派案例49(陈济棠): 三重寅木包一子水, 包局主贵, 体强包用得权
        # 判定: 至少2支同五行, 且包围的1支五行与之不同
        branch_elems = {}
        for b_idx, b in enumerate(all_branches_list):
            el = STEM_ELEMENT[b] if b in STEM_ELEMENT else _branch_element(b)
            branch_elems.setdefault(el, []).append(b)
        for el, bs in branch_elems.items():
            if len(bs) < 2:
                continue
            # 其他支(异五行)
            other_bs = [b for b in all_branches_list if b not in bs]
            if not other_bs:
                continue
            # 检查被包围支是否在日支(主位)或月支(提纲)
            for ob in other_bs:
                ob_idx = all_branches_list.index(ob)
                if ob_idx >= 2:  # 被包围者在主位(日时)
                    method = "包局"
                    if method not in triggered:
                        triggered.add(method)
                        methods.append(method)
                        detail.append(f"包局: {len(bs)}个{el}支{bs}包围{ob}({'主位' if ob_idx>=2 else ''})={('武力掌控权力' if len(bs)>=3 else '多方包围')}")
                    break
            else:
                continue
            break

        # ⑫ V2.5: 禄刃 — 禄神/羊刃特殊判定(身体、福报、自我意志)
        # 禄=福气身体, 刃=刀风险; 禄怕见绝更怕穿害; 禄合财=轻松赚钱, 禄克财=辛苦求财
        dm = day_master
        dm_lu = road_branch(dm)      # 日主禄位
        dm_ren = absolute_branch(dm)  # 日主帝旺(阳刃)位
        lu_in_chart = dm_lu in all_branches_list
        ren_in_chart = dm_ren in all_branches_list
        # 禄被穿害(六害) → 禄神受损, 身体/福报受损
        lu_chuaned = None
        if lu_in_chart:
            for other_b in all_branches_list:
                if other_b != dm_lu and BRANCH_CHUAN.get(dm_lu) == other_b:
                    lu_chuaned = other_b
                    break
        if lu_chuaned:
            method = "禄神受穿"
            if method not in triggered:
                triggered.add(method)
                methods.append(method)
                detail.append(f"禄神{dm_lu}被{lu_chuaned}穿害: 禄怕穿害, 身体/福报受损")
        # 阳刃(帝旺)下坐财星或冲官 → 军警/运动员/高风险(刃=刀)
        elif ren_in_chart:
            method = "阳刃"
            if method not in triggered:
                triggered.add(method)
                methods.append(method)
                detail.append(f"阳刃在{dm_ren}: 刃=刀, 身体能力自我意志强{'[主位]' if dm_ren in all_branches_list[2:] else ''}")

        result.zuo_gong = len(methods) > 0
        result.zuo_gong_type = "+".join(methods) if methods else ""
        result.zuo_gong_methods = methods
        result.zuo_gong_detail = detail

    # ── 做功强弱（WK-EFFICIENCY-001~005）────────────────────
    def _resolve_work_efficiency(self, result: "BlindBaziResult") -> None:
        """做功强弱 = 古籍三判据 → 四档枚举。

        古籍原文（《盲派初级命理学》第二章·做功效率 p.20-25）：
          "做功效率高低的判断：看做功路径是否直接、看做功力量是否集中、
            看做功对象是否得力。"
        全部结构判定，零数字化（BLIND-ARCH-006 / BLIND-G16）。
        """
        methods = result.zuo_gong_methods
        result.rules_triggered.append("WK-EFFICIENCY-001")

        if not methods:
            # WK-EFFICIENCY-002：路径/力量/对象全不满足 → 无效做功
            result.work_efficiency = WorkEfficiency.NONE.value
            result.structure_clarity = StructureClarity.CHAOTIC.value
            result.work_level = "POOR"
            result.undetermined_reasons.append(
                "无有效做功方法 → WORK_EFFICIENCY=NONE（古籍：无效做功=贫贱）"
            )
            return

        # 判据① 路径直接：做功方法存在且非遥隔（_analyze_zuogong 已按距离<=2 过滤）
        result.eff_path_direct = True

        # 判据② 力量集中：做功方法单一（≤1 种）= 单一作用集；禁 actor_count>=3 围制
        result.eff_power_concentrated = len(methods) <= 1

        # 判据③ 对象得力：做功对象（用）被明确 制/合/化/生/开库/收物
        result.eff_target_effective = any(
            ('制' in m or '合' in m or '化' in m or '生' in m
             or '开' in m or '收' in m or '包' in m)
            for m in methods
        )

        if result.eff_path_direct and result.eff_power_concentrated and result.eff_target_effective:
            result.work_efficiency = WorkEfficiency.LARGE.value
            result.structure_clarity = StructureClarity.CLEAR.value
            result.work_level = "LARGE_NOBLE"
        elif result.eff_path_direct and (
            result.eff_power_concentrated or result.eff_target_effective
        ):
            result.work_efficiency = WorkEfficiency.MEDIUM.value
            result.structure_clarity = StructureClarity.PARTIALLY_CLEAR.value
            result.work_level = "MEDIUM_NOBLE"
        elif result.eff_path_direct:
            result.work_efficiency = WorkEfficiency.SMALL.value
            result.structure_clarity = StructureClarity.MIXED.value
            result.work_level = "SMALL_NOBLE"
        else:
            result.work_efficiency = WorkEfficiency.NONE.value
            result.structure_clarity = StructureClarity.CHAOTIC.value
            result.work_level = "POOR"

        result.rules_triggered.append("WK-EFFICIENCY-002")
        result.rules_triggered.append("WK-EFFICIENCY-003")
        result.rules_triggered.append("WK-EFFICIENCY-004")

    # ── 功神/废神角色（GS-001~003）──────────────────────────
    def _resolve_gong_shen(self, result: "BlindBaziResult") -> None:
        """功神角色分配（结构枚举）。

        - 有做功：体支 = WORKING（功神），用支 = TARGET（目标）
        - 无做功：UNDETERMINED（不得自行补全）
        """
        result.rules_triggered.append("GS-001")
        if not result.zuo_gong_methods:
            result.gong_shen = {"UNDETERMINED": []}
            return
        working = sorted(result.ti_branches)
        target = sorted(result.yong_branches)
        if working or target:
            result.gong_shen = {
                "WORKING": working,
                "TARGET": target,
            }
            result.rules_triggered.append("GS-002")
        else:
            result.gong_shen = {"UNDETERMINED": []}

    # ── 断事信号 ───────────────────────────────────────────
    def _generate_signals(self, chart, result, birth_year, stems, day_master):
        signals = []
        # V2.1: 合并天干+地支藏干十神, 用于信号判定(原只看天干透干)
        tg_set = set(t for _, t in stems.values())
        for b in [chart.year_pillar.earthly_branch, chart.month_pillar.earthly_branch,
                  chart.day_pillar.earthly_branch, chart.hour_pillar.earthly_branch]:
            for hidden_stem, _pos in BRANCH_HIDDEN_STEMS.get(b, []):
                tg_set.add(ten_god(day_master, hidden_stem))
        methods = result.zuo_gong_methods

        # ── 信号强度合规（BLIND-ARCH-006 / BLIND-G16）：─────────────
        # 盲派禁止"能量/效率/层功"数字化评分；CanonicalSignal.strength 是
        # 平台契约必填字段（[0.0,1.0]），此处统一固定为中性值 0.5，
        # 不表达任何做功强弱排序。盲派做功强弱一律走结构枚举
        # （EFFECTIVE/PARTIAL/BLOCKED/BROKEN/COMPLETE/INCOMPLETE）。
        # ─────────────────────────────────────────────────────────────

        # ── 财运信号（盲派：合财/比劫制财/食伤生财/财星）──
        cai_signals = [m for m in methods if '财' in m]
        if cai_signals:
            signals.append(CanonicalSignal(
                signal_id=f"blind-cai-{birth_year}", source_engine=SourceEngine.BLIND,
                event_type="WEALTH_GAIN", domain=Domain.LIFE_EVENT,
                direction=EventDirection.POSITIVE, strength=0.5,  # 平台中性值，非做功数字化
                temporal_scope=SignalTemporalScope(granularity="YEARLY"),
                evidence_refs=[f"E-BLIND-CAI-{birth_year}"], rule_refs=["BLIND-CAI-001"],
                layer=SignalLayer.BASELINE))
        else:
            # 规则 §33 WEALTH-001/002：禁"财星存在=财富"。
            # 无做功链时财富事件结论 UNDETERMINED（结构事实=财星透藏已由
            # transparent_ten_gods 输出，此处不派生出事件信号）。
            result.undetermined_reasons.append(
                "财星存在但无做功链：WEALTH 事件 UNDETERMINED（WEALTH-001/002，禁星存在=吉凶）"
            )

        # ── 事业信号（合官/食伤制杀/印化官杀/官杀）──
        guan_signals = [m for m in methods if '官' in m or '杀' in m]
        if guan_signals:
            signals.append(CanonicalSignal(
                signal_id=f"blind-guan-{birth_year}", source_engine=SourceEngine.BLIND,
                event_type="CAREER_PROMOTION", domain=Domain.CAREER,
                direction=EventDirection.POSITIVE, strength=0.5,  # 平台中性值，非做功数字化
                temporal_scope=SignalTemporalScope(granularity="YEARLY"),
                evidence_refs=[f"E-BLIND-GUAN-{birth_year}"], rule_refs=["BLIND-GUAN-001"],
                layer=SignalLayer.BASELINE))
        else:
            # 规则 §30 OFF-001：禁"官星出现=官贵/事业"。
            # 无做功链时事业事件结论 UNDETERMINED。
            result.undetermined_reasons.append(
                "官杀存在但无做功链：CAREER 事件 UNDETERMINED（OFF-001，禁星存在=事业）"
            )

        # ── 性格（伤官/七杀/食神）──
        if '伤官' in tg_set:
            signals.append(CanonicalSignal(
                signal_id=f"blind-xing-shangguan-{birth_year}", source_engine=SourceEngine.BLIND,
                event_type="PERSONALITY", domain=Domain.LIFE_EVENT,
                direction=EventDirection.NEUTRAL, strength=0.5,
                temporal_scope=SignalTemporalScope(granularity="STATIC"),
                evidence_refs=[f"E-BLIND-XSG-{birth_year}"], rule_refs=["BLIND-X-001"],
                layer=SignalLayer.BASELINE))
        if '七杀' in tg_set:
            signals.append(CanonicalSignal(
                signal_id=f"blind-xing-qisha-{birth_year}", source_engine=SourceEngine.BLIND,
                event_type="PERSONALITY", domain=Domain.LIFE_EVENT,
                direction=EventDirection.NEUTRAL, strength=0.5,
                temporal_scope=SignalTemporalScope(granularity="STATIC"),
                evidence_refs=[f"E-BLIND-XQS-{birth_year}"], rule_refs=["BLIND-X-002"],
                layer=SignalLayer.BASELINE))

        # ── 婚姻（配偶宫冲害 → 纯结构判据）──
        # V2.7: 移除 spouse_star_strength=='weak' 消费（Bazi 判断层字段，
        # 标注 NOT_AUTHORIZED，违反 BLIND-ARCH-003 禁止消费子平判断）。
        # 仅用客观结构：日支（配偶宫）被冲/被穿/被合绊。
        day_branch_structure = (
            getattr(chart, 'day_branch_clash', False)
            or getattr(chart, 'day_branch_harm', False)
        )
        # 配偶宫被冲（寅申冲等）：日支对冲支出现在四柱
        day_branch_chong = BRANCH_CHONG.get(chart.day_pillar.earthly_branch)
        if day_branch_chong in [
            chart.year_pillar.earthly_branch,
            chart.month_pillar.earthly_branch,
            chart.hour_pillar.earthly_branch,
        ]:
            day_branch_structure = True

        if day_branch_structure:
            signals.append(CanonicalSignal(
                signal_id=f"blind-hunyin-{birth_year}", source_engine=SourceEngine.BLIND,
                event_type="MARRIAGE_CHALLENGE", domain=Domain.FAMILY,
                direction=EventDirection.NEGATIVE, strength=0.5,
                temporal_scope=SignalTemporalScope(granularity="YEARLY"),
                evidence_refs=[f"E-BLIND-HY-{birth_year}"], rule_refs=["BLIND-HY-001"],
                layer=SignalLayer.BASELINE))

        # ── 健康（五行失衡 / 体支被冲）──
        # V2.6 fix: 原逻辑BRANCH_CHONG.get(b) in ti_branches(用支对冲在体=体冲用)方向反了.
        # 盲派: 体支被冲=体受伤. 正确=体支的对冲支在用支中(体被用冲).
        body_chonged = any(
            BRANCH_CHONG.get(b) in result.yong_branches
            for b in result.ti_branches
        )
        if body_chonged:
            signals.append(CanonicalSignal(
                signal_id=f"blind-health-{birth_year}", source_engine=SourceEngine.BLIND,
                event_type="HEALTH_ISSUE", domain=Domain.LIFE_EVENT,
                direction=EventDirection.NEGATIVE, strength=0.5,
                temporal_scope=SignalTemporalScope(granularity="YEARLY"),
                evidence_refs=[f"E-BLIND-HEALTH-{birth_year}"], rule_refs=["BLIND-HEALTH-001"],
                layer=SignalLayer.BASELINE))

        # ── 事业变动（规则 §58 象→事过滤链）──
        # 原 BLIND-001"宾主五行相异→JOB_CHANGE"是"结构差异=事件"的泛化直断：
        # 宾主五行相异只是象层事实，未过 DOMAIN/PALACE/TEN_GOD/WORK 完整链，
        # 不得派生出 JOB_CHANGE 事件。结构事实（宾主支集合）已由
        # main_branches/guest_branches 输出，此处仅记 UNDETERMINED。
        main_elems = {_branch_element(b) for b in result.main_branches}
        guest_elems = {_branch_element(b) for b in result.guest_branches}
        if main_elems and guest_elems and main_elems.isdisjoint(guest_elems):
            result.undetermined_reasons.append(
                "宾主五行相异但无做功链：JOB_CHANGE 事件 UNDETERMINED（§58，象层事实不直断事件）"
            )

        result.signals = signals

    def get_adapter(self) -> "BlindAdapter":
        return BlindAdapter(self)


# ─── 盲派适配器 ───────────────────────────────────────────────────────────────

class BlindAdapter(BaseAdapter):
    """盲派信号适配器"""
    ENGINE_NAME = "BLIND"

    def adapt(self, engine_output: BlindBaziResult, context: Optional[AdapterContext] = None) -> List[CanonicalSignal]:
        return engine_output.signals


# ─── 导出接口 ─────────────────────────────────────────────────────────────────

def compute_blind_bazi(birth: Tuple[int, int, int, int], gender: str = "male") -> BlindBaziResult:
    engine = BlindBaziEngine()
    return engine.compute(birth, gender=gender)
