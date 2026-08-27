"""Validation Report Generator — 验证报告生成器

生成完整验证报告，包括：
- 测试覆盖摘要
- 通过率统计
- 消融实验结果
- 基线对比
- 改进建议
"""
from __future__ import annotations
import json
import logging
from datetime import datetime
from typing import Optional

logger = logging.getLogger(__name__)


class ValidationReport:
    """验证报告。"""

    def __init__(self):
        self._sections: dict[str, any] = {}

    def add_section(self, name: str, content: dict):
        """添加报告章节。"""
        self._sections[name] = content

    def generate(self) -> dict:
        """生成完整报告。"""
        return {
            "report_version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "summary": self._sections.get("summary", {}),
            "test_coverage": self._sections.get("test_coverage", {}),
            "backtest_results": self._sections.get("backtest_results", {}),
            "ablation_results": self._sections.get("ablation_results", {}),
            "baseline_comparison": self._sections.get("baseline_comparison", {}),
            "recommendations": self._sections.get("recommendations", []),
        }

    def to_json(self, indent: int = 2) -> str:
        """导出JSON格式报告。"""
        return json.dumps(self.generate(), indent=indent, ensure_ascii=False)

    def save(self, path: str):
        """保存到文件。"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.to_json())
        logger.info(f"Report saved to {path}")
