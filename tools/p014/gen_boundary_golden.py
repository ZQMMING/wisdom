# -*- coding: utf-8 -*-
"""P0-14 Boundary Golden 生成器。

从已验证的 TimeResolver + BaziAdapter 真实链,为 9 个边界用例
(G6-A..I)计算完整记录,并冻结为:
  1. docs/golden_cases/p014/BOUNDARY-G6-*.yaml   —— 规格(input + expected,回归断言源)
  2. docs/v40/p014_evidence/boundary_records/*.json —— 完整记录(input/resolver/context/
     engine_input/engine_output/expected/evidence/policy_version)

注意:expected_result 由已核验实现计算并冻结(回归护栏),语义正确性由
p014_evidence 的独立审计(EoT 天文核验/23:00 invariant/iztro 行为)背书。
"""
import json
import subprocess
from datetime import date
from pathlib import Path

import yaml

from tongshu.engines.time_resolver import TimeResolver
from tongshu.engines.bazi_adapter import BaziAdapter

REPO = Path(__file__).resolve().parents[3]
GOLDEN_DIR = REPO / "docs" / "golden_cases" / "p014"
REC_DIR = REPO / "docs" / "v40" / "p014_evidence" / "boundary_records"
GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
REC_DIR.mkdir(parents=True, exist_ok=True)

STEM_CN = {"JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
           "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸"}
BRANCH_CN = {"ZI": "子", "CHOU": "丑", "YIN": "寅", "MAO": "卯", "CHEN": "辰", "SI": "巳",
             "WU": "午", "WEI": "未", "SHEN": "申", "YOU": "酉", "XU": "戌", "HAI": "亥"}

r = TimeResolver()
bazi = BaziAdapter()


def pillar_str(p) -> str:
    return STEM_CN.get(p.heavenly_stem, p.heavenly_stem) + BRANCH_CN.get(p.earthly_branch, p.earthly_branch)


