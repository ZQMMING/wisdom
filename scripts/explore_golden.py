"""Golden case exploration tool (T601 扩集).

Two modes:
  --scan                     Scan a date range, bucket charts by rule paths
                             (seed rule / 格局 / main star / DAILY layer),
                             print bucket counts + representative dates.
  --dump YYYY-MM-DD H GENDER THEME ANALYSIS_DATE
                             Run the full pipeline (Stub) for one candidate and
                             dump complete ground truth: four pillars, ten gods,
                             藏干, main star, per-layer signals (all fields +
                             rule_refs/evidence_refs), cross analysis, claims.

Usage (from backend/):
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python explore_golden.py --scan
    PYTHONIOENCODING=utf-8 PYTHONPATH=src python explore_golden.py \
        --dump 1990-05-03 10 M WORK 2026-08-17

LLM env must be cleared to force Stub (same discipline as golden runner):
    DEEPSEEK_API_KEY= TONGSHU_LLM_API_KEY= TONGSHU_LLM_BASE_URL= \
    TONGSHU_LLM_MODEL=  ...
"""

from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

from tongshu.engines.bazi_engine import BaziEngine, STEM_ELEMENT
from tongshu.engines.ziwei_engine import ZiweiEngine
from tongshu.engines.huangli_engine import HuangliEngine
from tongshu.reasoning.bazi_ten_gods import (
    month_hidden_main_ten_god,
    hidden_main_stem_is_transparent,
    ZAGI_BRANCHES,
)
from tongshu.pipeline import TONGSHUPipeline

DM_POLARITY = {"JIA": "阳", "YI": "阴", "BING": "阳", "DING": "阴",
               "WU": "阳", "JI": "阴", "GENG": "阳", "XIN": "阴",
               "REN": "阳", "GUI": "阴"}


def _pillar_str(p) -> str:
    return f"{p.heavenly_stem}{p.earthly_branch}"


def chart_bucket(bazi, hour: int) -> str:
    dm_el = STEM_ELEMENT[bazi.day_master]
    seed = {
        "WOOD": "ZPZ-001", "FIRE": "ZPZ-002", "EARTH": "ZPZ-003",
        "METAL": "ZPZ-004", "WATER": "ZPZ-005",
    }[dm_el]
    mb = bazi.month_pillar.earthly_branch
    mh_tg = month_hidden_main_ten_god(bazi.day_master, mb)
    trans = hidden_main_stem_is_transparent(
        mb, [bazi.year_pillar.heavenly_stem, bazi.month_pillar.heavenly_stem,
             bazi.day_pillar.heavenly_stem, bazi.hour_pillar.heavenly_stem])
    zagi = mb in ZAGI_BRANCHES
    return (
        f"seed={seed}({dm_el}) | 格局={mh_tg} "
        f"| {'杂气' if zagi else '当令'}"
        f"{'透' if trans else ''}"
        f" | DM={bazi.day_master}"
    )


def scan(start: date, end: date, step_days: int = 7) -> None:
    # Phase A: pure-Bazi bucketing (no iztro subprocess — fast).
    be = BaziEngine()
    buckets: dict[str, list[tuple[date, int]]] = {}
    d = start
    n = 0
    while d <= end:
        for hour in (8, 12, 16, 20):
            bazi = be.compute((d.year, d.month, d.day, hour), gender="M")
            key = chart_bucket(bazi, hour)
            buckets.setdefault(key, []).append((d, hour))
            n += 1
        d += timedelta(days=step_days)
    print(f"scanned {n} chart-candidates ({start} .. {end}) -> {len(buckets)} distinct buckets")
    print("-" * 100)
    for key in sorted(buckets):
        dates = buckets[key]
        sample = ", ".join(f"{x[0]}+{x[1]:02d}h" for x in dates[:5])
        print(f"[{len(dates):3d}] {key}")
        print(f"       e.g. {sample} ...")


