# -*- coding: utf-8 -*-
"""盲派应期断法模块 — Blind Pai Yingqi (应期) Analyzer

基于段建业/杨清贫盲派应期断法（《盲派命理-案例资料集》§6 应期断法）。
只实现确定性算法，不使用 LLM。

盲派应期三法（2026-08-27 典籍校对）：
1. 大限应期：年柱1-18岁、月柱18-35岁、日柱35-55岁、时柱55岁以后
   - 八字讲贵贱，大运讲吉凶，流年看应期；大限+大运=和的关系
2. 禄与原身应期：某字在流年/大运出现，或其禄/原身出现 = 该字应期
3. 遁藏透干应期：地支遁藏字在大运/流年天干出现 = 该字的应期

运年引动（应期触发核心）：
- 大运/流年柱与命局四柱之间的 冲/穿(六害)/刑/三合/六合/墓库开闭
  引动命局的做功，能量迸发 → 该年为应期
- 穿倒/冲倒主位字 = 应灾（婚姻、健康、官非）
- 墓库被冲开 = 财官出（发财、发贵应期）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from ..engines.bazi_engine import BaziEngine, BaziChart, BRANCH_SANXING
from ..reasoning.bazi_ten_gods import BRANCH_HIDDEN_STEMS, ten_god
from ..reasoning.bazi_fixed_tables import road_branch, absolute_branch
from .blind_bazi_engine import (
    BRANCH_CHONG, BRANCH_CHUAN, BRANCH_LIUHE, BRANCH_SANHE, MU_KU,
    GROUP_CAI, GROUP_GUAN, GROUP_YIN, GROUP_BI, GROUP_SHI,
    TI_TEN_GODS, YONG_TEN_GODS, STEM_HE,
)

# 盲派大限分段：年柱1-18 / 月柱18-35 / 日柱35-55 / 时柱55+ (典籍)
DAXIAN_SEGMENTS = [
    (0, 18),     # 年柱: 1-18岁(0-18区间, 上界不含)
    (18, 35),    # 月柱: 18-35岁
    (35, 55),    # 日柱: 35-55岁
    (55, 150),   # 时柱: 55岁以后
]

# 大运覆盖个数(一生约80年, 每10年一运 → 8个足够)
LUCK_PILLAR_COUNT = 8


@dataclass
class YingqiResult:
    """盲派应期断法分析结果(单个年龄/流年)"""
    age: int = 0
    flow_year: int = 0                       # 流年(公历)
    flow_stem: str = ""                      # 流年天干
    flow_branch: str = ""                    # 流年地支
    daxian_pillar: str = ""                  # 所属大限柱(年/月/日/时)
    daxian_range: str = ""                   # 大限年龄段, 如 "1-18岁"
    luck_stem: str = ""                      # 当前大运天干
    luck_branch: str = ""                    # 当前大运地支
    triggers: List[Dict] = field(default_factory=list)  # 引动事件列表
    yingqi_events: List[Dict] = field(default_factory=list)  # 应期事件
    key_signals: List[str] = field(default_factory=list)    # 关键信号词

    def to_dict(self) -> dict:
        return {
            'age': self.age,
            'flow_year': self.flow_year,
            'flow_pillar': self.flow_stem + self.flow_branch,
            'daxian_pillar': self.daxian_pillar,
            'daxian_range': self.daxian_range,
            'luck_pillar': self.luck_stem + self.luck_branch,
            'triggers': self.triggers,
            'yingqi_events': self.yingqi_events,
            'key_signals': self.key_signals,
        }


class BlindYingqiEngine:
    """盲派应期断法引擎"""

    def __init__(self, bazi_engine: Optional[BaziEngine] = None):
        self.bazi_engine = bazi_engine or BaziEngine()

    # ── 干支工具 ──────────────────────────────────────────
    def _ganzhi_of_year(self, year: int) -> Tuple[str, str]:
        """公历年 → 干支(流年). 标准公式 (year-4)%10/(year-4)%12."""
        from ..engines.bazi_engine import HEAVENLY_STEMS, EARTHLY_BRANCHES
        return HEAVENLY_STEMS[(year - 4) % 10], EARTHLY_BRANCHES[(year - 4) % 12]

    def _next_pillar(self, stem: str, branch: str, delta: int) -> Tuple[str, str]:
        """从指定干支顺/逆推delta位."""
        from ..engines.bazi_engine import HEAVENLY_STEMS, EARTHLY_BRANCHES
        si = HEAVENLY_STEMS.index(stem)
        bi = EARTHLY_BRANCHES.index(branch)
        return (HEAVENLY_STEMS[(si + delta) % 10],
                EARTHLY_BRANCHES[(bi + delta) % 12])

    def _luck_pillars_ext(self, chart: BaziChart) -> List[Tuple[str, str]]:
        """扩展大运柱: 基于起运岁数 + 年干阴阳 + 性别, 覆盖一生(8个)."""
        from ..engines.bazi_engine import HEAVENLY_STEMS, EARTHLY_BRANCHES
        month_stem = chart.month_pillar.heavenly_stem
        month_branch = chart.month_pillar.earthly_branch
        # 顺逆方向: 年干阳男/阴女顺排, 否则逆排
        year_stem = chart.year_pillar.heavenly_stem
        is_yang = HEAVENLY_STEMS.index(year_stem) % 2 == 0
        if (chart.gender == "male" and is_yang) or (chart.gender == "female" and not is_yang):
            direction = +1
        else:
            direction = -1
        pillars = []
        si = HEAVENLY_STEMS.index(month_stem)
        bi = EARTHLY_BRANCHES.index(month_branch)
        for decade in range(1, LUCK_PILLAR_COUNT + 1):
            pillars.append((HEAVENLY_STEMS[(si + direction * decade) % 10],
                            EARTHLY_BRANCHES[(bi + direction * decade) % 12]))
        return pillars

    # ── 大限 / 大运定位 ───────────────────────────────────
    def _daxian_of_age(self, age: int) -> Tuple[str, str]:
        """根据年龄定位所属大限柱(年/月/日/时)和年龄段."""
        pillars = ["year", "month", "day", "hour"]
        for i, (lo, hi) in enumerate(DAXIAN_SEGMENTS):
            if lo <= age < hi:
                return pillars[i], f"{lo if lo>0 else 1}-{hi}岁"
        return "hour", "55岁以后"

    def _luck_of_age(self, chart: BaziChart, age: int) -> Tuple[str, str]:
        """根据年龄定位当前大运柱. 起运岁数后每10年一运."""
        start_age = getattr(chart, 'start_age', 0.0)
        pillars = self._luck_pillars_ext(chart)
        # 第decade个十年运: age - start_age 落在 [decade*10, (decade+1)*10)
        idx = max(0, int((age - start_age) // 10))
        idx = min(idx, len(pillars) - 1)
        return pillars[idx]

    # ── 主入口 ────────────────────────────────────────────
    def analyze(self, birth: Tuple[int, int, int, int], gender: str,
                target_age: Optional[int] = None,
                target_year: Optional[int] = None) -> YingqiResult:
        """分析某年龄/某流年的盲派应期.

        Args:
            birth: (年,月,日,时)
            gender: male/female
            target_age: 目标年龄; 与target_year二选一
            target_year: 目标公历年份
        """
        chart = self.bazi_engine.compute(birth, gender=gender)
        birth_year = birth[0]
        if target_age is None and target_year is None:
            # 默认中年窗口(断事窗口 35-55)
            target_age = 40
        if target_age is not None:
            age = target_age
            flow_year = birth_year + age
        else:
            flow_year = target_year
            age = flow_year - birth_year

        result = YingqiResult(age=age, flow_year=flow_year)
        result.flow_stem, result.flow_branch = self._ganzhi_of_year(flow_year)

        # 大限定位
        daxian_key, daxian_range = self._daxian_of_age(age)
        result.daxian_pillar = daxian_key
        result.daxian_range = daxian_range
        daxian_branch = getattr(chart, f"{daxian_key}_pillar").earthly_branch

        # 大运定位
        luck_stem, luck_branch = self._luck_of_age(chart, age)
        result.luck_stem, result.luck_branch = luck_stem, luck_branch

        # 命局四柱信息
        four_pillars = {
            'year': chart.year_pillar, 'month': chart.month_pillar,
            'day': chart.day_pillar, 'hour': chart.hour_pillar,
        }
        day_master = chart.day_master

        # 判定引动 + 应期
        triggers = []
        events = []
        key_signals = []

        # ① 运年柱与命局四柱的引动关系
        luck_trigger = self._check_trigger(luck_stem, luck_branch, four_pillars,
                                           day_master, chart, age, source="大运")
        flow_trigger = self._check_trigger(result.flow_stem, result.flow_branch,
                                           four_pillars, day_master, chart, age, source="流年")
        triggers.extend(luck_trigger)
        triggers.extend(flow_trigger)

        # ② 大限柱引动(大限+大运=和的关系)
        daxian_trigger = self._check_trigger(
            getattr(chart, f"{daxian_key}_pillar").heavenly_stem, daxian_branch,
            four_pillars, day_master, chart, age, source=f"大限{daxian_key}")
        triggers.extend(daxian_trigger)

        # ③ 应期事件整理
        for trg in triggers:
            evt = self._event_from_trigger(trg, day_master, age)
            if evt:
                events.append(evt)
                key_signals.append(trg['kind'])

        # 去重
        seen = set()
        dedup = []
        for e in events:
            k = e.get('mechanism') + '|' + e.get('keyword', '')
            if k not in seen:
                seen.add(k)
                dedup.append(e)
        result.triggers = triggers
        result.yingqi_events = dedup
        result.key_signals = list(dict.fromkeys(key_signals))
        return result

    # ── 引动判定 ──────────────────────────────────────────
    def _check_trigger(self, yun_stem: str, yun_branch: str,
                       four_pillars: Dict, day_master: str, chart: BaziChart,
                       age: int, source: str) -> List[Dict]:
        """检查大运/流年/大限柱与命局四柱的引动关系.

        返回引动事件列表, 每项含 kind/mech/keyword/direction.
        """
        triggers = []
        # 命局四支
        four_branches = {
            'year': four_pillars['year'].earthly_branch,
            'month': four_pillars['month'].earthly_branch,
            'day': four_pillars['day'].earthly_branch,
            'hour': four_pillars['hour'].earthly_branch,
        }
        # 主位支(日时)
        main_branches = [four_branches['day'], four_branches['hour']]

        # ── 运年支与命局支的冲/穿/合 ──
        for pos, nb in four_branches.items():
            # 六冲
            if BRANCH_CHONG.get(yun_branch) == nb:
                in_main = nb in main_branches
                triggers.append({
                    'kind': 'chong', 'source': source, 'position': pos,
                    'branch': nb, 'in_main': in_main,
                    'mech': f"{source}{yun_branch}冲{nb}({pos}支)",
                    'keyword': nb,
                    'direction': 'NEGATIVE' if in_main else 'CHANGE',
                })
            # 六穿(害) — 穿比冲更狠
            if BRANCH_CHUAN.get(yun_branch) == nb:
                in_main = nb in main_branches
                triggers.append({
                    'kind': 'chuan', 'source': source, 'position': pos,
                    'branch': nb, 'in_main': in_main,
                    'mech': f"{source}{yun_branch}穿{nb}({pos}支)",
                    'keyword': nb,
                    'direction': 'NEGATIVE' if in_main else 'CHANGE',
                })
            # 六合(合到主位=引动)
            if BRANCH_LIUHE.get(yun_branch) == nb:
                triggers.append({
                    'kind': 'liuhe', 'source': source, 'position': pos,
                    'branch': nb, 'in_main': nb in main_branches,
                    'mech': f"{source}{yun_branch}合{nb}({pos}支)",
                    'keyword': nb,
                    'direction': 'POSITIVE',
                })

        # ── 三合局(运支参与构成三合) ──
        yun_el = _branch_element_cached(yun_branch)
        for sanhe_key, sanhe_set in BRANCH_SANHE.items():
            if yun_branch in sanhe_set:
                # 检查命局是否已有另两支
                present = [b for b in four_branches.values() if b in sanhe_set]
                if len(present) >= 2:
                    triggers.append({
                        'kind': 'sanhe', 'source': source, 'position': 'day',
                        'branch': yun_branch, 'in_main': False,
                        'mech': f"{source}{yun_branch}构成三合局{sanhe_key}",
                        'keyword': sanhe_key,
                        'direction': 'POSITIVE',
                    })
                    break

        # ── 三刑引动(运/年支加入后与命局两支构成三刑) ──
        # 盲派案例: 丑未戌三刑应(案例14/15), 寅巳申三刑刑坏禄神(案例3)
        four_branch_set = set(four_branches.values())
        for xing_set, xing_name in BRANCH_SANXING.items():
            if not isinstance(xing_set, frozenset):
                continue  # self 自刑单独处理
            if yun_branch in xing_set:
                # 命局需已有该三刑组内另外两支(或一支+运支凑三刑)
                present_in_chart = [b for b in four_branch_set if b in xing_set]
                combined = set(present_in_chart) | {yun_branch}
                if xing_set.issubset(combined):
                    in_main = yun_branch in main_branches
                    triggers.append({
                        'kind': 'sanxing', 'source': source, 'position': 'day',
                        'branch': yun_branch, 'in_main': in_main,
                        'mech': f"{source}{yun_branch}构成{xing_name}({'-'.join(sorted(xing_set))}三刑)",
                        'keyword': xing_name,
                        'direction': 'NEGATIVE' if in_main else 'CHANGE',
                    })

        # ── 自刑(运/年支重复命局中自刑地支, 如辰辰) ──
        self_xing = BRANCH_SANXING.get('self', set())
        if yun_branch in self_xing and yun_branch in four_branch_set:
            triggers.append({
                'kind': 'zixing', 'source': source, 'position': 'day',
                'branch': yun_branch, 'in_main': yun_branch in main_branches,
                'mech': f"{source}{yun_branch}伏吟自刑(重复)",
                'keyword': yun_branch,
                'direction': 'CHANGE',
            })

        # ── 墓库开闭(运支冲墓库 → 开库出财官) ──
        for pos, nb in four_branches.items():
            if nb in MU_KU:
                chong_target = BRANCH_CHONG.get(nb)
                if chong_target == yun_branch:
                    muku_element = MU_KU[nb]
                    in_main = nb in main_branches
                    triggers.append({
                        'kind': 'muku_kai', 'source': source, 'position': pos,
                        'branch': nb, 'in_main': in_main,
                        'mech': f"{source}{yun_branch}冲开{nb}{muku_element}墓",
                        'keyword': nb,
                        'direction': 'POSITIVE' if in_main else 'CHANGE',
                    })

        # ── 遁藏透干应期: 命局地支藏干在运/年天干出现 ──
        for pos, nb in four_branches.items():
            for hidden_stem, _ in BRANCH_HIDDEN_STEMS.get(nb, []):
                if hidden_stem == yun_stem:
                    tg = ten_god(day_master, hidden_stem)
                    in_main = nb in main_branches
                    triggers.append({
                        'kind': 'tougan', 'source': source, 'position': pos,
                        'branch': nb, 'in_main': in_main,
                        'mech': f"{source}透干: {nb}藏{hidden_stem}({tg})现于天干",
                        'keyword': hidden_stem, 'ten_god': tg,
                        'direction': 'POSITIVE' if tg in GROUP_GUAN or tg in GROUP_CAI else 'NEUTRAL',
                    })

        # ── 禄与原身应期: 某字禄位在原命局, 运年出现该禄位 ──
        # 或日主禄位在原命局被运年引动
        dm_lu = road_branch(day_master)
        if dm_lu in four_branches.values():
            # 禄在原局, 运年出现该禄的禄(重复禄)或合禄
            if yun_branch == dm_lu:
                triggers.append({
                    'kind': 'lu', 'source': source, 'position': 'day',
                    'branch': dm_lu, 'in_main': True,
                    'mech': f"{source}{yun_branch}重现日主禄位{dm_lu}",
                    'keyword': '禄', 'direction': 'POSITIVE',
                })

        return triggers

    # ── 应期事件整理 ──────────────────────────────────────
    def _event_from_trigger(self, trg: Dict, day_master: str, age: int) -> Optional[Dict]:
        """将引动转为应期事件(带机制/方向/强度)."""
        kind = trg['kind']
        in_main = trg.get('in_main', False)
        direction = trg.get('direction', 'NEUTRAL')
        mech = trg['mech']

        # 强度: 主位 > 宾位
        strength = 0.7 if in_main else 0.45

        base = {
            'mechanism': kind, 'mech': mech, 'keyword': trg.get('keyword', ''),
            'source': trg['source'], 'direction': direction,
            'strength': strength, 'age': age,
        }

        # 按引动类型映射到断事主题
        if kind == 'chuan' and in_main:
            base['topic'] = '穿倒主位'
            base['direction'] = 'NEGATIVE'
            base['strength'] = 0.8  # 穿倒主位最狠
        elif kind == 'chong' and in_main:
            base['topic'] = '冲主位'
            base['direction'] = 'NEGATIVE' if '禄' not in str(trg.get('keyword')) else 'CHANGE'
            base['strength'] = 0.7
        elif kind == 'muku_kai':
            base['topic'] = '冲开墓库'
            base['direction'] = 'POSITIVE'
            base['strength'] = 0.7 if in_main else 0.5
        elif kind == 'sanhe':
            base['topic'] = '三合局引动'
            base['direction'] = 'POSITIVE'
            base['strength'] = 0.65
        elif kind == 'sanxing':
            # 三刑引动: 恃势之刑(丑戌未)主官非刑伤, 无恩之刑(寅巳申)主疾病, 无礼之刑(子卯)主婚姻口舌
            base['topic'] = '三刑引动'
            base['direction'] = 'NEGATIVE'
            base['strength'] = 0.75 if in_main else 0.55
            k = trg.get('keyword', '')
            if '恃势' in k:
                base['domain'] = '官非刑伤'
            elif '无恩' in k:
                base['domain'] = '健康灾伤'
            elif '无礼' in k:
                base['domain'] = '婚姻口舌'
        elif kind == 'zixing':
            base['topic'] = '伏吟自刑'
            base['direction'] = 'CHANGE'
            base['strength'] = 0.5
        elif kind == 'liuhe' and in_main:
            base['topic'] = '合入主位'
            base['direction'] = 'POSITIVE'
            base['strength'] = 0.6
        elif kind == 'lu':
            base['topic'] = '禄神重现'
            base['direction'] = 'POSITIVE'
            base['strength'] = 0.55
        elif kind == 'tougan':
            tg = trg.get('ten_god', '')
            base['topic'] = '透干应期'
            base['strength'] = 0.5 if in_main else 0.35
        else:
            base['topic'] = '运年引动'
        return base


# 地支五行缓存(避免重复计算)
_BRANCH_ELEM_CACHE = {}


def _branch_element_cached(branch: str) -> str:
    if branch not in _BRANCH_ELEM_CACHE:
        from ..engines.bazi_engine import _branch_element
        _BRANCH_ELEM_CACHE[branch] = _branch_element(branch)
    return _BRANCH_ELEM_CACHE[branch]


def analyze_yingqi(birth: Tuple[int, int, int, int], gender: str = "male",
                   target_age: Optional[int] = None,
                   target_year: Optional[int] = None) -> YingqiResult:
    """便捷入口."""
    engine = BlindYingqiEngine()
    return engine.analyze(birth, gender, target_age, target_year)
