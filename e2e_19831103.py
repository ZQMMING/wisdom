# -*- coding: utf-8 -*-
"""Z23 e2e: 1983-11-03 午时 男 广东中山 — 紫微引擎全链路验证"""
import io
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
os.environ["TONGSHU_ALLOW_ZIWEI_STUB"] = "1"

from tongshu.engines.ziwei_engine import ZiweiEngine
from tongshu.engines.ziwei.rules.multi_method import compute_multi_method_signals
from tongshu.engines.ziwei.rules.interpretation import interpret_with_nihai

OUT = os.path.join(os.path.dirname(__file__), "e2e_ziwei_report.json")

engine = ZiweiEngine()
chart = engine.full_chart((1983, 9, 29), 11, "male")
sig = compute_multi_method_signals(chart)
out = interpret_with_nihai(sig, chart)
d = out.to_dict()

report = {
    "命盘": {
        "出生": "1983-11-03 午时 男 广东中山（农历1983-9-29）",
        "五行局": chart.fiveElementsClass,
        "命宫": f"{chart.palaces['命宫']['branch']}（{chart.palaces['命宫']['stem']}干）",
        "身宫": chart.soul_earthly_branch,
        "命宫主星": chart.palaces["命宫"]["major"],
        "命宫辅星": chart.palaces["命宫"]["minor"],
    },
    "南派三合命中": [i.rule_id for i in out.sanhe],
    "北派钦天命中": [i.rule_id for i in out.qintian],
    "倪师断言": [
        {"星": e.star, "宫": e.palace, "类别": e.category, "内容": e.text}
        for e in out.nihai_assertions
    ],
    "大限论断": [
        {
            "年龄": f"{x['age_range'][0]}-{x['age_range'][1]}",
            "宫位": x["palace"],
            "四化": x["sihua"],
            "四化落宫": {k: v for k, v in x["sihua_palaces"].items() if v},
            "断言": len(x["assertions"]),
        }
        for x in out.decadal_fortune
    ],
    "流年论断": {
        "year": out.liunian_fortune.get("year"),
        "干支": out.liunian_fortune.get("stem", "") + out.liunian_fortune.get("branch", ""),
        "落宫": out.liunian_fortune.get("palace"),
        "主星": out.liunian_fortune.get("major_stars"),
        "四化落宫": {k: v for k, v in out.liunian_fortune.get("sihua_palaces", {}).items() if v},
    },
    "流月论断": {
        "年月": f"{out.liuyue_fortune.get('year')}-{out.liuyue_fortune.get('month')}",
        "干支": out.liuyue_fortune.get("stem", "") + out.liuyue_fortune.get("branch", ""),
        "落宫": out.liuyue_fortune.get("palace"),
        "四化落宫": {k: v for k, v in out.liuyue_fortune.get("sihua_palaces", {}).items() if v},
    },
}

txt = io.StringIO()
txt.write("=" * 60 + "\n")
txt.write("紫微引擎全链路验证 — 1983-11-03 午时 男 广东中山\n")
txt.write("=" * 60 + "\n")
txt.write(f"命盘: {report['命盘']}\n\n")
txt.write(f"【南派三合命中】{len(out.sanhe)} 条: {report['南派三合命中']}\n")
txt.write(f"【北派钦天命中】{len(out.qintian)} 条: {report['北派钦天命中']}\n\n")
txt.write(f"【倪师断言】{len(out.nihai_assertions)} 条:\n")
for a in report["倪师断言"]:
    txt.write(f"  [{a['星']}@{a['宫']}] {a['内容']}\n")
txt.write("\n【大限论断】12 宫:\n")
for x in report["大限论断"]:
    txt.write(f"  {x['年龄']}岁 {x['宫位']} 四化{x['四化落宫']} 断言{x['断言']}条\n")
txt.write(f"\n【流年论断】{report['流年论断']}\n")
txt.write(f"【流月论断】{report['流月论断']}\n")

with io.open(OUT, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(txt.getvalue())
print("报告已写入:", OUT)
