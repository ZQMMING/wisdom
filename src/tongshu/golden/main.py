"""Golden Test CLI — runs the full TONGSHU pipeline against all Golden Cases.

Usage (from backend/):
    PYTHONPATH=src python -m tongshu.golden

Runs the real pipeline for every docs/golden_cases/GOLDEN-*.yaml and reports
per-case pass/fail. Exit code 0 = all passed; 1 = any failure.

T601: this drives TONGSHUPipeline (engines + reasoning + canonical + render),
not a synthetic SIR.
"""

from __future__ import annotations
import sys
from pathlib import Path

from ..pipeline import TONGSHUPipeline
from .runner import GoldenRunner, pipeline_to_render_fn

REPO_ROOT = Path(__file__).resolve().parents[4]  # .../通书


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    golden_dir = Path(argv[0]) if argv else REPO_ROOT / "docs" / "golden_cases"
    schema_dir = REPO_ROOT / "docs"

    pipeline = TONGSHUPipeline.for_demo(REPO_ROOT)
    render_fn = pipeline_to_render_fn(pipeline)
    runner = GoldenRunner(golden_dir, schema_dir)

    cases = runner.discover()
    loaded = len(cases)
    print(f"LOADED_CASES: {loaded}")

    if loaded == 0:
        print("WARNING: no golden cases discovered — refusing false-green")
        return 2

    results = runner.run(render_fn)

    print("=" * 68)
    print("TONGSHU Golden Test Suite — full-pipeline run")
    print("=" * 68)
    all_pass = True
    for r in results:
        mark = "PASS" if r.passed else "FAIL"
        all_pass = all_pass and r.passed
        print(f"[{mark}] {r.case_id}")
        for f in r.failures:
            print(f"      - {f}")
    print("-" * 68)
    passed = sum(1 for r in results if r.passed)
    print(f"SUMMARY: {passed}/{len(results)} cases passed")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
