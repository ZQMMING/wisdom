# P0-1-C Fix Plan — Execution Roadmap

**任务**: 制定 P0-1-C 的具体修复路径
**执行者**: @bot-ziping
**日期**: 2026-09-07
**状态**: 待 BOT-MASTER 裁决后执行

---

## 一、当前代码问题（具体行号）

### 1.1 Ten Gods 重复计算

**位置**: `context_assembler.py:140, 146, 158, 265`

```python
# Line 140（年干十神）
stem_ten_god=compute_ten_god(chart.day_master, chart.year_pillar.heavenly_stem)

# Line 146（月干十神）
stem_ten_god=compute_ten_god(chart.day_master, chart.month_pillar.heavenly_stem)

# Line 152（日干十神）- 硬编码
stem_ten_god="DAY_MASTER"

# Line 158（时干十神）
stem_ten_god=compute_ten_god(chart.day_master, chart.hour_pillar.heavenly_stem)

# Line 265（大运十神）
stem_ten_god=compute_ten_god(natal.day_master, stem)
```

**问题**: BAZI 已计算十神关系，但 ContextAssembler 重新计算。

---

### 1.2 地支关系重复计算

**位置**: `context_assembler.py:165-186`

```python
branch_clashes = []
branch_combinations = []
branch_harms = []
branch_punishments = []
branch_three_combinations = []

for i, b1 in enumerate(branches):
    for j, b2 in enumerate(branches):
        if i >= j:
            continue
        pair = f"{b1}-{b2}"
        if BRANCH_CLASH.get(b1) == b2:           # ❌ 自己计算
            branch_clashes.append(pair)
        if BRANCH_COMBINATION.get(b1) == b2:    # ❌ 自己计算
            branch_combinations.append(pair)
        if BRANCH_HARM.get(b1) == b2:           # ❌ 自己计算
            branch_harms.append(pair)

for combo in set(THREE_COMBINATION.values()):  # ❌ 自己计算
    if all(b in branches for b in combo):
        branch_three_combinations.append("-".join(combo))
```

**问题**: BAZI Chart 已有 `branch_clash_map`, `branch_he_map`, `branch_harm_map`, `branch_sanhe_map`, `branch_sanxing_map`，但未使用。

---

### 1.3 大运第二套引擎（最严重）

**位置**: `context_assembler.py:218-313`

```python
def assemble_dayun_context(self, chart, natal: NatalContext, target_year: int) -> DaYunContext:
    # 自己计算大运 (不依赖chart.luck_pillars数量)  ← 注释明确说"不依赖"
    
    # 从月柱开始重新计算
    month_stem = natal.pillars[1].heavenly_stem
    month_branch = natal.pillars[1].earthly_branch
    
    # 计算12个大运
    da_yun_pillars = []
    for i in range(12):
        # ... 手动计算 stem/branch ...
        da_yun_pillars.append(DaYunPillar(
            stem_ten_god=compute_ten_god(natal.day_master, stem),  # ❌ 重算
        ))
```

**问题**: BAZI Chart 已有 `chart.luck_pillars` 和 `chart.start_age`，但 ContextAssembler 完全忽略，重新计算一遍。

---

### 1.4 流年干支重复计算

**位置**: `context_assembler.py:111-117, 318-319`

```python
def compute_year_pillar(year: int) -> tuple[str, str]:
    """计算流年干支 (1984甲子年基准)."""
    base_year = 1984
    offset = year - base_year
    stem_idx = offset % 10
    branch_idx = offset % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]

# Line 318
year_stem, year_branch = compute_year_pillar(target_year)  # ❌ 自己计算
year_stem_ten_god = compute_ten_god(natal.day_master, year_stem)  # ❌ 重算
```

**问题**: 流年干支是时间层确定性事实，不应由 ZIPING 计算。

---

### 1.5 交互关系计算

**位置**: `context_assembler.py:280-288, 324-361`

```python
# Natal × DaYun 交互
if current:
    for nb in natal_branches:
        if BRANCH_CLASH.get(current.earthly_branch) == nb:  # ❌ 自己计算
            natal_dayun_clashes.append(f"{current.earthly_branch}-{nb}")

# Natal × Year 交互
for nb in natal_branches:
    if BRANCH_CLASH.get(year_branch) == nb:  # ❌ 自己计算
        natal_year_clashes.append(f"{year_branch}-{nb}")
```

