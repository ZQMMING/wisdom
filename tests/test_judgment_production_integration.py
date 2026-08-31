"""
Phase 7 Production Chain Integration Validation
验证4条APPROVED Judgment的端到端流程
"""

import pytest
from pathlib import Path
from src.tongshu.assertion.judgment_production import (
    JudgmentProducer,
    evaluate_judgment,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def producer():
    """Judgment Producer实例"""
    return JudgmentProducer()


@pytest.fixture
def APPROVED_JUDGMENTS(producer):
    """4条APPROVED Judgment ID集合"""
    return producer.APPROVED_JUDGMENTS


@pytest.fixture
def registry_by_id(producer):
    """按judgment_id索引的Registry"""
    return {entry["judgment_id"]: entry for entry in producer.registry}


@pytest.fixture
def test_condition_data():
    """测试用condition数据"""
    return {
        "has_bing": True,
        "has_yao": True,
        "has_he_shang": False,
        "has_cun_guan": True,
        "xiang_shen_intact": True,
        "xiang_shen_injured": False,
    }


# ============================================================================
# Phase 7.1: End-to-End Integration Tests
# ============================================================================

class TestEndToEndFlow:
    """端到端流程测试"""

    def test_dts_judg_001_full_flow(self, APPROVED_JUDGMENTS, registry_by_id, test_condition_data):
        """DTS-JUDG-001完整流程测试"""
        # 验证注册状态
        assert "DTS-JUDG-001" in APPROVED_JUDGMENTS
        entry = registry_by_id["DTS-JUDG-001"]
        assert entry["production_status"] == "APPROVED_FOR_PRODUCTION"

        # 验证评估
        result = evaluate_judgment("DTS-JUDG-001", test_condition_data)
        assert result.judgment_id == "DTS-JUDG-001"
        assert result.verdict.value in ["APPROVED", "HOLD", "REJECTED"]

    def test_zpzq_judg_002_full_flow(self, APPROVED_JUDGMENTS, registry_by_id, test_condition_data):
        """ZPZQ-JUDG-002完整流程测试"""
        assert "ZPZQ-JUDG-002" in APPROVED_JUDGMENTS
        entry = registry_by_id["ZPZQ-JUDG-002"]
        assert entry["production_status"] == "APPROVED_FOR_PRODUCTION"

        result = evaluate_judgment("ZPZQ-JUDG-002", test_condition_data)
        assert result.judgment_id == "ZPZQ-JUDG-002"
        assert result.verdict.value in ["APPROVED", "HOLD", "REJECTED"]

    def test_zpzq_judg_003_full_flow(self, APPROVED_JUDGMENTS, registry_by_id, test_condition_data):
        """ZPZQ-JUDG-003完整流程测试"""
        assert "ZPZQ-JUDG-003" in APPROVED_JUDGMENTS
        entry = registry_by_id["ZPZQ-JUDG-003"]
        assert entry["production_status"] == "APPROVED_FOR_PRODUCTION"

        result = evaluate_judgment("ZPZQ-JUDG-003", test_condition_data)
        assert result.judgment_id == "ZPZQ-JUDG-003"
        assert result.verdict.value in ["APPROVED", "HOLD", "REJECTED"]

    def test_zpzq_judg_004_full_flow(self, APPROVED_JUDGMENTS, registry_by_id, test_condition_data):
        """ZPZQ-JUDG-004完整流程测试"""
        assert "ZPZQ-JUDG-004" in APPROVED_JUDGMENTS
        entry = registry_by_id["ZPZQ-JUDG-004"]
        assert entry["production_status"] == "APPROVED_FOR_PRODUCTION"

        result = evaluate_judgment("ZPZQ-JUDG-004", test_condition_data)
        assert result.judgment_id == "ZPZQ-JUDG-004"
        assert result.verdict.value in ["APPROVED", "HOLD", "REJECTED"]


# ============================================================================
# Phase 7.2: Traceability Verification
# ============================================================================

class TestTraceability:
    """溯源字段验证"""

    def test_traceability_fields_complete(self, APPROVED_JUDGMENTS, registry_by_id):
        """验证traceability字段完整"""
        for judg_id in APPROVED_JUDGMENTS:
            entry = registry_by_id[judg_id]
            assert "source_book" in entry, f"{judg_id}缺少source_book"
            assert "original_text" in entry, f"{judg_id}缺少original_text"
            assert "condition_part" in entry, f"{judg_id}缺少condition_part"
            assert "judgment_part" in entry, f"{judg_id}缺少judgment_part"
            assert "source_section" in entry, f"{judg_id}缺少source_section"

    def test_output_contains_traceability(self, test_condition_data):
        """验证输出包含溯源字段"""
        result = evaluate_judgment("DTS-JUDG-001", test_condition_data)
        assert result.source_book == "滴天髓"
        assert result.original_text == "有病方为贵，无伤不是奇。"
        assert result.condition_part == "有病（有症结需要解决）"
        assert result.judgment_part == "方为贵（才能显贵）"


# ============================================================================
# Phase 7.3: Pollution Isolation
# ============================================================================

class TestPollutionIsolation:
    """污染隔离验证"""

    def test_hold_not_in_output(self, test_condition_data):
        """验证HOLD Judgment不进入输出"""
        # DTS-JUDG-002是HOLD
        with pytest.raises(ValueError):
            evaluate_judgment("DTS-JUDG-002", test_condition_data)

    def test_rejected_not_in_output(self, test_condition_data):
        """验证REJECTED Judgment不进入输出"""
        # DTS-JUDG-003是REJECTED
        with pytest.raises(ValueError):
            evaluate_judgment("DTS-JUDG-003", test_condition_data)

    def test_unauthorized_not_in_output(self, test_condition_data):
        """验证未授权Judgment不进入输出"""
        with pytest.raises(ValueError):
            evaluate_judgment("UNAUTHORIZED-001", test_condition_data)


# ============================================================================
# Phase 7.4: Legacy/L4 Isolation
# ============================================================================

class TestLegacyL4Isolation:
    """Legacy/L4污染隔离验证"""

    def test_no_legacy_call_in_result(self, test_condition_data):
        """验证输出不包含Legacy字段"""
        result = evaluate_judgment("DTS-JUDG-001", test_condition_data)
        result_str = str(result)
        assert "evaluate_strength" not in result_str.lower()
        assert "wang_score" not in result_str.lower()

    def test_no_l4_in_result(self, test_condition_data):
        """验证输出不包含L4字段"""
        result = evaluate_judgment("ZPZQ-JUDG-002", test_condition_data)
        result_str = str(result)
        assert "旺衰" not in result_str
        assert "strength" not in result_str.lower() or "evaluate_strength" not in result_str


# ============================================================================
# Phase 7.5: Performance and Consistency
# ============================================================================

class TestPerformanceConsistency:
    """性能和一致性验证"""

    def test_all_judgments_fast(self, APPROVED_JUDGMENTS, test_condition_data):
        """验证所有Judgment评估速度快"""
        import time
        for judg_id in APPROVED_JUDGMENTS:
            start = time.time()
            evaluate_judgment(judg_id, test_condition_data)
            elapsed = time.time() - start
            assert elapsed < 0.1, f"{judg_id}评估时间过长: {elapsed}s"

    def test_consistent_results(self, test_condition_data):
        """验证结果一致性"""
        results = []
        for _ in range(10):
            results.append(evaluate_judgment("DTS-JUDG-001", test_condition_data))
        # 所有结果应该一致
        first = results[0]
        for r in results[1:]:
            assert r == first, "结果不一致"


# ============================================================================
# Summary Report
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])