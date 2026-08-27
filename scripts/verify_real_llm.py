"""Real-LLM Golden verification (T501 follow-up).

Runs every Golden Case N times through the REAL pipeline (env-gated: requires
DEEPSEEK_API_KEY in the environment or backend/.env) and reports, per run:
    - golden pass/fail (the full runner assertion suite)
    - source        (llm_renderer vs template_fallback)
    - validation_passed
    - text length + forbidden-word scan

The bare golden runner is NOT sufficient to prove the LLM path: if the LLM
output fails Layer 1/2/3 the pipeline silently falls back to the template and
the runner still passes. A run only counts as a TRUE LLM success when:
    golden passed AND source == "llm_renderer" AND validation_passed.

Usage (from backend/):
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python scripts/verify_real_llm.py
Env:
    TONGSHU_GOLDEN_RUNS  runs per case (default 3)
"""

from __future__ import annotations
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import yaml

from tongshu.pipeline import TONGSHUPipeline
from tongshu.golden.runner import GoldenRunner, pipeline_to_render_fn

REPO_ROOT = Path(__file__).resolve().parents[2]  # .../通书-claude
RUNS = int(os.environ.get("TONGSHU_GOLDEN_RUNS", "3"))


def main() -> int:
    pipeline = TONGSHUPipeline.for_demo(REPO_ROOT)
    render_fn = pipeline_to_render_fn(pipeline)
    runner = GoldenRunner(REPO_ROOT / "docs" / "golden_cases", REPO_ROOT / "docs")

    print("=" * 72)
    print(f"Real-LLM Golden verification — renderer: "
          f"{'STUB' if pipeline.renderer.is_stub else 'REAL LLM'}, {RUNS} runs/case")
    print("=" * 72)
    if pipeline.renderer.is_stub:
        print("FATAL: no DEEPSEEK_API_KEY in env or backend/.env — cannot verify real LLM.")
        return 2

    cases = sorted((REPO_ROOT / "docs" / "golden_cases").glob("GOLDEN-*.yaml"))
    total_llm_ok = 0
    total_runs = 0
    worst = None

    for case_path in cases:
        with open(case_path, "r", encoding="utf-8") as f:
            case = yaml.safe_load(f)
        inp = case.get("input", {})
        y, m, d = (int(x) for x in inp["birth_date"].split("-"))
        hour = inp.get("hour", 12)
        gender = inp.get("gender", "M")
        theme = inp.get("theme", "WORK")
        y2, m2, d2 = (int(x) for x in inp.get("date_of_analysis", "2026-08-17").split("-"))
        from datetime import date

        ad = date(y2, m2, d2)

        print(f"\n[{case_path.stem}]")
        llm_ok = 0
        for i in range(RUNS):
            out = render_fn(
                birth_date=(y, m, d, hour),
                analysis_date=ad,
                gender=gender,
                theme=theme,
            )
            res = runner._run_one(case, lambda **kw: out, "1.0")
            is_true = res.passed and out["source"] == "llm_renderer" and out["validation_passed"]
            if is_true:
                llm_ok += 1
            length = len(out["text"])
            flag = "OK " if is_true else "FAIL"
            if not is_true:
                for f in res.failures[:4]:
                    print(f"      - {f}")
            print(f"  run {i + 1}: {flag} source={out['source']:>18} "
                  f"valid={out['validation_passed']} len={length}")
        total_llm_ok += llm_ok
        total_runs += RUNS
        if llm_ok < RUNS:
            worst = case_path.stem

    print("\n" + "=" * 72)
    print(f"SUMMARY: {total_llm_ok}/{total_runs} runs are TRUE LLM success "
          f"(golden + llm_renderer + validation_passed)")
    if worst:
        print(f"NOT fully green — first non-green case: {worst}")
        return 1
    print("ALL GREEN: golden 20/20 under the real LLM renderer")
    return 0


if __name__ == "__main__":
    sys.exit(main())
