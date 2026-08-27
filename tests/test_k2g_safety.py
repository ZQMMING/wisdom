"""
K2G Safety Registry 测试
验证安全规则完整性和阻断逻辑
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
from tongshu.k2g.registry_loader import load_k2g_registry


class TestSafetyRegistry:
    @pytest.fixture(autouse=True)
    def load_registry(self):
        self.loader = load_k2g_registry()
        self.safety = self.loader.load_safety()
    
    def test_rule_count(self):
        assert len(self.safety) >= 20
    
    def test_severity_distribution(self):
        severities = [s.get('severity', '') for s in self.safety]
        assert 'BLOCK' in severities
        assert 'WARN' in severities
    
    def test_rule_structure(self):
        for rule in self.safety:
            assert 'safety_rule_id' in rule
            assert 'rule_type' in rule
            assert 'description' in rule


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
