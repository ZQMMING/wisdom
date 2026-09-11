# -*- coding: utf-8 -*-
"""BlindPaiEngine — 盲派主引擎（V2 架构，规则 V1-FINAL 生产路径）

生产路径（《盲派生产规则注册表_实现规格_V1-FINAL》）：

    FrozenBaziState → HostGuest(宾主) → BodyUse(体用)
        → WorkGraph(做功图) → WorkChain(做功链)
        → WorkEfficiency(做功强弱 WK-EFFICIENCY-001~005)
        → GongShen(功神/废神) → Evidence(证据) → BlindPaiResult

原则（BLIND-ARCH-001~006）：
- 只消费 BaziChart 事实层，不重排盘（FrozenBaziState = 冻结状态）
- 全布尔/枚举判定，零评分、零百分比、零权重（BLIND-ARCH-004/005/006）
- method_scope 隔离：当前实现 DUAN_JIANYE（段建业主线）
- 没有明确规则 → UNDETERMINED
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from ..bazi_engine import BaziChart
from ..blind_bazi_engine import (
    BRANCH_CHONG,
    BRANCH_CHUAN,
    BRANCH_HIDDEN_STEMS,
    BRANCH_LIUHE,
    BRANCH_SANHE,
    CONTROLS,
    GENERATES,
    GROUP_BI,
    GROUP_CAI,
    GROUP_GUAN,
    GROUP_SHI,
    GROUP_YIN,
    MU_KU,
    STEM_ELEMENT,
    STEM_HE,
    TI_TEN_GODS,
    YONG_TEN_GODS,
    ten_god,
)
from ...facts.bazi_facts import NAYIN_60
from .evidence_producer import (
    BlindEvidenceProducer,
    BlindFeatureState,
    EvidenceItem,
    EvidenceList,
    Relevance,
)
from .palace import PalaceFeatureCalculator, PalaceState
from .workchain import WorkChain, WorkChainResolver
from .workgraph import NodeType, RelationType, WorkEdge, WorkGraph, WorkNode

# ─── 中文干支映射（输出可读层；内部计算用拼音码事实）───────────────────

GAN_ZH = {
    "JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
    "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸",
}
ZHI_ZH = {
    "ZI": "子", "CHOU": "丑", "YIN": "寅", "MAO": "卯", "CHEN": "辰",
    "SI": "巳", "WU": "午", "WEI": "未", "SHEN": "申", "YOU": "酉",
    "XU": "戌", "HAI": "亥",
}


def _gan_zh(gan: str) -> str:
    return GAN_ZH.get(gan, gan)


def _zhi_zh(zhi: str) -> str:
    return ZHI_ZH.get(zhi, zhi)


# ─── 枚举 ─────────────────────────────────────────────────────────────────────

class MethodScope(str, Enum):
    """盲派传承隔离（规则 §4/§90）。当前仅实现段建业主线。"""
    DUAN_JIANYE = "DUAN_JIANYE"
    XIA_ZHONGQI = "XIA_ZHONGQI"
    HAO_JINYANG = "HAO_JINYANG"


class WorkEfficiency(str, Enum):
    """做功强弱四档（WK-EFFICIENCY-001，古籍：大/中/小/无效做功）。"""
    LARGE = "LARGE"      # 大效率
    MEDIUM = "MEDIUM"    # 中效率
    SMALL = "SMALL"      # 小效率
    NONE = "NONE"        # 无效做功
    UNDETERMINED = "UNDETERMINED"


class StructureClarity(str, Enum):
    """结构外显四态（WK-EFFICIENCY-003，古籍：清晰/较清/有杂/混乱）。"""
    CLEAR = "CLEAR"                # 结构清晰
    PARTIALLY_CLEAR = "PARTIALLY_CLEAR"  # 结构较清
    MIXED = "MIXED"                # 结构有杂
    CHAOTIC = "CHAOTIC"            # 结构混乱
    UNDETERMINED = "UNDETERMINED"


class GongShenRole(str, Enum):
    """功神/废神角色（规则 §22/23/77）。"""
    WORKING = "WORKING"        # 功神（实际做功）
    SUPPORTING = "SUPPORTING"  # 辅神（辅助做功）
    TARGET = "TARGET"          # 目标（做功对象）
    BLOCKING = "BLOCKING"      # 阻神（阻断/干扰做功）
    IDLE = "IDLE"              # 闲神（method_scope 定义无作用）
    WASTE = "WASTE"            # 废神（明确规则定义为废）
    UNDETERMINED = "UNDETERMINED"


class HostGuestScope(str, Enum):
    """宾主四 scope（规则 BG-001~005）。"""
    DAYMASTER = "DAYMASTER"      # 日主为体，余为宾
    DAYPILLAR = "DAYPILLAR"      # 日柱为主，年月时为宾
    INNER_OUTER = "INNER_OUTER"  # 内（日时）外（年月）
    TEMPORAL = "TEMPORAL"        # 时间（大运流年）为宾


# ─── 状态数据类 ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class FrozenBaziState:
    """冻结八字事实层 —— 只消费 BaziChart，不重排盘（规则第 0 节）。"""
    birth: Tuple[int, int, int, int]
    gender: str
    day_master: str
    pillars: Tuple[str, str, str, str]      # 四柱干支 (year, month, day, hour)
    stems: Tuple[str, str, str, str]
    branches: Tuple[str, str, str, str]
    hidden_stems: Tuple[Tuple[str, ...], ...]  # 每柱藏干
    ten_gods: Tuple[str, str, str, str]     # 透干十神 (year, month, day=比肩, hour)
    na_yin: Tuple[str, str, str, str]       # 纳音

    @classmethod
    def from_chart(cls, chart: BaziChart, birth: Tuple[int, int, int, int],
                   gender: str) -> "FrozenBaziState":
        ps = [
            chart.year_pillar, chart.month_pillar,
            chart.day_pillar, chart.hour_pillar,
        ]
        return cls(
            birth=birth,
            gender=gender,
            day_master=chart.day_master,
            pillars=tuple(f"{p.heavenly_stem}{p.earthly_branch}" for p in ps),
            stems=tuple(p.heavenly_stem for p in ps),
            branches=tuple(p.earthly_branch for p in ps),
            hidden_stems=tuple(
                tuple(hs for hs, _ in BRANCH_HIDDEN_STEMS.get(p.earthly_branch, []))
                for p in ps
            ),
            ten_gods=(
                ten_god(chart.day_master, ps[0].heavenly_stem),
                ten_god(chart.day_master, ps[1].heavenly_stem),
                "比肩",
                ten_god(chart.day_master, ps[3].heavenly_stem),
            ),
            na_yin=tuple(
                NAYIN_60.get((p.heavenly_stem, p.earthly_branch), "") for p in ps
            ),
        )


@dataclass(frozen=True)
class HostGuestState:
    """宾主判定（规则 §6 BG-001~005）。"""
    main_branches: frozenset = frozenset()
    guest_branches: frozenset = frozenset()
    main_stems: tuple = ()
    guest_stems: tuple = ()
    scopes: tuple = ()          # 命中的宾主 scope 枚举

    def to_dict(self) -> dict:
        return {
            "main_branches": sorted(_zhi_zh(b) for b in self.main_branches),
            "guest_branches": sorted(_zhi_zh(b) for b in self.guest_branches),
            "main_stems": [_gan_zh(s) for s in self.main_stems],
            "guest_stems": [_gan_zh(s) for s in self.guest_stems],
            "scopes": [s.value if isinstance(s, HostGuestScope) else s for s in self.scopes],
        }


@dataclass(frozen=True)
class BodyUseState:
    """体用判定（规则 §7-9 BU-001~011）。"""
    ti_branches: frozenset = frozenset()
    yong_branches: frozenset = frozenset()
    ti_stems: tuple = ()
    yong_stems: tuple = ()
    direction: str = "UNDETERMINED"   # FORWARD（正向做功）/ REVERSE（反向做功）
    ambiguous: bool = False           # BU 静态覆盖冲突 → AMBIGUOUS

    def to_dict(self) -> dict:
        return {
            "ti_branches": sorted(_zhi_zh(b) for b in self.ti_branches),
            "yong_branches": sorted(_zhi_zh(b) for b in self.yong_branches),
            "ti_stems": [_gan_zh(s) for s in self.ti_stems],
            "yong_stems": [_gan_zh(s) for s in self.yong_stems],
            "direction": self.direction,
            "ambiguous": self.ambiguous,
        }


@dataclass(frozen=True)
class WorkEfficiencyState:
    """做功强弱（WK-EFFICIENCY-001~005）。"""
    efficiency: WorkEfficiency = WorkEfficiency.UNDETERMINED
    clarity: StructureClarity = StructureClarity.UNDETERMINED
    path_direct: bool = False      # 做功路径是否直接
    power_concentrated: bool = False  # 做功力量是否集中
    target_effective: bool = False    # 做功对象是否得力
    work_level: str = "UNDETERMINED"  # 做功等级五档（理法-结果层）

    def to_dict(self) -> dict:
        return {
            "efficiency": self.efficiency.value,
            "clarity": self.clarity.value,
            "path_direct": self.path_direct,
            "power_concentrated": self.power_concentrated,
            "target_effective": self.target_effective,
            "work_level": self.work_level,
        }


@dataclass(frozen=True)
class GongShenState:
    """功神/废神角色分配（规则 §22/23/77）。"""
    assignments: Tuple[Tuple[str, str], ...] = ()  # ((node_id, role), ...)

    def to_dict(self) -> dict:
        return {"assignments": [list(a) for a in self.assignments]}


# ─── 主结果 ───────────────────────────────────────────────────────────────────

@dataclass
class BlindPaiResult:
    """盲派主引擎完整输出（全事实 + 已验证中间状态 + 枚举结论）。"""
    method_scope: str = MethodScope.DUAN_JIANYE.value
    frozen: Optional[FrozenBaziState] = None
    host_guest: HostGuestState = field(default_factory=HostGuestState)
    body_use: BodyUseState = field(default_factory=BodyUseState)
    work_graph: Optional[WorkGraph] = None
    work_chains: Tuple[WorkChain, ...] = ()
    work_efficiency: WorkEfficiencyState = field(default_factory=WorkEfficiencyState)
    gong_shen: GongShenState = field(default_factory=GongShenState)
    palace: Optional[PalaceState] = None
    evidence: Optional[EvidenceList] = None
    rules_triggered: Tuple[str, ...] = ()
    undetermined_reasons: Tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "method_scope": self.method_scope,
            "frozen": {
                "birth": list(self.frozen.birth) if self.frozen else None,
                "gender": self.frozen.gender if self.frozen else None,
                "day_master": _gan_zh(self.frozen.day_master) if self.frozen else None,
                "pillars": (
                    [
                        f"{_gan_zh(s)}{_zhi_zh(b)}"
                        for s, b in zip(self.frozen.stems, self.frozen.branches)
                    ]
                    if self.frozen
                    else None
                ),
                "ten_gods": list(self.frozen.ten_gods) if self.frozen else None,
                "na_yin": list(self.frozen.na_yin) if self.frozen else None,
            },
            "host_guest": self.host_guest.to_dict(),
            "body_use": self.body_use.to_dict(),
            "work_graph": self.work_graph.to_dict() if self.work_graph else None,
            "work_chains": [
                {
                    "chain_id": c.chain_id,
                    "nodes": [n.label for n in c.nodes],
                    "relations": c.relation_sequence,
                    "length": c.length,
                }
                for c in self.work_chains
            ],
            "work_efficiency": self.work_efficiency.to_dict(),
            "gong_shen": self.gong_shen.to_dict(),
            "palace": (
                {
                    "pillars": [
                        f"{self.palace.year_stem}{self.palace.year_branch}",
                        f"{self.palace.month_stem}{self.palace.month_branch}",
                        f"{self.palace.day_stem}{self.palace.day_branch}",
                        f"{self.palace.hour_stem}{self.palace.hour_branch}",
                    ],
                    "semantics": dict(self.palace.semantics),
                    "source": self.palace.source,
                }
                if self.palace
                else None
            ),
            "evidence": self.evidence.to_dict() if self.evidence else None,
            "rules_triggered": list(self.rules_triggered),
            "undetermined_reasons": list(self.undetermined_reasons),
        }


# ─── 主引擎 ───────────────────────────────────────────────────────────────────

class BlindPaiEngine:
    """盲派主引擎（V2）。

    输入：BaziChart（事实层，一次排盘冻结）
    输出：BlindPaiResult
    """

    def __init__(self, method_scope: MethodScope = MethodScope.DUAN_JIANYE) -> None:
        self.method_scope = method_scope
        self._palace = PalaceFeatureCalculator()

    # ── 主入口 ────────────────────────────────────────────

    def compute_from_chart(
        self,
        chart: BaziChart,
        birth: Tuple[int, int, int, int],
        gender: str = "male",
    ) -> BlindPaiResult:
        """从 BaziChart 计算（FrozenBaziState 只消费，不重排盘）。"""
        frozen = FrozenBaziState.from_chart(chart, birth, gender)

        host_guest = self._resolve_host_guest(frozen)
        body_use = self._resolve_body_use(frozen, host_guest)

        graph = self._build_work_graph(frozen, body_use)
        chains = self._resolve_chains(graph, body_use)

        efficiency = self._resolve_work_efficiency(graph, chains, body_use)
        gong_shen = self._resolve_gong_shen(graph, chains, body_use)

        palace = self._palace.calculate(
            year_stem=frozen.stems[0], year_branch=frozen.branches[0],
            month_stem=frozen.stems[1], month_branch=frozen.branches[1],
            day_stem=frozen.stems[2], day_branch=frozen.branches[2],
            hour_stem=frozen.stems[3], hour_branch=frozen.branches[3],
        )

        evidence = self._build_evidence(
            frozen, host_guest, body_use, graph, chains, efficiency,
        )

        rules_triggered, undetermined = self._collect_rules(
            host_guest, body_use, graph, chains, efficiency,
        )

        return BlindPaiResult(
            method_scope=self.method_scope.value,
            frozen=frozen,
            host_guest=host_guest,
            body_use=body_use,
            work_graph=graph,
            work_chains=tuple(chains),
            work_efficiency=efficiency,
            gong_shen=gong_shen,
            palace=palace,
            evidence=evidence,
            rules_triggered=tuple(rules_triggered),
            undetermined_reasons=tuple(undetermined),
        )

    def compute(
        self,
        birth: Tuple[int, int, int, int],
        gender: str = "male",
        chart: Optional[BaziChart] = None,
    ) -> BlindPaiResult:
        """兼容入口：无 chart 时由调用方保证已排盘；否则要求传入 chart。"""
        if chart is None:
            raise ValueError(
                "BlindPaiEngine 只消费 BaziChart 事实层（FrozenBaziState），"
                "不重排盘；请先排盘后传入 chart。"
            )
        return self.compute_from_chart(chart, birth, gender)

    # ── 宾主（规则 BG-001~005）────────────────────────────

    def _resolve_host_guest(self, frozen: FrozenBaziState) -> HostGuestState:
        """宾主四 scope。

        DAYPILLAR（主）：日柱为主，年月时为宾
        INNER_OUTER（内）：日时为内/主，年月为外/宾
        TEMPORAL：时间层（大运流年）为宾 —— 本引擎无时间输入时为 UNDETERMINED
        DAYMASTER：日主为体（主），余为宾
        """
        b = frozen.branches
        main_branches: Set[str] = set()
        guest_branches: Set[str] = set()
        scopes: List[HostGuestScope] = []

        # BG: 日柱为主
        main_branches.add(b[2])
        guest_branches.update({b[0], b[1], b[3]})
        scopes.append(HostGuestScope.DAYPILLAR)

        # 内外：日时内，年月外
        scopes.append(HostGuestScope.INNER_OUTER)

        # 日主为体
        scopes.append(HostGuestScope.DAYMASTER)

        return HostGuestState(
            main_branches=frozenset(main_branches),
            guest_branches=frozenset(guest_branches),
            main_stems=(frozen.stems[2],),
            guest_stems=(frozen.stems[0], frozen.stems[1], frozen.stems[3]),
            scopes=tuple(scopes),
        )

    # ── 体用（规则 BU-001~011）────────────────────────────

    def _resolve_body_use(
        self,
        frozen: FrozenBaziState,
        host_guest: HostGuestState,
    ) -> BodyUseState:
        """体（本钱）= 日主/比劫/印/食伤/禄；用（目标）= 财/官杀。

        V2.6 修正保留：日支为日主之根天然属体；按藏干十神分类，一支可同时属体用。
        """
        day_master = frozen.day_master
        b = frozen.branches
        ti_branches: Set[str] = {b[2]}  # 日支天然属体
        yong_branches: Set[str] = set()

        for br in b:
            for hidden_stem, _pos in BRANCH_HIDDEN_STEMS.get(br, []):
                tg = ten_god(day_master, hidden_stem)
                if tg in TI_TEN_GODS:
                    ti_branches.add(br)
                elif tg in YONG_TEN_GODS:
                    yong_branches.add(br)

        stems = frozen.stems
        ti_stems = tuple(
            stems[i] for i in (0, 1, 3)
            if ten_god(day_master, stems[i]) in TI_TEN_GODS
        )
        yong_stems = tuple(
            stems[i] for i in (0, 1, 3)
            if ten_god(day_master, stems[i]) in YONG_TEN_GODS
        )

        # 方向：体在主位（日时）取宾位用 = FORWARD；用克体 = REVERSE
        direction = "UNDETERMINED"
        if yong_branches or yong_stems:
            # 用位于宾位（年月）为主取用 = 正向
            outer_yong = any(br in {b[0], b[1]} for br in yong_branches)
            inner_ti = any(br in {b[2], b[3]} for br in ti_branches)
            if inner_ti and outer_yong:
                direction = "FORWARD"
            else:
                direction = "REVERSE"

        # AMBIGUOUS：日支既含体又含用且无主位优先 → 静态覆盖冲突
        day_tg_set = {
            ten_god(day_master, hs) for hs, _ in BRANCH_HIDDEN_STEMS.get(b[2], [])
        }
        ambiguous = bool(
            day_tg_set & set(TI_TEN_GODS) and day_tg_set & set(YONG_TEN_GODS)
        )

        return BodyUseState(
            ti_branches=frozenset(ti_branches),
            yong_branches=frozenset(yong_branches),
            ti_stems=ti_stems,
            yong_stems=yong_stems,
            direction=direction,
            ambiguous=ambiguous,
        )

    # ── 做功图（规则 WORK-001/002 + 制/合/冲/刑/穿/墓/生/泄/化）────────

    def _build_work_graph(
        self,
        frozen: FrozenBaziState,
        body_use: BodyUseState,
    ) -> WorkGraph:
        """构建做功关系图。

        节点：透干十神节点 + 地支节点（含藏干十神）
        边：制(ZHI)/生(SHENG)/合(HE)/冲(CHONG)/穿(CHUAN)/墓(STORE)/复合(COMPOSITE)
        只建立 体→用 方向的有效做功边（距离<=2，规则 WK-CONTROL 系）。
        """
        graph = WorkGraph()
        day_master = frozen.day_master
        b = frozen.branches
        s = frozen.stems

        # ── 节点 ──
        node_ids: Set[str] = set()
        for i in range(4):
            tg = "比肩" if i == 2 else ten_god(day_master, s[i])
            nid = f"stem_{i}"
            graph.add_node(WorkNode(id=nid, type=NodeType.STEM, value=s[i], position=f"柱{i}"))
            graph.add_node(WorkNode(id=f"tg_{nid}", type=NodeType.TEN_GOD, value=tg, position=f"柱{i}"))
            node_ids.add(nid)
            bnode = f"branch_{i}"
            graph.add_node(WorkNode(id=bnode, type=NodeType.BRANCH, value=b[i], position=f"柱{i}"))
            node_ids.add(bnode)

        # ── 体用集合 ──
        ti_node_ids: Set[str] = set()
        yong_node_ids: Set[str] = set()
        for i in range(4):
            tg = "比肩" if i == 2 else ten_god(day_master, s[i])
            if tg in TI_TEN_GODS or i == 2:
                ti_node_ids.add(f"tg_stem_{i}")
            if tg in YONG_TEN_GODS:
                yong_node_ids.add(f"tg_stem_{i}")
        # 地支藏干体用
        for i in range(4):
            for hidden_stem, _pos in BRANCH_HIDDEN_STEMS.get(b[i], []):
                tg = ten_god(day_master, hidden_stem)
                bnode = f"branch_{i}"
                nid = f"{bnode}_h_{hidden_stem}"
                graph.add_node(WorkNode(id=nid, type=NodeType.TEN_GOD, value=tg, position=f"柱{i}藏"))
                if tg in TI_TEN_GODS:
                    ti_node_ids.add(nid)
                if tg in YONG_TEN_GODS:
                    yong_node_ids.add(nid)

        # ── 边：体→用 有效作用（距离<=2）──
        edge_keys: Set[Tuple[str, str, str]] = set()
        for ti_idx in range(4):
            for yong_idx in range(4):
                if ti_idx == yong_idx:
                    continue
                distance = abs(ti_idx - yong_idx)
                if distance > 2:
                    continue

                ti_branch, yong_branch = b[ti_idx], b[yong_idx]
                ti_stem, yong_stem = s[ti_idx], s[yong_idx]

                relation = None
                # 天干五合
                if (ti_stem, yong_stem) in STEM_HE or (yong_stem, ti_stem) in STEM_HE:
                    relation = RelationType.HE
                # 地支六合
                if relation is None and BRANCH_LIUHE.get(ti_branch) == yong_branch:
                    relation = RelationType.HE
                # 地支六冲
                if relation is None and BRANCH_CHONG.get(ti_branch) == yong_branch:
                    relation = RelationType.CHONG
                # 地支六穿
                if relation is None and BRANCH_CHUAN.get(ti_branch) == yong_branch:
                    relation = RelationType.ZHI  # 穿制 = 制
                # 五行制（体克用）
                if relation is None and CONTROLS.get(STEM_ELEMENT[ti_stem]) == STEM_ELEMENT[yong_stem]:
                    relation = RelationType.ZHI
                # 五行生（体生用 / 用生体 均记 SHENG，方向见链）
                if relation is None and (
                    GENERATES.get(STEM_ELEMENT[ti_stem]) == STEM_ELEMENT[yong_stem]
                    or GENERATES.get(STEM_ELEMENT[yong_stem]) == STEM_ELEMENT[ti_stem]
                ):
                    relation = RelationType.SHENG

                if relation is None:
                    continue

                src = f"tg_stem_{ti_idx}"
                tgt = f"tg_stem_{yong_idx}"
                key = (src, tgt, relation.value)
                if key in edge_keys:
                    continue
                edge_keys.add(key)
                graph.add_edge(WorkEdge(source=src, target=tgt, relation=relation, valid=True))

        # ── 墓库边（规则 WK-STORE-001~003）：辰戌丑未 ──
        branches_list = list(b)
        for i, br in enumerate(branches_list):
            if br not in MU_KU:
                continue
            muku_element = MU_KU[br]
            chong_target = BRANCH_CHONG.get(br)
            is_chonged = chong_target in branches_list
            # 冲库开库 = 库→该五行目标节点 的 STORE 边
            if is_chonged:
                for j, other_br in enumerate(branches_list):
                    if j == i:
                        continue
                    for hidden_stem, _pos in BRANCH_HIDDEN_STEMS.get(other_br, []):
                        if STEM_ELEMENT.get(hidden_stem) == muku_element:
                            src = f"branch_{i}"
                            tgt = f"branch_{j}_h_{hidden_stem}"
                            key = (src, tgt, "STORE")
                            if key not in edge_keys:
                                edge_keys.add(key)
                                graph.add_edge(
                                    WorkEdge(source=src, target=tgt, relation=RelationType.ZHI, valid=True)
                                )

        return graph

    # ── 做功链（WORK-001/002）─────────────────────────────

    def _resolve_chains(
        self,
        graph: WorkGraph,
        body_use: BodyUseState,
    ) -> List[WorkChain]:
        """从体节点出发找用到节点的有向做功链。"""
        if graph.node_count() == 0:
            return []
        resolver = WorkChainResolver(graph, max_depth=6)
        return resolver.resolve()

    # ── 做功强弱（WK-EFFICIENCY-001~005）──────────────────

    def _resolve_work_efficiency(
        self,
        graph: WorkGraph,
        chains: List[WorkChain],
        body_use: BodyUseState,
    ) -> WorkEfficiencyState:
        """三判据（古籍原文）→ 做功强弱四档。

        WK-EFFICIENCY-002:
          路径直接 AND 力量集中 AND 对象得力 → LARGE
          路径直接 AND (力量集中 OR 对象得力) → MEDIUM
          路径直接 AND NOT 力量集中 AND NOT 对象得力 → SMALL
          NOT 路径直接 OR 做功有误 → NONE
        """
        if not chains:
            return WorkEfficiencyState(efficiency=WorkEfficiency.NONE, clarity=StructureClarity.CHAOTIC)

        # 判据1：路径直接 —— 存在从体到用的单一明确做功链（无阻断）
        path_direct = bool(chains) and any(
            c.length == 1 for c in chains
        ) or bool(chains) and all(
            all(e.valid for e in c.edges) for c in chains
        )

        # 判据2：力量集中 —— 做功链数<=1（单一作用集），禁 actor_count>=3 围制
        power_concentrated = len(chains) <= 1

        # 判据3：对象得力 —— 目标（用）节点未被反向制、链末端有效
        target_effective = any(
            len(c.edges) >= 1 and c.edges[-1].valid for c in chains
        )

        if path_direct and power_concentrated and target_effective:
            eff = WorkEfficiency.LARGE
            clarity = StructureClarity.CLEAR
        elif path_direct and (power_concentrated or target_effective):
            eff = WorkEfficiency.MEDIUM
            clarity = StructureClarity.PARTIALLY_CLEAR
        elif path_direct:
            eff = WorkEfficiency.SMALL
            clarity = StructureClarity.MIXED
        else:
            eff = WorkEfficiency.NONE
            clarity = StructureClarity.CHAOTIC

        # WK-EFFICIENCY-004：做功等级（理法-结果层）
        level = {
            WorkEfficiency.LARGE: "LARGE_NOBLE",
            WorkEfficiency.MEDIUM: "MEDIUM_NOBLE",
            WorkEfficiency.SMALL: "SMALL_NOBLE",
            WorkEfficiency.NONE: "POOR",
            WorkEfficiency.UNDETERMINED: "UNDETERMINED",
        }[eff]

        return WorkEfficiencyState(
            efficiency=eff,
            clarity=clarity,
            path_direct=path_direct,
            power_concentrated=power_concentrated,
            target_effective=target_effective,
            work_level=level,
        )

    # ── 功神/废神（规则 GS-001~003 / §77）─────────────────

    def _resolve_gong_shen(
        self,
        graph: WorkGraph,
        chains: List[WorkChain],
        body_use: BodyUseState,
    ) -> GongShenState:
        """角色分配：
        - 链上起点（体）= WORKING（功神）
        - 链上中间节点 = SUPPORTING（辅神）
        - 链上终点（用）= TARGET（目标）
        - 有边但不在任何链 = IDLE（当前 method_scope 定义为闲）
        - 无做功 = 全部 UNDETERMINED
        """
        if not chains:
            return GongShenState(assignments=())
        assignments: Dict[str, str] = {}
        for c in chains:
            for j, n in enumerate(c.nodes):
                if j == 0:
                    assignments[n.id] = GongShenRole.WORKING.value
                elif j == len(c.nodes) - 1:
                    assignments[n.id] = GongShenRole.TARGET.value
                else:
                    assignments[n.id] = GongShenRole.SUPPORTING.value
        return GongShenState(assignments=tuple(sorted(assignments.items())))

    # ── 证据（EvidenceProducer 扩展）──────────────────────

    def _build_evidence(
        self,
        frozen: FrozenBaziState,
        host_guest: HostGuestState,
        body_use: BodyUseState,
        graph: WorkGraph,
        chains: List[WorkChain],
        efficiency: WorkEfficiencyState,
    ) -> EvidenceList:
        evidences = EvidenceList()
        # 复用证据生产者（宾主/体用/做功结构/透干）
        feature = BlindFeatureState(
            main_branches=host_guest.main_branches,
            guest_branches=host_guest.guest_branches,
            ti_branches=body_use.ti_branches,
            yong_branches=body_use.yong_branches,
            ti_stems=body_use.ti_stems,
            yong_stems=body_use.yong_stems,
            zuo_gong=bool(chains),
            zuo_gong_type="做功链",
            zuo_gong_methods=tuple(c.relation_sequence for c in chains),
            zuo_gong_detail=tuple(str(c) for c in chains),
            transparent_ten_gods=tuple(
                (f"{['年','月','日','时'][i]}柱", tg) for i, tg in enumerate(frozen.ten_gods)
            ),
        )
        base = BlindEvidenceProducer().produce(feature)
        evidences.items.extend(base.items)

        # 做功强弱证据（WK-EFFICIENCY）
        evidences.add(EvidenceItem(
            id="E-BLIND-WORK_EFFICIENCY-001",
            source="《盲派初级命理学》段建业·第二章 做功详解·第二节 做功效率·p.20-25",
            content=(
                f"做功强弱三判据：路径直接={efficiency.path_direct}，"
                f"力量集中={efficiency.power_concentrated}，对象得力={efficiency.target_effective}"
                f" → {efficiency.efficiency.value}"
            ),
            relevance=Relevance.HIGH if efficiency.efficiency != WorkEfficiency.NONE else Relevance.MEDIUM,
            valid=True,
        ))
        return evidences

    # ── 规则触发收集 ──────────────────────────────────────

    def _collect_rules(
        self,
        host_guest: HostGuestState,
        body_use: BodyUseState,
        graph: WorkGraph,
        chains: List[WorkChain],
        efficiency: WorkEfficiencyState,
    ) -> Tuple[List[str], List[str]]:
        rules: List[str] = []
        undetermined: List[str] = []

        rules.append("BG-001")
        if body_use.ti_branches:
            rules.append("BU-001")
        if body_use.yong_branches:
            rules.append("BU-002")
        if chains:
            rules.append("WORK-001")
            rules.append("WK-EFFICIENCY-002")
            rules.append("WK-EFFICIENCY-003")
        else:
            undetermined.append("无有效做功链：WORK-001 未命中 → 做功强弱按 NONE 处理")
        if efficiency.efficiency != WorkEfficiency.UNDETERMINED:
            rules.append("WK-EFFICIENCY-001")
        if host_guest.scopes:
            rules.append("BG-005")

        return rules, undetermined
