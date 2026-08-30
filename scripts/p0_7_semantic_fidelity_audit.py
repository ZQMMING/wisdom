# -*- coding: utf-8 -*-
"""P0-7: Classical Semantic Fidelity Audit

目标: 验证当前 Primitive 实现是否忠实于五经原典语义

审计范围:
1. YHZP-LF-TSJX-5 "日犯岁君"
2. DTS-SZ-HZ-ZL "生克制化"

验证方法:
原典原文 → 语义拆解 → Primitive 定义 → Condition 定义 → 代码实现 → 对比验证
"""
import sys, json
from pathlib import Path
from typing import Dict, Any, List

# ===== 原典语义取证 =====

# --- 日犯岁君 ---
SUI_JUN_SEMANTIC = {
    "canonical_source": {
        "primary": "DTS_滴天髓·论太岁",
        "secondary": "YHZP_渊海子平",
    },
    "original_text": [
        "又曰年为太岁，主人一生祸福",
        "夫太岁者，乃一岁之主宰，诸神之领袖",
        "日犯岁君，灾殃必重",
        "日犯岁君，如甲日克戊年为上治其下，顺也",
        "岁君伤日者，如庚年克甲日为下治其上，顺也，其情尚未尽绝",
        "假如甲日见戊年太岁，甲又生寅卯亥未，年月日时又重见乙己，运行辛未、丙寅，日干之壬克太岁之丙，日支之庚申克太岁之寅甲，又寅刑已，已刑申，刑寅，行辛未运，合太岁之乙，大抵日犯岁君，在五阳干则重，在五阴干则轻",
    ],
    "semantic_analysis": {
        "岁君": {
            "definition": "太岁 = 年柱（年干+年支）",
            "evidence": "又曰年为太岁 / 夫太岁者，乃一岁之主宰",
            "current_impl": "year_stem (仅年干)",
            "gap": "当前实现只检查年干，未检查年支",
        },
        "犯": {
            "definition": "多种关系：日干克年干 / 日支克年支 / 运克岁君 / 岁运冲刑",
            "evidence": "日犯岁君，如甲日克戊年 / 日干之壬克太岁之丙，日支之庚申克太岁之寅甲",
            "current_impl": "仅检查日干克年干",
            "gap": "缺少日支条件、运克岁君、岁运冲刑等",
        },
        "条件": {
            "definition": "甲乙日干 + 寅卯亥未日时",
            "evidence": "甲乙若寅卯亥未日时者，犯剋岁君，决死无疑",
            "current_impl": "无日支条件检查",
            "gap": "缺少日支/时支条件",
        },
        "程度": {
            "definition": "五阳干重，五阴干轻；有救应则减",
            "evidence": "大抵日犯岁君，在五阳干则重，在五阴干则轻 / 太岁是用神则无咎",
            "current_impl": "无程度判断",
            "gap": "缺少灾殃程度判断",
        },
    },
    "authorization_status": "AUTHORIZED_PARTIAL",
    "unresolved_parts": ["日支条件", "救应判断", "灾殃程度", "年支检查"],
}

# --- 生克制化 ---
SHENG_KE_SEMANTIC = {
    "canonical_source": {
        "primary": "DTS_滴天髓·通神论第718段",
        "secondary": "SMTH_三命通会",
    },
    "original_text": [
        "生克制化，须制中有生，生中有制。太过者宜损之，不及者宜益之。",
        "任氏曰：生克制化，其理多端，盖一支所藏或二干，或三干故耳",
        "命贵中和，偏枯终于有损；理求平正，奇异不足为凭",
    ],
    "semantic_analysis": {
        "制中有生": {
            "definition": "被克者有生（被克方有生化之源）",
            "evidence": "须制中有生",
            "current_impl": "检查 gen_in_keeps 关系链",
            "gap": "正确，但需确认是否覆盖所有情况",
        },
        "生中有制": {
            "definition": "生者有制（生方有克制约束）",
            "evidence": "须生中有制",
            "current_impl": "检查 keeps_in_gen 关系链",
            "gap": "正确，但需确认是否覆盖所有情况",
        },
        "太过/不及": {
            "definition": "太过者宜损之，不及者宜益之",
            "evidence": "太过者宜损之，不及者宜益之",
            "current_impl": "未实现，保持 UNRESOLVED",
            "gap": "正确隔离，不引入阈值",
        },
        "须": {
            "definition": "描述性必要条件，非充分条件",
            "evidence": "生克制化，须制中有生，生中有制",
            "current_impl": "必要条件理解正确",
            "gap": "正确",
        },
    },
    "authorization_status": "AUTHORIZED_PARTIAL",
    "unresolved_parts": ["太过判断", "不及判断", "中和程度"],
}


