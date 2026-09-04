# -*- coding: utf-8 -*-
"""L2 断事层评测器 — 对 MingLi-Bench 41 命主跑顺天全量方向信号画像。

输入: data/evaluation/MingLi-Bench/data/data.json (200 题, 41 命主)
方法: 每个命主跑 6 个 theme (WORK/RELATION/EMOTION/LEARNING/FAMILY_SOCIAL/ACTION_LIFE)
      汇总 BASELINE/CYCLE_CONTEXT/DAILY_ACTIVATION 三层方向信号画像。
输出: evaluation/reports/direction/
  - cases/<case_id>.json   每个命主信号画像 + 关联大赛题
  - summary.json           汇总

用法:
    python -m src.tongshu.evaluation.l2_direction
"""
from __future__ import annotations
import json, sys
from pathlib import Path
from datetime import date
from collections import OrderedDict

# 本地项目路径
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
REPO = _PROJECT_ROOT
sys.path.insert(0, str(REPO / "src"))

from tongshu.pipeline import TONGSHUPipeline

THEMES = ["WORK", "RELATION", "EMOTION", "LEARNING", "FAMILY_SOCIAL", "ACTION_LIFE"]

# MingLi-Bench location 值 -> locations.json id
LOC_MAP = {
    "usa": "US_NEW_YORK", "香港": "HK_HONGKONG", "大陆": "CN_MAINLAND",
    "malaysia": "MY_KUALALUMPUR", "台湾": "TW_TAIPEI", "广东": "CN_GUANGDONG",
    "潮汕": "CN_CHAOSHAN", "中国": "CN_MAINLAND", "北京": "CN_BEIJING",
    "宫崎县": "JP_MIYAZAKI", "新加坡": "SG_SINGAPORE", "": None,
}
TZ_MAP = {
    "US_NEW_YORK": "America/New_York", "HK_HONGKONG": "Asia/Hong_Kong",
    "CN_MAINLAND": "Asia/Shanghai", "MY_KUALALUMPUR": "Asia/Kuala_Lumpur",
    "TW_TAIPEI": "Asia/Taipei", "CN_GUANGDONG": "Asia/Shanghai",
    "CN_CHAOSHAN": "Asia/Shanghai", "CN_BEIJING": "Asia/Shanghai",
    "JP_MIYAZAKI": "Asia/Tokyo", "SG_SINGAPORE": "Asia/Singapore",
}


def load_cases(data_path: Path):
    with open(data_path, encoding="utf-8") as f:
        data = json.load(f)
    cases = OrderedDict()
    for q in data["questions"]:
        cid = q["case_id"]
        cases.setdefault(cid, {"birth_info": q["birth_info"], "questions": []})
        cases[cid]["questions"].append({
            "id": q["id"], "category": q["category"],
            "question": q["question"], "options": q["options"],
            "answer": q["answer"],
        })
    return cases


def _run_case(pipeline, cid, case):
    b = case["birth_info"]
    loc_id = LOC_MAP.get(b.get("location"), None)
    tz = TZ_MAP.get(loc_id or "", None)
    gender = "male" if b["gender"] == "男" else "female"
    birth = (b["year"], b["month"], b["day"], b["hour"])
    analysis = date(b["year"], 12, 31)
    profile = {}
    for theme in THEMES:
        try:
            result = pipeline.run(
                analysis_date=analysis,
                birth_date=birth,
                gender=gender,
                theme=theme,
                compute_only=True,
                timezone=tz,
                location=loc_id,
                birth_minute=b.get("minute", 0),
            )
            canon = result.canonical.to_dict()
            signals = canon.get("signals") or {}
            norm = {}
            for layer, sigs in signals.items():
                norm[layer] = [
                    {"type": s.get("ontology_type"), "direction": s.get("direction"),
                     "polarity": s.get("polarity"), "strength": s.get("strength"),
                     "rule_refs": s.get("rule_refs")}
                    for s in sigs
                ]
            profile[theme] = norm
        except Exception as e:  # noqa
            profile[theme] = {"error": f"{type(e).__name__}: {e}"}
    return {
        "case_id": cid,
        "birth_info": {
            "raw": case["birth_info"]["raw"],
            "gender": b["gender"],
            "year": b["year"], "month": b["month"], "day": b["day"],
            "hour": b["hour"], "minute": b.get("minute", 0),
            "country": b["country"], "location": b["location"],
            "loc_id": loc_id, "timezone": tz,
        },
        "signal_profile": profile,
        "questions": case["questions"],
    }


def main():
    pipeline = TONGSHUPipeline.for_demo(REPO)
    cases = load_cases(REPO / "data" / "evaluation" / "MingLi-Bench" / "data" / "data.json")
    out_dir = REPO / "src" / "tongshu" / "evaluation" / "reports" / "direction"
    cases_dir = out_dir / "cases"
    cases_dir.mkdir(parents=True, exist_ok=True)

    results = []
    for cid, case in cases.items():
        print(f"[{cid}] {case['birth_info']['raw']}")
        r = _run_case(pipeline, cid, case)
        results.append(r)
        with open(cases_dir / f"{cid}.json", "w", encoding="utf-8") as f:
            json.dump(r, f, ensure_ascii=False, indent=2)

    summary = {
        "total_cases": len(results),
        "total_questions": sum(len(r["questions"]) for r in results),
        "themes": THEMES,
        "generated": date.today().isoformat(),
        "case_files": [f"cases/{r['case_id']}.json" for r in results],
    }
    with open(out_dir / "summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"完成: {len(results)} 命主, 输出到 {out_dir}")


if __name__ == "__main__":
    main()
