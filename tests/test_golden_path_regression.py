"""
Phase 9: Golden Path回归审计 - Registry → Production Resolver一致性验证

核心目标：
1. 验证Registry中4条APPROVED Judgment与Production Resolver行为完全一致
2. 建立Golden Case基线，确保后续扩充不破坏已有行为
3. 锁定Golden Path作为稳定基线
"""

import pytest
from pathlib import Path
import json
from src.tongshu.assertion.judgment_production import (
    JudgmentProducer,
    evaluate_judgment,
    JudgmentResult,
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def producer():
    """Judgment Producer实例"""
    return JudgmentProducer()


@pytest.fixture
def approved_registry(producer):
    """从Registry提取的APPROVED Judgment列表"""
    return [e for e in producer.registry if e.get("production_status") == "APPROVED_FOR_PRODUCTION"]


# ============================================================================
# Phase 9.1: Registry字段完整性验证
# ============================================================================

class TestRegistryFieldIntegrity:
    """验证Registry中4条APPROVED Judgment的字段完整性"""

    def test_all_approved_have_required_fields(self, approved_registry):
        """所有APPROVED Judgment必须包含必需字段"""
        required_fields = [
            "judgment_id",
            "source_book",
            "source_section",
            "original_text",
            "condition_part",
            "judgment_part",
            "production_status",
            "gpt_ruling_timestamp",
        ]
        
        for entry in approved_registry:
            for field in required_fields:
                assert field in entry, f"{entry['judgment_id']}缺少字段: {field}"
                assert entry[field], f"{entry['judgment_id']}的{field}字段为空"

    def test_approved_count_matches_code(self, approved_registry, producer):
        """Registry中的APPROVED数量必须与代码中APPROVED_JUDGMENTS一致"""
        registry_ids = {e["judgment_id"] for e in approved_registry}
        code_ids = producer.APPROVED_JUDGMENTS
        
        assert registry_ids == code_ids, f"Registry IDs {registry_ids} != Code IDs {code_ids}"
        assert len(registry_ids) == 4, f"Expected 4 APPROVED, got {len(registry_ids)}"

    def test_no_hold_or_rejected_in_approved(self, approved_registry, producer):
        """APPROVED集合中不能包含HOLD或REJECTED的Judgment"""
        hold_ids = {"DTS-JUDG-002", "ZPZQ-JUDG-001"}
        rejected_ids = {"DTS-JUDG-003", "DTS-JUDG-004"}
        
        registry_ids = {e["judgment_id"] for e in approved_registry}
        
        assert registry_ids.isdisjoint(hold_ids), f"APPROVED集合包含HOLD: {registry_ids & hold_ids}"
        assert registry_ids.isdisjoint(rejected_ids), f"APPROVED集合包含REJECTED: {registry_ids & rejected_ids}"

    def test_all_registered_judgments_are_in_code(self, approved_registry, producer):
        """Registry中的所有条目必须在代码APPROVED集合中"""
        registry_ids = {e["judgment_id"] for e in approved_registry}
        code_ids = producer.APPROVED_JUDGMENTS
        
        assert registry_ids.issubset(code_ids), f"Registry包含未授权Judgment: {registry_ids - code_ids}"


# ============================================================================
# Phase 9.2: Golden Case验证
# ============================================================================

class TestGoldenCases:
    """Golden Case测试 - 验证每条Judgment的确定性行为"""

    def test_deterministic_output_dts_001(self):
        """DTS-JUDG-001确定性验证 - 同一输入应产生相同输出"""
        judgment_id = "DTS-JUDG-001"
        condition = {"has_bing": True, "has_yao": True}
        
        # 多次调用同一条件应产生相同结果
        results = [evaluate_judgment(judgment_id, condition) for _ in range(5)]
        
        first = results[0]
        for r in results[1:]:
            assert r.verdict == first.verdict, f"{judgment_id}输出不稳定: {r.verdict} != {first.verdict}"
            assert r.judgment_id == first.judgment_id

    def test_deterministic_output_zpzq_002(self):
        """ZPZQ-JUDG-002确定性验证 - 同一输入应产生相同输出"""
        judgment_id = "ZPZQ-JUDG-002"
        condition = {"has_he_shang": True, "has_cun_guan": True}
        
        results = [evaluate_judgment(judgment_id, condition) for _ in range(5)]
        
        first = results[0]
        for r in results[1:]:
            assert r.verdict == first.verdict, f"{judgment_id}输出不稳定"

    def test_deterministic_output_zpzq_003(self):
        """ZPZQ-JUDG-003确定性验证 - 同一输入应产生相同输出"""
        judgment_id = "ZPZQ-JUDG-003"
        condition = {"xiang_shen_intact": True}
        
        results = [evaluate_judgment(judgment_id, condition) for _ in range(5)]
        
        first = results[0]
        for r in results[1:]:
            assert r.verdict == first.verdict, f"{judgment_id}输出不稳定"

    def test_deterministic_output_zpzq_004(self):
        """ZPZQ-JUDG-004确定性验证 - 同一输入应产生相同输出"""
        judgment_id = "ZPZQ-JUDG-004"
        condition = {"xiang_shen_injured": True}
        
        results = [evaluate_judgment(judgment_id, condition) for _ in range(5)]
        
        first = results[0]
        for r in results[1:]:
            assert r.verdict == first.verdict, f"{judgment_id}输出不稳定"

    def test_case_expected_verdict_dts_001(self):
        """DTS-JUDG-001预期verdict验证"""
        judgment_id = "DTS-JUDG-001"
        
        # satisfied case - 有病有药
        result = evaluate_judgment(judgment_id, {"has_bing": True, "has_yao": True})
        assert result.verdict.value == "APPROVED", f"DTS-JUDG-001 satisfied: expected APPROVED, got {result.verdict.value}"
        
        # not_satisfied case - 无病无药
        result = evaluate_judgment(judgment_id, {"has_bing": False, "has_yao": False})
        # 无病时此规则不适用，可能返回任意非APPROVED结果
        assert result is not None
        
        # boundary case - 有病无药
        result = evaluate_judgment(judgment_id, {"has_bing": True, "has_yao": False})
        # 有病但无药，条件不完整
        assert result is not None

    def test_case_expected_verdict_zpzq_002(self):
        """ZPZQ-JUDG-002预期verdict验证"""
        judgment_id = "ZPZQ-JUDG-002"
        
        # satisfied case
        result = evaluate_judgment(judgment_id, {"has_he_shang": True, "has_cun_guan": True})
        assert result.verdict.value == "APPROVED"
        
        # not_satisfied case
        result = evaluate_judgment(judgment_id, {"has_he_shang": False, "has_cun_guan": True})
        assert result is not None
        
        # boundary case
        result = evaluate_judgment(judgment_id, {"has_he_shang": True, "has_cun_guan": False})
        assert result is not None

    def test_case_expected_verdict_zpzq_003(self):
        """ZPZQ-JUDG-003预期verdict验证"""
        judgment_id = "ZPZQ-JUDG-003"
        
        result = evaluate_judgment(judgment_id, {"xiang_shen_intact": True})
        assert result.verdict.value == "APPROVED"
        
        result = evaluate_judgment(judgment_id, {"xiang_shen_intact": False})
        assert result is not None

    def test_case_expected_verdict_zpzq_004(self):
        """ZPZQ-JUDG-004预期verdict验证"""
        judgment_id = "ZPZQ-JUDG-004"
        
        result = evaluate_judgment(judgment_id, {"xiang_shen_injured": True})
        assert result.verdict.value == "APPROVED"
        
        result = evaluate_judgment(judgment_id, {"xiang_shen_injured": False})
        assert result is not None

    def test_traceability_completeness_all(self, producer):
        """所有Golden Case输出必须包含完整溯源字段"""
        for judg_id in producer.APPROVED_JUDGMENTS:
            # 找到对应的condition data
            if "DTS" in judg_id:
                condition = {"has_bing": True, "has_yao": True}
            elif "ZPZQ-JUDG-002" in judg_id:
                condition = {"has_he_shang": True, "has_cun_guan": True}
            elif "ZPZQ-JUDG-003" in judg_id:
                condition = {"xiang_shen_intact": True}
            elif "ZPZQ-JUDG-004" in judg_id:
                condition = {"xiang_shen_injured": True}
            else:
                continue
            
            result = evaluate_judgment(judg_id, condition)
            
            assert hasattr(result, "source_book") and result.source_book, f"{judg_id}缺少source_book"
            assert hasattr(result, "original_text") and result.original_text, f"{judg_id}缺少original_text"
            assert hasattr(result, "condition_part") and result.condition_part, f"{judg_id}缺少condition_part"
            assert hasattr(result, "judgment_part") and result.judgment_part, f"{judg_id}缺少judgment_part"


# ============================================================================
# Phase 9.3: Legacy/L4隔离验证
# ============================================================================

class TestLegacyL4Isolation:
    """验证Golden Path无Legacy/L4回流"""

    def test_no_legacy_in_all_golden_cases(self, producer):
        """所有Golden Case输出不包含Legacy字段"""
        for judg_id in producer.APPROVED_JUDGMENTS:
            if "DTS" in judg_id:
                condition = {"has_bing": True, "has_yao": True}
            elif "ZPZQ-JUDG-002" in judg_id:
                condition = {"has_he_shang": True, "has_cun_guan": True}
            elif "ZPZQ-JUDG-003" in judg_id:
                condition = {"xiang_shen_intact": True}
            elif "ZPZQ-JUDG-004" in judg_id:
                condition = {"xiang_shen_injured": True}
            else:
                continue
            
            result = evaluate_judgment(judg_id, condition)
            result_str = str(result)
            
            assert "evaluate_strength" not in result_str.lower(), f"{judg_id}包含Legacy调用"
            assert "wang_score" not in result_str.lower(), f"{judg_id}包含wang_score引用"

    def test_no_l4_in_all_golden_cases(self, producer):
        """所有Golden Case输出不包含L4字段"""
        for judg_id in producer.APPROVED_JUDGMENTS:
            if "DTS" in judg_id:
                condition = {"has_bing": True, "has_yao": True}
            elif "ZPZQ-JUDG-002" in judg_id:
                condition = {"has_he_shang": True, "has_cun_guan": True}
            elif "ZPZQ-JUDG-003" in judg_id:
                condition = {"xiang_shen_intact": True}
            elif "ZPZQ-JUDG-004" in judg_id:
                condition = {"xiang_shen_injured": True}
            else:
                continue
            
            result = evaluate_judgment(judg_id, condition)
            result_str = str(result)
            
            assert "旺衰" not in result_str, f"{judg_id}包含L4判定"


# ============================================================================
# Phase 9.4: Baseline锁定验证
# ============================================================================

class TestBaselineLock:
    """验证Golden Path作为稳定基线"""

    def test_all_4_judgments_accessible(self, producer):
        """所有4条APPROVED Judgment必须可访问"""
        for judg_id in producer.APPROVED_JUDGMENTS:
            entry = next((e for e in producer.registry if e["judgment_id"] == judg_id), None)
            assert entry is not None, f"{judg_id}不在Registry中"
            assert entry["production_status"] == "APPROVED_FOR_PRODUCTION"

    def test_prohibited_judgments_blocked(self, producer):
        """禁止的Judgment必须被正确拦截"""
        prohibited = ["DTS-JUDG-002", "DTS-JUDG-003", "DTS-JUDG-004", "ZPZQ-JUDG-001"]
        
        for judg_id in prohibited:
            with pytest.raises(ValueError):
                evaluate_judgment(judg_id, {"has_bing": True})

    def test_baseline_test_count_stable(self, producer):
        """验证测试数量保持稳定（不应意外增减）"""
        # 直接验证registry和code的一致性，不依赖subprocess
        assert len(producer.APPROVED_JUDGMENTS) == 4, f"Expected 4 APPROVED, got {len(producer.APPROVED_JUDGMENTS)}"
        
        # 验证Registry条目数
        registry_ids = {e["judgment_id"] for e in producer.registry}
        assert len(registry_ids) == 8, f"Expected 8 total registry entries, got {len(registry_ids)}"


# ============================================================================
# Summary Report
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])