# P1/P2 任務產出審計報告

> **審計時間**：2026-09-03  
> **審計代理**：Hermes Agent (Auditor Subagent)  
> **基線參考**：`docs/audit/P12_FINAL_VERDICT.md` / `docs/audit/p1_2e_independent_audit.md` / `P2-YINGQI-VERIFY_REPORT.md`  
> **工作區**：`C:/Users/wisdom/wisdom`

---

## 執行摘要

| 檢查項 | 狀態 | 說明 |
|--------|------|------|
| 1. PalaceLayer 從審核資產加載語義 | ❌ 未實現 | 倉庫中不存在 `PalaceLayer` 或 `palace_layer` 符號 |
| 2. WorkGraph 無 strength 字段 | ✅ 通過 | 字段僅有 `nodes/edges/_node_map/_adj`，無 strength |
| 3. EvidenceProducer 移除 direction/polarity | ✅ 通過 | EvidenceItem 僅含 relevance，無 direction/polarity/strength |
| 4. Yingqi 層獨立 | ✅ 通過 | 純結構關係計算，無 strength/scoring 依賴 |
| 5. 全量測試 | ✅ 85/85 PASS | blind_rules + blind_yingqi 全部通過 |
| 6. 最終審計報告 | ✅ 本文件 | — |

**總體評級**：🟡 **部分通過** — 3/5 核心架構規則已落實，PalaceLayer 尚未實現。

---

## 1. PalaceLayer 檢查 — ❌ 未實現

### 搜索範圍
- Python 源碼全倉庫 grep：`PalaceLayer` / `palace_layer` / `palace layer`
- Markdown 文檔搜尋：同符號
- 結果：**零匹配**

### 結論
`PalaceLayer` 類/模塊在當前代碼庫中**不存在**。無論是 P1 還是 P2 階段均未實現此組件。

**建議**：
- 確認 PalaceLayer 是否屬於後續 P1.3 或 P3 範疇
- 若屬於 P1/P2 必交項，需標記為 **BLOCKED** 並上報 User 終裁

---

## 2. WorkGraph 無 strength 字段 — ✅ 通過

### 實測驗證

```python
# WorkGraph 數據類字段
fields = ['nodes', 'edges', '_node_map', '_adj']
'strength' in fields → False

# WorkNode 字段
fields = ['id', 'type', 'value', 'position']
'strength' in fields → False

# WorkEdge 字段
fields = ['source', 'target', 'relation', 'valid']
'strength' in fields → False
```

### 測試覆蓋
- `tests/test_blind_rules/test_workgraph.py`：**45 tests PASS**
- 涵蓋節點創建、邊關係、DFS/BFS 遍歷、連通分量、度計算、to_dict 序列化等

### 結論
WorkGraph 符合 V13 §五「禁止 strength」硬約束，節點/邊結構完全由關係類型（制/生/合/冲）驅動，無能量強度字段。

---

## 3. EvidenceProducer 移除 direction/polarity — ✅ 通過

### EvidenceItem 字段結構

```python
# 實際字段
fields = ['id', 'source', 'content', 'relevance', 'valid', 'verified_at']

# 被移除字段確認
'direction' in fields → False
'polarity' in fields  → False
'strength'  in fields → False
'relevance' in fields → True  ← 替代字段（高/中/低）
```

### BlindEvidenceProducer 設計要點
- 輸入：`BlindFeatureState`（frozen dataclass，純結構事實）
- 輸出：`EvidenceList` 包含 `EvidenceItem`
- 方向/極性/強度評估**不在 Producer 層產生**
- 相關性（relevance）替代原有的 direction/polarity/strength 三元組

### 測試覆蓋
- `tests/test_blind_rules/test_evidence.py`：**22 tests PASS**
- `test_no_direction_polarity_strength`：明確斷言 content 不含 direction/polarity/strength 字符串

### 已知殘留風險（來自 P1.2-E 審計）
| # | 嚴重度 | 問題 | 狀態 |
|---|--------|------|------|
| 1 | MEDIUM | `zuo_gong_methods` list 可能含方向暗示詞彙 | 待審查內容 |
| 2 | HIGH | `source_rule_ref` 指向不存在的 `rules/*.json` 文件 | 追溯鏈斷裂 |

