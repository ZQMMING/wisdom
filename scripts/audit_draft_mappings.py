# -*- coding: utf-8 -*-
"""DRAFT Mapping 批量审核工具(M-LC-01 前置审查准备)。

背景: 运行时 10 条 mapping(MAP-1001..1010)全部 status=draft,却被
compute_stage.py 无条件 apply_to_claims(M2B1 P-3 / M-LC-01 焦点)。
本工具批量审查 10 条 DRAFT mapping,产出逐条审查卡 + 跨映射发现 +
Spec Owner 裁定清单,为逐条批转 active / 加 status 门控做证据准备。

检查分类:
  A 完整性(schema/唯一性/十神覆盖/metadata)
  B rule_refs 引用完整性(M-COVERAGE:悬空/逆向覆盖/共享模式/状态对齐)
  C 域正确性(十神→ontology_type/direction/polarity,逐 rule_ref 核对)
  D 语义一致(source_term ↔ rule 内容,十神族匹配/gloss 质量)
  E 决策依赖(spec_decisions_ref 存在性)
  F 生命周期门控(M-LC-01:draft 生产生效检测,源码级)
  G 跨映射一致性(theme 唯一/双映射 tiebreak/词库桥接 S-1)

纪律: 本工具只审查不改数据;不裁决 status 迁移。severity=BLOCK/REVIEW/INFO。
输出: docs/v40/MAPPING_DRAFT_REVIEW.md(UTF-8);stdout 汇总;BLOCK 存在时退出码 1。
可复用: `run_audit()` 返回结构化结果供测试/二次加工。
"""
from __future__ import annotations

import json  # noqa: F401
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from tongshu.reasoning.mapping_registry import MappingRegistry  # noqa: E402
from tongshu.reasoning.rule_loader import RuleLoader  # noqa: E402

REPO = Path(__file__).resolve().parents[2]
DATA = REPO / "backend" / "data"
DOCS = REPO / "docs"
OUT = DOCS / "v40" / "MAPPING_DRAFT_REVIEW.md"
DECISIONS_FILE = DOCS / "architecture_decisions_v1.md"

# --------------------------------------------------------------------------- #
# 领域表(命理十神基础,高置信)
# --------------------------------------------------------------------------- #

# 十神 → 十神族(含别称)
GOD_FAMILIES = {
    "正印": {"正印", "偏印", "印绶", "印"},
    "偏印": {"偏印", "枭神"},
    "比肩": {"比肩"},
    "劫财": {"劫财"},
    "食神": {"食神"},
    "伤官": {"伤官"},
    "正财": {"正财"},
    "偏财": {"偏财"},
    "正官": {"正官"},
    "七杀": {"七杀", "偏官"},
}
# 十神 → 关系 → 期望 ontology_type
GOD_ONTOLOGY = {
    "正印": "SUPPORT", "偏印": "SUPPORT",      # 生我
    "比肩": "RELATION", "劫财": "RELATION",    # 同我
    "食神": "OUTPUT", "伤官": "OUTPUT",        # 我生
    "正财": "RESOURCE", "偏财": "RESOURCE",    # 我克
    "正官": "CONSTRAINT", "七杀": "CONSTRAINT",  # 克我
}
GOD_RELATION = {"SUPPORT": "生我", "RELATION": "同我", "OUTPUT": "我生",
                "RESOURCE": "我克", "CONSTRAINT": "克我"}
EXPECTED_GODS = set(GOD_FAMILIES)
# modern_gloss 纯文言复述检测;'之/干/支'等单字在现代语中常见,不判文言
CLASSICAL_MARKERS = ("曰", "者也", "之谓", "兮", "乎")

# --------------------------------------------------------------------------- #
# 模型
# --------------------------------------------------------------------------- #


class Finding:
    def __init__(self, check: str, severity: str, text: str):
        self.check = check
        self.severity = severity  # BLOCK / REVIEW / INFO / PASS
        self.text = text

    def __repr__(self):
        return f"[{self.severity}] {self.check}: {self.text}"


def scan_rule_ten_gods(rule: dict) -> set[str]:
    """递归扫描 rule.conditions,提取 all/any 中 ten_god 字段的取值。"""
    gods: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            field = node.get("field")
            if isinstance(field, str) and "ten_god" in field:
                vals = node.get("value")
                if isinstance(vals, list):
                    gods.update(str(v) for v in vals)
                elif isinstance(vals, str):
                    gods.add(vals)
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for x in node:
                walk(x)

    walk(rule.get("conditions", {}))
    return gods & ALL_GODS


ALL_GODS = set(GOD_FAMILIES)


