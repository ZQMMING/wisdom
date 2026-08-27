"""V-FROZEN-2026-09-01 前瞻冻结协议

核心原则：
1. 冻结后模型不得修改（算法、参数、规则）
2. 只接受新事件数据（历史回测已完成）
3. 预测目标：2026-09-01之后的事件
4. 验证标准：精确到月，Major事件±3个月

使用方式：
    from tongshu.v_validation.freeze import FreezeProtocol
    
    freeze = FreezeProtocol("V-FROZEN-2026-09-01")
    predictions = freeze.predict_future_events(case, start_date="2026-09-01")
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# ─── 冻结状态 ──────────────────────────────────────────────────────────────

@dataclass
class FreezeSnapshot:
    """冻结快照：记录当前模型状态。"""
    freeze_id: str
    freeze_date: date
    commit_hash: str
    algorithm_version: str
    test_results: Dict[str, Any]
    golden_dataset_path: str
    ontology_version: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "freeze_id": self.freeze_id,
            "freeze_date": self.freeze_date.isoformat(),
            "commit_hash": self.commit_hash,
            "algorithm_version": self.algorithm_version,
            "test_results": self.test_results,
            "golden_dataset_path": self.golden_dataset_path,
            "ontology_version": self.ontology_version,
        }
    
    def save(self, path: str):
        """保存冻结快照。"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)


# ─── 预测窗口 ──────────────────────────────────────────────────────────────

class PredictionWindow:
    """前瞻预测窗口定义。"""
    
    # 冻结日期
    FROZEN_DATE = date(2026, 9, 1)
    
    # 时间粒度
    GRANULARITY = {
        "year": 365,
        "quarter": 90,
        "month": 30,
        "week": 7,
    }
    
    # 容忍度（按严重程度）
    TOLERANCE = {
        1: 365,   # TRIVIAL: ±1年
        2: 180,   # SLIGHT: ±6个月
        3: 90,    # MODERATE: ±3个月
        4: 30,    # MAJOR: ±1个月
        5: 7,     # CRITICAL: ±1周
    }
    
    @classmethod
    def is_future(cls, event_date: date) -> bool:
        """判断事件是否在冻结之后。"""
        return event_date > cls.FROZEN_DATE
    
    @classmethod
    def get_tolerance(cls, severity: int) -> int:
        """获取该严重程度的时间容忍度（天数）。"""
        return cls.TOLERANCE.get(severity, 90)


# ─── 冻结协议 ──────────────────────────────────────────────────────────────

class FreezeProtocol:
    """前瞻冻结协议主类。"""
    
    def __init__(
        self,
        freeze_id: str = "V-FROZEN-2026-09-01",
        commit_hash: str = "auto",
    ):
        self.freeze_id = freeze_id
        self.freeze_date = PredictionWindow.FROZEN_DATE
        self._commit_hash = commit_hash
        self._predictions: List[Dict[str, Any]] = []
        self._verifications: List[Dict[str, Any]] = []
    
    @property
    def commit_hash(self) -> str:
        """获取当前提交的hash。"""
        if self._commit_hash == "auto":
            import subprocess
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--short", "HEAD"],
                    capture_output=True, text=True, check=True
                )
                return result.stdout.strip()
            except Exception:
                return "unknown"
        return self._commit_hash
    
    def create_snapshot(self, test_results: Dict[str, Any]) -> FreezeSnapshot:
        """创建冻结快照。"""
        snapshot = FreezeSnapshot(
            freeze_id=self.freeze_id,
            freeze_date=self.freeze_date,
            commit_hash=self.commit_hash,
            algorithm_version="v1.0",
            test_results=test_results,
            golden_dataset_path="dataset/golden_v1/golden_cases.json",
            ontology_version="v1",
        )
        return snapshot
    
    def submit_prediction(
        self,
        case_id: str,
        predicted_date: date,
        category: str,
        description: str,
        confidence: float,
        severity: int = 3,
    ) -> Dict[str, Any]:
        """提交预测（冻结后唯一允许的写入操作）。"""
        if predicted_date <= self.freeze_date:
            raise ValueError(f"预测日期必须在冻结日期之后: {predicted_date}")
        
        prediction = {
            "freeze_id": self.freeze_id,
            "case_id": case_id,
            "predicted_date": predicted_date.isoformat(),
            "category": category,
            "description": description,
            "confidence": confidence,
            "severity": severity,
            "submitted_at": datetime.now().isoformat(),
            "verified": False,
        }
        self._predictions.append(prediction)
        return prediction
    
    def verify_prediction(
        self,
        prediction_id: str,
        actual_date: date,
        actual_description: str,
        match_score: float,
    ) -> Dict[str, Any]:
        """验证预测（外部调用，不修改模型）。"""
        verification = {
            "prediction_id": prediction_id,
            "actual_date": actual_date.isoformat(),
            "actual_description": actual_description,
            "match_score": match_score,
            "verified_at": datetime.now().isoformat(),
        }
        self._verifications.append(verification)
        return verification
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取预测统计。"""
        return {
            "freeze_id": self.freeze_id,
            "freeze_date": self.freeze_date.isoformat(),
            "commit_hash": self.commit_hash,
            "total_predictions": len(self._predictions),
            "total_verifications": len(self._verifications),
            "avg_confidence": sum(p["confidence"] for p in self._predictions) / len(self._predictions) if self._predictions else 0,
        }


# ─── 导出 ──────────────────────────────────────────────────────────────────

__all__ = [
    "FreezeProtocol",
    "FreezeSnapshot",
    "PredictionWindow",
]