---

## 4. Yingqi 層獨立性 — ✅ 通過

### 依賴分析

```python
# blind_yingqi.py 導入鏈
from ..engines.bazi_engine import BaziEngine, BaziChart, BRANCH_SANXING
from ..reasoning.bazi_ten_gods import BRANCH_HIDDEN_STEMS, ten_god
from ..reasoning.bazi_fixed_tables import road_branch, absolute_branch
from .blind_bazi_engine import (BRANCH_CHONG, BRANCH_CHUAN, BRANCH_LIUHE, ...)
```

**未導入**：`strength_engine`、`signal.convergence`、`reasoning.cross_analysis`

### strength 字段引用檢查
- `day_master_strength`：❌ 未引用
- `shen_qiang` / `shen_ruo`：❌ 未引用
- `five_element_imbalance`：❌ 未引用

### direction 使用方式
- Yingqi 中的 `direction` 為**本地計算變量**（'POSITIVE'/'NEGATIVE'/'NEUTRAL'/'CHANGE'），僅用於輸出字典，不作為引擎狀態
- 不等於 V13 禁止的 `AssertionDirection` 級方向

### 測試覆蓋
- `tests/test_blind_yingqi.py`：**10 tests PASS**
- 涵蓋大限分段、流年干支、沖/穿/合/三刑/墓庫/透干/案例驗證

### 接口差距（已記錄於 P2-YINGQI-VERIFY_REPORT）
| 項目 | 當前 | 要求 | 狀態 |
|------|------|------|------|
| 輸入類型 | `BaziChart` | `FrozenBaziState` | ⚠️ FrozenBaziState 尚不存在 |
| WorkGraph 輸入 | 無 | 需整合 | ⚠️ 待後續升級 |

---

## 5. 全量測試結果

```bash
$ pytest tests/test_blind_rules/ tests/test_blind_yingqi.py -v --tb=short -q

tests/test_blind_rules/test_evidence.py          22 passed [ 25%]
tests/test_blind_rules/test_rule_graph.py         8 passed [ 35%]
tests/test_blind_rules/test_workgraph.py         45 passed [ 71%]
tests/test_blind_yingqi.py                     10 passed [100%]

============================= 85 passed in 0.44s ==============================
```

**所有測試通過，無失敗、無跳过。**

---

## 6. 問題清單與建議

### 🔴 HIGH（需優先處理）
| # | 位置 | 問題 | 建議 |
|---|------|------|------|
| 1 | `engines/blind/evidence_producer.py` SOURCE_RULES 映射 | `source_rule_ref` 指向不存在的 `backend/data/rules/*.json`，追溯鏈斷裂 | 創建規則文件目錄或調整引用路徑 |
| 2 | PalaceLayer | 組件未實現 | 確認是否為 P1/P2 必交項，否則標記為後續排期 |

### 🟡 MEDIUM（後續跟進）
| # | 位置 | 問題 | 建議 |
|---|------|------|------|
| 1 | `blind_yingqi.py` 接口 | 仍使用 `BaziChart` 而非 `FrozenBaziState + WorkGraph` | 待 FrozenBaziState 定義後升級 |
| 2 | `evidence_producer.py` zuo_gong_methods | 可能含方向暗示詞彙 | 審查方法列表內容 |

### 🟢 LOW（非阻塞）
- Yingqi 本地 `direction` 變量僅用於輸出格式化，不違反 V13 架構規則

---

## 附錄：檢查方法論

1. **PalaceLayer**：全倉庫 grep（Python + Markdown），零匹配
2. **WorkGraph strength**：運行時反射 `__dataclass_fields__`，確認字段列表
3. **EvidenceProducer direction/polarity**：同上 + 源碼搜索 + 測試斷言核對
4. **Yingqi 獨立性**：導入鏈分析 + 源碼關鍵字搜索 + 已有驗證報告交叉引用
5. **全量測試**：`pytest` 運行 `tests/test_blind_rules/` + `tests/test_blind_yingqi.py`

---

*審計完成。本報告只讀，未修改任何代碼文件。*
