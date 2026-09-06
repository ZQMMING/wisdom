# BOT-ZIPING Phase 2 最终裁决报告

**任务 ID**: T-ENGINE-BAZI-002 Phase 2 Deep Audit  
**执行者**: @bot-ziping  
**日期**: 2026-09-06  
**状态**: 🔴 NOT READY FOR FREEZE

---

## 执行摘要

完成 Rule-level 深度审计后，发现 **核心辨证引擎未实现**。证据数据库存在（1404+文件），但五个辨证代理的 `_load_classic_entries()` 全部为空实现，规则链完全缺失。

---

## 关键发现

### 1. 证据数据库状态 ✅ 存在

| 经典 | 文件数 | 质量 |
|------|--------|------|
| 渊海子平 | 117 | ✅ 结构化证据，含完整 provenance |
| 子平真诠 | ~130 | ⚠️ 部分存在 |
| 滴天髓 | 44 | ⚠️ 部分存在 |
| 穷通宝鉴 | 1233 | ✅ 调候数据完整 |
| 三命通会 | 10 | ❌ 太少 |

**证据示例** (`E-YHZP-001-001.json`):
```json
{
  "evidence_id": "E-YHZP-001-001",
  "original_text": "予尝观唐书所载...",
  "source_locator": {
    "classic": "yuan_hai_zi_ping",
    "chapter": "卷一·总论",
    "passage_id": "YHZP_0250",
    "source_hash": "d7c2..."
  },
  "authorization_level": "PARTIAL",
  "verification_status": "UNVERIFIED"
}
```

### 2. 辨证代理状态 🔴 空实现

```python
# bian/pzzq_agent.py:47-49
def _load_classic_entries(self) -> List[Dict]:
    """加载子平真诠原文数据"""
    return []  # ← 空实现！

# bian/yhzp_agent.py:47-49
def _load_classic_entries(self) -> List[Dict]:
    """加载渊海子平原文数据"""
    return []  # ← 空实现！

# bian/dts_agent.py:51-54
def _load_classic_entries(self) -> List[Dict]:
    """加载滴天髓原文数据"""
    # TODO: 实现具体加载逻辑
    return []  # ← 空实现！
```

**所有 5 个代理均返回空列表**。

### 3. 规则链状态 🔴 完全缺失

| 规则类型 | 应有逻辑 | 实际状态 |
|----------|----------|----------|
| 月令得令 | 判断日主是否得月令之气 | ❌ 未实现 |
| 通根判定 | 检查地支藏干是否含日主 | ⚠️ 数据结构存在，无应用 |
| 生扶统计 | 统计印比数量 | ❌ 未实现 |
| 格局判定 | 透干→成格/破格 | ❌ 未实现 |
| 用神选择 | 调候/扶抑/制化优先级 | ❌ 未实现 |
| 事件判断 | 大运流年作用→事件 | ❌ 未实现 |

---

## 架构审计结果

### BAZI → ZIPING 数据流

```
BaziEngine.compute() → BaziChart
    ↓
ContextAssembler.assemble_natal_context()
    ↓
NatalContext (day_master, pillars, ten_god_distribution)
    ↓
❓ BianAgent.extract_*_evidence() ← 空实现
    ↓
❓ RuleEngine.apply_rules() ← 完全缺失
    ↓
❓ AssertionEngine.judge() ← 完全缺失
```

**问题**: 数据流在 `BianAgent` 层断裂，后续层完全未实现。

---

## 逐项裁决

| 层级 | 状态 | 说明 |
|------|------|------|
| BAZI → ZIPING 接通 | 🟢 PASS | 数据流正常 |
| ZIPING 不重算 BAZI | 🟢 PASS | 边界清晰 |
| 十神单一权威源 | 🟢 PASS | 已修复 |
| 藏干表 | 🟢 PASS | 单一权威源 |
| 十二长生基础算法 | 🟢 PASS | 正确实现 |
| BAZI 强度边界 | 🟢 PASS | fail-closed 已实现 |
| **旺衰语义审计** | 🔴 **FAIL** | 规则链未实现 |
| **格局语义审计** | 🔴 **FAIL** | 规则链未实现 |
| **用神/调候/制化** | 🔴 **FAIL** | 无优先级链 |
| **十神组合语义** | 🔴 **FAIL** | 无语义映射 |
| **事件判断** | 🔴 **FAIL** | 完全缺失 |
| **五经 Evidence 权威性** | 🟡 **PARTIAL** | 数据存在但代理未连接 |
| `MODERATE` fallback | ✅ **FIXED** | 已改为 MISSING + fail-closed |

---

## 生产级「辨」层要求 vs 实际

### 应有规则链

```
经典原文
  ↓
规则抽取 (Rule Extraction)
  ↓
条件定义 (Condition Definition)
  ↓
Feature 映射 (Feature Mapping)
  ↓
Judgment 生成 (Judgment Generation)
  ↓
Assertion 输出 (Assertion Output)
  ↓
最终子平判断 (Final Judgment)
```

