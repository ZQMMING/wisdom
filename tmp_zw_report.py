# -*- coding: utf-8 -*-
"""紫微斗数解层 — 15 例完整输出。只跑紫微引擎。"""
import sys, os
sys.path.insert(0, 'src')
os.environ['TONGSHU_ALLOW_ZIWEI_STUB'] = '1'

from tongshu.engines.ziwei_engine import ZiweiEngine, GAN_SIHUA
from tongshu.engines.ziwei.rules.multi_method import compute_multi_method_signals
from tongshu.engines.ziwei.rules.interpretation import build_life_reading

CASES = [
    ("男", "壬子辛亥壬辰丙午", (1912, 10, 4), "一九一二年十月初四", 11),
    ("女", "丁未癸卯庚子丁丑", (2027, 2, 15), "二零二七年二月十五", 1),
    ("男", "戊申己未庚申辛巳", (2028, 6, 13), "二零二八年六月十三", 9),
    ("女", "甲寅丙子己亥戊辰", (1974, 11, 11), "一九七四年冬月十一", 7),
    ("男", "丁亥癸丑己未癸酉", (1947, 12, 25), "一九四七年腊月廿五", 17),
    ("男", "庚寅戊寅己亥丙寅", (2010, 1, 5), "二零一零年正月初五", 3),
    ("男", "戊申己未癸巳己未", (1968, 6, 27), "一九六八年六月廿七", 13),
    ("男", "乙巳甲申辛酉乙未", (1965, 8, 9), "一九六五年八月初九", 13),
    ("男", "癸丑乙卯戊戌癸亥", (1913, 2, 11), "一九一三年二月十一", 21),
    ("女", "戊申壬戌甲子丙寅", (1968, 8, 30), "一九六八年八月三十", 3),
    ("女", "庚寅乙酉戊午丁巳", (1950, 8, 9), "一九五零年八月初九", 9),
    ("女", "丁亥甲辰己巳丙寅", (1947, 2, 29), "一九四七年闰二月廿九", 3),
    ("女", "甲辰庚午甲辰戊辰", (1964, 5, 15), "一九六四年五月十五", 7),
    ("女", "乙丑辛巳辛酉己亥", (1985, 4, 3), "一九八五年四月初三", 21),
    ("女", "乙未乙酉庚子丁丑", (2015, 8, 9), "二零一五年八月初九", 1),
]

DIM_NAMES = {
    "temperament":"①性情禀赋","social":"②交游人际","marriage":"③婚姻配偶",
    "children":"④子女","wealth":"⑤财帛","health":"⑥身体疾厄",
    "migration":"⑦迁移出行","career":"⑧事业功名","property":"⑨田宅家业",
    "fortune":"⑩福德精神","parents":"⑪父母长辈","talent":"⑫才艺学业",
}

eng = ZiweiEngine()
print("="*72)
print("  紫微斗数解层 — 15 例完整报告")
print("="*72)

for idx,(g,baz,ld,lun,hour) in enumerate(CASES,1):
    y,m,d = ld
    print()
    print("="*72)
    print("【紫微案例 %d】%s | %s | %d时" % (idx, lun, g, hour))
    print("  四柱参考: %s" % baz)
    try:
        chart = eng.full_chart((y,m,d), hour, g)
        if not hasattr(chart,'palaces') or not chart.palaces:
            print("  ⚠️ 排盘为空(stub)，跳过")
            continue

        signal = compute_multi_method_signals(chart)
        print("  [派别信号] 总命中=%d 状态=%s" % (
            signal.total_matched_rules, signal.compute_status))
        for mid, bundle in signal.bundles.items():
            if bundle.matched_rules:
                print("    %s: %d条 (%s)" % (mid, len(bundle.matched_rules), bundle.implementation_status))

        reading = build_life_reading(chart, signal, target_year=2024)
        main_star = (chart.soul_palace_main_stars[0] if chart.soul_palace_main_stars
                     else getattr(chart,'soul_palace_main_star',''))
        print("  [命宫] 主星=%s 五行局=%s 命支=%s" % (
            main_star or '(空)', getattr(chart,'fiveElementsClass',''),
            getattr(chart,'soul_earthly_branch','')))

        for dim_key, dim_name in DIM_NAMES.items():
            items = getattr(reading, dim_key, [])
            if items and len(items) > 0:
                t = items[0].text[:90] if hasattr(items[0],'text') else str(items[0])[:90]
                src = items[0].classic if hasattr(items[0],'classic') else ''
                print("  [%s] %s: %s" % (dim_name, src, t))
            else:
                print("  [%s] (无触发断语)" % dim_name)
    except Exception as ex:
        print("  ERROR: %s: %s" % (type(ex).__name__, ex))
        import traceback; traceback.print_exc()

print()
print("="*72)
print("  紫微解层报告完毕")
print("="*72)