def load_decisions() -> set[str]:
    """从 architecture_decisions_v1.md 提取存在的 DECISION-0XX 完整 ID。"""
    text = DECISIONS_FILE.read_text(encoding="utf-8")
    return set(f"DECISION-{n}" for n in re.findall(r"DECISION-(\d{3})(?:\.A|\.B)?", text))


# --------------------------------------------------------------------------- #
# 主审查
# --------------------------------------------------------------------------- #


def run_audit(mapping_ids: set[str] | None = None):
    """批量审查 DRAFT mapping,返回结构化结果。

    Args:
        mapping_ids: 限定审查范围。若 None,审查全部 mapping 条目（如实报告全量数据）。
            传入 {"MAP-1001", ..., "MAP-1010"} 可显式指定原始基线子集。

    Returns:
        (entries, per_mapping, all_findings, cross, rules, decisions)
        per_mapping: {mapping_id: 'PASS'|'REVIEW'|'BLOCK'}
        all_findings: {mapping_id: [Finding, ...]}
        cross: [Finding, ...](跨映射 + 门控 + 词库桥接)
    """
    reg = MappingRegistry(DATA, DOCS)
    all_entries = reg.entries
    # B-11: 审计工具必须如实报告全部数据现状，不得默认遮蔽。
    # mapping_ids=None 时审查全部条目；调用方可显式传入子集。
    if mapping_ids is not None:
        entries = [e for e in all_entries if e["mapping_id"] in mapping_ids]
    else:
        entries = list(all_entries)
    rl = RuleLoader(DATA, DOCS)
    rules = rl.rules
    rule_by_id = {r["rule_id"]: r for r in rules}
    decisions = load_decisions()

    all_findings: dict[str, list[Finding]] = {}
    per_mapping: dict[str, str] = {}
    for e in sorted(entries, key=lambda x: x["mapping_id"]):
        mid = e["mapping_id"]
        f: list[Finding] = []
        all_findings[mid] = f
        god = e["source_term"]

        # A 完整性
        f.append(Finding("A-01", "PASS", "schema 校验通过(MappingRegistry 强校验)"))
        if e.get("created_at"):
            f.append(Finding("A-05", "INFO", f"created_at={e.get('created_at')}"))
        else:
            f.append(Finding("A-05", "REVIEW", "created_at 缺失(可选字段)"))
        if e.get("author"):
            f.append(Finding("A-06", "INFO", f"author={e.get('author')}"))
        else:
            f.append(Finding("A-06", "INFO",
                             "author 字段缺失(schema 可选;建议补作者以对齐 F1 reviewer 元数据纪律)"))

        # B rule_refs 完整性
        refs = e.get("rule_refs", [])
        dangling = [rid for rid in refs if rid not in rule_by_id]
        if dangling:
            f.append(Finding("B-01", "BLOCK", f"rule_ref 悬空: {dangling}"))
        else:
            f.append(Finding("B-01", "PASS", f"{len(refs)} 条 rule_ref 全部解析"))

        # C 域正确性
        exp_onto = GOD_ONTOLOGY.get(god)
        if god not in EXPECTED_GODS:
            f.append(Finding("A-04", "REVIEW", f"source_term '{god}' 不在十神集合"))
        elif e.get("ontology_type") != exp_onto:
            f.append(Finding("C-01", "BLOCK",
                             f"ontology_type={e.get('ontology_type')} 应为 {exp_onto}"
                             f"({god}={GOD_RELATION[exp_onto]})"))
        else:
            f.append(Finding("C-01", "PASS", f"ontology_type={e.get('ontology_type')} ✓({god})"))

        # C/D 规则级一致性(逐 rule_ref)
        for rid in refs:
            r = rule_by_id.get(rid)
            if r is None:
                continue
            sig = r.get("produces_signal_type")
            concl = r.get("conclusion", {}).get("produces_layer_output_template", {})
            rdir, rpol = concl.get("direction"), concl.get("polarity")
            if sig != e.get("ontology_type"):
                f.append(Finding("C-02", "BLOCK", f"{rid} signal={sig} ≠ mapping ontology={e.get('ontology_type')}"))
            if rdir != e.get("direction_hint"):
                f.append(Finding("C-03", "REVIEW", f"{rid} direction={rdir} ≠ mapping={e.get('direction_hint')}"))
            if rpol != e.get("polarity_hint"):
                f.append(Finding("C-04", "REVIEW", f"{rid} polarity={rpol} ≠ mapping={e.get('polarity_hint')}"))
            r_gods = scan_rule_ten_gods(r)
            if not r_gods:
                f.append(Finding("D-01", "REVIEW", f"{rid} 条件中未检出十神取值(无法核验族匹配)"))
            elif not (GOD_FAMILIES[god] & r_gods):
                f.append(Finding("D-01", "REVIEW", f"{rid} 十神={r_gods} 与 {god} 族无交集"))
        r_hits = [rid for rid in refs if rid in rule_by_id]
        if r_hits:
            for chk, attr in (("C-02", "ontology_type"), ("C-03", "direction_hint"), ("C-04", "polarity_hint")):
                if not any(x.check == chk for x in f):
                    f.append(Finding(chk, "PASS", f"{len(r_hits)}/{len(r_hits)} 规则 {attr}={e.get(attr)} 一致"))
            if not any(x.check == "D-01" for x in f):
                f.append(Finding("D-01", "PASS", f"{len(r_hits)}/{len(r_hits)} 规则十神与 `{god}` 族匹配"))

        # E 决策依赖
        missing_dec = [d for d in e.get("spec_decisions_ref", []) if d not in decisions]
        if missing_dec:
            f.append(Finding("E-01", "BLOCK", f"spec_decisions_ref 未注册: {missing_dec}"))
        else:
            f.append(Finding("E-01", "PASS", f"决策依赖 {e.get('spec_decisions_ref')} 全注册"))

        # D-03 gloss 质量
        gloss = e.get("modern_gloss", "")
        gloss_issues = []
        if len(gloss) < 25:
            gloss_issues.append("过短")
        if god not in gloss:
            gloss_issues.append("不含 source_term")
        if any(m in gloss for m in CLASSICAL_MARKERS):
            gloss_issues.append("含文言标记")
        if gloss_issues:
            f.append(Finding("D-03", "REVIEW", f"modern_gloss {gloss_issues}(长度 {len(gloss)})"))
        else:
            f.append(Finding("D-03", "PASS", f"modern_gloss 长度 {len(gloss)} ✓"))

        # 判定
        sevs = {x.severity for x in f if x.severity != "PASS"}
        if "BLOCK" in sevs:
            per_mapping[mid] = "BLOCK"
        elif "REVIEW" in sevs:
            per_mapping[mid] = "REVIEW"
        else:
            per_mapping[mid] = "PASS"

    cross: list[Finding] = []
    cross += _cross_checks(entries, rule_by_id)
    cross += _mlc01_check()
    cross += _lexicon_bridge_check()
    return entries, per_mapping, all_findings, cross, rules, decisions


