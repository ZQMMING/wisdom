"""
K2G Golden Dataset 测试
验证黄金数据集完整性和覆盖度
"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))
from tongshu.k2g.registry_loader import load_k2g_registry


class TestGoldenDataset:
    @pytest.fixture(autouse=True)
    def load_registry(self):
        self.loader = load_k2g_registry()
        self.golden = self.loader.load_golden()
    
    def test_total_count(self):
        assert self.golden.get('total_count', 0) >= 250
    
    def test_domain_distribution(self):
        domains = self.golden.get('domains', {})
        for domain in ['BAZI', 'BLIND', 'TONGSHU', 'YIJING', 'ZIWEI']:
            assert domains.get(domain, 0) >= 30, f"{domain}域样本不足"
    
    def test_case_structure(self):
        cases = self.golden.get('cases', [])
        for c in cases[:10]:
            assert 'golden_id' in c
            assert 'domain' in c
            assert 'input' in c
            assert 'expected_guidance' in c


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
