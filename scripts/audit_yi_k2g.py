#!/usr/bin/env python3
"""Deep audit of YIJING K2G concepts against engine data."""
import yaml
from pathlib import Path
from tongshu.engines.yi.hexagram_symbol import TRIGRAM_DATA, SIXTY_FOUR_MAP
from tongshu.engines.yi.yao_ci_data import YAO_CI

concepts_dir = Path("src/tongshu/k2g/concepts")
yi = yaml.safe_load((concepts_dir / "yi_concepts.yaml").read_text(encoding="utf-8"))
concepts = yi["concepts"]

errors = []
warnings = []

# 1. 八卦审核
print("=" * 60)
print("1. 八卦 TRIGRAMS 审核")
print("=" * 60)
trigram_concepts = [c for c in concepts if c["category"] == "TRIGRAMS"]
print(f"数量: {len(trigram_concepts)} (期望8)")
for c in trigram_concepts:
    name = c["traditional_term"]
    engine = TRIGRAM_DATA.get(name, {})
    defn = c["canonical_definition"]
    # 检查五行
    expected_elem = engine.get("element", "")
    if expected_elem and expected_elem not in defn:
        errors.append(f"[TRIGRAM] {name}: 定义未含五行'{expected_elem}'")
    # 检查先天数
    expected_num = engine.get("number", "")
    if expected_num and str(expected_num) not in defn:
        errors.append(f"[TRIGRAM] {name}: 定义未含先天数'{expected_num}'")
    print(f"  {name}: 五行={expected_elem} 数={expected_num} 符号={engine.get('symbol','')} -> {'OK' if expected_elem in defn and str(expected_num) in defn else 'FAIL'}")

# 2. 六十四卦审核
print("\n" + "=" * 60)
print("2. 六十四卦 HEXAGRAMS 审核")
print("=" * 60)
hex_concepts = [c for c in concepts if c["category"] == "HEXAGRAMS"]
print(f"数量: {len(hex_concepts)} (期望64)")

# 建立反向映射: 卦名 -> (上卦, 下卦)
name_to_trigrams = {v: k for k, v in SIXTY_FOUR_MAP.items()}
engine_hex_names = set(name_to_trigrams.keys())
concept_hex_names = set(c["traditional_term"] for c in hex_concepts)

# 检查卦名一致性
missing_in_concepts = engine_hex_names - concept_hex_names
extra_in_concepts = concept_hex_names - engine_hex_names
if missing_in_concepts:
    errors.append(f"[HEXAGRAM] 引擎有但概念缺失: {missing_in_concepts}")
if extra_in_concepts:
    errors.append(f"[HEXAGRAM] 概念有但引擎缺失: {extra_in_concepts}")

# 检查YAO_CI一致性
yao_ci_names = set(YAO_CI.keys())
missing_yao = engine_hex_names - yao_ci_names
if missing_yao:
    warnings.append(f"[YAO_CI] 引擎SIXTY_FOUR_MAP有但YAO_CI缺: {missing_yao}")

# 逐卦检查上下卦
mismatch = 0
for c in hex_concepts:
    name = c["traditional_term"]
    defn = c["canonical_definition"]
    if name in name_to_trigrams:
        upper, lower = name_to_trigrams[name]
        expected = f"{upper}上{lower}下"
        if expected not in defn:
            errors.append(f"[HEXAGRAM] {name}: 定义应为'{expected}'，实际定义: {defn}")
            mismatch += 1
        # 检查五行
        elem_upper = TRIGRAM_DATA.get(upper, {}).get("element", "")
        elem_lower = TRIGRAM_DATA.get(lower, {}).get("element", "")
        expected_elem = f"{elem_upper}{elem_lower}"
        if expected_elem not in defn:
            warnings.append(f"[HEXAGRAM] {name}: 五行标注'{expected_elem}'未在定义中")

print(f"  引擎卦名: {len(engine_hex_names)} 概念卦名: {len(concept_hex_names)}")
print(f"  上下卦不匹配: {mismatch}")
print(f"  YAO_CI覆盖: {len(yao_ci_names)}/64")

# 3. 核心术语审核
print("\n" + "=" * 60)
print("3. 核心术语 KEY_TERMS 审核")
print("=" * 60)
kt_concepts = [c for c in concepts if c["category"] == "KEY_TERMS"]
print(f"数量: {len(kt_concepts)}")
for c in kt_concepts:
    print(f"  {c['traditional_term']}: {c['canonical_definition'][:50]}...")

# 4. ID格式审核
print("\n" + "=" * 60)
print("4. ID格式审核")
print("=" * 60)
ids = [c["concept_id"] for c in concepts]
prefixes = {}
for cid in ids:
    prefix = cid.split("_")[0] + "_" + cid.split("_")[1]
    prefixes[prefix] = prefixes.get(prefix, 0) + 1
print(f"ID前缀分布: {prefixes}")
# 检查ID连续性
tr_ids = sorted([int(c["concept_id"].split("_")[2]) for c in concepts if c["category"] == "TRIGRAMS"])
hx_ids = sorted([int(c["concept_id"].split("_")[2]) for c in concepts if c["category"] == "HEXAGRAMS"])
kt_ids = sorted([int(c["concept_id"].split("_")[2]) for c in concepts if c["category"] == "KEY_TERMS"])
print(f"TR IDs: {tr_ids[0]}-{tr_ids[-1]} (连续: {tr_ids == list(range(tr_ids[0], tr_ids[-1]+1))})")
print(f"HX IDs: {hx_ids[0]}-{hx_ids[-1]} (连续: {hx_ids == list(range(hx_ids[0], hx_ids[-1]+1))})")
print(f"KT IDs: {kt_ids[0]}-{kt_ids[-1]} (连续: {kt_ids == list(range(kt_ids[0], kt_ids[-1]+1))})")

# 5. 必填字段审核
print("\n" + "=" * 60)
print("5. 必填字段审核")
print("=" * 60)
required = ["concept_id", "traditional_term", "canonical_definition", "category", "product_semantic", "source_refs", "verification_status", "created_at"]
missing_fields = 0
for c in concepts:
    for f in required:
        if f not in c or c[f] is None or c[f] == "":
            errors.append(f"[FIELD] {c.get('concept_id','?')}: 缺少字段'{f}'")
            missing_fields += 1
print(f"缺失字段: {missing_fields}")

# 总结
print("\n" + "=" * 60)
print("审核总结")
print("=" * 60)
print(f"错误: {len(errors)}")
for e in errors:
    print(f"  ❌ {e}")
print(f"警告: {len(warnings)}")
for w in warnings[:10]:
    print(f"  ⚠️  {w}")
if len(warnings) > 10:
    print(f"  ... 还有{len(warnings)-10}条警告")
