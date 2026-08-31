"""
Judgment Production Tests - 仅测试4条APPROVED Judgment

依据: GPT裁决 9d770f6
范围: 仅测试APPROVED的4个Judgment，不包含HOLD或REJECTED
"""

import pytest
from src.tongshu.assertion.judgment_production import (
    JudgmentProducer,
    JudgmentVerdict,
    evaluate_judgment,
    get_judgment_producer
)


class TestJudgmentProducerAuthorization:
    """测试Judgment Producer授权验证"""
    
    def setup_method(self):
        """每个测试前初始化Producer"""
        self.producer = JudgmentProducer()
    
    def test_approved_judgments_count(self):
        """验证仅4个APPROVED Judgment"""
        approved = self.producer.get_approved_judgments()
        assert len(approved) == 4, f"Expected 4 approved judgments, got {len(approved)}"
    
    def test_approved_judgments_ids(self):
        """验证4个APPROVED Judgment的ID"""
        approved = self.producer.get_approved_judgments()
        expected = {"DTS-JUDG-001", "ZPZQ-JUDG-002", "ZPZQ-JUDG-003", "ZPZQ-JUDG-004"}
        assert approved == expected, f"Approved judgments mismatch: {approved}"
    
    def test_prohibited_judgments_not_approved(self):
        """验证禁止实现的Judgment不在APPROVED列表中"""
        prohibited = {"DTS-JUDG-002", "ZPZQ-JUDG-001", "DTS-JUDG-003", "DTS-JUDG-004"}
        approved = self.producer.get_approved_judgments()
        
        for judgment_id in prohibited:
            assert judgment_id not in approved, f"Prohibited judgment {judgment_id} should not be approved"
    
    def test_unauthorized_judgment_raises_error(self):
        """验证未授权Judgment调用时抛出异常"""
        with pytest.raises(ValueError, match="not approved for production"):
            self.producer.evaluate("UNAUTHORIZED-JUDG-001", {})
    
    def test_hold_judgment_raises_error(self):
        """验证HOLD Judgment调用时抛出异常"""
        with pytest.raises(ValueError, match="not approved for production"):
            self.producer.evaluate("DTS-JUDG-002", {})
    
    def test_rejected_judgment_raises_error(self):
        """验证REJECTED Judgment调用时抛出异常"""
        with pytest.raises(ValueError, match="not approved for production"):
            self.producer.evaluate("DTS-JUDG-003", {})


class TestDTSJUDG001:
    """测试DTS-JUDG-001: 有病方为贵"""
    
    def setup_method(self):
        self.producer = JudgmentProducer()
    
    def test_has_bing_has_yao(self):
        """有病且有药 → APPROVED"""
        result = self.producer.evaluate(
            "DTS-JUDG-001",
            {"has_bing": True, "has_yao": True}
        )
        assert result.verdict == JudgmentVerdict.APPROVED
        assert "有病得药" in result.reason
        assert result.judgment_id == "DTS-JUDG-001"
        assert result.source_book == "滴天髓"
        assert "有病方为贵" in result.original_text
    
    def test_has_bing_no_yao(self):
        """有病但无药 → HOLD"""
        result = self.producer.evaluate(
            "DTS-JUDG-001",
            {"has_bing": True, "has_yao": False}
        )
        assert result.verdict == JudgmentVerdict.HOLD
        assert "无药" in result.reason
    
    def test_no_bing(self):
        """无病 → APPROVED（正常格局）"""
        result = self.producer.evaluate(
            "DTS-JUDG-001",
            {"has_bing": False}
        )
        assert result.verdict == JudgmentVerdict.APPROVED
        assert "无病无伤" in result.reason


class TestZPZQJUDG002:
    """测试ZPZQ-JUDG-002: 合伤存官，遂成贵格"""
    
    def setup_method(self):
        self.producer = JudgmentProducer()
    
    def test_he_shang_cun_guan(self):
        """合伤存官结构成立 → APPROVED"""
        result = self.producer.evaluate(
            "ZPZQ-JUDG-002",
            {"has_he_shang": True, "has_cun_guan": True}
        )
        assert result.verdict == JudgmentVerdict.APPROVED
        assert "合伤存官" in result.reason
        assert result.judgment_id == "ZPZQ-JUDG-002"
        assert result.source_book == "子平真诠"
        assert "合伤存官" in result.original_text
    
    def test_no_he_shang(self):
        """无合伤存官结构 → HOLD"""
        result = self.producer.evaluate(
            "ZPZQ-JUDG-002",
            {"has_he_shang": False, "has_cun_guan": False}
        )
        assert result.verdict == JudgmentVerdict.HOLD
        assert "未满足" in result.reason


class TestZPZQJUDG003:
    """测试ZPZQ-JUDG-003: 相神无破，贵格已成"""
    
    def setup_method(self):
        self.producer = JudgmentProducer()
    
    def test_xiang_shen_intact(self):
        """相神无破 → APPROVED"""
        result = self.producer.evaluate(
            "ZPZQ-JUDG-003",
            {"xiang_shen_intact": True}
        )
        assert result.verdict == JudgmentVerdict.APPROVED
        assert "相神无破" in result.reason
        assert result.judgment_id == "ZPZQ-JUDG-003"
        assert result.source_book == "子平真诠"
        assert "贵格已成" in result.original_text
    
    def test_xiang_shen_not_intact(self):
        """相神有破 → HOLD"""
        result = self.producer.evaluate(
            "ZPZQ-JUDG-003",
            {"xiang_shen_intact": False}
        )
        assert result.verdict == JudgmentVerdict.HOLD
        assert "相神有破" in result.reason