**问题**: 这些是派生 Context，需要确认归属。

---

## 二、修复策略（分层处理）

### 策略 A：BAZI 端扩展（最干净）

**原则**: BAZI 计算所有确定性事实，ZIPING 只消费。

#### Step 1: 扩展 Pillar 类

```python
# src/tongshu/engines/bazi_engine.py
@dataclass(frozen=True)
class Pillar:
    heavenly_stem: str
    earthly_branch: str
    stem_ten_god: str = ""  # ← 新增
    hidden_stems: list = field(default_factory=list)
    main_qi: str = ""
```

#### Step 2: 扩展 LuckPillar 类

```python
@dataclass(frozen=True)
class LuckPillar:
    index: int
    heavenly_stem: str
    earthly_branch: str
    stem_ten_god: str = ""  # ← 新增
    start_age: float
    end_age: float
    start_year: int
    end_year: int
    is_current: bool = False
```

#### Step 3: 修改 BaziEngine.compute()

```python
# 计算四柱十神
chart.year_pillar = Pillar(
    heavenly_stem=year_stem,
    earthly_branch=year_branch,
    stem_ten_god=ten_god(chart.day_master, year_stem),  # ← 补充
)
chart.month_pillar = Pillar(...)
chart.day_pillar = Pillar(stem_ten_god="DAY_MASTER")
chart.hour_pillar = Pillar(...)

# 计算大运十神
for i, luck in enumerate(chart.luck_pillars):
    luck.stem_ten_god = ten_god(chart.day_master, luck.heavenly_stem)  # ← 补充
```

#### Step 4: 修改 ContextAssembler

```python
# ❌ 删除
from tongshu.reasoning.bazi_ten_gods import ten_god as compute_ten_god
def compute_year_pillar(year): ...
BRANCH_CLASH = {...}
BRANCH_COMBINATION = {...}
BRANCH_HARM = {...}
THREE_COMBINATION = {...}

# ✅ 改为消费
pillar = NatalPillar(
    stem_ten_god=chart.year_pillar.stem_ten_god,  # ← 读取
)

branch_clashes = list(chart.branch_clash_map.keys())  # ← 读取
branch_combinations = list(chart.branch_he_map.keys())  # ← 读取

da_yun_pillars = []
for luck in chart.luck_pillars:
    da_yun_pillars.append(DaYunPillar(
        stem_ten_god=luck.stem_ten_god,  # ← 读取
    ))
```

---

### 策略 B：Temporal Engine 提供流年（备选）

如果 BOT-MASTER 裁决流年属于 Temporal Engine：

#### Step 1: 扩展 TemporalContext

```python
@dataclass(frozen=True)
class TemporalContext:
    target_year: int
    target_year_pillar: tuple[str, str] = ("", "")  # ← 新增
    target_year_stem_ten_god: str = ""  # ← 新增
```

#### Step 2: TimeEngine 计算流年

```python
def compute_temporal_context(self, birth_chart: BaziChart, target_year: int) -> TemporalContext:
    year_stem, year_branch = compute_year_pillar(target_year)  # ← 统一入口
    year_stem_ten_god = ten_god(birth_chart.day_master, year_stem)
    
    return TemporalContext(
        target_year=target_year,
        target_year_pillar=(year_stem, year_branch),  # ← 补充
        target_year_stem_ten_god=year_stem_ten_god,  # ← 补充
    )
```

#### Step 3: ContextAssembler 消费

```python
def assemble_year_context(self, natal: NatalContext, dayun: DaYunContext,
                           temporal: TemporalContext, target_year: int) -> YearContext:
    year_stem, year_branch = temporal.target_year_pillar  # ← 读取
    year_stem_ten_god = temporal.target_year_stem_ten_god  # ← 读取
```

---

### 策略 C：派生 Context 允许 ZIPING 计算（边界确认）

对于 Natal × DaYun × Year 的交互关系，需要明确归属：

