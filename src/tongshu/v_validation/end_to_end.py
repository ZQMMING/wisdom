"""端到端验证脚本：人生时间轴回测

对单个命例进行完整人生时间线回测，验证系统在不同年份的预测能力。

使用方式:
    python -m src.tongshu.v_validation.end_to_end
"""
from __future__ import annotations
import sys
import json
import logging
from datetime import date
from pathlib import Path

# Add project root to path
_PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from tongshu.v_validation import (
    Case, Event, EvidenceGrade, EventSeverity, EventCategory,
    BacktestEngine, BlindProtocol, ScoringMatrix,
    AblationRunner, BaselineSystem, ValidationReport,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

# ─── 种子案例（纪晓岚） ───────────────────────────────────────────────
# 公历 1724-08-03 午时，已知历史事件
SEED_CASE = Case(
    case_id="GOLDEN-JIXIAOLAN",
    gender="male",
    birth_year=1724, birth_month=8, birth_day=3, birth_hour=12,
    birth_location="Xian County, Hebei",
    timezone="Asia/Shanghai",
    events=[
        Event(date=date(1749, 3, 15), category=EventCategory.JOB_CHANGE,
              severity=EventSeverity.MAJOR, description="中举",
              evidence_grade=EvidenceGrade.B),
        Event(date=date(1754, 6, 20), category=EventCategory.JOB_CHANGE,
              severity=EventSeverity.MAJOR, description="中进士",
              evidence_grade=EvidenceGrade.A),
        Event(date=date(1766, 1, 10), category=EventCategory.PROMOTION,
              severity=EventSeverity.MODERATE, description="任职翰林院",
              evidence_grade=EvidenceGrade.B),
        Event(date=date(1780, 9, 5), category=EventCategory.PROMOTION,
              severity=EventSeverity.MAJOR, description="官至体仁阁大学士",
              evidence_grade=EvidenceGrade.A),
    ],
    source_type="historical",
    source_url="https://en.wikipedia.org/wiki/Ji_Xiaolan",
)


def run_end_to_end() -> dict:
    """运行端到端验证"""
    logger.info("=" * 60)
    logger.info("V-VALIDATION: End-to-End Life Timeline Backtest")
    logger.info("=" * 60)

    # 运行回测
    engine = BacktestEngine()
    results = engine.backtest(SEED_CASE)

    # 生成报告
    report = ValidationReport(
        case_id=SEED_CASE.case_id,
        results=results,
        metadata={
            "test_type": "end_to_end",
            "engine_version": "v13",
            "validation_date": "2026-09-03",
            "notes": [
                "实现真正的pipeline集成（当前使用模拟数据）",
                "制定前瞻冻结协议（V-FROZEN-2026-09-01）",
            ]
        },
    )

    # 保存报告到项目目录
    output_path = _PROJECT_ROOT / "docs" / "validation_report.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report.save(str(output_path))
    logger.info(f"  Report saved: {output_path}")

    logger.info("=" * 60)
    logger.info("V-VALIDATION COMPLETE")
    logger.info("=" * 60)
    return report.generate()


if __name__ == "__main__":
    result = run_end_to_end()
    print("\n" + json.dumps(result, indent=2, ensure_ascii=False))
