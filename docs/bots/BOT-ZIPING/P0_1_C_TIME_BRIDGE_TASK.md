# P0-1-C-TIME-BRIDGE: Phase 2 Temporal Engine Task

**Issue**: BOT-MASTER 裁决 - P0-1-C 仍 BLOCKED  
**原因**: `chart.year_pillar` 是 Natal Year Pillar，不是 Target Year Pillar  
**Owner**: BOT-TIME  
**Priority**: P0 (阻塞 ZIPING Phase 4 完整通过)

---

## 问题诊断

### 当前错误架构

```
target_year = 2026
     ↓
chart.year_pillar (癸亥 - 本命年柱) ← 错误! 这是出生年的干支
     ↓
ZIPING YearContext
     ↓
year_stem="GUI", year_branch="HAI"  ← 应该是 丙午
```

### 正确架构

```
target_year = 2026
     ↓
Temporal Engine (BOT-TIME)
     ↓
TemporalContext.target_year_pillar = 丙午  ← 流年柱
TemporalContext.target_year_stem_ten_god = ...  ← 对日主的十神
     ↓
ZIPING ContextAssembler
     ↓
YearContext(year_stem="BING", year_branch="WU", ...)
```

---

## 任务清单

### 1. Temporal Engine 实现

**文件**: `src/tongshu/engines/temporal_engine.py` (新建或完善)

**职责**:
- 计算目标年份的流年干支 (`target_year_pillar`)
- 计算流年天干对日主的十神 (`target_year_stem_ten_god`)
- 提供 TemporalContext 所有 temporal 事实

**API**:
```python
class TimeEngine:
    def compute_temporal_context(
        self,
        birth_year: int,
        target_year: int,
        natal_day_master: str
    ) -> TemporalContext:
        """计算 temporal context，包含 target_year_pillar"""
```

**关键方法**:
```python
def compute_year_pillar(self, year: int) -> Pillar:
    """根据年份计算干支（甲子循环）"""
    # 使用标准甲子循环算法
    # base = 4 (公元4年为甲子年)
    # offset = (year - 4) % 60
    # stem = STEMS[offset % 10]
    # branch = BRANCHES[offset % 12]

def compute_year_stem_ten_god(self, day_master: str, year_stem: str) -> str:
    """计算流年天干对日主的十神"""
    # 使用 BAZI 的 ten_god 函数
    from ..reasoning.bazi_ten_gods import ten_god
    return ten_god(day_master, year_stem)
```

### 2. TemporalContext Contract 更新

**文件**: `src/tongshu/reasoning/temporal_context_contract.py`

**新增字段**:
```python
@dataclass(frozen=True)
class TemporalContext:
    # ... existing fields ...
    
    # NEW: Target Year Pillar (流年柱)
    target_year_pillar: Optional[Pillar] = None
    target_year_stem_ten_god: Optional[str] = None
```

### 3. ContextAssembler 更新

**文件**: `src/tongshu/reasoning/context_assembler.py`

**修改 assemble_year_context**:
```python
def assemble_year_context(
    self, 
    natal: NatalContext, 
    dayun: DaYunContext,
    temporal_context: TemporalContext  # 新参数
) -> YearContext:
    """组装YearContext - 流年干支由 TemporalContext 提供"""
    
    # P0-1-C: 从 TemporalContext 消费目标流年
    year_pillar = temporal_context.target_year_pillar
    
    if year_pillar is None:
        raise ValueError(
            "TemporalContext.target_year_pillar 不能为 None。\n"
            "必须由 Temporal Engine 计算后传入。"
        )
    
    year_stem = year_pillar.heavenly_stem
    year_branch = year_pillar.earthly_branch
    year_stem_ten_god = year_pillar.stem_ten_god or temporal_context.target_year_stem_ten_god
```

**修改 assemble()**:
```python
def assemble(
    self, 
    case_id: str, 
    chart,  # Frozen BAZI Chart
    temporal_context: TemporalContext,  # 新参数
    gender: str,
    target_year: int
) -> TemporalContext:
    """组装完整 TemporalContext"""
    
    natal = self.assemble_natal_context(chart, birth_year, gender)
    dayun = self.assemble_dayun_context(chart, natal, target_year)
    year = self.assemble_year_context(natal, dayun, temporal_context)
    
    # ... merge into TemporalContext ...
```

### 4. 测试更新

**新增测试**: `tests/test_temporal_engine.py`

