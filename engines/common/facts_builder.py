"""通用 Facts Builder（Phase 6 §65/§B-3）· 多引擎。

消费 L0 Chart → 生成求值上下文 → Rule Engine → 按 output 字段分六组 facts →
attach evidence（§64）→ EngineResult（§70）。

引擎无关：FactsBuilder(engine="pzzq") 即加载 pzzq 正式 Registry 并输出对应引擎结果。
禁重排盘：只消费 L0；不计算命盘。
"""

from __future__ import annotations

from typing import Any, Dict, List

from shared_types.fail_closed import FailClosedReason, FailClosedError
from engines.common.l0_adapter import build_base_view, build_contexts
from engines.common.result import EngineResult, FactGroups
from engines.yuhai_ziping.evidence.evidence_registry import EvidenceRegistry
from engines.yuhai_ziping.rule.rule_engine import RuleEngine

# engine 目录名（registry 文件后缀）→ ENGINE_ID
ENGINE_ID_MAP = {
    "yhzp": "YUHAI_ZIPING",
    "pzzq": "ZIPING_ZHENQUAN",
    "dts": "DITIANSUI",
    "qtbj": "QIONGTONG_BAOJIAN",
    "smth": "SANMING_TONGHUI",
    "sftk": "SHENFENG_TONGKAO",
}

# output 字段 → §B-3 六组映射
TEN_GOD_FIELDS = {"ten_god", "food_god_stem", "yang_ren", "lu"}
SIX_RELATIVE_FIELDS = {"liu_qin"}
PALACE_FIELDS = {"day_pillar", "hour_zi_pillar", "yin_month_pillar"}
RELATION_FIELDS = {"liu_he", "liu_chong", "liu_chuan", "kong_wang", "san_he_ju"}
# 其余（element/stem_he/hidden_stem/na_yin/zodiac/twelve_stage/神煞/格局等）→ basic_structure
GEJU_CANDIDATE_FIELDS: set = set()  # 格局候选由各引擎 Phase 6+ 派生，Phase 3/4 暂留空


def _group_for(field: str) -> str:
    if field in TEN_GOD_FIELDS:
        return "ten_god_facts"
    if field in SIX_RELATIVE_FIELDS:
        return "six_relative_facts"
    if field in PALACE_FIELDS:
        return "palace_facts"
    if field in RELATION_FIELDS:
        return "relation_facts"
    if field in GEJU_CANDIDATE_FIELDS:
        return "geju_candidates"
    return "basic_structure_facts"


class FactsBuilder:
    """L0 Chart → 六组 facts（带完整证据链）· 引擎参数化。"""

    def __init__(self, engine: str = "yhzp", rule_engine: RuleEngine | None = None,
                 evidence: EvidenceRegistry | None = None) -> None:
        if engine not in ENGINE_ID_MAP:
            raise FailClosedError(FailClosedReason.CONTRACT_INVALID, f"未知引擎: {engine}")
        self.engine = engine
        self.engine_id = ENGINE_ID_MAP[engine]
        self.rules = rule_engine or RuleEngine(engine=engine)
        self.evd = evidence or EvidenceRegistry(engine=engine)

    def build(self, l0_chart: Dict[str, Any], input_ref: str | None = None) -> EngineResult:
        if not l0_chart.get("canonical_input"):
            raise FailClosedError(FailClosedReason.INPUT_FORBIDDEN, "缺少 canonical_input")
        base = build_base_view(l0_chart)
        ctxs = build_contexts(base)
        grouped: Dict[str, List[Dict[str, Any]]] = {g: [] for g in (
            "ten_god_facts", "six_relative_facts", "palace_facts",
            "basic_structure_facts", "geju_candidates", "relation_facts")}
        seen = set()

        def consume(run_ctxs: List[Dict[str, Any]]) -> Dict[str, str]:
            """跑规则、去重、分组；返回 target_stem → ten_god 映射。"""
            ten_god_map: Dict[str, str] = {}
            for ctx in run_ctxs:
                for raw in self.rules.run(ctx):
                    if raw["field"] == "ten_god" and ctx.get("target_stem"):
                        ten_god_map.setdefault(ctx["target_stem"], str(raw["value"]))
                    key = (raw["rule_id"], raw["field"], str(raw["value"]), ctx.get("context"))
                    if key in seen:
                        continue
                    seen.add(key)
                    fact = self.evd.attach(dict(raw))
                    fact["context"] = ctx.get("context")
                    fact["fact_id"] = f"FCT-{len(seen):04d}"
                    grouped[_group_for(fact["field"])].append(fact)
            return ten_god_map

        # 阶段 A：基础上下文
        ten_god_map = consume(ctxs)
        # 阶段 B：十神派生回填（liu_qin 等依赖 ten_god 值的规则）
        if ten_god_map:
            injected = []
            for ctx in ctxs:
                if ctx.get("target_stem") in ten_god_map:
                    ctx = dict(ctx)
                    ctx["ten_god"] = ten_god_map[ctx["target_stem"]]
                    injected.append(ctx)
            consume(injected)

        result = EngineResult(
            engine=self.engine_id,
            canonical_input={"ref": input_ref or l0_chart["canonical_input"].get("ref", ""),
                             "hash": l0_chart["canonical_input"].get("hash", "")},
        )
        result.facts.ten_god_facts = grouped["ten_god_facts"]
        result.facts.six_relative_facts = grouped["six_relative_facts"]
        result.facts.palace_facts = grouped["palace_facts"]
        result.facts.basic_structure_facts = grouped["basic_structure_facts"]
        result.facts.geju_candidates = grouped["geju_candidates"]
        result.facts.relation_facts = grouped["relation_facts"]
        return result
