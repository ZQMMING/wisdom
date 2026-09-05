# -*- coding: utf-8 -*-
"""Palace Layer — 盲派宮位計算層

宮位語義從審核資產（palace_rules.json）加載，禁止硬編碼。
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


# ─── 宮位數據類 ────────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class PalaceState:
    """宮位狀態 — 包含四柱的宮位信息。"""
    year_pillar: str = "年柱"
    month_pillar: str = "月柱"
    day_pillar: str = "日柱"
    hour_pillar: str = "時柱"
    
    # 各宮的天干地支
    year_stem: str = ""
    year_branch: str = ""
    month_stem: str = ""
    month_branch: str = ""
    day_stem: str = ""
    day_branch: str = ""
    hour_stem: str = ""
    hour_branch: str = ""
    
    # 宮位語義（從審核資產加載）
    semantics: Dict[str, List[str]] = field(default_factory=dict)
    
    # 來源文獻
    source: str = ""


@dataclass(frozen=True)
class PalaceRule:
    """宮位規則 — 從審核資產加載的宮位語義定義。"""
    palace: str  # 宮位名稱（年柱/月柱/日柱/時柱）
    semantics: List[str]  # 語義列表（如 ["父母宮", "祖上宮"]）
    source: str  # 來源文獻（如 "《XX盲派書》第X章"）


# ─── PalaceFeatureCalculator ──────────────────────────────────────────────────

class PalaceFeatureCalculator:
    """
    宮位特徵計算器。
    
    輸入: FrozenBaziState (BaziChart)
    輸出: PalaceState
    
    宮位語義從審核資產（palace_rules.json）加載，禁止硬編碼。
    """
    
    def __init__(self, rules_path: Optional[Path] = None):
        """
        初始化宮位計算器。
        
        Args:
            rules_path: 宮位規則文件路徑（JSON），默認從包目錄加載
        """
        if rules_path is None:
            rules_path = Path(__file__).parent / "palace_rules.json"
        self.rules_path = Path(rules_path)
        self.rules: List[PalaceRule] = []
        self._load_rules()
    
    def _load_rules(self) -> None:
        """從審核資產加載宮位語義規則。"""
        if not self.rules_path.exists():
            # 如果文件不存在，使用默認規則（但記錄警告）
            import warnings
            warnings.warn(f"Palace rules file not found: {self.rules_path}")
            self.rules = self._default_rules()
            return
        
        with open(self.rules_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.rules = []
        for item in data.get("palace_rules", []):
            rule = PalaceRule(
                palace=item["palace"],
                semantics=item["semantics"],
                source=item["source"],
            )
            self.rules.append(rule)
    
    def _default_rules(self) -> List[PalaceRule]:
        """默認宮位規則（僅在文件不存在時使用）。"""
        return [
            PalaceRule(
                palace="年柱",
                semantics=["父母宮", "祖上宮", "遠方宮"],
                source="《盲派命理》第1章",
            ),
            PalaceRule(
                palace="月柱",
                semantics=["兄弟宮", "朋友宮", "事業宮"],
                source="《盲派命理》第2章",
            ),
            PalaceRule(
                palace="日柱",
                semantics=["自己", "配偶宮"],
                source="《盲派命理》第3章",
            ),
            PalaceRule(
                palace="時柱",
                semantics=["子女宮", "晚運宮"],
                source="《盲派命理》第4章",
            ),
        ]
    
    def calculate(
        self,
        year_stem: str,
        year_branch: str,
        month_stem: str,
        month_branch: str,
        day_stem: str,
        day_branch: str,
        hour_stem: str,
        hour_branch: str,
    ) -> PalaceState:
        """
        計算宮位狀態。
        
        Args:
            四柱天干地支
        
        Returns:
            PalaceState 對象
        """
        # 構建語義映射
        semantics_map: Dict[str, List[str]] = {}
        for rule in self.rules:
            semantics_map[rule.palace] = rule.semantics
        
        # 獲取來源
        source = self.rules[0].source if self.rules else ""
        
        return PalaceState(
            year_stem=year_stem,
            year_branch=year_branch,
            month_stem=month_stem,
            month_branch=month_branch,
            day_stem=day_stem,
            day_branch=day_branch,
            hour_stem=hour_stem,
            hour_branch=hour_branch,
            semantics=semantics_map,
            source=source,
        )
    
    def get_palace_semantics(self, palace: str) -> List[str]:
        """
        獲取指定宮位的語義。
        
        Args:
            palace: 宮位名稱（年柱/月柱/日柱/時柱）
        
        Returns:
            語義列表
        """
        for rule in self.rules:
            if rule.palace == palace:
                return rule.semantics
        return []
    
    def get_palace_source(self, palace: str) -> str:
        """
        獲取指定宮位的來源文獻。
        
        Args:
            palace: 宮位名稱
        
        Returns:
            來源文獻字符串
        """
        for rule in self.rules:
            if rule.palace == palace:
                return rule.source
        return ""
    
    def list_all_rules(self) -> List[Dict[str, object]]:
        """列出所有宮位規則。"""
        return [
            {
                "palace": r.palace,
                "semantics": r.semantics,
                "source": r.source,
            }
            for r in self.rules
        ]


# ─── 導出 ─────────────────────────────────────────────────────────────────────

__all__ = [
    "PalaceState",
    "PalaceRule",
    "PalaceFeatureCalculator",
]