def hour_to_time_index(hour: int) -> int:
    """solar hour → iztro timeIndex(早子时=0,丑=1..亥=11,晚子时=12)。"""
    if hour == 0:
        return 0
    return min((hour + 1) // 2, 12)


def iztro_chinese_date(date_str: str, ti: int) -> str:
    """直接调 iztro(证据层,不经 Adapter——Adapter 政策 PENDING)。"""
    js = (
        f"const {{bySolar}}=require('iztro').astro;"
        f"process.stdout.write(bySolar('{date_str}',{ti},'male',true).chineseDate);"
    )
    p = subprocess.run(["node", "-e", js], capture_output=True, text=True,
                       encoding="utf-8", cwd=str(REPO))
    return p.stdout.strip() if p.returncode == 0 else f"ERROR:{p.stderr.strip()}"


# ---- 9 个 Boundary Golden 用例定义(input only) ----
CASES = [
    dict(id="G6-A", label="23:00前:北京 civil 23:17 → solar 22:59 亥时,不换日",
         bd="2020-01-01", t="23:17", tz="Asia/Shanghai", loc="Beijing"),
    dict(id="G6-B", label="23:00整:北京 civil 23:18 → solar 23:00 子时(晚),换日",
         bd="2020-01-01", t="23:18", tz="Asia/Shanghai", loc="Beijing"),
    dict(id="G6-C", label="23:00后:北京 civil 23:30 → solar 23:12 子时(晚),换日",
         bd="2020-01-01", t="23:30", tz="Asia/Shanghai", loc="Beijing"),
    dict(id="G6-D1", label="00:00前:北京 civil 23:59 → solar 23:41 晚子时,换日",
         bd="2020-01-01", t="23:59", tz="Asia/Shanghai", loc="Beijing"),
    dict(id="G6-D2", label="00:00后:北京 civil 00:30 → solar 00:11 早子时,同日",
         bd="2020-01-02", t="00:30", tz="Asia/Shanghai", loc="Beijing"),
    dict(id="G6-E", label="solar date ≠ civil date:civil 2020-01-02 00:10 → solar 01-01 23:51 晚子时,effective=01-02",
         bd="2020-01-02", t="00:10", tz="Asia/Shanghai", loc="Beijing"),
    dict(id="G6-F1", label="DST 夏季 柏林(CEST ref=30):23:30 → solar 22:17 亥时,不换日",
         bd="2020-07-15", t="23:30", tz="Europe/Berlin", loc="Berlin"),
    dict(id="G6-F2", label="DST 冬季 柏林(CET ref=15):23:30 → solar 23:14 子时(晚),换日",
         bd="2020-01-15", t="23:30", tz="Europe/Berlin", loc="Berlin"),
    dict(id="G6-G", label="中国东部经度极值 上海(正校正 +5.88min):23:30 → solar 23:32 子时(晚),换日",
         bd="2020-01-01", t="23:30", tz="Asia/Shanghai", loc="Shanghai"),
    dict(id="G6-H", label="中国西部经度 乌鲁木齐(solar 滞后约2h10m):12:00 → solar 09:49 巳时,同日",
         bd="2020-06-15", t="12:00", tz="Asia/Shanghai", loc="Urumqi"),
    dict(id="G6-I", label="海外 纽约 冬季(EST ref=−75):23:30 → solar 23:24 子时(晚),换日",
         bd="2020-01-15", t="23:30", tz="America/New_York", loc="New York"),
]

records = {}
for c in CASES:
    y, mo, d = map(int, c["bd"].split("-"))
    hh, mm = map(int, c["t"].split(":"))
    ctx = r.resolve_context(birth_date=date(y, mo, d), hour=hh, minute=mm,
                            timezone=c["tz"], location=c["loc"],
                            timezone_source="location_derived")
    chart = bazi.compute(ctx)

    zw = list(ctx.ziwei_view)          # (solar y,m,d,hour)
    ti = hour_to_time_index(zw[3])
    iztro_gz = iztro_chinese_date(f"{zw[0]:04d}-{zw[1]:02d}-{zw[2]:02d}", ti)

    record = {
        "case_id": c["id"],
        "label": c["label"],
        "input": {"birth_date": c["bd"], "birth_time": c["t"],
                  "timezone": c["tz"], "location": c["loc"],
                  "apparent_solar": True},
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
        "engine_input": {"bazi_view": list(ctx.bazi_view), "ziwei_view_iztro": zw},
        "engine_output": {
            "bazi": {"year": pillar_str(chart.year_pillar),
                     "month": pillar_str(chart.month_pillar),
                     "day": pillar_str(chart.day_pillar),
                     "hour": pillar_str(chart.hour_pillar)},
            "iztro_chineseDate": iztro_gz,
        },
        "expected_result": {
            "effective_date": ctx.effective_date.isoformat(),
            "effective_hour": ctx.effective_hour,
            "effective_minute": ctx.effective_minute,
            "day_rolled": ctx.day_rolled,
            "traditional_hour": ctx.traditional_hour,
            "bazi_day_pillar": pillar_str(chart.day_pillar),
            "bazi_hour_pillar": pillar_str(chart.hour_pillar),
            "eot_min": ctx.equation_of_time,
            "longitude_correction_min": ctx.corrections["longitude_correction_min"],
        },
        "evidence": ("docs/v40/p014_evidence/iztro_version.json, "
                     "g6_ab.json, timeindex_matrix.json, time_resolver_audit.json"),
        "policy_version": "V4.0.1-CC-1",
    }
    records[c["id"]] = record

    spec = {k: record[k] for k in ("case_id", "label", "input", "expected_result",
                                   "evidence", "policy_version")}
    with open(GOLDEN_DIR / f"BOUNDARY-{c['id']}.yaml", "w", encoding="utf-8") as f:
        yaml.safe_dump(spec, f, allow_unicode=True, sort_keys=False)
    with open(REC_DIR / f"{c['id']}.json", "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)

print(f"wrote {len(records)} boundary golden cases")
for cid, rec in records.items():
    e = rec["expected_result"]
    print(f"  {cid}: eff={e['effective_date']} {e['effective_hour']:02d}:{e['effective_minute']:02d} "
          f"rolled={e['day_rolled']} {e['traditional_hour']} "
          f"bazi={e['bazi_day_pillar']}{e['bazi_hour_pillar']} iztroGZ={rec['engine_output']['iztro_chineseDate']}")
