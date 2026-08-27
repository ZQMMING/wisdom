# -*- coding: utf-8 -*-
"""P0-15 FINALIZATION — G15 晚子时边界 Golden 草案实测。

对 5 个提议 Golden 案例,计算 S1(子正)与 S2(子初)两候选下的:
  - solar_date / solar_hour / traditional_hour(TimeResolver 输出,两候选共享)
  - S1: CCD=solar_date;bazi=sxtwl(solar_date,hour)+S2-hour 后修正(晚子时);ziwei=iztro(solar_date, ti12 若晚子)
  - S2: CCD=solar_date+1(若晚子);bazi=sxtwl(CCD,hour);ziwei=iztro(CCD, ti0 若晚子)
输出 docs/v40/p015_evidence/g15_spec.json。不修改任何引擎/契约代码。
"""
import json
import subprocess
from datetime import date, timedelta
from pathlib import Path

from tongshu.engines.bazi_adapter import BaziAdapter
from tongshu.engines.time_resolver import TimeResolver

REPO = Path(__file__).resolve().parents[3]
OUT = REPO / "docs" / "v40" / "p015_evidence"
OUT.mkdir(parents=True, exist_ok=True)

STEM_CN = {"JIA": "甲", "YI": "乙", "BING": "丙", "DING": "丁", "WU": "戊",
           "JI": "己", "GENG": "庚", "XIN": "辛", "REN": "壬", "GUI": "癸"}
BRANCH_CN = {"ZI": "子", "CHOU": "丑", "YIN": "寅", "MAO": "卯", "CHEN": "辰", "SI": "巳",
             "WU": "午", "WEI": "未", "SHEN": "申", "YOU": "酉", "XU": "戌", "HAI": "亥"}
WUSHU = {"JIA": "甲", "YI": "丙", "BING": "戊", "DING": "庚", "WU": "壬",
         "JI": "甲", "GENG": "丙", "XIN": "戊", "REN": "庚", "GUI": "壬"}
HOUR_CN = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]

_resolver = TimeResolver()
_bazi = BaziAdapter()


def pillar(p):
    return STEM_CN.get(p.heavenly_stem, p.heavenly_stem) + BRANCH_CN.get(p.earthly_branch, p.earthly_branch)