def _dump_to(pipeline, out_path: Path, bd: str, hour: int, gender: str,
             theme: str, ad: str) -> None:
    y, m, d = (int(x) for x in bd.split("-"))
    ay, am, ad2 = (int(x) for x in ad.split("-"))
    birth_date = (y, m, d, hour)

    # Ground-truth charts (same engines the pipeline uses).
    be, ze, he = BaziEngine(), ZiweiEngine(node_modules_dir=REPO_ROOT / "node_modules"), HuangliEngine()
    bazi = be.compute(birth_date, gender=gender)
    ziwei = ze.compute(birth_date, gender=gender)
    hl = he.get_day(date(ay, am, ad2))

    out: dict = {
        "input": {"birth_date": bd, "hour": hour, "gender": gender,
                  "theme": theme, "date_of_analysis": ad},
        "pillars": {
            "year": _pillar_str(bazi.year_pillar),
            "month": _pillar_str(bazi.month_pillar),
            "day": _pillar_str(bazi.day_pillar),
            "hour": _pillar_str(bazi.hour_pillar),
            "day_master": bazi.day_master,
            "day_master_element": STEM_ELEMENT[bazi.day_master],
        },
        "ten_gods": {
            "month_hidden_main": month_hidden_main_ten_god(
                bazi.day_master, bazi.month_pillar.earthly_branch),
            "month_branch_transparent": hidden_main_stem_is_transparent(
                bazi.month_pillar.earthly_branch,
                [bazi.year_pillar.heavenly_stem, bazi.month_pillar.heavenly_stem,
                 bazi.day_pillar.heavenly_stem, bazi.hour_pillar.heavenly_stem]),
        },
        "ziwei": {"main_star": ziwei.soul_palace_main_star or "N/A"},
        "huangli": {"day_stem": hl.day_stem, "day_branch": hl.day_branch},
    }

    result = pipeline.run(analysis_date=date(ay, am, ad2), birth_date=birth_date,
                          gender=gender, theme=theme)
    canon = result.canonical
    out["cross_analysis"] = canon.cross_analysis
    out["cross_status"] = canon.cross_analysis.get("status")
    out["signals"] = canon.signals
    out["atomic_claims"] = canon.atomic_claims
    out["source"] = result.source
    out["validation_passed"] = result.validation_passed
    out["rendered_text"] = result.rendered_text
    out["rendered_len"] = len(result.rendered_text)
    if out_path:
        out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        print(json.dumps(out, ensure_ascii=False, indent=2))


def dump(bd: str, hour: int, gender: str, theme: str, ad: str) -> None:
    pipeline = TONGSHUPipeline.for_demo(REPO_ROOT)
    _dump_to(pipeline, None, bd, hour, gender, theme, ad)


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--scan":
        scan(date(1955, 1, 1), date(2005, 12, 31))
        return 0
    if argv and argv[0] == "--dump":
        if len(argv) < 6:
            print("usage: --dump YYYY-MM-DD HOUR GENDER THEME ANALYSIS_DATE")
            return 2
        dump(argv[1], int(argv[2]), argv[3], argv[4], argv[5])
        return 0
    if argv and argv[0] == "--batch":
        # lines: "YYYY-MM-DD HOUR GENDER THEME ANALYSIS_DATE [TAG]"
        out_dir = REPO_ROOT / "backend" / "_explore"
        out_dir.mkdir(exist_ok=True)
        for line in open(argv[1], encoding="utf-8"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            bd, hour, gender, theme, ad = parts[0], int(parts[1]), parts[2], parts[3], parts[4]
            tag = parts[5] if len(parts) > 5 else f"{bd}+{hour:02d}h"
            out = out_dir / f"{tag}.json"
            if out.exists():
                print(f"skip {tag} (exists)")
                continue
            pipeline = TONGSHUPipeline.for_demo(REPO_ROOT)
            try:
                _dump_to(pipeline, out, bd, hour, gender, theme, ad)
                print(f"ok {tag}")
            except Exception as e:
                print(f"FAIL {tag}: {e}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
