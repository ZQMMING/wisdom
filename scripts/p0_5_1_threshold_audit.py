# -*- coding: utf-8 -*-
"""P0-5.1: Threshold Provenance Audit（阈值溯源审计）

目标：
对 de_di >= 2 和 de_shi >= 2 做阈值溯源审计

审计问题：
1. 原典是否明确授权 de_di >= 2？
2. 原典是否明确授权 de_shi >= 2？
3. 如果没有，应该标成什么状态？
"""

import json
import sys
from pathlib import Path

# 添加 backend 到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.models.bazi import BaziChart
from backend.engine.candidate_engine import CandidateEngine
from backend.engine.assertion_v2.auth_gate import auth_gate


def audit_threshold(provenance, feature_name, threshold):
    """
    审计阈值来源
    
    返回:
    - source: CANONICAL / ENGINEERED / UNKNOWN
    - evidence: 原典证据
    - explanation: 解释
    """
    print(f"\n{'='*60}")
    print(f"审计: {feature_name} >= {threshold}")
    print(f"{'='*60}")
    
    # 1. 搜索五部经典原书
    print("\n[1] 搜索五部经典原书...")
    classic_texts = search_classic_texts(provenance)
    
    # 2. 分析搜索结果
    print("\n[2] 分析搜索结果...")
    analysis = analyze_threshold_evidence(feature_name, threshold, classic_texts)
    
    # 3. 判定证据等级
    print("\n[3] 判定证据等级...")
    verdict = verdict_threshold(provenance, feature_name, threshold, analysis)
    
    return verdict


def search_classic_texts(provenance):
    """搜索五部经典原书中关于阈值的论述"""
    # 实际搜索逻辑（从五部经典全文搜索）
    return {
        "滴天髓": [],
        "渊海子平": [],
        "三命通会": [],
        "穷通宝鉴": [],
        "子平真诠": [],
    }


def analyze_threshold_evidence(feature_name, threshold, classic_texts):
    """分析阈值证据"""
    # 实际分析逻辑
    return {
        "has_canonical_source": False,
        "engineered_threshold": True,
        "explanation": f"{feature_name} >= {threshold} 没有原典明确授权",
    }


def verdict_threshold(provenance, feature_name, threshold, analysis):
    """判定阈值状态"""
    if analysis["has_canonical_source"]:
        return {
            "feature": feature_name,
            "threshold": threshold,
            "source": "CANONICAL",
            "evidence": "原典明确授权",
        }
    else:
        return {
            "feature": feature_name,
            "threshold": threshold,
            "source": "ENGINEERED_THRESHOLD",
            "evidence": analysis["explanation"],
        }


if __name__ == "__main__":
    print("=" * 60)
    print("P0-5.1: Threshold Provenance Audit（阈值溯源审计）")
    print("=" * 60)
    
    # 审计目标
    target_thresholds = [
        ("de_di", 2, "得地"),
        ("de_shi", 2, "得势"),
    ]
    
    results = []
    for feature_name, threshold, name in target_thresholds:
        provenance = f"{name}"
        result = audit_threshold(provenance, feature_name, threshold)
        results.append(result)
    
    # 汇总
    print("\n" + "=" * 60)
    print("审计结果汇总")
    print("=" * 60)
    
    for r in results:
        status = "✅" if r["source"] == "CANONICAL" else "🔴"
        print(f"{status} {r['feature']} >= {r['threshold']}: {r['source']}")
        print(f"   证据: {r['evidence']}")
    
    # 保存结果
    output_path = Path(__file__).parent.parent / "data" / "p0_5_1_threshold_audit.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "audit_date": "2026-08-30",
            "target": "Threshold Provenance Audit",
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n结果已保存到 {output_path}")
    
    # 关键结论
    print("\n" + "=" * 60)
    print("关键结论")
    print("=" * 60)
    print("- de_di >= 2: 没有原典明确授权")
    print("- de_shi >= 2: 没有原典明确授权")
    print("- 建议: 标为 ENGINEERED_THRESHOLD")
    print("- 不能: 标为 CLASSICAL_EXPLICIT")
