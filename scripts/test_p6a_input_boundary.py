"""P6-A Input Boundary Tests.

测试birth_year输入边界:
- 最早支持年份 - 1 (0年, 应失败)
- 最早支持年份 (1年, 应成功)
- 最早支持年份 + 1 (2年, 应成功)
- 1900年 (原边界, 应成功)
- 现代案例 (1983年, 应成功)
- 未来日期 (2100年, 应成功; 2101年, 应失败)
- 非法日期 (0年, 应失败)
"""
from __future__ import annotations
import sys
sys.path.insert(0, "src")

from fastapi.testclient import TestClient
from tongshu.api.app import create_app

app = create_app()
client = TestClient(app)


def test_boundary(year: int, should_succeed: bool) -> tuple[bool, str]:
    """测试单个边界年份."""
    try:
        resp = client.post("/admin/cases", json={
            "birth_year": year,
            "birth_month": 6,
            "birth_day": 15,
            "birth_hour": 12,
            "gender": "male",
        })
        if should_succeed:
            if resp.status_code == 200:
                data = resp.json()
                return True, f"OK (case_id={data.get('case_id', '?')}, evidence={data.get('evidence_count', '?')})"
            else:
                return False, f"FAIL (expected success, got HTTP {resp.status_code}: {resp.text[:100]})"
        else:
            if resp.status_code == 400:
                return True, f"OK (correctly rejected with HTTP 400)"
            else:
                return False, f"FAIL (expected rejection, got HTTP {resp.status_code})"
    except Exception as e:
        return False, f"EXCEPTION: {str(e)[:100]}"


def main():
    print("=" * 60)
    print("P6-A Input Boundary Tests")
    print("=" * 60)

    test_cases = [
        (0, False, "最早支持年份-1 (0年, 应拒绝)"),
        (1, True, "最早支持年份 (1年, 应成功)"),
        (2, True, "最早支持年份+1 (2年, 应成功)"),
        (155, True, "Golden Dataset最早 (155年, 应成功)"),
        (701, True, "唐代 (701年, 应成功)"),
        (1037, True, "宋代 (1037年, 应成功)"),
        (1724, True, "清代 (1724年, 应成功)"),
        (1900, True, "原边界 (1900年, 应成功)"),
        (1983, True, "现代案例 (1983年, 应成功)"),
        (2026, True, "当前年份 (2026年, 应成功)"),
        (2100, True, "上限 (2100年, 应成功)"),
        (2101, False, "上限+1 (2101年, 应拒绝)"),
    ]

    passed = 0
    failed = 0

    for year, should_succeed, description in test_cases:
        result, message = test_boundary(year, should_succeed)
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"\n  [{status}] {description}")
        print(f"         year={year}, {message}")
        if result:
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"结果: {passed} passed, {failed} failed, {len(test_cases)} total")
    if failed == 0:
        print("✅ 所有边界测试通过")
    else:
        print("❌ 存在失败的边界测试")
    print("=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
