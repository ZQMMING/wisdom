# -*- coding: utf-8 -*-
"""盲派命理 Golden Set v2 执行测试

测试加载机制: LOAD → EXECUTE → COMPARE_CORE_FIELDS → GRADE

V2 E5 格式:
  PASS: 实际结果符合预期 (核心字段 + 信号断言)
  FAIL: 实际结果不符合预期
  ERROR: 执行异常 (崩溃/异常)
  SKIP: 跳过 (缺少必要信息)

升级内容: 新增盲派核心字段断言
- zuo_gong_type (做功类型)
- main_branches (主位支)
- guest_branches (宾位支)
- ti_branches (体支)
- yong_branches (用支)
- zuo_gong_methods (做功方式列表)
"""
import sys
import json
import unittest
from pathlib import Path
from typing import List, Dict, Any, Optional

sys.path.insert(0, str(Path('D:/shuntian/src')))

from tongshu.engines.blind_bazi_engine import compute_blind_bazi


# ─── 加载配置 ─────────────────────────────────────────────────────────────────

CASES_FILE = Path('D:/shuntian/cases/golden/blind_golden_set_v2.json')
CASES = json.loads(CASES_FILE.read_text(encoding='utf-8'))['cases']

LOAD_COUNT = len(CASES)
EXECUTE_COUNT = 0
ERROR_COUNT = 0
SKIP_COUNT = 0
CORE_FIELDS_ASSERTED = 0


# ─── 断言辅助 ─────────────────────────────────────────────────────────────────

def assert_no_crash(result) -> bool:
    """检查引擎不崩溃且有基本属性"""
    return (result is not None and
            hasattr(result, 'signals') and
            hasattr(result, 'zuo_gong_methods') and
            hasattr(result, 'zuo_gong_type') and
            hasattr(result, 'main_branches') and
            hasattr(result, 'guest_branches') and
            hasattr(result, 'ti_branches') and
            hasattr(result, 'yong_branches'))


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


def check_core_fields(result, expected: Dict) -> tuple:
    """检查核心字段，返回 (pass, details)"""
    global CORE_FIELDS_ASSERTED
    
    core = expected.get('core_fields', {})
    if not core:
        return True, "No core field assertions"
    
    CORE_FIELDS_ASSERTED += 1
    details = []
    all_pass = True
    
    # 检查做功类型存在
    if core.get('has_zuo_gong'):
        has_zg = bool(result.zuo_gong_type)
        details.append(f"zuo_gong_type={'✓' if has_zg else '✗'}")
        all_pass &= has_zg
    
    # 检查主位支
    if core.get('has_main_branches'):
        has_mb = bool(result.main_branches)
        details.append(f"main_branches={'✓' if has_mb else '✗'}")
        all_pass &= has_mb
    
    # 检查宾位支
    if core.get('has_guest_branches'):
        has_gb = bool(result.guest_branches)
        details.append(f"guest_branches={'✓' if has_gb else '✗'}")
        all_pass &= has_gb
    
    # 检查体用
    if core.get('has_ti_yong'):
        has_ty = bool(result.ti_branches) and bool(result.yong_branches)
        details.append(f"ti_yong={'✓' if has_ty else '✗'}")
        all_pass &= has_ty
    
    # 检查做功方法数量
    min_methods = core.get('zuo_gong_methods_min', 0)
    actual_methods = len(result.zuo_gong_methods) if result.zuo_gong_methods else 0
    methods_ok = actual_methods >= min_methods
    details.append(f"zuo_gong_methods={actual_methods}>={min_methods} {'✓' if methods_ok else '✗'}")
    all_pass &= methods_ok
    
    return all_pass, ", ".join(details)


# ─── 测试类 ────────────────────────────────────────────────────────────────────

class TestBlindGoldenSet(unittest.TestCase):
    """盲派命理 Golden Set v2 测试"""

    @classmethod
    def setUpClass(cls):
        """加载golden set"""
        cls.cases = CASES
        cls.load_count = LOAD_COUNT
        cls.core_fields_asserted = 0

    def _run_case(self, case: Dict[str, Any]) -> tuple:
        """执行单个案例，返回 (grade, actual, expected, core_details)"""
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

            # 验证strength范围
            strength_min = expected.get('strength_range', [0.0, 1.0])[0]
            strength_max = expected.get('strength_range', [0.0, 1.0])[1]
            strength_ok = check_strength_range(actual_signals, strength_min, strength_max)

            # 验证核心字段
            core_ok, core_details = check_core_fields(result, expected)

            # 综合判定
            all_pass = no_crash and has_signals and count_ok and strength_ok and core_ok

            if all_pass:
                grade = "PASS"
            else:
                grade = "FAIL"

            return grade, actual_signals, expected, core_details

        except Exception as e:
            ERROR_COUNT += 1
            return "ERROR", None, expected, f"Exception: {e}"

    def test_99_summary(self):
        """最终统计摘要 - 验证核心字段断言覆盖率"""
        # 直接统计CASES中有多少案例包含core_fields
        cases_with_core = sum(1 for c in CASES if c.get('expected_calculation', {}).get('core_fields'))
        self.assertGreaterEqual(cases_with_core, 15,
            f"应有至少15个案例的核心字段断言，实际{cases_with_core}/20")


# ─── 动态生成测试方法 ──────────────────────────────────────────────────────────

def _generate_case_tests():
    """为每个case生成测试方法并注册到测试类"""
    for _case in CASES:
        case_id = _case['case_id']
        test_name = f"test_{case_id.lower().replace('-', '_')}"

        def _create_test_method(case, name):
            """工厂函数创建测试方法"""
            case_id = case['case_id']
            has_core = bool(case.get('expected_calculation', {}).get('core_fields'))

            def _test_impl(self):
                grade, actual, expected, core_details = self._run_case(case)

                # 断言
                self.assertEqual(grade, 'PASS',
                    f"{case_id}: {case.get('description', '')}\n"
                    f"Grade: {grade}\n"
                    f"Core fields: {core_details}\n"
                    f"Expected signals: {expected.get('min_signal_count', 0)}-{expected.get('max_signal_count', 20)}\n"
                    f"Actual signal count: {len(actual) if actual else 0}\n"
                    f"Actual signals: {[s.signal_id for s in (actual or [])]}")

                # 更新核心字段计数
                if has_core:
                    self.__class__.core_fields_asserted += 1

            _test_impl.__name__ = name
            _test_impl.__doc__ = f"Test case {case_id} - {case.get('description', '')}"
            return _test_impl

        test_func = _create_test_method(_case, test_name)
        setattr(TestBlindGoldenSet, test_name, test_func)


_generate_case_tests()


# ─── 主入口 ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    unittest.main(verbosity=2)