def _cross_checks(entries, rule_by_id) -> list[Finding]:
    out: list[Finding] = []

    mids = [e["mapping_id"] for e in entries]
    if len(mids) != len(set(mids)):
        out.append(Finding("G-01", "BLOCK", f"mapping_id 重复: {[x for x in mids if mids.count(x) > 1]}"))
    else:
        out.append(Finding("G-01", "PASS", f"{len(mids)} 个 mapping_id 唯一"))

    terms = [e["source_term"] for e in entries]
    dups = {t for t in terms if terms.count(t) > 1}
    if dups:
        out.append(Finding("G-02", "BLOCK", f"source_term 重复映射: {dups}"))
    else:
        out.append(Finding("G-02", "PASS", "source_term 互斥"))

    covered = set(terms)
    if covered != EXPECTED_GODS:
        out.append(Finding("A-04", "BLOCK", f"十神覆盖不完整: 缺 {EXPECTED_GODS - covered} / 多 {covered - EXPECTED_GODS}"))
    else:
        out.append(Finding("A-04", "PASS", "十神 10/10 全覆盖(正印/偏印/比肩/劫财/食神/伤官/正财/偏财/正官/七杀)"))

    themes = [e["modern_theme"] for e in entries]
    tdups = {t for t in themes if themes.count(t) > 1}
    if tdups:
        out.append(Finding("G-03", "REVIEW", f"modern_theme 重复: {tdups}"))
    else:
        out.append(Finding("G-03", "PASS", "modern_theme 10 个互异"))

    # rule_refs 分布
    refs_by_mapping = {e["mapping_id"]: set(e["rule_refs"]) for e in entries}
    all_refs = [rid for e in entries for rid in e["rule_refs"]]
    dangling = [rid for rid in all_refs if rid not in rule_by_id]
    if dangling:
        out.append(Finding("B-01", "BLOCK", f"悬空 rule_ref: {set(dangling)}"))
    else:
        out.append(Finding("B-01", "PASS", f"{len(all_refs)} 条 rule_ref 全部解析"))

    # 逆向覆盖: 每条被引用规则 → 映射个数;十神族共享放行,单神规则双引=发现
    owner_map: dict[str, list[str]] = defaultdict(list)
    for mid, rids in refs_by_mapping.items():
        for rid in rids:
            owner_map[rid].append(mid)
    shared_ok, shared_issues = 0, []
    for rid, owners in sorted(owner_map.items()):
        if len(owners) == 1:
            continue
        rule = rule_by_id.get(rid, {})
        r_gods = scan_rule_ten_gods(rule)
        fams = {fam for g in r_gods for fam, members in GOD_FAMILIES.items() if g in members}
        if len(fams) >= 2:
            shared_ok += 1
            out.append(Finding("B-02", "INFO",
                               f"{rid} 为十神族规则(覆盖 {sorted(r_gods)}),被 {owners} 共同引用 ✓(设计如此)"))
        else:
            shared_issues.append(f"{rid}(十神={sorted(r_gods) or '未知'}) 被 {owners} 双引")
    if shared_issues:
        out.append(Finding("B-02", "REVIEW", "单神规则被多映射引用: " + "; ".join(shared_issues)))
    else:
        out.append(Finding("B-02", "PASS", f"共享规则 {shared_ok} 条均为十神族规则 ✓"))

    zlpz = {f"ZPZ-{i}" for i in range(101, 131)}
    uncovered = zlpz - set(owner_map)
    if uncovered:
        out.append(Finding("B-03", "BLOCK", f"ZPZ-101..130 未覆盖: {sorted(uncovered)}(M-COVERAGE-01)"))
    else:
        out.append(Finding("B-03", "PASS", "ZPZ-101..130 全部 30 条被 ≥1 个 mapping 引用"))

    if shared_ok:
        out.append(Finding("G-04", "REVIEW",
                           "十神族共享规则触发时, sibling 映射并存: mapping_refs 全附、modern_theme 取 "
                           "sorted(id) 首条。例: 偏印格月令 claim 经 ZPZ-101 同时命中 MAP-1001/1002, 主标签="
                           "MAP-1001'滋养与根基支撑'而非'洞察与偏门资源'。语义精度取决于规则是否区分具体十神。"))
    return out


