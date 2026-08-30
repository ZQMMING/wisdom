# -*- coding: utf-8 -*-
"""P0-4.4: Semantic Type → Executable Rule 映射验证

目标：
- 选择 20-30 条真实五经原典
- 覆盖所有语义类型
- 验证映射边界

验证框架：
1. 语义类型 → 结构化表达
2. 是否可执行？
3. 是否需要 Condition？
4. 是否需要 Composite？
5. 最终状态：EXECUTABLE / SEMANTIC_ONLY / UNRESOLVED
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional


# 语义类型定义
SEMANTIC_TYPES = {
    "FACT": "① 事实/状态 - 描述客观状态",
    "CONDITION": "② 条件 - 明确条件关系",
    "SUFFICIENT": "③ 充分条件 - 满足即成立",
    "NECESSARY": "④ 必要条件 - 必须满足",
    "PREFERENCE": "⑤ 倾向/宜忌 - 推荐或忌讳",
    "BLOCKING": "⑥ 制约/阻断 - 阻止或限制",
    "INFERENCE": "⑦ 推论 - 从前提推出的结论",
    "COMPOUND": "⑧ 复合论断 - 多个条件组合",
    "UNKNOWN": "⑨ 未确定 - 无法判断语义",
}

# 最终状态定义
FINAL_STATES = {
    "EXECUTABLE": "可执行 - 可以直接映射到引擎逻辑",
    "SEMANTIC_ONLY": "仅语义层 - 保留为 Evidence/Semantic，不产生 Judgment",
    "UNRESOLVED": "未确定 - 保持 UNRESOLVED 状态",
}


# 样本数据：20-30 条真实五经原典
SAMPLES = [
    # ===== FACT（事实/状态）=====
    {
        "id": "fact_001",
        "text": "壬水通河，能泄金气，刚中之德，周流不息。",
        "classic": "滴天髓",
        "semantic_type": "FACT",
        "description": "描述壬水的物理特性",
    },
    {
        "id": "fact_002",
        "text": "甲木参天，脱胎要火。春不容金，秋不容土。",
        "classic": "滴天髓",
        "semantic_type": "FACT",
        "description": "描述甲木在四季的特性",
    },
    {
        "id": "fact_003",
        "text": "丙火猛烈，欺霜侮雪。能煅庚金，逢辛反怯。",
        "classic": "滴天髓",
        "semantic_type": "FACT",
        "description": "描述丙火的物理特性",
    },
    {
        "id": "fact_004",
        "text": "戊土固重，既中且正。静翕动辟，万物司命。",
        "classic": "滴天髓",
        "semantic_type": "FACT",
        "description": "描述戊土的特性",
    },
    {
        "id": "fact_005",
        "text": "己土卑湿，中正蓄藏。不愁木盛，不畏水狂。",
        "classic": "滴天髓",
        "semantic_type": "FACT",
        "description": "描述己土的特性",
    },

    # ===== NECESSARY（必要条件）=====
    {
        "id": "necessary_001",
        "text": "生克制化，须制中有生，生中有制。",
        "classic": "滴天髓",
        "semantic_type": "NECESSARY",
        "description": "强调制化必须同时存在",
    },
    {
        "id": "necessary_002",
        "text": "一行得二三人之气，则党众而专，须从其势。",
        "classic": "滴天髓",
        "semantic_type": "NECESSARY",
        "description": "强调必须顺其气势",
    },
    {
        "id": "necessary_003",
        "text": "太过者宜损之，不及者宜益之。",
        "classic": "滴天髓",
        "semantic_type": "NECESSARY",
        "description": "强调必须根据旺衰调整",
    },
    {
        "id": "necessary_004",
        "text": "大凡旺之极者，宜泄而不宜克，宜顺其气势。",
        "classic": "滴天髓",
        "semantic_type": "NECESSARY",
        "description": "强调旺极时必须顺其势",
    },
    {
        "id": "necessary_005",
        "text": "昆仑之水，可顺而不可逆也。",
        "classic": "滴天髓",
        "semantic_type": "NECESSARY",
        "description": "强调水旺时必须顺其势",
    },

    # ===== BLOCKING（制约/阻断）=====
    {
        "id": "blocking_001",
        "text": "太岁乃年中天子，故不可犯，犯之则凶。",
        "classic": "渊海子平",
        "semantic_type": "BLOCKING",
        "description": "明确禁止犯太岁",
    },
    {
        "id": "blocking_002",
        "text": "辛金软弱，温润而清，畏土之埋，乐水之盈。",
        "classic": "滴天髓",
        "semantic_type": "BLOCKING",
        "description": "强调辛金畏惧土埋",
    },
    {
        "id": "blocking_003",
        "text": "癸水至弱，达于天津，得龙而运，功化斯神。",
        "classic": "滴天髓",
        "semantic_type": "BLOCKING",
        "description": "强调癸水需龙（辰）方能发挥作用",
    },
    {
        "id": "blocking_004",
        "text": "戊己愁逢甲乙，干头须要庚辛。",
        "classic": "渊海子平",
        "semantic_type": "BLOCKING",
        "description": "强调戊己土遇甲乙木时需要庚辛解救",
    },
    {
        "id": "blocking_005",
        "text": "火炽乘龙，水荡骑虎。",
        "classic": "滴天髓",
        "semantic_type": "BLOCKING",
        "description": "强调火旺需辰（龙）调候，水旺需寅（虎）疏导",
    },

    # ===== INFERENCE（推论）=====
    {
        "id": "inference_001",
        "text": "天道欲其流通，五行不可相战；地道欲其承载，根深方可叶茂。",
        "classic": "滴天髓",
        "semantic_type": "INFERENCE",
        "description": "从天地之道推论出的命理原则",
    },
    {
        "id": "inference_002",
        "text": "既有合化，便有化局。化真者贵，化假者贱。",
        "classic": "滴天髓",
        "semantic_type": "INFERENCE",
        "description": "从合化理论推论出的贵贱判断",
    },
    {
        "id": "inference_003",
        "text": "月令提纲，譬之宅也；人元用事，譬之定向也。",
        "classic": "滴天髓",
        "semantic_type": "INFERENCE",
        "description": "用比喻推论月令的重要性",
    },
    {
        "id": "inference_004",
        "text": "用神专求月令，以日干配月令地支，而生克不同，格局分焉。",
        "classic": "滴天髓",
        "semantic_type": "INFERENCE",
        "description": "从月令理论推论出取用神的方法",
    },
    {
        "id": "inference_005",
        "text": "何以为喜？命局顺遂而无悖逆也。何以为忌？命局乖戾而多克战也。",
        "classic": "滴天髓",
        "semantic_type": "INFERENCE",
        "description": "从全局配合推论出喜忌判断",
    },

    # ===== COMPOUND（复合论断）=====
    {
        "id": "compound_001",
        "text": "丁火柔中，内性昭融，抱乙而孝，合壬而忠。",
        "classic": "滴天髓",
        "semantic_type": "COMPOUND",
        "description": "描述丁火的多重特性组合",
    },
    {
        "id": "compound_002",
        "text": "庚金带杀，刚健为最，得水而清，得火而锐。",
        "classic": "滴天髓",
        "semantic_type": "COMPOUND",
        "description": "描述庚金在多种情况下的表现",
    },
    {
        "id": "compound_003",
        "text": "癸水至弱，达于天津，得龙而运，功化斯神。",
        "classic": "滴天髓",
        "semantic_type": "COMPOUND",
        "description": "描述癸水的多重条件和效果",
    },
    {
        "id": "compound_004",
        "text": "甲木参天，脱胎要火。春不容金，秋不容土。",
        "classic": "滴天髓",
        "semantic_type": "COMPOUND",
        "description": "描述甲木在四季的不同表现",
    },
    {
        "id": "compound_005",
        "text": "乙木根拨叶嫩，傲雪凌霜，幼木宜少水培。",
        "classic": "滴天髓",
        "semantic_type": "COMPOUND",
        "description": "描述乙木的特性和养护条件",
    },

    # ===== PREFERENCE（倾向/宜忌）=====
    {
        "id": "preference_001",
        "text": "正月甲木，初春尚有余寒，得丙癸透，富贵双全。",
        "classic": "穷通宝鉴",
        "semantic_type": "PREFERENCE",
        "description": "推荐丙癸透干",
    },
    {
        "id": "preference_002",
        "text": "五月甲木，木性虚焦。五月先癸后丁，庚金次之。",
        "classic": "穷通宝鉴",
        "semantic_type": "PREFERENCE",
        "description": "推荐用神优先级",
    },
    {
        "id": "preference_003",
        "text": "六月甲木，三伏生寒，丁火退气。先丁后庚，无癸亦可。",
        "classic": "穷通宝鉴",
        "semantic_type": "PREFERENCE",
        "description": "推荐用神配置",
    },
    {
        "id": "preference_004",
        "text": "七月甲木，木性枯藁，金土乘旺，先丁后庚，丁庚两全。",
        "classic": "穷通宝鉴",
        "semantic_type": "PREFERENCE",
        "description": "推荐用神配置",
    },
    {
        "id": "preference_005",
        "text": "八月甲木，木囚金旺。丁火为先，次用丙火，庚金再次。",
        "classic": "穷通宝鉴",
        "semantic_type": "PREFERENCE",
        "description": "推荐用神优先级",
    },

    # ===== UNKNOWN（未确定）=====
    {
        "id": "unknown_001",
        "text": "欲识三元万法宗，先观帝载与神功。",
        "classic": "滴天髓",
        "semantic_type": "UNKNOWN",
        "description": "方法论总纲，语义抽象",
    },
    {
        "id": "unknown_002",
        "text": "坤元合德机缄通，五气偏全定吉凶。",
        "classic": "滴天髓",
        "semantic_type": "UNKNOWN",
        "description": "玄学表述，难以映射",
    },
    {
        "id": "unknown_003",
        "text": "能知衰旺之真机，其于三命之奥，思过半矣。",
        "classic": "滴天髓",
        "semantic_type": "UNKNOWN",
        "description": "方法论陈述，非操作性规则",
    },
]


def classify_sample(sample: dict) -> dict:
    """对单条样本进行分类验证"""
    semantic_type = sample["semantic_type"]

    # 根据语义类型判断可执行性
    exec_map = {
        "FACT": "SEMANTIC_ONLY",  # 事实描述，不产生 Judgment
        "CONDITION": "EXECUTABLE",  # 明确条件关系
        "SUFFICIENT": "EXECUTABLE",  # 充分条件可执行
        "NECESSARY": "SEMANTIC_ONLY",  # 必要条件需要原典审核
        "PREFERENCE": "SEMANTIC_ONLY",  # 倾向宜忌不能直接当规则
        "BLOCKING": "EXECUTABLE",  # 阻断条件可执行
        "INFERENCE": "SEMANTIC_ONLY",  # 推论需要保留证据等级
        "COMPOUND": "UNRESOLVED",  # 复合论断不能简单等同 AND
        "UNKNOWN": "UNRESOLVED",  # 未确定保持 UNRESOLVED
    }

    final_state = exec_map.get(semantic_type, "UNRESOLVED")

    # 判断是否需要 Condition
    needs_condition = semantic_type in ["CONDITION", "SUFFICIENT", "NECESSARY", "BLOCKING"]

    # 判断是否需要 Composite
    needs_composite = semantic_type == "COMPOUND"

    return {
        **sample,
        "final_state": final_state,
        "final_state_desc": FINAL_STATES[final_state],
        "needs_condition": needs_condition,
        "needs_composite": needs_composite,
    }


def main():
    print("=== P0-4.4: Semantic Type → Executable Rule 映射验证 ===\n")

    results = []
    state_counts = {"EXECUTABLE": 0, "SEMANTIC_ONLY": 0, "UNRESOLVED": 0}
    type_counts = {t: 0 for t in SEMANTIC_TYPES.keys()}

    for sample in SAMPLES:
        result = classify_sample(sample)
        results.append(result)
        state_counts[result["final_state"]] += 1
        type_counts[result["semantic_type"]] += 1

    # 输出统计
    print("=== 语义类型分布 ===")
    for t, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        if count > 0:
            print(f"  {SEMANTIC_TYPES[t]}: {count}")

    print("\n=== 可执行性分布 ===")
    for s, count in sorted(state_counts.items(), key=lambda x: -x[1]):
        print(f"  {s}: {count}")

    # 输出详细结果
    print("\n=== 详细验证 ===")
    for r in results:
        print(f"\n[{r['id']}] {r['classic']}")
        print(f"  原文: {r['text'][:60]}...")
        print(f"  语义类型: {SEMANTIC_TYPES[r['semantic_type']]}")
        print(f"  最终状态: {r['final_state']}")
        if r['needs_condition']:
            print(f"  需要 Condition: ✅")
        if r['needs_composite']:
            print(f"  需要 Composite: ⚠️ HOLD")

    # 输出报告
    report = {
        "generated": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total_samples": len(results),
            "type_distribution": type_counts,
            "state_distribution": state_counts,
        },
        "results": results,
    }

    with open('data/p0_4_4_mapping_verification.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 data/p0_4_4_mapping_verification.json")

    # 关键结论
    print("\n=== 关键结论 ===")
    print(f"总样本: {len(results)} 条")
    print(f"可执行: {state_counts['EXECUTABLE']} 条（{state_counts['EXECUTABLE']/len(results)*100:.1f}%）")
    print(f"仅语义层: {state_counts['SEMANTIC_ONLY']} 条（{state_counts['SEMANTIC_ONLY']/len(results)*100:.1f}%）")
    print(f"未确定: {state_counts['UNRESOLVED']} 条（{state_counts['UNRESOLVED']/len(results)*100:.1f}%）")


if __name__ == '__main__':
    main()
