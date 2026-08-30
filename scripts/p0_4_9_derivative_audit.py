# -*- coding: utf-8 -*-
"""P0-4.9: DERIVABLE_FEATURE 确定性定义审计

目标：
对 support_ratio 和 wu_ji_pressure 做确定性定义审计

审计问题：
1. 数学/计算定义是否唯一？
2. 输入来自哪个 Canonical State？
3. 是否存在人为权重？
4. 是否存在人为阈值？
5. 不同命例是否产生稳定、可重复结果？

判断标准：
- 任一问题无法给出无歧义答案 → 永久保持非生产状态
"""
import json
import sys
from pathlib import Path
from typing import List, Dict, Optional


# 审计样本
AUDIT_SAMPLES = [
    {
        "id": "support_ratio",
        "name": "support_ratio",
        "source_text": "一行得二三人之气，则党众而专，须从其势。",
        "classic": "滴天髓",
        "proposed_definition": "support_count / total_count",
        "audit_questions": [
            {
                "question": "数学/计算定义是否唯一？",
                "answer": "不确定",
                "evidence": "原典未明确定义'二三人'的计算方式。是支持数/总数？还是支持数≥2？",
                "issue": "『二三人』可能是约数（多数）而非确数（≥2）",
            },
            {
                "question": "输入来自哪个 Canonical State？",
                "answer": "待定",
                "evidence": "需要 support_count 和 total_count，但这两个 Feature 本身需要定义",
                "issue": "support_count 可能不准确",
            },
            {
                "question": "是否存在人为权重？",
                "answer": "是",
                "evidence": "如果写成 support_count / total_count，权重为 1:1，这是人为假设",
                "issue": "权重需要原典明确授权",
            },
            {
                "question": "是否存在人为阈值？",
                "answer": "是",
                "evidence": "如果判断'得二三人之气'需要 ratio >= 0.5 或 >= 2/3，这是人为阈值",
                "issue": "阈值需要原典明确授权",
            },
            {
                "question": "不同命例是否产生稳定、可重复结果？",
                "answer": "无法验证",
                "evidence": "定义不明确，无法验证可重复性",
                "issue": "需要先明确定义才能验证",
            },
        ],
    },
    {
        "id": "wu_ji_pressure",
        "name": "wu_ji_pressure",
        "source_text": "戊己愁逢甲乙，干头须要庚辛。",
        "classic": "渊海子平",
        "proposed_definition": "jia_yi_transparent AND wu_wuji_wang",
        "audit_questions": [
            {
                "question": "数学/计算定义是否唯一？",
                "answer": "不确定",
                "evidence": "原典未明确定义'愁逢'的计算方式。是甲乙透干？还是甲乙旺相？",
                "issue": "『愁逢』语义不明确",
            },
            {
                "question": "输入来自哪个 Canonical State？",
                "answer": "待定",
                "evidence": "需要 jia_yi_transparent 和 wu_wuji_wang，但这两个 Feature 需要验证",
                "issue": "输入 Feature 需要明确定义",
            },
            {
                "question": "是否存在人为权重？",
                "answer": "否",
                "evidence": "当前是 AND 逻辑，无权重",
                "issue": "无权重问题",
            },
            {
                "question": "是否存在人为阈值？",
                "answer": "是",
                "evidence": "如果判断'愁逢'需要 jia_yi_transparent=True，这是人为阈值",
                "issue": "阈值需要原典明确授权",
            },
            {
                "question": "不同命例是否产生稳定、可重复结果？",
                "answer": "无法验证",
                "evidence": "定义不明确，无法验证可重复性",
                "issue": "需要先明确定义才能验证",
            },
        ],
    },
]


def audit_sample(sample: dict) -> dict:
    """审计单条样本"""
    results = []
    all_pass = True

    for q in sample["audit_questions"]:
        is_pass = q["answer"] == "否" or "明确" in q["answer"]
        if not is_pass:
            all_pass = False

        results.append({
            "question": q["question"],
            "answer": q["answer"],
            "evidence": q["evidence"],
            "issue": q["issue"],
            "pass": is_pass,
        })

    # 最终判断
    if all_pass:
        final_verdict = "DEFINABLE"  # 可以给出确定性定义
    else:
        final_verdict = "NOT_DEFINABLE"  # 无法给出确定性定义

    return {
        "id": sample["id"],
        "name": sample["name"],
        "source_text": sample["source_text"],
        "classic": sample["classic"],
        "proposed_definition": sample["proposed_definition"],
        "audit_results": results,
        "final_verdict": final_verdict,
        "recommendation": "永久保持非生产状态" if final_verdict == "NOT_DEFINABLE" else "可以继续定义",
    }


def main():
    print("=== P0-4.9: DERIVABLE_FEATURE 确定性定义审计 ===\n")

    results = []

    for sample in AUDIT_SAMPLES:
        print(f"审计: {sample['id']} - {sample['classic']}")
        print(f"  原文: {sample['source_text'][:60]}...")
        print(f"  提议定义: {sample['proposed_definition']}")
        print()

        result = audit_sample(sample)
        results.append(result)

        # 输出审计结果
        print("  审计问题:")
        for r in result["audit_results"]:
            status = "✅" if r["pass"] else "❌"
            print(f"    {status} {r['question']}")
            print(f"       答案: {r['answer']}")
            if r["issue"]:
                print(f"       问题: {r['issue']}")
        print()
        print(f"  最终判定: {result['final_verdict']}")
        print(f"  建议: {result['recommendation']}")
        print()

    # 输出统计
    definable = sum(1 for r in results if r["final_verdict"] == "DEFINABLE")
    not_definable = sum(1 for r in results if r["final_verdict"] == "NOT_DEFINABLE")

    print("=== 审计结果汇总 ===")
    print(f"总样本: {len(results)}")
    print(f"可定义: {definable}")
    print(f"不可定义: {not_definable}")

    # 保存结果
    report = {
        "generated": __import__('datetime').datetime.now().isoformat(),
        "summary": {
            "total_samples": len(results),
            "definable": definable,
            "not_definable": not_definable,
        },
        "results": results,
    }

    with open('data/p0_4_9_derivative_audit_result.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 data/p0_4_9_derivative_audit_result.json")


if __name__ == '__main__':
    main()