### 实际实现

```
经典原文 ✅ (证据数据库存在)
  ↓
规则抽取 ❌ (代理空实现)
  ↓
条件定义 ❌ (未实现)
  ↓
Feature 映射 ⚠️ (数据结构存在，无应用)
  ↓
Judgment 生成 ❌ (完全缺失)
  ↓
Assertion 输出 ❌ (完全缺失)
  ↓
最终子平判断 ❌ (无法生成)
```

**语义漂移**: 从「规则抽取」层开始，整条链断裂。

---

## ZIPING Freeze 裁决

### 裁决结论

**❌ 不建议 Freeze**

### 原因

1. **核心辨证引擎未实现**
   - 五个辨证代理的 `_load_classic_entries()` 全部返回空列表
   - 证据数据库存在但未被代理使用

2. **规则链完全缺失**
   - 无旺衰计算逻辑
   - 无格局判定逻辑
   - 无用药选择逻辑
   - 无事件判断逻辑

3. **无法进行 Rule-level provenance 追溯**
   - 证据数据存在（如 `E-YHZP-001-001.json`）
   - 但代理无法加载和引用这些证据
   - 无法建立 Evidence → Feature → Judgment → Assertion 的追溯链

---

## 必须完成的工作（P0）

### 1. 实现 `_load_classic_entries()`

```python
def _load_classic_entries(self) -> List[Dict]:
    """加载经典原文数据"""
    evidence_dir = self.classics_data_dir / self.CLASSIC_ID
    entries = []
    for json_file in evidence_dir.glob("*.json"):
        with open(json_file, 'r', encoding='utf-8') as f:
            entries.append(json.load(f))
    return entries
```

### 2. 实现基础规则链

```python
class WangShuaiRuleEngine:
    """旺衰规则引擎"""
    
    def judge_seasonal_support(self, chart: BaziChart) -> bool:
        """判断是否得令"""
        month_branch = chart.month_pillar.earthly_branch
        dm_element = STEM_ELEMENT[chart.day_master]
        branch_element = BRANCH_ELEMENT[month_branch]
        # 得令: 月支五行生助日主或同五行
        return branch_element == dm_element or \
               GENERATES.get(branch_element) == dm_element
    
    def judge_root_present(self, chart: BaziChart) -> bool:
        """判断是否有根"""
        for pillar in [chart.year_pillar, chart.month_pillar, 
                       chart.day_pillar, chart.hour_pillar]:
            hidden = BRANCH_HIDDEN_STEMS.get(pillar.earthly_branch, [])
            if chart.day_master in hidden:
                return True
        return False

class PatternRuleEngine:
    """格局规则引擎"""
    
    def determine_pattern(self, chart: BaziChart) -> str:
        """判定格局"""
        # 1. 检查特殊格局
        if self.is_congruent_pattern(chart):
            return "从格"
        if self.is_transformation_pattern(chart):
            return "化格"
        
        # 2. 检查建禄阳刃
        if chart.month_pillar.earthly_branch == ROAD_BRANCH.get(chart.day_master):
            return "建禄格"
        if chart.month_pillar.earthly_branch == ABSOLUTE_BRANCH.get(chart.day_master):
            return "阳刃格"
        
        # 3. 正格判定（需透干）
        # ...
```

### 3. 建立证据连接

```python
class BianAgent:
    def __init__(self, classics_data_dir: Path, evidence_output_dir: Path):
        self.classics_data_dir = classics_data_dir
        self.evidence_output_dir = evidence_output_dir
        self._entries = self._load_classic_entries()  # 加载证据
        self._build_passage_index()  # 建立索引
```

---

## 建议优先级

### 立即行动（P0）

1. ✅ 修复 `day_master_strength` fallback（已完成）
2. 🔴 实现 `_load_classic_entries()` 连接证据数据库
3. 🔴 实现基础旺衰规则（得令、通根）
4. 🔴 实现基础格局判定（正格、建禄、阳刃）

### 中期行动（P1）

1. 完善格局判定（从格、化格）
2. 实现用神选择逻辑
3. 建立优先级链（格局 > 调候 > 扶抑）

### 长期行动（P2）

1. 实现事件判断引擎
2. 补充《三命通会》证据
3. 完善证据验证流程

---

## 最终结论

**Phase 2 当前状态**: 基础框架完成，核心规则链未实现

** Freeze 条件**: 不满足

**下一步**: 完成 P0-1 到 P0-5 的规则链实现后，重新进行审计

---

**裁决者**: @bot-ziping  
**日期**: 2026-09-06  
**状态**: 🔴 NOT READY FOR FREEZE

---
*此报告基于 Rule-level 深度审计，证据数据库存在但辨证代理未连接，规则链完全缺失。*
