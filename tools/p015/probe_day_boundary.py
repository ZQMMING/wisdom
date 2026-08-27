# -*- coding: utf-8 -*-
"""P0-15 日界分歧实测:晚子时窗口下 V1(子正)与 iztro/sxtwl 的一致性检验。

对同一出生(真太阳时 2020-01-01 23:30,北京),计算三种编码:
  A) V1 子正+S2(袁树珊):  日柱=solar date(01-01), 时柱=次日日干遁(甲子)
  B) V1 子正+S3(今日遁):  日柱=solar date(01-01), 时柱=当日日干遁(壬子)= sxtwl 原生
  C) iztro 2.6.0 实际:    (01-01, ti12) → 日柱 甲辰(次日), 时柱 甲子
  D) iztro 2.6.0 对照:    (01-02, ti0)  → 日柱 甲辰, 时柱 甲子 (次日早子时)
对照早子时窗口(真太阳时 01-02 00:30):三途径应一致(甲辰 甲子)。

输出写 p015_evidence/day_boundary_divergence.json
"""
import json
import subprocess
from datetime import date
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

_resolver = TimeResolver()
_bazi = BaziAdapter()


def pillar(p):
    return STEM_CN.get(p.heavenly_stem, p.heavenly_stem) + BRANCH_CN.get(p.earthly_branch, p.earthly_branch)


def iztro_gz(date_str, ti):
    js = (f"const {{bySolar}}=require('iztro').astro;"
          f"const a=bySolar('{date_str}',{ti},'male',true);"
          f"process.stdout.write(JSON.stringify({{chineseDate:a.chineseDate,"
          f"soul:a.earthlyBranchOfSoulPalace,solarDate:a.solarDate,lunarDate:a.lunarDate}}));")
    p = subprocess.run(["node", "-e", js], capture_output=True, text=True,
                       encoding="utf-8", cwd=str(REPO))
    if p.returncode != 0:
        return {"error": p.stderr.strip()}
    import json as _j
    return _j.loads(p.stdout)


def solve(bd, t):
    """返回 solar date/hour + 三种八字编码 + iztro 两个对照。"""
    y, mo, d = map(int, bd.split("-"))
    hh, mm = map(int, t.split(":"))
    ctx = _resolver.resolve_context(birth_date=date(y, mo, d), hour=hh, minute=mm,
                                    timezone="Asia/Shanghai", location="Beijing")
    solar = ctx.true_solar_datetime  # tzinfo=民用帧,读 wall-clock
    sy, smo, sd = solar.year, solar.month, solar.day
    sh = solar.hour
    solar_date = f"{sy:04d}-{smo:02d}-{sd:02d}"

    # sxtwl 对 solar date + hour 的原生输出(即 子正+S3 / 今日遁)
    sxtwl_chart = _bazi.engine.compute((sy, smo, sd, sh), gender="M")
    s3 = f"{pillar(sxtwl_chart.day_pillar)} {pillar(sxtwl_chart.hour_pillar)}"

    # V1 子正(袁树珊 S2 规则):
    #   夜子时(真太阳 23:00-23:59):日柱=solar date(今日),时柱=次日日干遁(作明日算)
    #   早子时(真太阳 00:00-00:59):日柱=今日(已跨日),时柱=今日日干遁(标准,=sxtwl native)
    wushu = {"JIA": "甲", "YI": "丙", "BING": "戊", "DING": "庚", "WU": "壬",
             "JI": "甲", "GENG": "丙", "XIN": "戊", "REN": "庚", "GUI": "壬"}
    from datetime import date as _d, timedelta as _td
    nd = _d(sy, smo, sd) + _td(days=1)
    next_chart = _bazi.engine.compute((nd.year, nd.month, nd.day, 0), gender="M")
    hour_branch = sxtwl_chart.hour_pillar.earthly_branch
    s2_day = pillar(sxtwl_chart.day_pillar)
    if sh >= 23:
        # 夜子时: 时柱=次日日干遁
        next_stem = next_chart.day_pillar.heavenly_stem
        s2 = f"{s2_day} {wushu[next_stem]}{BRANCH_CN[hour_branch]}"
    else:
        # 早子时及更晚: 时柱=当日日干遁(= sxtwl native)
        s2 = s3

    # iztro:ti12(solar date 晚子时)与 ti0(次日早子时)
    iztro_ti = iztro_gz(solar_date, 12)
    nxt = f"{nd.year:04d}-{nd.month:02d}-{nd.day:02d}"
    iztro_ti0_nxt = iztro_gz(nxt, 0)

    return {
        "civil_input": f"{bd} {t}",
        "solar_datetime": ctx.true_solar_datetime.isoformat(),
        "solar_date": solar_date,
        "solar_hour": sh,
        "effective_date_p014": ctx.effective_date.isoformat(),  # P0-14 子初翻日结果
        "encodings": {
            "A_V1_subzheng_S2_yuanshushan": s2,          # 日柱今日+时柱次日遁
            "B_V1_subzheng_S3_sxtwl_native": s3,         # 日柱今日+时柱今日遁(sxtwl 原生)
            "C_iztro_actual_ti12": iztro_ti,             # iztro (solar_date, ti12)
            "D_iztro_ti0_nextday": iztro_ti0_nxt,        # iztro (次日, ti0)
        },
    }


results = {}
for label, (bd, t) in {
    "晚子时_北京_solar_2330": ("2020-01-01", "23:47"),   # → solar 01-01 23:29(晚子)
    "晚子时_次日_北京_solar_2330": ("2020-01-02", "23:47"),  # → solar 01-02 23:29(晚子;展示时柱一致仅日柱分歧)
    "民用午夜_北京_solar_2352": ("2020-01-02", "00:10"),  # → solar 01-01 23:51(民用00:10仍是晚子!)
    "正子时后_北京_solar_0110": ("2020-01-02", "00:50"),  # → solar 01-02 00:31(早子)
}.items():
    results[label] = solve(bd, t)

with open(OUT / "day_boundary_divergence.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

for k, v in results.items():
    print(f"== {k} | solar {v['solar_datetime']} | eff(p014) {v['effective_date_p014']}")
    for ek, ev in v["encodings"].items():
        print(f"    {ek}: {ev}")
