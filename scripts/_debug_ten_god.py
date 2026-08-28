"""检查十神计算错误的具体原因."""
import json
import sys
sys.path.insert(0, "src")

from p6c_temporal_contract import compute_year_pillar, compute_ten_god, HEAVENLY_STEMS
from tongshu.engines.bazi_engine import BaziEngine

# 加载Baseline V1
with open("docs/audit/p6c_temporal_baseline_v1.json", encoding="utf-8") as f:
    baseline = json.load(f)

results = baseline["detailed_results"]

# 加载Golden Dataset
with open("dataset/golden_v1/golden_cases.json", encoding="utf-8") as f:
    golden_cases = json.load(f)["cases"]

# 建立case_id -> birth info
case_birth = {}
for case in golden_cases:
    case_birth[case["case_id"]] = {
        "birth_date": case["birth_date"],
        "birth_hour": case["birth_hour"],
        "gender": case["gender"],
    }

# 检查前10个错误案例
error_count = 0
for r in results[:50]:
    case_id = r["case_id"]
    target_year = r["target_year"]
    pred_ten_god = r["ten_god"]

    birth = case_birth[case_id]
    birth_parts = birth["birth_date"].split("-")
    birth_year = int(birth_parts[0])
    birth_month = int(birth_parts[1])
    birth_day = int(birth_parts[2])
    birth_hour = birth["birth_hour"]
    gender = birth["gender"]

    engine = BaziEngine()
    try:
        chart = engine.compute((birth_year, birth_month, birth_day, birth_hour), gender)
        day_master = chart.day_master
    except Exception as e:
        day_master = "ERROR"
        print(f"  BaziEngine error for {case_id}: {e}")

    year_stem, year_branch = compute_year_pillar(target_year)
    expected_ten_god = compute_ten_god(day_master, year_stem)

    if pred_ten_god != expected_ten_god:
        error_count += 1
        if error_count <= 10:
            print(f"\n  错误案例 {error_count}:")
            print(f"    case_id: {case_id}")
            print(f"    birth: {birth['birth_date']} {birth_hour}:00 {gender}")
            print(f"    target_year: {target_year}")
            print(f"    day_master (BaziEngine): {day_master}")
            print(f"    year_stem: {year_stem}")
            print(f"    pred_ten_god: {pred_ten_god}")
            print(f"    expected_ten_god: {expected_ten_god}")

            # 手动验证十神
            print(f"    手动验证: 日主={day_master}, 流年干={year_stem}")
            if (day_master, year_stem) in __import__('p6c_temporal_contract').TEN_GOD_MAP:
                manual = __import__('p6c_temporal_contract').TEN_GOD_MAP[(day_master, year_stem)]
                print(f"    TEN_GOD_MAP查找: {manual}")

print(f"\n前50条中错误数: {error_count}")
print(f"错误率: {error_count/50*100:.1f}%")