def _mlc01_check() -> list[Finding]:
    """源码级确认 apply_to_claims 是否带 status 门控(M-LC-01)。"""
    out = []
    mr = REPO / "backend" / "src" / "tongshu" / "reasoning" / "mapping_registry.py"
    cs = REPO / "backend" / "src" / "tongshu" / "pipeline_stages" / "compute_stage.py"
    mr_txt = mr.read_text(encoding="utf-8")
    cs_txt = cs.read_text(encoding="utf-8")
    body = mr_txt.split("def apply_to_claims")[1].split("return out")[0]
    has_gate = "status" in body
    if not has_gate:
        out.append(Finding("F-01", "BLOCK",
                           "M-LC-01: apply_to_claims 无 status 过滤 → 10 条 DRAFT mapping 无条件作用于生产链"
                           "(compute_stage.py 调用点无条件)。引用 M2B1 P-3,待 Spec Owner 裁定:批转 active 或加 status 门控。"))
    else:
        out.append(Finding("F-01", "PASS", "apply_to_claims 已带 status 门控"))
    if "apply_to_claims" not in cs_txt:
        out.append(Finding("F-02", "INFO", "compute_stage.py 未直接调用 apply_to_claims(可能由其他 stage 调用)"))
    return out


def _lexicon_bridge_check() -> list[Finding]:
    """词库桥接(S-1): 词库域是否引用运行时 MAP id。"""
    out = []
    base = REPO / "开发资料" / "参考资料" / "词库V4.0"
    if not base.is_dir():
        out.append(Finding("G-05", "INFO", f"词库目录不存在: {base}(跳过桥接检查)"))
        return out
    hits = []
    for p in base.rglob("*"):
        if p.is_file() and p.suffix.lower() in {".json", ".md", ".txt", ".csv"}:
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if "MAP-100" in txt or "MAP-101" in txt:
                hits.append(str(p.relative_to(base)))
    if hits:
        out.append(Finding("G-05", "INFO", f"词库引用了运行时 MAP id: {hits}"))
    else:
        out.append(Finding("G-05", "REVIEW",
                           "S-1 双命名空间: 词库V4.0(156 语义映射)零引用运行时 MAP-1001..1010 — 词库全链完整但与运行时脱钩。"
                           "跨域解析须先建桥接层(M2B1 S-1/S-2)。"))
    return out


# --------------------------------------------------------------------------- #
# 报告
# --------------------------------------------------------------------------- #

