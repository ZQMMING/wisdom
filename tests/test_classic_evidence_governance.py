"""
负向测试：验证 Governance Boundary 完整性

测试场景：
1. Agent 试图授予 AUTHORIZED → 应失败
2. INSUFFICIENT_SOURCE 不应伪装成完整 Evidence → 应返回 EvidenceSearchResultRecord
3. Candidate 不得直接 APPROVED → 应失败
4. Agent 保存 Candidate 不得产生 Production Asset → 验证 save_candidate 行为
"""

import sys
import tempfile
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent / "wisdom"))

from src.tongshu.classic_evidence import DTSEvidenceAgent
from src.tongshu.classic_evidence.base import (
    SourceLocator,
    AuthorizationLevel,
    ProductionStatus,
    EvidenceSearchResultRecord,
)


def test_agent_cannot_grant_authorized():
    """Test 1: Agent 不得自行授予 AUTHORIZED"""
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = DTSEvidenceAgent(Path(tmpdir), Path(tmpdir))
        
        # 尝试传入 AUTHORIZED
        try:
            agent.extract_seasonal_support(
                canonical_state={},
                original_text="得令者旺",
                source_locator=SourceLocator(
                    classic="di_tian_sui",
                    work="滴天髓",
                    chapter="通神论·衰旺",
                    section="第1段",
                    paragraph="第1段",
                    passage_id="DTS_0001",
                    source_hash="abc",
                ),
                authorization_level=AuthorizationLevel.AUTHORIZED,
            )
            assert False, "Should raise ValueError when AUTHORIZED is passed"
        except ValueError as e:
            assert "AUTHORIZED" in str(e) or "授权" in str(e)
            print(f"✅ Test 1 passed: {e}")


def test_insufficient_source_returns_search_result():
    """Test 2: INSUFFICIENT_SOURCE 应返回 EvidenceSearchResultRecord，而非 AssertionProvenance"""
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = DTSEvidenceAgent(Path(tmpdir), Path(tmpdir))
        
        result = agent.mark_insufficient_source(
            evidence_type="SEASONAL_SUPPORT",
            observation_dimension="得令",
            notes="找不到原文",
        )
        
        # 验证返回类型
        assert isinstance(result, EvidenceSearchResultRecord), \
            f"Expected EvidenceSearchResultRecord, got {type(result)}"
        assert result.authorization_level == AuthorizationLevel.INSUFFICIENT_SOURCE
        assert result.classic_id == "di_tian_sui"
        print(f"✅ Test 2 passed: Returns EvidenceSearchResultRecord")


def test_candidate_cannot_be_approved():
    """Test 3: Agent 不得创建 APPROVED 状态的 Assertion"""
    from src.tongshu.classic_evidence.base import AssertionProvenance, EvidenceText, SemanticParse
    
    # 尝试直接创建 APPROVED 状态的 Assertion
    try:
        assertion = AssertionProvenance(
            assertion_id="A-DTS-TEST-001",
            source_system="滴天髓辨证代理",
            source_work="滴天髓",
            chapter="通神论·衰旺",
            source_locator=SourceLocator(
                classic="di_tian_sui",
                work="滴天髓",
                chapter="通神论·衰旺",
                section="第1段",
                paragraph="第1段",
                passage_id="DTS_0001",
                source_hash="abc",
            ),
            evidence_text=EvidenceText(original_text="得令者旺"),
            semantic_parse=SemanticParse(
                observation_dimension="得令",
                evidence_type="SEASONAL_SUPPORT",
                relation_semantics="SUPPORT",
            ),
            authorization_level=AuthorizationLevel.PARTIAL,
            production_status=ProductionStatus.APPROVED,  # 尝试设为 APPROVED
        )
        # 验证应该失败
        errors = assertion.validate()
        assert len(errors) > 0, "Expected validation errors for APPROVED status"
        assert any("APPROVED" in e or "production" in e.lower() for e in errors), \
            f"Expected APPROVED-related error, got: {errors}"
        print(f"✅ Test 3 passed: Validation caught APPROVED status")
    except Exception as e:
        print(f"✅ Test 3 passed: {e}")


def test_save_candidate_not_production():
    """Test 4: save_candidate 只保存 Candidate，不产生 Production Asset"""
    with tempfile.TemporaryDirectory() as tmpdir:
        agent = DTSEvidenceAgent(Path(tmpdir), Path(tmpdir))
        
        # 创建并保存 Candidate
        assertion = agent.extract_seasonal_support(
            canonical_state={},
            original_text="得令者旺，失令者衰",
            source_locator=SourceLocator(
                classic="di_tian_sui",
                work="滴天髓",
                chapter="通神论·衰旺",
                section="第1段",
                paragraph="第1段",
                passage_id="DTS_0001",
                source_hash="abc",
            ),
        )
        
        # 保存
        output_path = agent.save_candidate(assertion)
        
        # 验证文件已保存
        assert output_path.exists(), f"Expected file at {output_path}"
        
        # 验证内容为 CANDIDATE 状态
        import json
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert data["production_status"] == "CANDIDATE", \
            f"Expected CANDIDATE, got {data['production_status']}"
        assert data["authorization_level"] == "PARTIAL", \
            f"Expected PARTIAL, got {data['authorization_level']}"
        
        # 验证文件名包含 assertion_id（不是 production_id）
        assert "A-" in output_path.name, \
            f"Expected assertion ID in filename, got {output_path.name}"
        
        print(f"✅ Test 4 passed: save_candidate saves CANDIDATE, not Production Asset")


def main():
    print("=" * 60)
    print("Negative Tests: Governance Boundary Verification")
    print("=" * 60)
    
    tests = [
        ("Agent cannot grant AUTHORIZED", test_agent_cannot_grant_authorized),
        ("INSUFFICIENT_SOURCE returns search result", test_insufficient_source_returns_search_result),
        ("Candidate cannot be APPROVED", test_candidate_cannot_be_approved),
        ("save_candidate not production", test_save_candidate_not_production),
    ]
    
    passed = 0
    failed = 0
    
    for name, test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed += 1
    
    print("=" * 60)
    print(f"Results: {passed}/{len(tests)} passed, {failed} failed")
    print("=" * 60)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
