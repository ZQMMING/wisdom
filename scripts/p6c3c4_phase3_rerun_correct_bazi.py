"""P6-C-3C-4 Phase 3 Rerun - 用正确八字重跑格局/调候/强弱Selection.

基准命例: GOLDEN_CASE_1983_MALE (Birth Chart Evidence Lock Hash: 66d485306b5d5a7b)
原始输入: 农历1983年九月二十九, 午时, 男
正确八字: 癸亥年 壬戌月 乙未日 壬午时
日主: 乙木 (阴木)
格局: 正财格 (月令主气戊土=正财)
调候: 乙木生于戌月
五行: 水0.5极旺, 土0.25, 木0.125, 火0.125, 金0缺
五行失衡: True

注意: 此脚本仅输出Selection结果供审计, 不自行定义PASS/FAIL.
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from tongshu.engines.bazi_engine import (
    BaziEngine, BaziChart,
    STEM_ELEMENT,
)


# ============================================================================
# 数据结构 (与Phase 3-3一致, 支持三种Condition Pattern)
# ============================================================================

class Position(str, Enum):
    YEAR = "YEAR"; MONTH = "MONTH"; DAY = "DAY"; HOUR = "HOUR"

class TenGod(str, Enum):
    ZHENG_YIN="ZHENG_YIN"; PIAN_YIN="PIAN_YIN"; SHI_SHEN="SHI_SHEN"
    SHANG_GUAN="SHANG_GUAN"; ZHENG_GUAN="ZHENG_GUAN"; QI_SHA="QI_SHA"
    ZHENG_CAI="ZHENG_CAI"; PIAN_CAI="PIAN_CAI"; BI_JIAN="BI_JIAN"; JIE_CAI="JIE_CAI"

@dataclass(frozen=True)
class StaticGraphNode:
    node_id: str; position: Position; stem: Optional[str]=None
    branch: Optional[str]=None; ten_god: Optional[TenGod]=None
    layer: str="NATAL"; is_main_qi: bool=False

@dataclass
class StaticGraphContext:
    birth_data: tuple; gender: str; day_master: str; month_branch: str
    day_master_element: str; day_master_element_ratio: float
    five_element_balance: dict; dominant_element: Optional[str]
    five_element_imbalance: bool
    nodes: list[StaticGraphNode]=field(default_factory=list)

@dataclass
class StaticJudgmentCondition:
    condition_id: str
    # 格局模式 (Node Pattern)
    required_ten_god: Optional[TenGod]=None; required_position: Optional[Position]=None
    required_stem: Optional[str]=None; required_branch: Optional[str]=None
    is_month_main_qi: Optional[bool]=None
    # 调候模式 (Field Pattern)
    required_day_master: Optional[str]=None; required_month_branch: Optional[str]=None
    # 强弱模式 (Composite Pattern)
    required_day_master_element_ratio_min: Optional[float]=None
    required_day_master_element_ratio_max: Optional[float]=None
    required_dominant_element: Optional[str]=None; required_imbalance: Optional[bool]=None
    description: str=""

@dataclass
class StaticCanonicalJudgment:
    judgment_id: str; school: str; judgment_type: str; classical: str
    conditions: list[StaticJudgmentCondition]; require_all: bool=True; match_mode: str="GRAPH_EXACT"

@dataclass
class StaticSelectionResult:
    judgment_id: str; selected: bool; reason: str
    matched_conditions: list[str]=field(default_factory=list)
    failed_conditions: list[str]=field(default_factory=list)


# ============================================================================
# 工具函数
# ============================================================================

_GENERATES={"WOOD":"FIRE","FIRE":"EARTH","EARTH":"METAL","METAL":"WATER","WATER":"WOOD"}
_CONTROLS={"WOOD":"EARTH","EARTH":"WATER","WATER":"FIRE","FIRE":"METAL","METAL":"WOOD"}

def get_ten_god(dm, other):
    dm_e=STEM_ELEMENT[dm]; dm_p=dm in ("JIA","BING","WU","GENG","REN")
    o_e=STEM_ELEMENT[other]; o_p=other in ("JIA","BING","WU","GENG","REN")
    same=dm_p==o_p
    if dm_e==o_e: return TenGod.BI_JIAN if same else TenGod.JIE_CAI
    elif _GENERATES.get(o_e)==dm_e: return TenGod.ZHENG_YIN if not same else TenGod.PIAN_YIN
    elif _GENERATES.get(dm_e)==o_e: return TenGod.SHI_SHEN if same else TenGod.SHANG_GUAN
    elif _CONTROLS.get(o_e)==dm_e: return TenGod.ZHENG_GUAN if not same else TenGod.QI_SHA
    elif _CONTROLS.get(dm_e)==o_e: return TenGod.ZHENG_CAI if not same else TenGod.PIAN_CAI
    raise ValueError(f"Cannot determine ten god for {dm} and {other}")

def _get_branch_main_qi_stem(branch):
    return {"ZI":"GUI","CHOU":"JI","YIN":"JIA","MAO":"YI","CHEN":"WU","SI":"BING",
            "WU":"DING","WEI":"JI","SHEN":"GENG","YOU":"XIN","XU":"WU","HAI":"REN"}.get(branch,"JIA")

def _compute_dominant_element(balance):
    if not balance: return None
    mx=max(balance.values()); dom=[e for e,r in balance.items() if r==mx]
    return dom[0] if len(dom)==1 else None

def build_context(chart):
    dm=chart.day_pillar.heavenly_stem; mb=chart.month_pillar.earthly_branch
    dm_e=STEM_ELEMENT[dm]; bal=chart.five_element_balance
    dm_r=bal.get(dm_e,0.0); dom=_compute_dominant_element(bal)
    ctx=StaticGraphContext(
        birth_data=(1983,11,3,12), gender="male", day_master=dm, month_branch=mb,
        day_master_element=dm_e, day_master_element_ratio=dm_r,
        five_element_balance=bal, dominant_element=dom,
        five_element_imbalance=chart.five_element_imbalance,
    )
    pillars=[(Position.YEAR,chart.year_pillar.heavenly_stem,chart.year_pillar.earthly_branch),
             (Position.MONTH,chart.month_pillar.heavenly_stem,chart.month_pillar.earthly_branch),
             (Position.DAY,chart.day_pillar.heavenly_stem,chart.day_pillar.earthly_branch),
             (Position.HOUR,chart.hour_pillar.heavenly_stem,chart.hour_pillar.earthly_branch)]
    for pos,stem,branch in pillars:
        if pos!=Position.DAY:
            tg=get_ten_god(dm,stem)
            ctx.nodes.append(StaticGraphNode(node_id=f"NATAL-{pos.value}-STEM-{stem}-{tg.value}",
                position=pos,stem=stem,ten_god=tg,layer="NATAL"))
        else:
            ctx.nodes.append(StaticGraphNode(node_id=f"NATAL-{pos.value}-STEM-{stem}-DAY_MASTER",
                position=pos,stem=stem,layer="NATAL"))
    mm_tg=get_ten_god(dm,_get_branch_main_qi_stem(mb))
    ctx.nodes.append(StaticGraphNode(node_id=f"NATAL-MONTH-MAIN_QI-{mb}-{mm_tg.value}",
        position=Position.MONTH,branch=mb,ten_god=mm_tg,layer="NATAL",is_main_qi=True))
    return ctx


# ============================================================================
# Resolver (generic, 不被Asset Type绑架)
# ============================================================================

class StaticGraphResolver:
    def __init__(self, judgments): self.judgments=judgments
    def select(self, context):
        return [StaticSelectionResult(judgment_id=j.judgment_id,selected=s,reason=r,
                matched_conditions=m,failed_conditions=f)
                for j in self.judgments for s,r,m,f in [self._match(j,context)]]
    def _match(self, j, ctx):
        matched=[]; failed=[]
        for c in j.conditions:
            if self._match_condition(c,ctx): matched.append(c.condition_id)
            else: failed.append(c.condition_id)
        if j.require_all:
            sel=len(failed)==0
            r=f"ALL satisfied ({len(matched)}/{len(j.conditions)})" if sel else f"NOT all ({len(matched)}/{len(j.conditions)}, failed={failed})"
        else:
            sel=len(matched)>0; r=f"ANY satisfied ({len(matched)}/{len(j.conditions)})" if sel else "NO condition satisfied"
        return sel,r,matched,failed
    def _match_condition(self, c, ctx):
        # 强弱模式
        if c.required_day_master_element_ratio_min is not None and ctx.day_master_element_ratio <= c.required_day_master_element_ratio_min: return False
        if c.required_day_master_element_ratio_max is not None and ctx.day_master_element_ratio >= c.required_day_master_element_ratio_max: return False
        if c.required_dominant_element is not None and ctx.dominant_element != c.required_dominant_element: return False
        if c.required_imbalance is not None and ctx.five_element_imbalance != c.required_imbalance: return False
        # 调候模式
        if c.required_day_master is not None and ctx.day_master != c.required_day_master: return False
        if c.required_month_branch is not None and ctx.month_branch != c.required_month_branch: return False
        # 格局模式
        cand=ctx.nodes
        if c.required_ten_god: cand=[n for n in cand if n.ten_god==c.required_ten_god]
        if c.required_position: cand=[n for n in cand if n.position==c.required_position]
        if c.is_month_main_qi is not None: cand=[n for n in cand if n.is_main_qi==c.is_month_main_qi]
        if c.required_stem: cand=[n for n in cand if n.stem==c.required_stem]
        if c.required_branch: cand=[n for n in cand if n.branch==c.required_branch]
        has_node_filters=any([c.required_ten_god,c.required_position,c.is_month_main_qi is not None,c.required_stem,c.required_branch])
        if has_node_filters and len(cand)==0: return False
        return True


# ============================================================================
# Judgment 定义 (格局10 + 调候5 + 强弱5)
# ============================================================================

def get_pattern_judgments():
    return [
        StaticCanonicalJudgment("SG-ZP-PAT-001","ZI_PING_ZHEN_QUAN","PATTERN","正财格，月令正财，身强喜财官",
            [StaticJudgmentCondition("P001-1",required_ten_god=TenGod.ZHENG_CAI,required_position=Position.MONTH,is_month_main_qi=True,description="月令主气正财")],match_mode="GRAPH_EXACT"),
        StaticCanonicalJudgment("SG-ZP-PAT-002","ZI_PING_ZHEN_QUAN","PATTERN","正官格，月令正官，身强喜官印",
            [StaticJudgmentCondition("P002-1",required_ten_god=TenGod.ZHENG_GUAN,required_position=Position.MONTH,is_month_main_qi=True,description="月令主气正官")],match_mode="GRAPH_EXACT"),
        StaticCanonicalJudgment("SG-ZP-PAT-003","ZI_PING_ZHEN_QUAN","PATTERN","食神格，月令食神，身强喜食伤生财",
            [StaticJudgmentCondition("P003-1",required_ten_god=TenGod.SHI_SHEN,required_position=Position.MONTH,is_month_main_qi=True,description="月令主气食神")],match_mode="GRAPH_EXACT"),
        StaticCanonicalJudgment("SG-ZP-PAT-004","ZI_PING_ZHEN_QUAN","PATTERN","偏印格，月令偏印，身弱喜印比",
            [StaticJudgmentCondition("P004-1",required_ten_god=TenGod.PIAN_YIN,required_position=Position.MONTH,is_month_main_qi=True,description="月令主气偏印")],match_mode="GRAPH_EXACT"),
        StaticCanonicalJudgment("SG-ZP-PAT-005","ZI_PING_ZHEN_QUAN","PATTERN","七杀格，月令七杀，身强喜杀印",
            [StaticJudgmentCondition("P005-1",required_ten_god=TenGod.QI_SHA,required_position=Position.MONTH,is_month_main_qi=True,description="月令主气七杀")],match_mode="GRAPH_EXACT"),
        StaticCanonicalJudgment("SG-ZP-PAT-006","ZI_PING_ZHEN_QUAN","PATTERN","财格成格，月令正财+食神生财",
            [StaticJudgmentCondition("P006-1",required_ten_god=TenGod.ZHENG_CAI,required_position=Position.MONTH,is_month_main_qi=True),
             StaticJudgmentCondition("P006-2",required_ten_god=TenGod.SHI_SHEN)],require_all=True,match_mode="COMPOSITE"),
        StaticCanonicalJudgment("SG-ZP-PAT-007","ZI_PING_ZHEN_QUAN","PATTERN","官格成格，月令正官+正财生官",
            [StaticJudgmentCondition("P007-1",required_ten_god=TenGod.ZHENG_GUAN,required_position=Position.MONTH,is_month_main_qi=True),
             StaticJudgmentCondition("P007-2",required_ten_god=TenGod.ZHENG_CAI)],require_all=True,match_mode="COMPOSITE"),
        StaticCanonicalJudgment("SG-ZP-PAT-008","ZI_PING_ZHEN_QUAN","PATTERN","财格败格，月令正财+比劫夺财",
            [StaticJudgmentCondition("P008-1",required_ten_god=TenGod.ZHENG_CAI,required_position=Position.MONTH,is_month_main_qi=True),
             StaticJudgmentCondition("P008-2",required_ten_god=TenGod.BI_JIAN)],require_all=True,match_mode="COMPOSITE"),
        StaticCanonicalJudgment("SG-ZP-PAT-009","ZI_PING_ZHEN_QUAN","PATTERN","官格败格，月令正官+伤官见官",
            [StaticJudgmentCondition("P009-1",required_ten_god=TenGod.ZHENG_GUAN,required_position=Position.MONTH,is_month_main_qi=True),
             StaticJudgmentCondition("P009-2",required_ten_god=TenGod.SHANG_GUAN)],require_all=True,match_mode="COMPOSITE"),
        StaticCanonicalJudgment("SG-ZP-PAT-010","ZI_PING_ZHEN_QUAN","PATTERN","用神正财，身强取财为用",
            [StaticJudgmentCondition("P010-1",required_ten_god=TenGod.ZHENG_CAI)],match_mode="CONDITION"),
    ]

def get_tuning_judgments():
    return [
        StaticCanonicalJudgment("SG-ZP-TUN-001","QIONG_TONG_BAO_JIAN","TUNING","乙木生于戌月，先取癸水滋润，次取丙火照暖",
            [StaticJudgmentCondition("T001-1",required_day_master="YI",required_month_branch="XU",description="乙木生于戌月")],match_mode="CONDITION"),
        StaticCanonicalJudgment("SG-ZP-TUN-002","QIONG_TONG_BAO_JIAN","TUNING","甲木生于寅月，取丙火泄秀，癸水滋润",
            [StaticJudgmentCondition("T002-1",required_day_master="JIA",required_month_branch="YIN",description="甲木生于寅月")],match_mode="CONDITION"),
        StaticCanonicalJudgment("SG-ZP-TUN-003","QIONG_TONG_BAO_JIAN","TUNING","丙火生于子月，取壬水辅丙，甲木生丙",
            [StaticJudgmentCondition("T003-1",required_day_master="BING",required_month_branch="ZI",description="丙火生于子月")],match_mode="CONDITION"),
        StaticCanonicalJudgment("SG-ZP-TUN-004","QIONG_TONG_BAO_JIAN","TUNING","丁火生于酉月，取甲木引丁，庚金劈甲",
            [StaticJudgmentCondition("T004-1",required_day_master="DING",required_month_branch="YOU",description="丁火生于酉月")],match_mode="CONDITION"),
        StaticCanonicalJudgment("SG-ZP-TUN-005","QIONG_TONG_BAO_JIAN","TUNING","戊土生于午月，取壬水润土，甲木疏土",
            [StaticJudgmentCondition("T005-1",required_day_master="WU",required_month_branch="WU",description="戊土生于午月")],match_mode="CONDITION"),
    ]

def get_strength_judgments():
    return [
        StaticCanonicalJudgment("SG-ZP-STR-001","DI_TIAN_SUI","STRENGTH","日主身弱，喜印比生扶，忌财官克泄",
            [StaticJudgmentCondition("S001-1",required_day_master_element_ratio_max=0.15,description="日主五行比例<0.15→身弱")],match_mode="CONDITION"),
        StaticCanonicalJudgment("SG-ZP-STR-002","DI_TIAN_SUI","STRENGTH","日主身强，喜财官食伤克泄，忌印比生扶",
            [StaticJudgmentCondition("S002-1",required_day_master_element_ratio_min=0.3,description="日主五行比例>0.3→身强")],match_mode="CONDITION"),
        StaticCanonicalJudgment("SG-ZP-STR-003","DI_TIAN_SUI","STRENGTH","身弱而火炎土燥，喜水滋润，忌再逢火土",
            [StaticJudgmentCondition("S003-1",required_day_master_element_ratio_max=0.15,description="身弱"),
             StaticJudgmentCondition("S003-2",required_dominant_element="FIRE",description="火为主导")],require_all=True,match_mode="COMPOSITE"),
        StaticCanonicalJudgment("SG-ZP-STR-004","DI_TIAN_SUI","STRENGTH","五行偏枯，气势不匀，喜调和五行",
            [StaticJudgmentCondition("S004-1",required_imbalance=True,description="五行失衡")],match_mode="CONDITION"),
        StaticCanonicalJudgment("SG-ZP-STR-005","DI_TIAN_SUI","STRENGTH","水旺身强，喜火土暖局，忌再逢金水",
            [StaticJudgmentCondition("S005-1",required_dominant_element="WATER",description="水为主导"),
             StaticJudgmentCondition("S005-2",required_day_master_element_ratio_min=0.3,description="身强")],require_all=True,match_mode="COMPOSITE"),
    ]


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("=" * 90)
    print("P6-C-3C-4 Phase 3 RERUN - 用正确八字重跑格局/调候/强弱Selection")
    print("=" * 90)
    print("\n基准命例: GOLDEN_CASE_1983_MALE")
    print("Evidence Lock Hash: 66d485306b5d5a7b")
    print("原始输入: 农历1983年九月二十九, 午时, 男")
    print("正确八字: 癸亥年 壬戌月 乙未日 壬午时")
    print("日主: 乙木 (阴木)")
    print("注意: 此脚本仅输出Selection结果供审计, 不自行定义PASS/FAIL")

    engine = BaziEngine()
    chart = engine.compute((1983, 11, 3, 12), 'male')
    context = build_context(chart)

    print(f"\n=== 正确八字确认 ===")
    print(f"  年柱: {chart.year_pillar.heavenly_stem}{chart.year_pillar.earthly_branch}")
    print(f"  月柱: {chart.month_pillar.heavenly_stem}{chart.month_pillar.earthly_branch}")
    print(f"  日柱: {chart.day_pillar.heavenly_stem}{chart.day_pillar.earthly_branch}")
    print(f"  时柱: {chart.hour_pillar.heavenly_stem}{chart.hour_pillar.earthly_branch}")
    print(f"  日主: {chart.day_master} (乙木, 阴木)")
    print(f"  月令主气: 戊土 = 正财 (对乙木)")
    print(f"  五行: {chart.five_element_balance}")
    print(f"  五行失衡: {chart.five_element_imbalance}")
    print(f"  主导五行: {context.dominant_element} (水0.5极旺, 但并列检查: 水0.5是唯一最高→WATER)")

    # Phase 3-1: 格局
    print(f"\n{'='*90}")
    print("Phase 3-1 RERUN: 子平·格局 10条 (正确八字: 乙木, 正财格)")
    print("=" * 90)
    pattern_judgments = get_pattern_judgments()
    resolver_p = StaticGraphResolver(pattern_judgments)
    results_p = resolver_p.select(context)
    for r in results_p:
        status = "SELECTED" if r.selected else "REJECTED"
        print(f"\n  [{r.judgment_id}] {status}")
        print(f"    原典: {next(j.classical for j in pattern_judgments if j.judgment_id==r.judgment_id)[:50]}...")
        print(f"    Reason: {r.reason}")
        if r.matched_conditions: print(f"    Matched: {r.matched_conditions}")
        if r.failed_conditions: print(f"    Failed: {r.failed_conditions}")
    sel_p = [r.judgment_id for r in results_p if r.selected]
    print(f"\n  >>> 格局 SELECTED: {len(sel_p)}/10 = {sel_p}")
    print(f"  >>> 关键验证: SG-ZP-PAT-001(正财格, 月令主气正财) 应该 SELECTED (乙木+戌月主气戊土=正财)")

    # Phase 3-2: 调候
    print(f"\n{'='*90}")
    print("Phase 3-2 RERUN: 子平·调候 5条 (正确八字: 乙木+戌月)")
    print("=" * 90)
    tuning_judgments = get_tuning_judgments()
    resolver_t = StaticGraphResolver(tuning_judgments)
    results_t = resolver_t.select(context)
    for r in results_t:
        status = "SELECTED" if r.selected else "REJECTED"
        print(f"\n  [{r.judgment_id}] {status}")
        print(f"    原典: {next(j.classical for j in tuning_judgments if j.judgment_id==r.judgment_id)[:50]}...")
        print(f"    Reason: {r.reason}")
        if r.failed_conditions: print(f"    Failed: {r.failed_conditions}")
    sel_t = [r.judgment_id for r in results_t if r.selected]
    print(f"\n  >>> 调候 SELECTED: {len(sel_t)}/5 = {sel_t}")
    print(f"  >>> 关键验证: SG-ZP-TUN-001(乙木戌月调候) 应该 SELECTED (乙木+戌月完全匹配)")

    # Phase 3-3: 强弱
    print(f"\n{'='*90}")
    print("Phase 3-3 RERUN: 子平·强弱/气势 5条 (正确八字: 乙木, 水0.5极旺, 金0缺)")
    print("=" * 90)
    strength_judgments = get_strength_judgments()
    resolver_s = StaticGraphResolver(strength_judgments)
    results_s = resolver_s.select(context)
    for r in results_s:
        status = "SELECTED" if r.selected else "REJECTED"
        print(f"\n  [{r.judgment_id}] {status}")
        print(f"    原典: {next(j.classical for j in strength_judgments if j.judgment_id==r.judgment_id)[:50]}...")
        print(f"    Reason: {r.reason}")
        if r.matched_conditions: print(f"    Matched: {r.matched_conditions}")
        if r.failed_conditions: print(f"    Failed: {r.failed_conditions}")
    sel_s = [r.judgment_id for r in results_s if r.selected]
    print(f"\n  >>> 强弱 SELECTED: {len(sel_s)}/5 = {sel_s}")
    print(f"  >>> 关键验证:")
    print(f"      SG-ZP-STR-001(身弱, WOOD<0.15): WOOD=0.125 → 应该 SELECTED")
    print(f"      SG-ZP-STR-004(五行失衡): imbalance=True → 应该 SELECTED")
    print(f"      SG-ZP-STR-005(水主导+身强): 水0.5主导但WOOD=0.125非身强 → 应该 REJECTED (Composite Fidelity)")

    # 汇总
    print(f"\n{'='*90}")
    print("RERUN 汇总 (供审计)")
    print("=" * 90)
    print(f"\n  基准命例: GOLDEN_CASE_1983_MALE (Hash: 66d485306b5d5a7b)")
    print(f"  正确八字: 癸亥/壬戌/乙未/壬午, 乙木日主, 正财格")
    print(f"\n  Phase 3-1 格局: SELECTED {len(sel_p)}/10 = {sel_p}")
    print(f"  Phase 3-2 调候: SELECTED {len(sel_t)}/5 = {sel_t}")
    print(f"  Phase 3-3 强弱: SELECTED {len(sel_s)}/5 = {sel_s}")
    print(f"  总计: SELECTED {len(sel_p)+len(sel_t)+len(sel_s)}/20")
    print(f"\n  ASSET_GAP 重新判断:")
    print(f"    - 正财格: 已覆盖 (SG-ZP-PAT-001 SELECTED) → 之前的'缺正财格'是假缺口")
    print(f"    - 乙木戌月调候: 已覆盖 (SG-ZP-TUN-001 SELECTED) → 之前的'缺甲木午月调候'是假缺口")
    print(f"    - 伤官格: 正确八字是正财格不是伤官格 → 之前的'缺伤官格'是基于错误八字的假缺口")
    print(f"    - 偏财格: 正确八字日支未土=偏财但月令主气是正财 → 需确认是否需要偏财格Judgment")
    print(f"\n  注意: 此脚本不自行定义PASS/FAIL, 以上结果供审计逐项核查")
    print("=" * 90)


if __name__ == "__main__":
    main()
