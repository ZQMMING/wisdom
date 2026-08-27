"""
K2G State Engine 测试
验证多信号融合算法和状态判定逻辑
"""
import pytest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'src'))

from tongshu.k2g.registry_loader import load_k2g_registry


class TestStateEngine:
    """State Engine测试套件"""
    
    @pytest.fixture(autouse=True)
    def load_registry(self):
        """加载Registry数据"""
        self.loader = load_k2g_registry()
        self.semantics = {s['semantic_id']: s for s in self.loader.load_semantics()}
        self.relations = self.loader.load_relations()
        self.states = {s['state_id']: s for s in self.loader.load_states()}
        self.golden = self.loader.load_golden()
    
    def test_semantic_coverage(self):
        """测试语义覆盖率"""
        counts = self.loader.get_all_counts()
        assert counts['semantics'] >= 100, f"语义覆盖不足: {counts['semantics']}"
    
    def test_relation_coverage(self):
        """测试关系覆盖率"""
        counts = self.loader.get_all_counts()
        assert counts['relations'] >= 20, f"关系覆盖不足: {counts['relations']}"
    
    def test_state_coverage(self):
        """测试状态覆盖率"""
        counts = self.loader.get_all_counts()
        assert counts['states'] >= 10, f"状态覆盖不足: {counts['states']}"
    
    def test_golden_dataset(self):
        """测试黄金数据集"""
        counts = self.loader.get_all_counts()
        assert counts['golden'] >= 250, f"黄金数据集不足: {counts['golden']}"
        
        # 验证各域分布
        domains = self.golden.get('domains', {})
        for domain in ['BAZI', 'BLIND', 'TONGSHU', 'YIJING', 'ZIWEI']:
            assert domains.get(domain, 0) >= 30, f"{domain}域黄金样本不足"
    
    def test_semantic_parent_theme(self):
        """测试语义主题分布"""
        themes = {}
        for s in self.loader.load_semantics():
            theme = s.get('parent_theme', 'UNKNOWN')
            themes[theme] = themes.get(theme, 0) + 1
        
        # 六大主题应有覆盖
        expected_themes = {'XING', 'SHI', 'REN', 'JU', 'YANG', 'SHI_T'}
        actual_themes = set(themes.keys())
        assert expected_themes.issubset(actual_themes), f"缺少主题: {expected_themes - actual_themes}"
    
    def test_state_transition_rules(self):
        """测试State转换规则"""
        for state_id, state in self.states.items():
            assert 'transition_rules' in state, f"{state_id} 缺少转换规则"
    
    def test_safety_rules(self):
        """测试安全规则"""
        safety_rules = self.loader.load_safety()
        assert len(safety_rules) >= 20, f"安全规则不足: {len(safety_rules)}"
        
        # 验证BLOCK/WARN分级
        severities = set(r.get('severity', '') for r in safety_rules)
        assert 'BLOCK' in severities or 'WARN' in severities, "缺少BLOCK或WARN级别规则"
    
    def test_mapping_evidence_binding(self):
        """测试Mapping Evidence绑定"""
        core = self.loader.load_core()
        mappings = core.get('mappings', [])
        
        bound = sum(1 for m in mappings if m.get('evidence_refs'))
        assert bound == len(mappings), f"Evidence绑定不完整: {bound}/{len(mappings)}"
    
    def test_expression_tone_coverage(self):
        """测试Expression tone覆盖"""
        core = self.loader.load_core()
        expressions = core.get('expressions', [])
        
        tones = set(e.get('tone', '') for e in expressions)
        expected_tones = {'calm_modern', 'warm_modern', 'neutral_modern'}
        assert expected_tones.issubset(tones), f"缺少tone: {expected_tones - tones}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