```text
第一层：确定性关系（BAZI-owned）
  - 四柱本身的冲合害刑
  - 大运本身的干支和十神
  → BAZI 计算，ZIPING 消费

第二层：时间层关系（Temporal-owned）
  - 流年干支和十神
  → Temporal Engine 计算，ZIPING 消费

第三层：交互关系（ZIPING-owned）
  - Natal × DaYun 的冲合
  - Natal × Year 的冲合害
  - DaYun × Year 的冲合
  - 三层交互（三合局完成等）
  → ZIPING 可以计算（这是派生 Context）
```

---

## 三、具体修复步骤

### Phase 1: BAZI 端（BOT-BAZI 负责）

```text
1. 扩展 Pillar 类，添加 stem_ten_god 字段
2. 扩展 LuckPillar 类，添加 stem_ten_god 字段
3. 修改 BaziEngine.compute()，计算 pillar.stem_ten_god 和 luck.stem_ten_god
4. 运行 test_bazi_engine.py 验证
```

### Phase 2: Temporal Engine 端（BOT-TIME 负责）

```text
5. 扩展 TemporalContext 类，添加 target_year_pillar 和 target_year_stem_ten_god
6. 修改 TimeEngine.compute_temporal_context()，计算流年干支和十神
7. 运行 test_time_engine.py 验证
```

### Phase 3: ZIPING 端（BOT-ZIPING 负责）

```text
8. 删除 compute_ten_god() 函数和 import
9. 删除 compute_year_pillar() 函数
10. 删除 BRANCH_CLASH / BRANCH_COMBINATION / BRANCH_HARM / THREE_COMBINATION 表
11. 修改 assemble_natal_context()，消费 chart 字段
12. 修改 assemble_dayun_context()，消费 chart.luck_pillars
13. 修改 assemble_year_context()，消费 temporal_context 字段
14. 保留交互关系计算（作为派生 Context）
15. 运行 test_phase3_p0.py 验证
```

---

## 四、需要 BOT-MASTER 裁决的问题

### 问题 1：流年干支归属

```text
选项 A: TimeEngine 计算并返回到 TemporalContext
选项 B: BAZI Engine 计算并返回到 BaziChart
选项 C: 允许 ZIPING 保留 compute_year_pillar()（纯数学问题）
```

### 问题 2：交互关系归属

```text
选项 A: BAZI 计算所有交互关系（Natal×DaYun×Year）
选项 B: Temporal Engine 计算时间层交互
选项 C: ZIPING 计算派生交互（允许）
```

### 问题 3：修复顺序

```text
选项 A: BAZI → Temporal → ZIPING（顺序执行）
选项 B: BAZI + Temporal 并行 → ZIPING（并行执行）
```

---

## 五、禁止事项

```text
❌ 不得修改 Judgment 层算法（旺衰/格局/用神/十神语义/事件判断）
❌ 不得修改 Golden Dataset 期望值
❌ 不得修改 BAZI Engine 的确定性计算逻辑（只补充字段）
❌ 不得引入新的确定性计算入口
❌ 不得将 day_master_strength 塞入 BaziChart
❌ 不得修改 BAZI 的 Ten Gods 计算算法
```

---

## 六、验收标准

```text
✅ test_phase3_p0.py 3/3 PASS
✅ test_bazi_engine.py 全部 PASS
✅ ContextAssembler.assemble() 不报错
✅ ContextAssembler 不调用 compute_ten_god()
✅ ContextAssembler 不调用 compute_year_pillar()
✅ ContextAssembler 不计算地支关系（BRANCH_CLASH/HARM/COMBINATION）
✅ ContextAssembler 消费 chart.luck_pillars 而不是自己计算大运
✅ Git 边界检查通过（BAZI 改动在 BAZI 域，ZIPING 改动在 ZIPING 域）
```

---

## 七、等待 BOT-MASTER 裁决

**当前状态**: P0-1-C Fix Plan 已定义，等待 BOT-MASTER 对以下问题裁决：
1. 流年干支归属
2. 交互关系归属
3. 修复顺序

**一旦裁决完成，立即开始执行 Phase 1（BAZI 端扩展）。**
