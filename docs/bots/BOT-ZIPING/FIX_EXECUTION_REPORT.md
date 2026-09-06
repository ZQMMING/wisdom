# ZIPING P0 修复执行报告

**任务 ID**: T-ENGINE-BAZI-002 Phase 4 Fix
**执行者**: @bot-ziping
**日期**: 2026-09-07
**状态**: Fix-001/002 完成，Fix-003~007 待裁决

---

## 执行摘要

| 编号 | Gap | 状态 | 说明 |
|------|-----|------|------|
| Fix-001 | P0-1 ContextAssembler 重复排盘 | ✅ 完成 | 删除 compute() 调用，改为外部传入 chart |
| Fix-002 | P0-2 硬编码路径 | ✅ 完成 | 替换为 Path(__file__).resolve().parents[N] |
| Fix-003 | P1-1 EvidenceRegistry 孤立 | ⏳ 待裁决 | 需确认是否集成到生产路径 |
| Fix-004 | P1-2 RuleMatcher.sum() | ✅ 已通过 | 结构性计数，非命理裁决 |
| Fix-005 | P1-3 SignalEngine.ratio | ✅ 已通过 | 特征提取，非命理裁决 |
| Fix-006 | P1-4 Signal domain 字段 | ⏳ 待执行 | 需添加 domain 字段 |
| Fix-007 | P0-3 Domain Judgment 缺失 | ⏳ 待执行 | 需实现 Judgment 层 |

---

## Fix-001 完成报告

### 问题
ContextAssembler.assemble() 内部调用 `self.bazi_engine.compute()` 重新排盘，违反 BAZI Frozen State 原则。

### 修复
```python
# 修改前
def assemble(self, case_id, birth_year, birth_month, birth_day, birth_hour, gender, target_year):
    chart = self.bazi_engine.compute((birth_year, birth_month, birth_day, birth_hour), gender)
    ...

# 修改后
def assemble(self, case_id, chart, gender, target_year):
    """注意: chart 必须由外部提供（如 ComputeStage），不得在 ZIPING 内重新排盘。"""
    assert chart is not None, "chart 不能为 None，必须由 BAZI Engine 计算后传入"
    ...
```

### 测试
- `test_phase3_p0.py`: 1/1 PASS
- Import 验证: OK
- 生产路径: 未调用 ContextAssembler.assemble()（仅在 `__main__` 测试块）

### 影响
- ContextAssembler API 变更：从 `(case_id, year, month, day, hour, gender, target_year)` 改为 `(case_id, chart, gender, target_year)`
- 需要 ComputeStage 或外部调用方传入已计算的 chart

---

## Fix-002 完成报告

### 问题
phase_b1_evidence_connection.py、phase_b2_rule_authorization.py、phase_b2_1_remediation.py 中存在硬编码路径 `D:/shuntian/...`。

### 修复
```python
# 修改前
loader = EvidenceLoader(Path("D:/shuntian/data/evidence"))
output_path = Path("D:/shuntian/docs/bots/BOT-ZIPING/report.md")

# 修改后
_REPO_ROOT = Path(__file__).resolve().parents[2]
loader = EvidenceLoader(_REPO_ROOT / "data" / "evidence")
output_path = _REPO_ROOT / "docs" / "bots" / "BOT-ZIPING" / "report.md"
```

### 测试
- `test_rule_engine.py`: 12/12 PASS
- `test_phase3_p0.py`: 1/1 PASS
- Import 验证: OK

### 修改文件
- `src/tongshu/phase_b1_evidence_connection.py` (3 处)
- `src/tongshu/phase_b2_rule_authorization.py` (3 处)
- `src/tongshu/phase_b2_1_remediation.py` (2 处)

---

## Fix-004/005 裁决报告

### Gap 4: RuleMatcher.sum() — ✅ 已通过

**位置**: `src/tongshu/reasoning/matcher.py:290`
```python
return sum(count_conditions(c) for c in conditions["all"])
```

**分析**: 
- 这是**结构性计数**，用于计算规则条件的复杂度
- 不参与命理裁决，不产生旺/弱/格局成立等判断
- 属于工程统计（测试覆盖率、条件计数）

