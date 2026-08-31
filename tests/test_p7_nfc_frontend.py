"""Phase 7: NFC体验层前端对接测试"""

from __future__ import annotations
import unittest
from pathlib import Path


class TestNFCDailyFrontend(unittest.TestCase):
    """NFC每日通书前端页面测试"""
    
    def test_nfc_html_exists(self):
        """NFC页面HTML存在"""
        path = Path(__file__).parent.parent.parent / "frontend" / "nfc-daily.html"
        self.assertTrue(path.exists(), "nfc-daily.html 不存在")
    
    def test_nfc_html_structure(self):
        """NFC页面结构验证"""
        path = Path(__file__).parent.parent.parent / "frontend" / "nfc-daily.html"
        content = path.read_text(encoding='utf-8')
        
        # 核心结构检查
        self.assertIn('<!DOCTYPE html>', content)
        self.assertIn('顺天', content)
        self.assertIn('nfcPrompt', content)  # NFC触发区域
        self.assertIn('hexagram-card', content)
        self.assertIn('state-card', content)
        self.assertIn('guidance-grid', content)
        self.assertIn('time-seq', content)
    
    def test_nfc_api_integration_points(self):
        """前端API集成点检查"""
        path = Path(__file__).parent.parent.parent / "frontend" / "nfc-daily.html"
        content = path.read_text(encoding='utf-8')
        
        # 检查是否预留了API调用接口
        self.assertIn('/api/v1/daily', content)
        
        # 检查NFC Reader API使用
        self.assertIn('NDEFReader', content)
        
        # 检查数据字段对应
        self.assertIn('hexagram.name', content)
        self.assertIn('hexagram.binary', content)
        self.assertIn('state', content)
        self.assertIn('guidance', content)
    
    def test_frontend_data_protocol(self):
        """前端数据协议验证"""
        path = Path(__file__).parent.parent.parent / "frontend" / "nfc-daily.html"
        content = path.read_text(encoding='utf-8')
        
        # 检查required fields
        required_fields = ['hexagram', 'state', 'guidance', 'sources']
        for field in required_fields:
            self.assertIn(field, content, f"缺少数据字段: {field}")
        
        # 检查六爻数据结构
        self.assertIn('binary', content)
        self.assertIn('upper', content)
        self.assertIn('lower', content)


if __name__ == '__main__':
    unittest.main()
