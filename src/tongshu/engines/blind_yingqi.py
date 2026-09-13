# -*- coding: utf-8 -*-
"""盲派应期断法模块 — Blind Pai Yingqi (应期) Analyzer

基于段建业/杨清贫盲派应期断法（段建业原书应期章）。
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

from ..engines.bazi_engine import BaziEngine, BaziChart, canonical_bazi_engine
from ..facts.bazi_facts import (
    BRANCH_SANXING_TRIPLE,
    BRANCH_SANXING_DOUBLE,
    BRANCH_SANXING_SELF,
    CONTROLS,
    STEM_ELEMENT,
)
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

    def __init__(self, bazi_engine=None):
        self.bazi_engine = bazi_engine or canonical_bazi_engine

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

        # ── fail-closed 输入守卫（规范 §55/E4，盲派规则 V1-FINAL §46）──
        # 越界目标（负年龄 / 出生前年份 / 超设计范围）必须拒绝计算并抛 ValueError，
        # 不得静默返回结果。设计范围 = 大限末段 (55,150) 含上界 149。
        if target_age is not None:
            if target_age < 0 or target_age > 149:
                raise ValueError(
                    f"fail-closed: target_age={target_age} 越界，"
                    f"盲派应期设计范围为 0-149"
                )
        if target_year is not None:
            age_from_year = target_year - birth_year
            if age_from_year < 0 or age_from_year > 149:
                raise ValueError(
                    f"fail-closed: target_year={target_year} 越界，"
                    f"相对出生年 {birth_year} 的年龄须在 0-149 内"
                )

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
            # 六冲（旺衰冲应: 冲去/冲起, 段建业第02章）
            if BRANCH_CHONG.get(yun_branch) == nb:
                in_main = nb in main_branches
                chong_effect = _chong_effect(chart, yun_branch, nb)
                triggers.append({
                    'kind': 'chong', 'source': source, 'position': pos,
                    'branch': nb, 'in_main': in_main,
                    'mech': f"{source}{yun_branch}冲{nb}({pos}支)",
                    'keyword': nb,
                    'chong_effect': chong_effect,
                    'direction': 'NEGATIVE' if in_main else 'CHANGE',
                })
            # 六穿(害) — 穿比冲更狠（穿中带生=轻/有动意; 带克=重, 段建业第02章案例）
            if BRANCH_CHUAN.get(yun_branch) == nb:
                in_main = nb in main_branches
                chuan_nature = _chuan_nature(yun_branch, nb)
                triggers.append({
                    'kind': 'chuan', 'source': source, 'position': pos,
                    'branch': nb, 'in_main': in_main,
                    'mech': f"{source}{yun_branch}穿{nb}({pos}支)",
                    'keyword': nb,
                    'chuan_nature': chuan_nature,
                    'direction': 'NEGATIVE' if in_main else 'CHANGE',
                })
            # 六合(合到主位=引动)
            # 合动/合绊: 支合=合动; 天地合(天干五合+地支六合同柱)=合绊
            # （段建业第02章: 子丑合为合动子水, 若是天地合则为合绊）
            if BRANCH_LIUHE.get(yun_branch) == nb:
                pp_stem = four_pillars[pos].heavenly_stem
                is_tiandi = (yun_stem, pp_stem) in STEM_HE or (pp_stem, yun_stem) in STEM_HE
                he_nature = '合绊' if is_tiandi else '合动'
                triggers.append({
                    'kind': 'liuhe', 'source': source, 'position': pos,
                    'branch': nb, 'in_main': nb in main_branches,
                    'mech': f"{source}{yun_branch}合{nb}({pos}支)",
                    'keyword': nb,
                    'he_nature': he_nature,
                    'direction': 'POSITIVE',
                })

        # ── 三合局(运支参与构成三合) ──
        yun_el = _branch_element_cached(yun_branch)
        for sanhe_key, sanhe_set in BRANCH_SANHE.items():
            if yun_branch in sanhe_set:
                # 检查命局是否已有另两支
                present = [b for b in four_branches.values() if b in sanhe_set]
                if len(present) >= 2:
                    # 三合局引动主位判定：运支入主位 或 三合组内已有支在主位（盲派：三合成局=事成）
                    sanhe_in_main = (
                        yun_branch in main_branches
                        or any(b in sanhe_set and b in main_branches for b in four_branches.values())
                    )
                    triggers.append({
                        'kind': 'sanhe', 'source': source, 'position': 'day',
                        'branch': yun_branch, 'in_main': sanhe_in_main,
                        'mech': f"{source}{yun_branch}构成三合局{sanhe_key}",
                        'keyword': sanhe_key,
                        'direction': 'POSITIVE' if sanhe_in_main else 'CHANGE',
                    })
                    break

        # ── 三刑引动(运/年支加入后与命局两支构成三刑) ──
        # 盲派应期: 丑未戌三刑应期, 寅巳申三刑刑坏禄神（盲派应期章）
        four_branch_set = set(four_branches.values())
        # P0-FNDR-05 (R-11 ⑨ 地支关系): BRANCH_SANXING 已拆分为 TRIPLE/DOUBLE/SELF
        # 刑名从 _SANXING_MING 映射表获取 (单源真相)
        from tongshu.engines.bazi_engine import _SANXING_MING
        for xing_set in BRANCH_SANXING_TRIPLE:
            xing_name = _SANXING_MING.get(xing_set, "三刑")
            if yun_branch in xing_set:
                # 命局需已有该三刑组内另外两支(或一支+运支凑三刑)
                present_in_chart = [b for b in four_branch_set if b in xing_set]
                combined = set(present_in_chart) | {yun_branch}
                if xing_set.issubset(combined):
                    in_main = yun_branch in main_branches
                    triggers.append({
                        'kind': 'sanxing', 'source': source, 'position': 'day',
                        'branch': yun_branch, 'in_main': in_main,
                        'mech': f"{source}{yun_branch}引动三刑{xing_name}",
                        'keyword': xing_name,
                        'direction': 'NEGATIVE' if in_main else 'CHANGE',
                    })

        # 二支刑 (子卯) 引动
        for xing_set in BRANCH_SANXING_DOUBLE:
            xing_name = _SANXING_MING.get(xing_set, "二支刑")
            if yun_branch in xing_set:
                present_in_chart = [b for b in four_branch_set if b in xing_set]
                combined = set(present_in_chart) | {yun_branch}
                if xing_set.issubset(combined):
                    in_main = yun_branch in main_branches
                    triggers.append({
                        'kind': 'sanxing', 'source': source, 'position': 'day',
                        'branch': yun_branch, 'in_main': in_main,
                        'mech': f"{source}{yun_branch}引动二支刑{xing_name}",
                        'keyword': xing_name,
                        'direction': 'NEGATIVE' if in_main else 'CHANGE',
                    })

        # ── 自刑(运/年支重复命局中自刑地支, 如辰辰) ──
        # P0-FNDR-05 (R-11 ⑨ 地支关系): 自刑地支集合改为 BRANCH_SANXING_SELF
        if yun_branch in BRANCH_SANXING_SELF and yun_branch in four_branch_set:
            triggers.append({
                'kind': 'zixing', 'source': source, 'position': 'day',
                'branch': yun_branch, 'in_main': yun_branch in main_branches,
                'mech': f"{source}{yun_branch}伏吟自刑(重复)",
                'keyword': yun_branch,
                'direction': 'CHANGE',
            })

        # ── 墓库开闭 ──
        # 开库: 运支冲墓库(冲开) 或 丑未戌三刑刑墓库(刑开) → 财官出
        #   （段建业第02章案例"丙戌年, 戌刑未开库"; VERIFY-BLIND-020: 冲则开库）
        # 闭库: 运支合墓库(库收物) → 收藏聚拢
        #   （本地盲派资料: 闭库=库收物如辰收水=财富聚拢）
        for pos, nb in four_branches.items():
            if nb in MU_KU:
                muku_element = MU_KU[nb]
                in_main = nb in main_branches
                chong_target = BRANCH_CHONG.get(nb)
                xing_open = (
                    nb in ("CHOU", "WEI", "XU")
                    and yun_branch in ("CHOU", "WEI", "XU")
                    and yun_branch != nb
                )
                if chong_target == yun_branch:
                    triggers.append({
                        'kind': 'muku_kai', 'source': source, 'position': pos,
                        'branch': nb, 'in_main': in_main,
                        'mech': f"{source}{yun_branch}冲开{nb}{muku_element}墓",
                        'keyword': nb,
                        'direction': 'POSITIVE' if in_main else 'CHANGE',
                    })
                elif xing_open:
                    triggers.append({
                        'kind': 'muku_kai', 'source': source, 'position': pos,
                        'branch': nb, 'in_main': in_main,
                        'mech': f"{source}{yun_branch}刑开{nb}{muku_element}墓(丑未戌三刑)",
                        'keyword': nb,
                        'direction': 'POSITIVE' if in_main else 'CHANGE',
                    })
                # 闭库: 运支与墓库支六合
                if BRANCH_LIUHE.get(yun_branch) == nb:
                    triggers.append({
                        'kind': 'muku_bi', 'source': source, 'position': pos,
                        'branch': nb, 'in_main': in_main,
                        'mech': f"{source}{yun_branch}合{nb}闭库({muku_element}墓收)",
                        'keyword': nb,
                        'direction': 'POSITIVE' if in_main else 'CHANGE',
                    })

        # ── 合见冲 / 冲见合为应 (段建业第02章: 原局有合,以冲为应; 原局有冲,以合为应) ──
        # 原局六合支对被岁运冲 → 合见冲应期; 原局六冲支对被岁运合 → 冲见合应期
        branch_items = list(four_branches.items())  # [(pos, branch), ...]
        for i in range(len(branch_items)):
            for j in range(i + 1, len(branch_items)):
                pos_a, ba = branch_items[i]
                pos_b, bb = branch_items[j]
                if BRANCH_LIUHE.get(ba) == bb:
                    for pos_x, bx in ((pos_a, ba), (pos_b, bb)):
                        if BRANCH_CHONG.get(yun_branch) == bx:
                            triggers.append({
                                'kind': 'hejianchong', 'source': source, 'position': pos_x,
                                'branch': bx, 'in_main': bx in main_branches,
                                'mech': f"原局{pos_a}{ba}-{pos_b}{bb}合, {source}{yun_branch}冲{bx}=以冲为应",
                                'keyword': bx,
                                'direction': 'NEGATIVE' if bx in main_branches else 'CHANGE',
                            })
                if BRANCH_CHONG.get(ba) == bb:
                    for pos_x, bx in ((pos_a, ba), (pos_b, bb)):
                        if BRANCH_LIUHE.get(yun_branch) == bx:
                            triggers.append({
                                'kind': 'chongjianhe', 'source': source, 'position': pos_x,
                                'branch': bx, 'in_main': bx in main_branches,
                                'mech': f"原局{pos_a}{ba}-{pos_b}{bb}冲, {source}{yun_branch}合{bx}=以合为应",
                                'keyword': bx,
                                'direction': 'POSITIVE' if bx in main_branches else 'CHANGE',
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

        # ── 伏吟/反吟（规则 §48-49）──
        # 伏吟 = 运/年/限柱与命局某柱干支完全相同
        # 反吟 = 运/年/限柱与命局某柱 天干相克 且 地支相冲（天克地冲）
        for pos, pp in four_pillars.items():
            chart_full = f"{pp.heavenly_stem}{pp.earthly_branch}"
            yun_full = f"{yun_stem}{yun_branch}"
            in_main_pos = pos in ("day", "hour")
            # 伏吟
            if yun_full == chart_full:
                triggers.append({
                    'kind': 'fuyin', 'source': source, 'position': pos,
                    'branch': yun_branch, 'in_main': in_main_pos,
                    'mech': f"{source}{yun_full}伏吟{pos}柱{chart_full}",
                    'keyword': yun_full, 'direction': 'CHANGE',
                })
            # 反吟：天克地冲
            else:
                stem_ke = (
                    CONTROLS.get(STEM_ELEMENT.get(yun_stem))
                    == STEM_ELEMENT.get(pp.heavenly_stem)
                )
                if stem_ke and BRANCH_CHONG.get(yun_branch) == pp.earthly_branch:
                    triggers.append({
                        'kind': 'fanyin', 'source': source, 'position': pos,
                        'branch': yun_branch, 'in_main': in_main_pos,
                        'mech': f"{source}{yun_full}反吟{pos}柱{chart_full}(天克地冲)",
                        'keyword': yun_full,
                        'direction': 'NEGATIVE' if in_main_pos else 'CHANGE',
                    })

        # ── 字再现（规则 §55）：运年支同字在命局重现（非自刑支）──
        # 自刑支的重复已在 zixing 处理，此处补普通支的字再现。
        for pos, nb in four_branches.items():
            if nb == yun_branch and nb not in BRANCH_SANXING_SELF:
                in_main = nb in main_branches
                triggers.append({
                    'kind': 'zizaixian', 'source': source, 'position': pos,
                    'branch': nb, 'in_main': in_main,
                    'mech': f"{source}{yun_branch}再现命局{pos}支{nb}",
                    'keyword': nb, 'direction': 'CHANGE',
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

        # 严重度枚举（BLIND-ARCH-006 / BLIND-G16：禁数字化强度）
        # 结构规则：主位被穿/冲/反吟/三刑 = HIGH；主位其余 = MEDIUM；宾位 = LOW
        severity = 'LOW'
        if in_main:
            severity = 'MEDIUM'
            if kind in ('chuan', 'chong', 'fanyin', 'sanxing'):
                severity = 'HIGH'

        base = {
            'mechanism': kind, 'mech': mech, 'keyword': trg.get('keyword', ''),
            'source': trg['source'], 'direction': direction,
            'severity': severity, 'age': age,
        }
        # 应期细化事实透传（旺衰冲应/穿中生克/合动合绊, 段建业第02章）
        for detail_key in ('chong_effect', 'chuan_nature', 'he_nature'):
            if trg.get(detail_key):
                base[detail_key] = trg[detail_key]

        # 按引动类型映射到断事主题
        if kind == 'chuan' and in_main:
            base['topic'] = '穿倒主位'
            base['direction'] = 'NEGATIVE'
        elif kind == 'chong' and in_main:
            base['topic'] = '冲主位'
            base['direction'] = 'NEGATIVE' if '禄' not in str(trg.get('keyword')) else 'CHANGE'
        elif kind == 'muku_kai':
            base['topic'] = '冲开墓库'
            base['direction'] = 'POSITIVE'
        elif kind == 'muku_bi':
            base['topic'] = '闭库'
            base['direction'] = 'POSITIVE' if in_main else 'CHANGE'
        elif kind == 'hejianchong':
            base['topic'] = '合见冲应期'
            base['direction'] = 'NEGATIVE' if in_main else 'CHANGE'
        elif kind == 'chongjianhe':
            base['topic'] = '冲见合应期'
            base['direction'] = 'POSITIVE' if in_main else 'CHANGE'
        elif kind == 'sanhe':
            base['topic'] = '三合局引动'
            base['direction'] = 'POSITIVE'
        elif kind == 'sanxing':
            # 三刑引动: 盲派第02章只论"丑未戌/寅巳申三刑"应凶(案例: 死父/车祸/官非),
            # 不细分恃势/无恩; 恃势(丑戌未)/无恩(寅巳申)/无礼(子卯)细分属
            # 《三命通会》卷二·论三刑(传统口径), 且《渊海子平》称呼相反 ——
            # METHOD_SCOPE=TRADITIONAL 降级标注, 不进盲派核心规则
            base['topic'] = '三刑引动'
            base['direction'] = 'NEGATIVE'
            base['method_scope'] = 'TRADITIONAL'
            k = trg.get('keyword', '')
            if '恃势' in k:
                base['domain'] = '官非刑伤'
                base['domain_scope'] = 'SAN_MING_TONG_HUI'
            elif '无恩' in k:
                base['domain'] = '健康灾伤'
                base['domain_scope'] = 'SAN_MING_TONG_HUI'
            elif '无礼' in k:
                base['domain'] = '婚姻口舌'
                base['domain_scope'] = 'SAN_MING_TONG_HUI'
        elif kind == 'zixing':
            base['topic'] = '伏吟自刑'
            base['direction'] = 'CHANGE'
        elif kind == 'liuhe' and in_main:
            base['topic'] = '合入主位'
            base['direction'] = 'POSITIVE'
        elif kind == 'lu':
            base['topic'] = '禄神重现'
            base['direction'] = 'POSITIVE'
        elif kind == 'tougan':
            tg = trg.get('ten_god', '')
            base['topic'] = '透干应期'
        elif kind == 'fuyin':
            base['topic'] = '伏吟引动'
            base['direction'] = 'CHANGE'
        elif kind == 'fanyin':
            base['topic'] = '反吟引动'
            base['direction'] = 'NEGATIVE' if in_main else 'CHANGE'
        elif kind == 'zizaixian':
            base['topic'] = '字再现引动'
            base['direction'] = 'CHANGE'
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

# 六穿生克性质（段建业第02章案例"寅冲穿巳是动了巳（穿而生，有动意）"
# → 穿中带生=轻/有动意；穿中带克=重/直接受损）
CHUAN_NATURE = {
    # 键为拼音地支(sorted), 与引擎干支枚举一致
    ("WEI", "ZI"): "带克",   # 子未: 未土克子水
    ("CHOU", "WU"): "带生",  # 丑午: 午火生丑土
    ("SI", "YIN"): "带生",   # 寅巳: 寅木生巳火
    ("CHEN", "MAO"): "带克", # 卯辰: 卯木克辰土
    ("HAI", "SHEN"): "带生", # 申亥: 申金生亥水
    ("XU", "YOU"): "带生",   # 酉戌: 戌土生酉金
}


def _chuan_nature(a: str, b: str) -> str:
    """六穿对的生克性质: 带生(轻,有动意) / 带克(重)."""
    return CHUAN_NATURE.get(tuple(sorted([a, b])), "带克")


# 五行相生（用于得令判定: 当令或得月令生 → 旺）
_GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}


def _branch_strong(chart, branch: str) -> bool:
    """支的旺衰（得月令判定）: 当令(同月令五行) 或 得月令生(相) → 旺.

    段建业冲应旺衰以月令为权（盲派弃日主旺衰、用月令轻重），
    此处只做支的得令判定，不引入任何评分。
    """
    month_branch = chart.month_pillar.earthly_branch
    el = _branch_element_cached(branch)
    mel = _branch_element_cached(month_branch)
    return el == mel or _GENERATES.get(mel) == el


def _chong_effect(chart, yun_branch: str, nb: str) -> str:
    """旺衰冲应（段建业第02章: 旺者冲衰为冲去；旺者冲旺为冲起；
    弱神冲旺神为冲起；两弱相冲典未明说→NEUTRAL 不标去/起）."""
    yun_strong = _branch_strong(chart, yun_branch)
    nb_strong = _branch_strong(chart, nb)
    if yun_strong and not nb_strong:
        return "冲去"
    if yun_strong and nb_strong:
        return "冲起"
    if not yun_strong and nb_strong:
        return "冲起"
    return "NEUTRAL"


def analyze_yingqi(birth: Tuple[int, int, int, int], gender: str = "male",
                   target_age: Optional[int] = None,
                   target_year: Optional[int] = None) -> YingqiResult:
    """便捷入口."""
    engine = BlindYingqiEngine()
    return engine.analyze(birth, gender, target_age, target_year)