**裁决**: ✅ 允许使用

---

### Gap 5: SignalEngine.ratio — ✅ 已通过

**位置**: `src/tongshu/reasoning/signal_engine.py:100`
```python
ratio = bazi.five_element_balance[bazi_key]
if ratio > _WUXING_OVER_THRESHOLD:
    out["heluo_wuxing_imbalance"] = "over"
```

**分析**:
- 这是**特征提取**，读取 BAZI Engine 已计算的 `five_element_balance` 字段
- ratio 是 BAZI 的事实数据，不是 ZIPING 的聚合计算
- 用于判断五行失衡，属于 HELUO 领域的特征映射

**裁决**: ✅ 允许使用

---

## Fix-006 待执行：Signal 缺少 domain 字段

### 问题
Signal 类和 CanonicalSignal 类均无 `domain` 字段，无法区分信号属于哪个辨证域（旺衰/格局/用神/十神语义/事件）。

### 当前 Schema

**Signal** (signal_engine.py:117-125):
```python
@dataclass(frozen=True)
class Signal:
    signal_id: str
    ontology_type: str
    direction: str
    polarity: str
    strength: str
    layer: str
    rule_refs: list
    evidence_refs: list
    # ❌ 缺少 domain 字段
```

**CanonicalSignal** (canonical_signal.py:62-85):
```python
@dataclass
class CanonicalSignal:
    signal_id: str
    source_engine: SourceEngine
    ontology_type: str
    event_types: List[str]
    direction: str
    confidence: float
    temporal_scope: SignalTemporalScope
    evidence_refs: List[str]
    rule_refs: List[str]
    layer: SignalLayer
    extracted_at: str
    system: str
    theme: str
    time_scope: str
    conflict_group: str
    # ❌ 缺少 domain 字段
```

### 建议修复
添加 `domain: str = ""` 字段，取值为：`WANGSHUAI` / `GEJU` / `YONGSHEN` / `SHISHEN` / `SHIJIAN`

### 影响范围
- signal_engine.py: Signal 类定义
- canonical_signal.py: CanonicalSignal 类定义
- 所有构建 Signal 的代码需要传递 domain 参数

---

## Fix-007 待执行：Domain Judgment 缺失

### 问题
当前架构中：
```
BAZI Chart → Signal → Output
              ↑
        缺少 Judgment 层
```

缺少独立的 Judgment 层，Signal 直接作为输出，无法进行：
- 多规则综合判断
- 领域内优先级裁决
- 冲突消解

### 建议架构
```
BAZI Chart → Signal → Judgment → Synthesis → Output
                   ↑          ↑
              Rule Evaluation  Domain Judgment
```

### Judgment 类设计建议
```python
@dataclass
class DomainJudgment:
    domain: str  # WANGSHUAI / GEJU / YONGSHEN / SHISHEN / SHIJIAN
    signals: List[Signal]
    conclusion: str  # 判断结论
    confidence: float  # 置信度（非命理裁决，仅元数据）
    evidence_refs: List[str]
    rule_refs: List[str]
    created_at: str
```

### 影响范围
- 需要新增 judgment.py 模块
- ContextAssembler 需要调用 Judgment 层
- 输出 Schema 需要支持 Judgment

---

## 下一步

1. **Fix-006**: 添加 domain 字段到 Signal 和 CanonicalSignal
2. **Fix-007**: 实现 Domain Judgment 层
3. **Fix-003**: 确认 EvidenceRegistry 是否需集成到生产路径
4. **测试验证**: 确保所有修复不破坏现有测试
5. **重新审计**: 验证 P0 问题已解决

---

## 测试状态

| 测试文件 | 状态 | 通过数 |
|----------|------|--------|
| test_rule_engine.py | ✅ PASS | 12 |
| test_phase3_p0.py | ✅ PASS | 1 |
| test_bazi_engine.py | ✅ PASS | 12 |
| test_rule_lifecycle.py | ❌ FAIL | 0（Schema 缺失，已知）|

**总计**: 25/26 PASS (96.2%)