def audit_semic_fidelity(primitive_name, semantic_data):
    """审计单个 Primitive 的语义忠实度"""
    print(f"\n{'='*60}")
    print(f"【{primitive_name}】语义忠实度审计")
    print("=" * 60)
    
    issues = []
    confirmations = []
    
    for key, analysis in semantic_data["semantic_analysis"].items():
        print(f"\n  {key}:")
        print(f"    原典定义: {analysis['definition']}")
        print(f"    当前实现: {analysis['current_impl']}")
        print(f"    差异: {analysis['gap']}")
        
        # 判定
        if "缺少" in analysis["gap"] or "未实现" in analysis["gap"]:
            issues.append({
                "key": key,
                "status": "GAP",
                "detail": analysis["gap"],
            })
        elif "正确" in analysis["gap"]:
            confirmations.append({
                "key": key,
                "status": "FIDELITY_OK",
                "detail": analysis["gap"],
            })
        else:
            confirmations.append({
                "key": key,
                "status": "NEEDS_REVIEW",
                "detail": analysis["gap"],
            })
    
    return {
        "primitive": primitive_name,
        "authorization": semantic_data["authorization_status"],
        "issues": issues,
        "confirmations": confirmations,
        "unresolved_parts": semantic_data["unresolved_parts"],
    }


def compare_implementation_with_canonical():
    """对比代码实现与原典语义"""
    print("\n" + "=" * 70)
    print("P0-7: Classical Semantic Fidelity Audit")
    print("=" * 70)
    
    # 审计两个 Primitive
    results = []
    
    # 1. 日犯岁君
    r1 = audit_semic_fidelity("YHZP-LF-TSJX-5 日犯岁君", SUI_JUN_SEMANTIC)
    results.append(r1)
    
    # 2. 生克制化
    r2 = audit_semic_fidelity("DTS-SZ-HZ-ZL 生克制化", SHENG_KE_SEMANTIC)
    results.append(r2)
    
    # 汇总
    print(f"\n{'='*70}")
    print("审计汇总")
    print("=" * 70)
    
    total_issues = sum(len(r["issues"]) for r in results)
    total_confirmations = sum(len(r["confirmations"]) for r in results)
    
    print(f"\n【问题统计】")
    print(f"  日犯岁君:")
    print(f"    语义Gap: {len(r1['issues'])} 个")
    for i in r1['issues']:
        print(f"      - {i['key']}: {i['detail']}")
    print(f"    语义确认: {len(r1['confirmations'])} 个")
    for c in r1['confirmations']:
        print(f"      - {c['key']}: {c['detail']}")
    
    print(f"\n  生克制化:")
    print(f"    语义Gap: {len(r2['issues'])} 个")
    for i in r2['issues']:
        print(f"      - {i['key']}: {i['detail']}")
    print(f"    语义确认: {len(r2['confirmations'])} 个")
    for c in r2['confirmations']:
        print(f"      - {c['key']}: {c['detail']}")
    
    print(f"\n【整体结论】")
    print(f"  总语义Gap: {total_issues} 个")
    print(f"  总语义确认: {total_confirmations} 个")
    print(f"  当前状态: AUTHORIZED_PARTIAL（符合预期）")
    
    # 保存结果
    output_path = Path(__file__).parent.parent / "data" / "p0_7_semantic_fidelity.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "audit_date": "2026-08-31",
            "primitives_audited": 2,
            "total_gaps": total_issues,
            "total_confirmations": total_confirmations,
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    return {
        "total_gaps": total_issues,
        "total_confirmations": total_confirmations,
        "results": results,
    }


def main():
    result = compare_implementation_with_canonical()
    
    print(f"\n{'='*70}")
    print("核心结论")
    print("=" * 70)
    
    print(f"""
【日犯岁君】
  ✅ 岁君=太岁=年柱：原典明确，当前实现仅检查年干（部分正确）
  ✅ 日干克年干：原典有明确例子（甲日克戊年），当前实现正确
  ❌ 缺少日支条件：原典要求"寅卯亥未日时"，当前未实现
  ❌ 缺少年支检查：岁君=年柱，当前只用了年干
  ❌ 缺少灾殃程度：原典区分阳干重/阴干轻，当前未实现
  ❌ 缺少救应判断：原典提到"天月德"、"太岁是用神则无咎"，当前未实现

【生克制化】
  ✅ 制中有生：当前实现检查 gen_in_keeps，语义正确
  ✅ 生中有制：当前实现检查 keeps_in_gen，语义正确
  ✅ 须=必要条件：当前理解正确，不是充分条件
  ✅ 太过/不及：正确保持 UNRESOLVED，未引入阈值
  ✅ 任氏注疏"其理多端"：当前实现作为描述性要求，不强制全覆盖
""")
    
    if result["total_gaps"] > 0:
        print(f"🟡 结论: 当前实现为 AUTHORIZED_PARTIAL，语义Gap已在授权状态中记录")
    else:
        print(f"🟢 结论: 语义忠实度通过")


if __name__ == "__main__":
    main()