class TestZPZQJUDG004:
    """测试ZPZQ-JUDG-004: 相神有伤，立败其格"""
    
    def setup_method(self):
        self.producer = JudgmentProducer()
    
    def test_xiang_shen_injured(self):
        """相神有伤 → APPROVED"""
        result = self.producer.evaluate(
            "ZPZQ-JUDG-004",
            {"xiang_shen_injured": True}
        )
        assert result.verdict == JudgmentVerdict.APPROVED
        assert "相神有伤" in result.reason
        assert result.judgment_id == "ZPZQ-JUDG-004"
        assert result.source_book == "子平真诠"
        assert "立败其格" in result.original_text
    
    def test_xiang_shen_not_injured(self):
        """相神无伤 → HOLD"""
        result = self.producer.evaluate(
            "ZPZQ-JUDG-004",
            {"xiang_shen_injured": False}
        )
        assert result.verdict == JudgmentVerdict.HOLD
        assert "相神无伤" in result.reason


class TestNoLegacyReturn:
    """测试无Legacy回流验证"""

    def setup_method(self):
        self.producer = JudgmentProducer()

    def test_validate_no_legacy_return(self):
        """验证无Legacy回流（AST分析）"""
        # 当前文件应该通过验证
        assert self.producer.validate_no_legacy回流() is True

    def test_validate_no_l4_risk(self):
        """验证无L4风险（关键字匹配）"""
        # 当前文件应该通过验证
        assert self.producer.validate_no_l4风险() is True

    def test_validate_legacy_rejection(self):
        """验证检测到wang_score时返回False"""
        import tempfile
        import os

        # 创建一个包含wang_score的测试文件
        test_code = '''
def test():
    wang_score = 100
    return wang_score
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(test_code)
            temp_path = f.name

        try:
            assert self.producer.validate_no_legacy回流(temp_path) is False
        finally:
            os.unlink(temp_path)

    def test_validate_l4_rejection(self):
        """验证检测到body_strong赋值时返回False"""
        import tempfile
        import os

        # 创建一个包含body_strong赋值的测试文件
        test_code = '''
def test():
    body_strong = True
    return body_strong
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(test_code)
            temp_path = f.name

        try:
            assert self.producer.validate_no_l4风险(temp_path) is False
        finally:
            os.unlink(temp_path)

    def test_validate_infer_verdict_rejection(self):
        """验证检测到infer_verdict调用时返回False"""
        import tempfile
        import os

        test_code = '''
def test():
    result = infer_verdict()
    return result
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
            f.write(test_code)
            temp_path = f.name

        try:
            assert self.producer.validate_no_legacy回流(temp_path) is False
            assert self.producer.validate_no_l4风险(temp_path) is False
        finally:
            os.unlink(temp_path)


class TestRegistryProtection:
    """测试Registry状态变更保护（TD-001.3）"""

    def setup_method(self):
        self.producer = JudgmentProducer()

    def test_prevent_hold_to_approved(self):
        """验证不能将HOLD状态的Judgment改为APPROVED"""
        # DTS-JUDG-002在Registry中是HOLD状态
        with pytest.raises(ValueError, match="cannot be changed"):
            self.producer.prevent_unauthorized_status_change(
                "DTS-JUDG-002",
                "APPROVED_FOR_PRODUCTION"
            )

    def test_prevent_rejected_to_approved(self):
        """验证不能将REJECTED状态的Judgment改为APPROVED"""
        # DTS-JUDG-003在Registry中是PERMANENTLY_REJECTED状态
        with pytest.raises(ValueError, match="cannot be changed"):
            self.producer.prevent_unauthorized_status_change(
                "DTS-JUDG-003",
                "APPROVED_FOR_PRODUCTION"
            )

    def test_allow_same_status_change(self):
        """验证允许保持相同状态"""
        # 保持不变应该允许
        assert self.producer.prevent_unauthorized_status_change(
            "DTS-JUDG-001",
            "APPROVED_FOR_PRODUCTION"
        ) is True


class TestConvenienceFunctions:
    """测试便捷函数"""
    
    def test_evaluate_judgment(self):
        """测试便捷函数evaluate_judgment"""
        result = evaluate_judgment(
            "DTS-JUDG-001",
            {"has_bing": True, "has_yao": True}
        )
        assert result.verdict == JudgmentVerdict.APPROVED
        assert result.judgment_id == "DTS-JUDG-001"
    
    def test_get_judgment_producer_singleton(self):
        """测试单例模式"""
        producer1 = get_judgment_producer()
        producer2 = get_judgment_producer()
        assert producer1 is producer2


class TestRegistryValidation:
    """测试Registry验证"""
    
    def test_registry_has_correct_status(self):
        """验证Registry中只有APPROVED_FOR_PRODUCTION状态的Judgment在APPROVED列表中"""
        producer = JudgmentProducer()
        approved = producer.get_approved_judgments()
        
        # 验证每个approved judgment都有正确的production_status
        for judgment_id in approved:
            assert producer.is_approved(judgment_id), f"{judgment_id} should be approved"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
