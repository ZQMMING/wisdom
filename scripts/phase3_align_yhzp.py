"""Phase 3：YHZP Source/Rule 正式化（V2.22 §62/§63 + 6 项数据→正式 Schema 对齐）。

输入：D:\\顺天系统资料\\豆包资料\\六部经典校对版\\SourceRegistry重建\\yhzp\\
      sources.jsonl / rules_candidate.jsonl
输出：registries/source/sources.yhzp.jsonl
      registries/rule/rules.yhzp.jsonl
      registries/qa_report.yhzp.md

对齐项（KEY_FACTS 6 项）：
  ① source 补 evidence_grade（§78：ORIGINAL→A / ANNOTATION→B / LATER_COMMENTARY→C / UNVERIFIED→D）
  ② rule 补 version=0.1.0
  ③ 条件算子：数据已全部为 equals/in（§46 白名单），无需映射；校验断言
  ④ source_id(单) → source_ids(数组)
  ⑤ operation → operator（§45）；outputs → output（单对象/多输出数组）
  ⑥ evidence_requirement 保留字段，Phase 5 迁移 Evidence Registry（本阶段不迁移）

铁律：不修改 source_text/规则语义；status 保留 CANDIDATE（Human 审批不代行）。
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(r"D:\顺天系统资料\豆包资料\六部经典校对版\SourceRegistry重建\yhzp")
OUT_SRC = ROOT / "registries" / "source"
OUT_RULE = ROOT / "registries" / "rule"

TEXT_LAYER_TO_GRADE = {
    "ORIGINAL": "A",
    "ANNOTATION": "B",
    "LATER_COMMENTARY": "C",
    "UNVERIFIED": "D",
    "NEEDS_REVIEW": "D",
}


def load_jsonl(p: Path):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    sources = load_jsonl(SRC / "sources.jsonl")
    rules = load_jsonl(SRC / "rules_candidate.jsonl")
    print(f"输入：sources={len(sources)} rules={len(rules)}")

    # ① source 补 evidence_grade
    src_ids = set()
    for s in sources:
        g = TEXT_LAYER_TO_GRADE.get(s["text_layer"])
        if not g:
            print(f"FAIL 未知 text_layer: {s['text_layer']} @ {s['source_id']}")
            return 1
        s["evidence_grade"] = g
        src_ids.add(s["source_id"])
        s.setdefault("notes", "")

    # ②⑤ rule 对齐
    rule_ids = set()
    for r in rules:
        # ② version
        r["version"] = "0.1.0"
        # ④ source_id → source_ids
        sid = r.pop("source_id")
        r["source_ids"] = [sid]
        # ⑤ operation → operator；outputs → output
        op = r.pop("operation")
        outs = r.pop("outputs")
        r["operator"] = op
        r["output"] = outs if len(outs) > 1 else outs[0]
        rule_ids.add(r["rule_id"])

    # ③ 算子断言（§46 白名单）
    allowed_ops = {"equals", "in", "not_in", "exists", "not_exists"}
    for r in rules:
        for c in r["preconditions"].get("conditions", []):
            if c["operator"] not in allowed_ops:
                print(f"FAIL 非法算子 {c['operator']} @ {r['rule_id']}")
                return 1

    # §63：没有 Source 的 Rule STOP
    orphan = [r["rule_id"] for r in rules if not (set(r["source_ids"]) & src_ids)]
    if orphan:
        print(f"FAIL 无 Source 绑定的 Rule: {orphan[:10]}")
        return 1

    # 唯一性
    if len(src_ids) != len(sources):
        print("FAIL source_id 不唯一")
        return 1
    if len(rule_ids) != len(rules):
        print("FAIL rule_id 不唯一")
        return 1

    # Schema 校验
    src_schema = json.loads((ROOT / "shared_schema" / "source.schema.json").read_text(encoding="utf-8"))
    rule_schema = json.loads((ROOT / "shared_schema" / "rule.schema.json").read_text(encoding="utf-8"))
    vs, vr = Draft202012Validator(src_schema), Draft202012Validator(rule_schema)
    errs_s = sum(1 for s in sources for _ in vs.iter_errors(s))
    errs_r = sum(1 for r in rules for _ in vr.iter_errors(r))
    if errs_s or errs_r:
        print(f"FAIL schema: source errors={errs_s} rule errors={errs_r}")
        for r in rules:
            for e in vr.iter_errors(r):
                print("  ", r["rule_id"], e.message)
        return 1

    # 写正式 Registry
    OUT_SRC.mkdir(parents=True, exist_ok=True)
    OUT_RULE.mkdir(parents=True, exist_ok=True)
    (OUT_SRC / "sources.yhzp.jsonl").write_text(
        "".join(json.dumps(s, ensure_ascii=False) + "\n" for s in sources), encoding="utf-8")
    (OUT_RULE / "rules.yhzp.jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rules), encoding="utf-8")

    from collections import Counter
    print("OK 正式化完成")
    print("  text_layer:", dict(Counter(s["text_layer"] for s in sources)))
    print("  evidence_grade:", dict(Counter(s["evidence_grade"] for s in sources)))
    print("  operator:", dict(Counter(r["operator"] for r in rules)))
    print("  output 数组(多输出):", sum(1 for r in rules if isinstance(r["output"], list)))
    print(f"  输出: {OUT_SRC/'sources.yhzp.jsonl'} / {OUT_RULE/'rules.yhzp.jsonl'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
