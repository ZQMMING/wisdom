"""Phase 3 全引擎：Source/Rule 正式化（V2.22 §62/§63）。

对 pzzq/dts/qtbj/smth/sftk 执行与 yhzp 相同的 6 项对齐：
  ① evidence_grade（§78）② version=0.1.0 ③ has→exists、absent→not_exists（§46）
  ④ source_id→source_ids ⑤ operation→operator、outputs→output ⑥ evidence_requirement 保留
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = Path(r"D:\顺天系统资料\豆包资料\六部经典校对版\SourceRegistry重建")
ENGINES = ["pzzq", "dts", "qtbj", "smth", "sftk"]

ENGINE_MAP = {
    "pzzq": "ZIPING_ZHENQUAN", "dts": "DITIANSUI", "qtbj": "QIONGTONG_BAOJIAN",
    "smth": "SANMING_TONGHUI", "sftk": "SHENFENG_TONGKAO", "yhzp": "YUHAI_ZIPING",
}

# 候选数据 engine 标识笔误 → 正式化规范映射（QA 报告记录）
ENGINE_TYPO_FIX = {
    "ZIPIN_ZHENQUAN": "ZIPING_ZHENQUAN",
    "DI_TIAN_SUI": "DITIANSUI",
}

TEXT_LAYER_TO_GRADE = {
    "ORIGINAL": "A", "ANNOTATION": "B", "LATER_COMMENTARY": "C",
    "UNVERIFIED": "D", "NEEDS_REVIEW": "D",
}

OP_MAP = {"has": "exists", "absent": "not_exists"}


def load_jsonl(p: Path):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def align_one(engine: str) -> dict:
    src_dir = SRC_ROOT / engine
    sources = load_jsonl(src_dir / "sources.jsonl")
    rules = load_jsonl(src_dir / "rules_candidate.jsonl")

    src_ids = set()
    for s in sources:
        g = TEXT_LAYER_TO_GRADE.get(s["text_layer"])
        if not g:
            raise SystemExit(f"FAIL 未知 text_layer {s['text_layer']} @ {s['source_id']}")
        s["evidence_grade"] = g
        src_ids.add(s["source_id"])

    rule_ids = set()
    for r in rules:
        r["version"] = "0.1.0"
        sid = r.pop("source_id")
        r["source_ids"] = [sid]
        r["operator"] = r.pop("operation")
        outs = r.pop("outputs")
        r["output"] = outs if len(outs) > 1 else outs[0]
        # engine 标识笔误规范（ZIPIN_ZHENQUAN→ZIPING_ZHENQUAN、DI_TIAN_SUI→DITIANSUI）
        if r.get("engine") in ENGINE_TYPO_FIX:
            r["engine"] = ENGINE_TYPO_FIX[r["engine"]]
        for c in r["preconditions"].get("conditions", []):
            if c["operator"] in OP_MAP:
                c["operator"] = OP_MAP[c["operator"]]
        rule_ids.add(r["rule_id"])

    allowed = {"equals", "in", "not_in", "exists", "not_exists"}
    for r in rules:
        for c in r["preconditions"].get("conditions", []):
            if c["operator"] not in allowed:
                raise SystemExit(f"FAIL 非法算子 {c['operator']} @ {r['rule_id']} ({engine})")

    orphan = [r["rule_id"] for r in rules if not (set(r["source_ids"]) & src_ids)]
    if orphan:
        raise SystemExit(f"FAIL 孤儿 Rule: {orphan[:5]} ({engine})")
    if len(src_ids) != len(sources) or len(rule_ids) != len(rules):
        raise SystemExit(f"FAIL id 不唯一 ({engine})")

    src_schema = json.loads((ROOT / "shared_schema" / "source.schema.json").read_text(encoding="utf-8"))
    rule_schema = json.loads((ROOT / "shared_schema" / "rule.schema.json").read_text(encoding="utf-8"))
    vs, vr = Draft202012Validator(src_schema), Draft202012Validator(rule_schema)
    es = sum(1 for s in sources for _ in vs.iter_errors(s))
    er = sum(1 for r in rules for _ in vr.iter_errors(r))
    if es or er:
        raise SystemExit(f"FAIL schema: source={es} rule={er} ({engine})")

    out_src = ROOT / "registries" / "source" / f"sources.{engine}.jsonl"
    out_rule = ROOT / "registries" / "rule" / f"rules.{engine}.jsonl"
    out_src.parent.mkdir(parents=True, exist_ok=True)
    out_rule.parent.mkdir(parents=True, exist_ok=True)
    out_src.write_text("".join(json.dumps(s, ensure_ascii=False) + "\n" for s in sources), encoding="utf-8")
    out_rule.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rules), encoding="utf-8")

    from collections import Counter
    return {
        "engine": ENGINE_MAP[engine], "sources": len(sources), "rules": len(rules),
        "grades": dict(Counter(s["evidence_grade"] for s in sources)),
        "ops": dict(Counter(r["operator"] for r in rules)),
        "multi_output": sum(1 for r in rules if isinstance(r["output"], list)),
    }


def main() -> int:
    ok = 0
    for e in ENGINES:
        try:
            info = align_one(e)
            print(f"OK {e}: {info}")
            ok += 1
        except SystemExit as ex:
            print(str(ex))
    print(f"完成 {ok}/{len(ENGINES)}")
    return 0 if ok == len(ENGINES) else 1


if __name__ == "__main__":
    sys.exit(main())
