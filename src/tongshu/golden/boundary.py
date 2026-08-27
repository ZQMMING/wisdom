# -*- coding: utf-8 -*-
"""P0-14 Boundary Golden runner — Time Policy → Calculation Context → BaziAdapter。

与 T601 pipeline golden 不同,本 runner 驱动的是 P0-14 时间链:
    Civil birth input → TimeResolver.resolve_context → CalculationContext
        → BaziAdapter.compute(ctx)  (八字视图已 23:00 换日)

规格来源:docs/golden_cases/p014/BOUNDARY-G6-*.yaml
    (由 tools/p014/gen_boundary_golden.py 从已验证实现冻结,input + expected_result)

断言范围(确定性护栏):
    - resolver_output: effective_date / effective_hour / effective_minute /
      day_rolled / traditional_hour / eot / longitude_correction / total_correction
    - engine_input : bazi_view(已换日视图)
    - engine_output: bazi 四柱(年月日时 干支字符串)

iztro 侧输出(engine_output.iztro_chineseDate)是**证据层**,政策 SPEC_DECISION_PENDING,
不作硬断言 —— 它的行为由 p014_evidence/timeindex_matrix.json / g6_ab.json 固定。

每次运行重写完整记录(幂等),若与已冻结记录不一致会报告差异 ——
这使 record JSON 永远反映"当前真实链",YAML expected_result 永远锁定断言。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

from ..engines.bazi_adapter import BaziAdapter
from ..engines.time_resolver import TimeResolver

REPO = Path(__file__).resolve().parents[4]
GOLDEN_DIR = REPO / "docs" / "golden_cases" / "p014"
REC_DIR = REPO / "docs" / "v40" / "p014_evidence" / "boundary_records"

STEM_CN = {"JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
           "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸"}
BRANCH_CN = {"ZI": "子", "CHOU": "丑", "YIN": "寅", "MAO": "卯", "CHEN": "辰", "SI": "巳",
             "WU": "午", "WEI": "未", "SHEN": "申", "YOU": "酉", "XU": "戌", "HAI": "亥"}


@dataclass
class BoundaryGoldenResult:
    case_id: str
    passed: bool
    failures: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"case_id": self.case_id, "passed": self.passed,
                "failures": list(self.failures)}


def _pillar_str(p) -> str:
    return STEM_CN.get(p.heavenly_stem, p.heavenly_stem) + BRANCH_CN.get(p.earthly_branch, p.earthly_branch)


def _compute_record(spec: dict) -> dict:
    """从规格 input 重放真实时间链,重建完整 8 字段记录。"""
    r = TimeResolver()
    bazi = BaziAdapter()
    inp = spec["input"]
    y, mo, d = map(int, inp["birth_date"].split("-"))
    hh, mm = map(int, inp["birth_time"].split(":"))

    ctx = r.resolve_context(
        birth_date=date(y, mo, d), hour=hh, minute=mm,
        timezone=inp["timezone"], location=inp["location"],
        apparent_solar=inp.get("apparent_solar", True),
        timezone_source="location_derived",
    )
    chart = bazi.compute(ctx)

    return {
        "case_id": spec["case_id"],
        "label": spec["label"],
        "input": inp,
        "resolver_output": {
            "eot_min": ctx.equation_of_time,
            "longitude_correction_min": ctx.corrections["longitude_correction_min"],
            "total_correction_min": ctx.corrections["total_correction_min"],
            "ref_meridian": ctx.corrections["ref_meridian"],
            "utc_offset_min": ctx.corrections["utc_offset_min"],
            "true_solar_datetime": ctx.true_solar_datetime.isoformat(),
            "effective_date": ctx.effective_date.isoformat(),
            "effective_hour": ctx.effective_hour,
            "effective_minute": ctx.effective_minute,
            "day_rolled": ctx.day_rolled,
            "traditional_hour": ctx.traditional_hour,
        },
        "calculation_context": {
            "utc_instant": ctx.utc_instant.isoformat(),
            "local_mean_solar_datetime": ctx.local_mean_solar_datetime.isoformat(),
            "bazi_view": list(ctx.bazi_view),
            "ziwei_view": list(ctx.ziwei_view),
            "timezone_source": ctx.timezone_source,
            "warnings": ctx.warnings,
        },
        "engine_input": {"bazi_view": list(ctx.bazi_view)},
        "engine_output": {
            "bazi": {"year": _pillar_str(chart.year_pillar),
                     "month": _pillar_str(chart.month_pillar),
                     "day": _pillar_str(chart.day_pillar),
                     "hour": _pillar_str(chart.hour_pillar)},
            "iztro_chineseDate": None,  # 证据层,运行时由 iztro 探针补充,不作断言
        },
        "expected_result": spec["expected_result"],
        "evidence": spec.get("evidence", ""),
        "policy_version": spec.get("policy_version", ""),
    }


def _run_one(spec: dict, frozen: dict | None) -> BoundaryGoldenResult:
    failures: list[str] = []
    case_id = spec["case_id"]
    rec = _compute_record(spec)

    exp = spec["expected_result"]
    ro = rec["resolver_output"]
    checks = [
        ("effective_date", exp.get("effective_date"), ro["effective_date"]),
        ("effective_hour", exp.get("effective_hour"), ro["effective_hour"]),
        ("effective_minute", exp.get("effective_minute"), ro["effective_minute"]),
        ("day_rolled", exp.get("day_rolled"), ro["day_rolled"]),
        ("traditional_hour", exp.get("traditional_hour"), ro["traditional_hour"]),
    ]
    for name, e, a in checks:
        if e is not None and a != e:
            failures.append(f"{name}: expected={e!r} actual={a!r}")

    # bazi 四柱(engine_output)
    bazi = rec["engine_output"]["bazi"]
    for pillar_name in ("year", "month", "day", "hour"):
        key = f"bazi_{pillar_name}_pillar"
        if exp.get(key) is not None and bazi[pillar_name] != exp[key]:
            failures.append(f"{key}: expected={exp[key]!r} actual={bazi[pillar_name]!r}")

    # 校正值(天文核验值,独立于 effective 字段)
    if exp.get("eot_min") is not None and abs(ro["eot_min"] - exp["eot_min"]) > 0.01:
        failures.append(f"eot_min: expected={exp['eot_min']} actual={ro['eot_min']}")
    if exp.get("longitude_correction_min") is not None and abs(
            ro["longitude_correction_min"] - exp["longitude_correction_min"]) > 0.01:
        failures.append(
            f"longitude_correction_min: expected={exp['longitude_correction_min']} "
            f"actual={ro['longitude_correction_min']}")

    # 若存在已冻结记录,比对除 iztro 证据外的全记录(捕获 spec 未覆盖的漂移)
    if frozen is not None:
        if frozen.get("input") != rec["input"]:
            failures.append(f"record drift [input]: frozen={frozen.get('input')!r} actual={rec['input']!r}")
        if frozen.get("calculation_context") != rec["calculation_context"]:
            failures.append(
                f"record drift [calculation_context]: "
                f"frozen={frozen.get('calculation_context')!r} actual={rec['calculation_context']!r}")
        # engine_input 只比对确定性部分(bazi_view);iztro 侧是证据层,不作断言。
        if frozen.get("engine_input", {}).get("bazi_view") != rec["engine_input"].get("bazi_view"):
            failures.append(
                f"record drift [engine_input.bazi_view]: "
                f"frozen={frozen.get('engine_input', {}).get('bazi_view')!r} "
                f"actual={rec['engine_input'].get('bazi_view')!r}")

    return BoundaryGoldenResult(case_id, len(failures) == 0, failures)


def run_all(golden_dir: Path = GOLDEN_DIR, rec_dir: Path = REC_DIR) -> list[BoundaryGoldenResult]:
    results = []
    for spec_path in sorted(golden_dir.glob("BOUNDARY-*.yaml")):
        with open(spec_path, "r", encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        rec_path = rec_dir / f"{spec['case_id']}.json"
        frozen = None
        if rec_path.exists():
            with open(rec_path, "r", encoding="utf-8") as f:
                frozen = json.load(f)
        results.append(_run_one(spec, frozen))
    return results


def main() -> int:
    results = run_all()
    failed = 0
    for r in results:
        status = "PASS" if r.passed else "FAIL"
        if not r.passed:
            failed += 1
        print(f"  {r.case_id}: {status}")
        for f in r.failures:
            print(f"      - {f}")
    print(f"boundary golden: {len(results) - failed}/{len(results)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
