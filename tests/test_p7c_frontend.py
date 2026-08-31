"""Phase 7-C: 前端页面测试（HTML结构验证）"""
from __future__ import annotations
import unittest
from pathlib import Path


class TestFrontendPages(unittest.TestCase):
    """前端页面结构测试。"""
    
    def test_index_html_exists(self):
        """首页HTML存在。"""
        index_path = Path(__file__).parent.parent.parent / "frontend" / "index.html"
        self.assertTrue(index_path.exists(), "index.html不存在")
    
    def test_index_html_structure(self):
        """首页HTML结构验证。"""
        index_path = Path(__file__).parent.parent.parent / "frontend" / "index.html"
        content = index_path.read_text(encoding='utf-8')
        
        # 核心结构检查
        self.assertIn('<!DOCTYPE html>', content)
        self.assertIn('<title>顺天', content)
        self.assertIn('hexagram-card', content)
        self.assertIn('state-card', content)
        self.assertIn('guidance-grid', content)
        self.assertIn('elements-card', content)
        self.assertIn('time-seq', content)
    
    def test_viewmodel_integration(self):
        """ViewModel与前端数据协议一致性。"""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
        
        from tongshu.services.daily_viewmodel import create_sample_tongshu
        
        tongshu = create_sample_tongshu()
        data = tongshu.to_dict()
        
        # 检查前端需要的字段
        required_fields = ['date', 'hexagram', 'state', 'guidance', 
                          'element_balance', 'liu_nian', 'liu_yue', 'liu_ri']
        
        for field in required_fields:
            self.assertIn(field, data, f"缺少字段: {field}")
        
        # 检查hexagram子字段
        hexagram = data['hexagram']
        for field in ['name', 'upper', 'lower', 'binary', 'meaning']:
            self.assertIn(field, hexagram, f"缺少卦名字段: {field}")
        
        # 检查state子字段
        state = data['state']
        for field in ['title', 'description', 'energy_level']:
            self.assertIn(field, state, f"缺少状态字段: {field}")
        
        # 检查guidance子字段
        guidance = data['guidance']
        for field in ['opportunity', 'attention', 'suggestion']:
            self.assertIn(field, guidance, f"缺少指导字段: {field}")


if __name__ == '__main__':
    unittest.main()