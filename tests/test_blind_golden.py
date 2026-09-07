# -*- coding: utf-8 -*-
"""盲派命理 Golden Set 执行测试

测试加载机制: LOAD → EXECUTE → COMPARE → GRADE

V2 E5 格式:
  PASS: 实际结果符合预期
  FAIL: 实际结果不符合预期
  ERROR: 执行异常 (崩溃/异常)
  SKIP: 跳过 (缺少必要信息)
"""
import sys
import json
import unittest
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path('D:/shuntian/src')))

from tongshu.engines.blind_bazi_engine import compute_blind_bazi


# ─── 加载配置 ─────────────────────────────────────────────────────────────────

CASES_FILE = Path('D:/shuntian/cases/golden/blind_golden_set.json')
CASES = json.loads(CASES_FILE.read_text(encoding='utf-8'))['cases']

LOAD_COUNT = len(CASES)
EXECUTE_COUNT = 0
ERROR_COUNT = 0
SKIP_COUNT = 0


# ─── 断言辅助 ─────────────────────────────────────────────────────────────────

def assert_no_crash(result) -> bool:
    """检查引擎不崩溃且有基本属性"""
    return (result is not None and
            hasattr(result, 'signals') and
            hasattr(result, 'zuo_gong_methods'))


def check_signal_range(actual_signals, min_count, max_count) -> bool:
    """检查信号数量是否在范围内"""
    count = len(actual_signals)
    return min_count <= count <= max_count


def check_strength_range(actual_signals, min_strength, max_strength) -> bool:
    """检查所有信号的strength是否在范围内"""
    if not actual_signals:
        return False
    strengths = [s.strength for s in actual_signals]
    return all(min_strength <= s <= max_strength for s in strengths)


def check_type_match(actual_signals, must_have_types: List[str]) -> bool:
    """检查预期事件类型是否存在（宽松匹配）"""
    if not must_have_types or not actual_signals:
        return len(actual_signals) > 0
    actual_types = {s.event_type for s in actual_signals}
    return bool(actual_types & set(must_have_types))


# ─── 测试类 ────────────────────────────────────────────────────────────────────

class TestBlindGoldenSet(unittest.TestCase):
    """盲派命理 Golden Set 测试"""

    @classmethod
    def setUpClass(cls):
        """加载golden set"""
        cls.cases = CASES
        cls.load_count = LOAD_COUNT

    def _run_case(self, case: Dict[str, Any]) -> tuple:
        """执行单个案例，返回 (grade, actual_signals, expected)"""
        global EXECUTE_COUNT, ERROR_COUNT

        case_id = case['case_id']
        input_data = case['input']
        expected = case['expected_calculation']

        EXECUTE_COUNT += 1

        try:
            birth = (
                input_data['birth_year'],
                input_data['birth_month'],
                input_data['birth_day'],
                input_data['birth_hour']
            )
            gender = input_data['gender']

            result = compute_blind_bazi(birth, gender)
            actual_signals = result.signals

            # 验证引擎不崩溃
            no_crash = assert_no_crash(result)

            # 验证信号存在
            has_signals = len(actual_signals) > 0

            # 验证信号数量
            min_count = expected.get('min_signal_count', 0)
            max_count = expected.get('max_signal_count', 20)
            count_ok = check_signal_range(actual_signals, min_count, max_count)

            # 验证事件类型
            must_have_types = expected.get('must_have_types', [])
            types_ok = check_type_match(actual_signals, must_have_types)

            # 验证strength范围
            strength_min = expected.get('strength_range', [0.0, 1.0])[0]
            strength_max = expected.get('strength_range', [0.0, 1.0])[1]
            strength_ok = check_strength_range(actual_signals, strength_min, strength_max)

            # 综合判定
            all_pass = no_crash and has_signals and count_ok and types_ok and strength_ok

            if all_pass:
                grade = "PASS"
            else:
                grade = "FAIL"

            return grade, actual_signals, expected

        except Exception as e:
            ERROR_COUNT += 1
            return "ERROR", None, expected

    def test_00_execution_summary(self):
        """执行摘要: 统计LOAD/EXECUTE"""
        self.assertGreaterEqual(LOAD_COUNT, 20, "Golden Set应至少20个案例")


# ─── 动态生成测试方法 ──────────────────────────────────────────────────────────

def _generate_case_tests():
    """为每个case生成测试方法并注册到测试类"""
    for _case in CASES:
        case_id = _case['case_id']
        test_name = f"test_{case_id.lower().replace('-', '_')}"

        def _create_test_method(case, name):
            """工厂函数创建测试方法"""
            def _test_impl(self):
                grade, actual, expected = self._run_case(case)

                # 断言
                self.assertEqual(grade, 'PASS',
                    f"{case['case_id']}: {case.get('description', '')}\n"
                    f"Grade: {grade}\n"
                    f"Expected min signals: {expected.get('min_signal_count', 0)}\n"
                    f"Expected max signals: {expected.get('max_signal_count', 20)}\n"
                    f"Must have types: {expected.get('must_have_types', [])}\n"
                    f"Actual signal count: {len(actual) if actual else 0}\n"
                    f"Actual signals: {[s.signal_id for s in (actual or [])]}")

            _test_impl.__name__ = name
            _test_impl.__doc__ = f"Test case {case['case_id']}"
            return _test_impl

        test_func = _create_test_method(_case, test_name)
        setattr(TestBlindGoldenSet, test_name, test_func)


_generate_case_tests()


# ─── 主入口 ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    unittest.main(verbosity=2)
