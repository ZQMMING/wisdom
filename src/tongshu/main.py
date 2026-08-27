"""TONGSHU CLI entry point — runs GOLDEN-001 end-to-end.

This is the first vertical slice through the entire pipeline.
"""

from __future__ import annotations
import json
import sys
from datetime import date
from pathlib import Path

from .pipeline import TONGSHUPipeline


def main():
    repo_root = Path(__file__).parent.parent.parent.parent
    pipeline = TONGSHUPipeline.for_demo(repo_root)

    print("=" * 60)
    print("TONGSHU Pipeline v1.0 - Demo Run")
    print("=" * 60)

    # GOLDEN-001: 1984-12-07 16:00 男命 / WORK theme
    result = pipeline.run(
        analysis_date=date(2026, 8, 17),
        birth_date=(1984, 12, 7, 16),
        gender="male",
        theme="WORK",
    )

    print(f"\n[Canonical Content]")
    print(f"  canonical_id: {result.canonical.canonical_id}")
    print(f"  schema_version: {result.canonical.schema_version}")
    print(f"  cross_status: {result.canonical.cross_analysis['status']}")
    print(f"  signals: BASELINE={len(result.canonical.signals.get('BASELINE', []))}, CYCLE={len(result.canonical.signals.get('CYCLE_CONTEXT', []))}, DAILY={len(result.canonical.signals.get('DAILY_ACTIVATION', []))}")
    print(f"  atomic_claims: {len(result.canonical.atomic_claims)}")
    print(f"  exclusions: {len(result.canonical.exclusions)}")

    print(f"\n[Rendered Output] (source={result.source})")
    print(f"  {result.rendered_text}")

    print(f"\n[Audit]")
    print(f"  entry_id: {result.audit_entry_id}")
    print(f"  validation_passed: {result.validation_passed}")

    print(f"\n[Canonical Content JSON]")
    print(json.dumps(result.canonical.to_dict(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

