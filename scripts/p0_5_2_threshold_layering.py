# -*- coding: utf-8 -*-
"""P0-5.2: Threshold 来源审计 + 规则分层

目标：
- 扩展 AuthorizationStatus 枚举
- 更新 auth_gate 逻辑
- 隔离 ENGINEERED_THRESHOLD
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from enum import Enum
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))


class AuthorizationStatus(Enum):
    """授权状态枚举（5层）"""
    # 可授权层
    CLASSICAL_EXPLICIT = "CLASSICAL_EXPLICIT"
    CLASSICAL_IMPLICIT = "CLASSICAL_IMPLICIT"

    # 研究层（禁止生产）
    ENGINEERED_THRESHOLD = "ENGINEERED_THRESHOLD"

    # 禁止层
    SEMANTIC_ONLY = "SEMANTIC_ONLY"
    UNRESOLVED = "UNRESOLVED"


class AuthGate:
    """授权门控"""

    @staticmethod
    def check(
        authorization_status: AuthorizationStatus,
        feature_name: str,
        threshold,
    ) -> dict:
        """
        检查授权状态

        返回:
        - passed: bool（是否可以进入生产）
        - status: AuthorizationStatus
        - layer: str（生产层/研究层/禁止层）
        - message: str
        """
        result = {
            "feature": feature_name,
            "threshold": threshold,
            "status": authorization_status.value,
            "passed": False,
            "layer": None,
            "message": "",
        }

        if authorization_status == AuthorizationStatus.CLASSICAL_EXPLICIT:
            result["passed"] = True
            result["layer"] = "生产层"
            result["message"] = "Classical EXPLICIT → 可授权"
        elif authorization_status == AuthorizationStatus.CLASSICAL_IMPLICIT:
            result["passed"] = False
            result["layer"] = "研究层"
            result["message"] = "Classical IMPLICIT → 暂不授权"
        elif authorization_status == AuthorizationStatus.ENGINEERED_THRESHOLD:
            result["passed"] = False
            result["layer"] = "研究层"
            result["message"] = "Engineered Threshold → 禁止生产"
        elif authorization_status in (
            AuthorizationStatus.SEMANTIC_ONLY,
            AuthorizationStatus.UNRESOLVED,
        ):
            result["passed"] = False
            result["layer"] = "禁止层"
            result["message"] = f"{authorization_status.value} → 禁止 Judgment"
        else:
            result["passed"] = False
            result["layer"] = "未知"
            result["message"] = "未知授权状态"

        return result


def run_threshold_audit():
    """运行阈值溯源审计"""
    print("=" * 60)
    print("P0-5.2: Threshold 来源审计 + 规则分层")
    print("=" * 60)

    # 测试用例
    test_cases = [
        {
            "feature": "de_ling",
            "threshold": True,
            "status": AuthorizationStatus.CLASSICAL_EXPLICIT,
            "source": "滴天髓·得令者旺",
        },
        {
            "feature": "de_di",
            "threshold": 2,
            "status": AuthorizationStatus.ENGINEERED_THRESHOLD,
            "source": "工程定义（无原典授权）",
        },
        {
            "feature": "de_shi",
            "threshold": 2,
            "status": AuthorizationStatus.ENGINEERED_THRESHOLD,
            "source": "工程定义（无原典授权）",
        },
        {
            "feature": "support_ratio",
            "threshold": None,
            "status": AuthorizationStatus.SEMANTIC_ONLY,
            "source": "经典语义（不能硬算）",
        },
        {
            "feature": "wu_ji_pressure",
            "threshold": None,
            "status": AuthorizationStatus.UNRESOLVED,
            "source": "未确定",
        },
    ]

    results = []
    for case in test_cases:
        result = AuthGate.check(case["status"], case["feature"], case["threshold"])
        result["source"] = case["source"]
        results.append(result)

        status_icon = "✅" if result["passed"] else "🔴"
        print(f"\n{status_icon} {case['feature']} >= {case['threshold']}")
        print(f"   状态: {result['status']}")
        print(f"   层级: {result['layer']}")
        print(f"   来源: {case['source']}")
        print(f"   结果: {result['message']}")

    # 汇总
    print("\n" + "=" * 60)
    print("阈值溯源审计汇总")
    print("=" * 60)

    passed = sum(1 for r in results if r["passed"])
    total = len(results)

    print(f"总样本: {total}")
    print(f"可授权: {passed}")
    print(f"不可授权: {total - passed}")

    # 保存
    output_path = Path(__file__).parent.parent / "data" / "p0_5_2_threshold_audit.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({
            "audit_date": datetime.now().isoformat(),
            "total": total,
            "passed": passed,
            "results": results,
        }, f, ensure_ascii=False, indent=2)

    print(f"\n结果已保存到 {output_path}")

    return results


if __name__ == "__main__":
    run_threshold_audit()