def traditional_hour(sh):
    return HOUR_CN[((sh + 1) // 2) % 12]


def time_index(sh):
    if sh == 23:
        return 12
    return (sh + 1) // 2


def iztro_astro(date_str, ti):
    js = (f"const {{bySolar}}=require('iztro').astro;"
          f"const a=bySolar('{date_str}',{ti},'male',true);"
          f"process.stdout.write(JSON.stringify({{solarDate:a.solarDate,lunarDate:a.lunarDate,"
          f"chineseDate:a.chineseDate,soul:a.earthlyBranchOfSoulPalace}}));")
    p = subprocess.run(["node", "-e", js], capture_output=True, text=True,
                       encoding="utf-8", cwd=str(REPO))
    return json.loads(p.stdout) if p.returncode == 0 else {"error": p.stderr.strip()}


def sxtwl(y, mo, d, h):
    chart = _bazi.engine.compute((y, mo, d, h), gender="M")
    return {"day": pillar(chart.day_pillar), "hour": pillar(chart.hour_pillar),
            "day_stem": chart.day_pillar.heavenly_stem,
            "hour_branch": chart.hour_pillar.earthly_branch}


def s2_hour_corrected(next_day_stem, hour_branch):
    """袁树珊 S2:晚子时时柱 = 次日日干遁。"""
    return WUSHU[next_day_stem] + BRANCH_CN[hour_branch]


def solve(bd, t, tz, loc):
    y, mo, d = map(int, bd.split("-"))
    hh, mm = map(int, t.split(":"))
    ctx = _resolver.resolve_context(birth_date=date(y, mo, d), hour=hh, minute=mm,
                                    timezone=tz, location=loc)
    solar = ctx.true_solar_datetime
    sy, smo, sd, sh = solar.year, solar.month, solar.day, solar.hour
    solar_date = date(sy, smo, sd)
    next_day = solar_date + timedelta(days=1)
    th = traditional_hour(sh)
    ti = time_index(sh)
    is_late_zi = (sh == 23)

    # ---- S1 子正 ----
    s1_ccd = solar_date
    b1 = sxtwl(s1_ccd.year, s1_ccd.month, s1_ccd.day, sh)
    if is_late_zi:
        n = sxtwl(next_day.year, next_day.month, next_day.day, 0)
        s1_bazi = f"{b1['day']} {s2_hour_corrected(n['day_stem'], b1['hour_branch'])}"
    else:
        s1_bazi = f"{b1['day']} {b1['hour']}"
    z1 = iztro_astro(s1_ccd.isoformat(), 12 if is_late_zi else ti)

    # ---- S2 子初 ----
    s2_ccd = next_day if is_late_zi else solar_date
    b2 = sxtwl(s2_ccd.year, s2_ccd.month, s2_ccd.day, sh)
    s2_bazi = f"{b2['day']} {b2['hour']}"
    z2 = iztro_astro(s2_ccd.isoformat(), 0 if is_late_zi else ti)

    return {
        "civil_input": f"{bd} {t}",
        "timezone": tz,
        "location": loc,
        "solar_datetime": solar.isoformat(),
        "solar_date": solar_date.isoformat(),
        "solar_hour": sh,
        "traditional_hour": th,
        "is_late_zi_window": is_late_zi,
        "S1_zizheng": {
            "CCD": s1_ccd.isoformat(),
            "bazi": s1_bazi,
            "ziwei": {"call": f"iztro({s1_ccd.isoformat()}, ti{12 if is_late_zi else ti})", **z1},
        },
        "S2_zichu": {
            "CCD": s2_ccd.isoformat(),
            "bazi": s2_bazi,
            "ziwei": {"call": f"iztro({s2_ccd.isoformat()}, ti{0 if is_late_zi else ti})", **z2},
        },
    }


CASES = {
    "G15-A_北京_晚子时": ("2020-01-01", "23:47", "Asia/Shanghai", "北京"),
    "G15-B_北京_民用午夜后": ("2020-01-02", "00:10", "Asia/Shanghai", "北京"),
    "G15-C_北京_早子时": ("2020-01-02", "00:50", "Asia/Shanghai", "北京"),
    "G15-D_乌鲁木齐_民用午夜": ("2020-01-02", "00:00", "Asia/Shanghai", "乌鲁木齐"),
    "G15-E_柏林_夏令时午夜后": ("2019-06-16", "00:30", "Europe/Berlin", "柏林"),
}

results = {k: solve(*v) for k, v in CASES.items()}
with open(OUT / "g15_spec.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

for k, v in results.items():
    print(f"== {k} | {v['civil_input']} {v['timezone']}")
    print(f"   solar {v['solar_datetime']} | 日 {v['solar_date']} | 时 {v['solar_hour']} | 传统时辰 {v['traditional_hour']} | 晚子时窗口 {v['is_late_zi_window']}")
    print(f"   S1子正: CCD={v['S1_zizheng']['CCD']} bazi={v['S1_zizheng']['bazi']} ziwei={v['S1_zizheng']['ziwei']['call']} -> {v['S1_zizheng']['ziwei'].get('lunarDate')} 日柱={v['S1_zizheng']['ziwei'].get('chineseDate')}")
    print(f"   S2子初: CCD={v['S2_zichu']['CCD']} bazi={v['S2_zichu']['bazi']} ziwei={v['S2_zichu']['ziwei']['call']} -> {v['S2_zichu']['ziwei'].get('lunarDate')} 日柱={v['S2_zichu']['ziwei'].get('chineseDate')}")