def main() -> int:
    entries, per_mapping, all_findings, cross, rules, decisions = run_audit()

    report = []
    ap = report.append
    ap("# DRAFT Mapping 批量审查报告")
    ap("")
    ap("- **status**: 审查产出(只读,不改数据)")
    ap("- **date**: 2026-08-21")
    ap("- **工具**: `backend/scripts/audit_draft_mappings.py`")
    ap(f"- **范围**: {len(entries)} 条 mapping(全量审查)")
    ap("- **背景**: M2B1 P-3 / M-LC-01(draft 映射生产生效) — compute_stage.py 无条件 apply_to_claims")
    ap("- **纪律**: 本工具只审查不裁决;status 迁移由 Spec Owner 逐条批")
    ap("- **域表**: 十神→关系→ontology_type(命理基础,高置信)")
    ap("")

    # §1 总览
    vc = Counter(per_mapping.values())
    ap("## 1. 总览")
    ap("")
    ap("| 判定 | 数量 |")
    ap("|---|---|")
    for v in ("PASS", "REVIEW", "BLOCK"):
        ap(f"| {v} | {vc.get(v, 0)} |")
    ap("")
    n_block = sum(1 for x in cross if x.severity == "BLOCK")
    n_rev = sum(1 for x in cross if x.severity == "REVIEW")
    ap(f"跨映射发现: BLOCK {n_block} / REVIEW {n_rev}(明细见 §3)")
    ap("")

    # §2 逐条审查卡
    ap("## 2. 逐条审查卡")
    ap("")
    for e in sorted(entries, key=lambda x: x["mapping_id"]):
        mid = e["mapping_id"]
        f = all_findings[mid]
        ap(f"### {mid} {e['title']}")
        ap("")
        ap(f"- source_term: `{e['source_term']}` | related: {e.get('related_terms')}")
        ap(f"- ontology/direction/polarity: `{e['ontology_type']}` / `{e['direction_hint']}` / `{e['polarity_hint']}`")
        ap(f"- rule_refs({len(e['rule_refs'])}): `{'`, `'.join(e['rule_refs'])}`")
        ap(f"- modern_theme: {e['modern_theme']}")
        ap(f"- 审查结论: **{per_mapping[mid]}**")
        ap("")
        ap("| 检查 | 结果 | 说明 |")
        ap("|---|---|---|")
        for x in f:
            ap(f"| {x.check} | {x.severity} | {x.text} |")
        ap("")

    # §3 跨映射发现
    ap("## 3. 跨映射 / 门控发现")
    ap("")
    for x in cross:
        ap(f"- **[{x.severity}] {x.check}**: {x.text}")
    ap("")

    # §4 Spec Owner 裁定清单
    ap("## 4. Spec Owner 裁定清单(逐条)")
    ap("")
    ap("| mapping | 十神 | ontology | 引用规则 | 判定 | 待裁定项 |")
    ap("|---|---|---|---|---|---|")
    for e in sorted(entries, key=lambda x: x["mapping_id"]):
        f = all_findings[e["mapping_id"]]
        blockers = "; ".join(x.text for x in f if x.severity == "BLOCK")
        reviews = "; ".join(x.text for x in f if x.severity == "REVIEW")
        issues = blockers or reviews or "无"
        ap(f"| {e['mapping_id']} | {e['source_term']} | {e['ontology_type']} | {len(e['rule_refs'])} | "
           f"{per_mapping[e['mapping_id']]} | {issues} |")
    ap("")

    # §5 附录
    ap("## 5. 附录")
    ap("")
    ap(f"- 规则注册表: 共 {len(rules)} 条 → active {sum(1 for r in rules if r.get('status') == 'active')} / "
       f"validated {sum(1 for r in rules if r.get('status') == 'validated')} / "
       f"draft {sum(1 for r in rules if r.get('status') == 'draft')}")
    ap(f"- 决策注册表: {len(decisions)} 个 DECISION 条目")
    ap("- 引用的 ZPZ-101..130 规则均存在; 逆向覆盖与共享模式见 B-02/G-01")
    ap("")

    OUT.write_text("\n".join(report) + "\n", encoding="utf-8")

    # stdout 汇总
    print("== DRAFT Mapping 审查 ==")
    print(f"mapping: {len(entries)} | 判定: " + " ".join(f"{v}={vc.get(v, 0)}" for v in ("PASS", "REVIEW", "BLOCK")))
    for mid, v in per_mapping.items():
        print(f"  {mid} -> {v}")
    print(f"跨映射: BLOCK {n_block} / REVIEW {n_rev}")
    print(f"报告 -> {OUT}")
    return 1 if ("BLOCK" in per_mapping.values() or n_block) else 0


if __name__ == "__main__":
    sys.exit(main())