```python
def test_compute_year_pillar():
    """测试流年干支计算"""
    engine = TimeEngine()
    
    # 2026 年应该是 丙午
    pillar = engine.compute_year_pillar(2026)
    assert pillar.heavenly_stem == "BING"
    assert pillar.earthly_branch == "WU"
    
    # 2024 年应该是 甲辰
    pillar = engine.compute_year_pillar(2024)
    assert pillar.heavenly_stem == "JIA"
    assert pillar.earthly_branch == "CHEN"
```

**更新负向测试**: `tests/test_p0_1c_negative.py`

```python
def test_temporal_context_required():
    """测试 TemporalContext 必须提供 target_year_pillar"""
    # 如果没有 temporal_context，应该报错
    assembler = ContextAssembler()
    # ... test that temporal_context is required
```

---

## 架构约束 (BOT-MASTER 明确)

### 允许的行为

```python
# BAZI 计算确定性事实 → ZIPING 消费
chart.luck_pillars  →  ZIPING 消费
chart.branch_clash_map  →  ZIPING 消费
chart.year_pillar  →  ZIPING 消费 (仅用于 Natal 四柱)
```

### 禁止的行为

```python
# ZIPING 重新计算 BAZI 拥有的确定性事实
base_year = 1984
offset = (target_year - base_year) % 60  # ❌ 禁止
ten_god(day_master, year_stem)  # ❌ 在 Year context 中禁止
```

### 正确边界

```
BAZI Frozen Chart:
├── natal.year_pillar      ← 本命年柱 (出生年)
├── natal.month_pillar     ← 月柱
├── natal.day_pillar       ← 日柱
├── natal.hour_pillar      ← 时柱
├── luck_pillars[]         ← 大运列表
└── branch_*_maps          ← 地支关系

Temporal Engine (BOT-TIME):
├── compute_year_pillar(year)  ← 流年柱 (目标年)
└── compute_year_ten_god(day_master, year_stem)

ZIPING ContextAssembler:
├── consume natal.*          ← 本命信息
├── consume luck_pillars     ← 大运信息
├── consume TemporalContext  ← 流年信息 (NEW!)
└── NO re-calculation        ← 不重新计算
```

---

## 验收标准

### 功能测试

```bash
python -m pytest tests/test_temporal_engine.py -v
python -m pytest tests/test_p0_1c_negative.py -v
python -m pytest tests/test_bazi_engine.py tests/test_phase3_p0.py tests/test_rule_engine.py -v --tb=short
```

预期: 所有测试 PASS

### 负向测试 (防止 regression)

```python
# 禁止的模式
assert "base_year = 1984" not in source
assert "% 60" not in source
assert "stem_idx = offset" not in source

# 必须消费的字段
assert "temporal_context.target_year_pillar" in source
assert "ValueError" in source  # fail-closed
```

### 边界验证

| 输入 | 期望输出 |
|------|----------|
| `target_year=2026` | `year_stem="BING"`, `year_branch="WU"` |
| `target_year=2024` | `year_stem="JIA"`, `year_branch="CHEN"` |
| `target_year_pillar=None` | `ValueError` (fail-closed) |
| 无 `temporal_context` 参数 | `TypeError` (签名错误) |

---

## 依赖关系

### 前置条件 (已完成)

- [x] P0-1-C-FIX-2: 删除 ZIPING deterministic relation tables
- [x] P0-1-C-FIX-3: Year pillar fail-closed boundary
- [x] BAZI Pillar.stem_ten_god (Phase 1)
- [x] ZIPING 消费 BAZI 字段 (Phase 3)

### 本任务依赖

- [x] TemporalContext contract 已定义基础结构
- [ ] Temporal Engine 实现 (本任务)
- [ ] ContextAssembler 更新消费 TemporalContext
- [ ] 测试更新

### 后续任务 (P0-2)

- [ ] WANGSHUAIJudgment 完整算法
- [ ] GEJUJudgment 完整算法
- [ ] YONGSHENJudgment 完整算法

---

## 时间预估

- Temporal Engine 实现: 2-3 hours
- Contract 更新: 30 minutes
- ContextAssembler 更新: 1 hour
- 测试编写与验证: 1 hour
- **总计**: ~5 hours

---

## 备注

BOT-MASTER 明确指出:

> "不重新计算 ≠ 消费了正确的 Canonical Fact"

当前 ZIPING 消费的是 `chart.year_pillar` (本命年柱)，但需要的是 `target_year` 对应的流年柱。这两个是**完全不同**的事实。

Phase 2 的核心任务是提供正确的 **Temporal Fact Supply Chain**:

```
target_year → Temporal Engine → TemporalContext.target_year_pillar → ZIPING
```

ZIPING 不再需要知道如何计算流年干支，只需要从 TemporalContext 消费。
