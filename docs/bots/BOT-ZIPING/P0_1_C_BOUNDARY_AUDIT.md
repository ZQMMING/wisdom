# P0-1-C 边界审计报告

**任务**: ContextAssembler 不得重新计算 BAZI-owned deterministic facts
**执行者**: @bot-ziping
**日期**: 2026-09-07
**状态**: 🔴 FAIL — 发现 4 类边界违规

---

## 问题总览

| # | 位置 | 类型 | 问题描述 |
|---|------|------|----------|
| 1 | context_assembler.py:37 | Import | ZIPING 有自己的 `ten_god` 计算入口 |
| 2 | context_assembler.py:111 | 函数 | ZIPING 自己计算 `compute_year_pillar()` |
| 3 | context_assembler.py:140,146,158 | 调用 | NatalContext 重新计算 `stem_ten_god` |
| 4 | context_assembler.py:165-186 | 计算 | NatalContext 重新计算地支关系 |
| 5 | context_assembler.py:218-313 | 函数 | DaYunContext 自己计算大运（第二套 DaYun Engine） |
| 6 | context_assembler.py:265 | 调用 | 大运十神重新计算 |
| 7 | context_assembler.py:318-319 | 调用 | YearContext 重新计算流年 + 十神 |
| 8 | context_assembler.py:330-361 | 计算 | YearContext 重新计算交互关系 |

---

## 问题 1-3：Ten Gods 重复计算

### 当前代码

```python
# context_assembler.py:37
from tongshu.reasoning.bazi_ten_gods import ten_god as compute_ten_god

# context_assembler.py:140,146,158
pillar = NatalPillar(
    position="YEAR",
    heavenly_stem=chart.year_pillar.heavenly_stem,
    earthly_branch=chart.year_pillar.earthly_branch,
    stem_ten_god=compute_ten_god(chart.day_master, chart.year_pillar.heavenly_stem),  # ❌ 重新计算
)
```

### 问题分析

1. BaziChart 应该包含每个 pillar 的 `stem_ten_god` 字段
2. ContextAssembler 应该**读取** `chart.year_pillar.stem_ten_god`，而不是自己计算
3. 当前 BaziEngine.compute() 没有计算此字段，是 BAZI 端遗漏

### BaziChart 当前字段

```python
@dataclass(frozen=True)
class BaziChart:
    year_pillar: Pillar           # ✅ 有
    month_pillar: Pillar          # ✅ 有
    day_pillar: Pillar            # ✅ 有
    hour_pillar: Pillar           # ✅ 有
    day_master: str               # ✅ 有
    luck_pillars: list            # ✅ 有（但不完整）
```

### Pillar 类定义

```python
@dataclass(frozen=True)
class Pillar:
    heavenly_stem: str
    earthly_branch: str
    # ❌ 没有 stem_ten_god 字段
```

---

## 问题 4：地支关系重复计算

### 当前代码

```python
# context_assembler.py:165-186
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
        if BRANCH_CLASH.get(b1) == b2:          # ❌ ZIPING 自己计算
            branch_clashes.append(pair)
        if BRANCH_COMBINATION.get(b1) == b2:    # ❌ ZIPING 自己计算
            branch_combinations.append(pair)
        # ...
```

### BaziChart 已有字段

```python
branch_clash_map: dict = field(default_factory=dict)   # ✅ BAZI 已计算
branch_harm_map: dict = field(default_factory=dict)     # ✅ BAZI 已计算
branch_he_map: dict = field(default_factory=dict)       # ✅ BAZI 已计算
branch_sanhe_map: dict = field(default_factory=dict)    # ✅ BAZI 已计算
branch_sanxing_map: dict = field(default_factory=dict)  # ✅ BAZI 已计算
kong_wang: tuple = field(default_factory=tuple)         # ✅ BAZI 已计算
```

### 问题

ContextAssembler 完全忽略 BaziChart 已有的字段，重新计算了一遍。

---

## 问题 5-6：大运重复计算（严重）

### 当前代码

```python
# context_assembler.py:218
def assemble_dayun_context(self, chart, natal: NatalContext, target_year: int) -> DaYunContext:
    """组装DaYunContext."""
    # 自己计算大运 (不依赖chart.luck_pillars数量)  ← 注释明确说"不依赖 chart.luck_pillars"
    
    # 从月柱开始
    month_stem = natal.pillars[1].heavenly_stem
    month_branch = natal.pillars[1].earthly_branch
    month_stem_idx = HEAVENLY_STEMS.index(month_stem)
    month_branch_idx = EARTHLY_BRANCHES.index(month_branch)
    
    start_age = getattr(chart, 'start_age', 0.0)
    
    # 计算12个大运 (覆盖到120岁)
    da_yun_pillars = []
    for i in range(12):
        if is_forward:
            stem_idx = (month_stem_idx + 1 + i) % 10
            branch_idx = (month_branch_idx + 1 + i) % 12
        else:
            stem_idx = (month_stem_idx - 1 - i) % 10
            branch_idx = (month_branch_idx - 1 - i) % 12
        
        stem = HEAVENLY_STEMS[stem_idx]
        branch = EARTHLY_BRANCHES[branch_idx]
        # ...
```

### BaziChart 已有字段

```python
luck_pillars: list  # ✅ BAZI 已计算（大运）
start_age: float = 0.0  # ✅ BAZI 已计算（起运岁数）
```

### 问题

这是一个**第二套 DaYun Engine**：
- BAZI 已经计算了 `chart.luck_pillars` 和 `chart.start_age`
- ContextAssembler 却自己用公式重新计算了一遍
- 两套算法可能存在不一致

---

## 问题 7-8：流年干支重复计算

### 当前代码

```python
# context_assembler.py:111-117
def compute_year_pillar(year: int) -> tuple[str, str]:
    """计算流年干支 (1984甲子年基准)."""
    base_year = 1984
    offset = year - base_year
    stem_idx = offset % 10
    branch_idx = offset % 12
    return HEAVENLY_STEMS[stem_idx], EARTHLY_BRANCHES[branch_idx]

# context_assembler.py:318-319
year_stem, year_branch = compute_year_pillar(target_year)  # ❌ ZIPING 自己计算
year_stem_ten_god = compute_ten_god(natal.day_master, year_stem)  # ❌ 重新计算
```

### 问题

流年干支是一个纯数学问题，但：
1. 应该由 TimeEngine 或 BAZI 统一管理
2. ContextAssembler 应该消费而不是自己生成
3. 如果 BAZI/TimeEngine 有更正算法，这里不会自动更新

---

## BaziChart 已有但被忽略的字段

| 字段 | 类型 | 说明 | 是否被使用 |
|------|------|------|-----------|
| `branch_clash_map` | `dict` | 四支冲关系 | ❌ 未使用 |
| `branch_harm_map` | `dict` | 四支害关系 | ❌ 未使用 |
| `branch_he_map` | `dict` | 地支六合 | ❌ 未使用 |
| `branch_sanhe_map` | `dict` | 三合局 | ❌ 未使用 |
| `branch_sanxing_map` | `dict` | 三刑局 | ❌ 未使用 |
| `kong_wang` | `tuple` | 空亡 | ❌ 未使用 |
| `luck_pillars` | `list` | 大运列表 | ❌ 未使用（自己重新计算） |
| `start_age` | `float` | 起运岁数 | ⚠️ 部分使用 |
| `day_master_strength` | `str` | 日主强度 | ❌ 缺失 |
| `five_element_balance` | `dict` | 五行分布 | ❌ 未使用 |
| `spouse_star` | `dict` | 配偶星 | ❌ 未使用 |
| `spouse_star_strength` | `str` | 配偶星强度 | ❌ 未使用 |
| `day_branch_main_ten_god` | `str` | 日支主气十神 | ❌ 未使用 |

---

## 修复建议

### 方案 A：扩展 BaziChart + Pillar（推荐）

在 BaziEngine 端补充缺失字段：

```python
@dataclass(frozen=True)
class Pillar:
    heavenly_stem: str
    earthly_branch: str
    stem_ten_god: str = ""  # ✅ 新增：由 BAZI 计算
    
    # 藏干等字段...

@dataclass(frozen=True)
class BaziChart:
    # ... 现有字段
    
    day_master_strength: str = "MISSING"  # ✅ 新增（Phase 3 P0 要求）
    pillar_ten_gods: dict = field(default_factory=dict)  # 可选：更完整的十神映射
```

然后 ContextAssembler 改为消费：

```python
# context_assembler.py:140（修复后）
pillar = NatalPillar(
    position="YEAR",
    heavenly_stem=chart.year_pillar.heavenly_stem,
    earthly_branch=chart.year_pillar.earthly_branch,
    stem_ten_god=chart.year_pillar.stem_ten_god,  # ✅ 直接读取
)

# context_assembler.py:165-186（修复后）
branch_clashes = list(chart.branch_clash_map.keys())  # ✅ 读取已有数据
branch_combinations = [...]  # 类似
```

### 方案 B：ContextAssembler 只消费

完全禁止 ContextAssembler 计算任何 deterministic facts：

```python
# ❌ 禁止
def compute_ten_god(...)  # 删除此函数或标记为 deprecated
def compute_year_pillar(...)  # 删除，改用 TimeEngine

# ✅ 只允许读取
chart.luck_pillars  # 直接使用
chart.branch_clash_map  # 直接使用
```

---

## 需要裁决的问题

1. **Ten Gods 计算应该在哪一层？**
   - BAZI 端计算（BaziChart.pillar.stem_ten_god）
   - 还是 ZIPING 端计算（当前方式）

2. **大运计算应该由谁负责？**
   - BAZI 端已计算 `chart.luck_pillars`
   - 为什么 ContextAssembler 还要重新计算？

3. **流年干支应该由谁计算？**
   - TimeEngine？
   - BAZI Engine？
   - 还是 ZIPING 可以独立计算？

4. **BaziChart 缺少的字段是否应该补充？**
   - `day_master_strength`（Phase 3 P0 要求）
   - `pillar.stem_ten_god`
   - 其他字段

---

## 当前状态

```
┌─────────────────────────────────────────────────────────────┐
│ P0-1-C 边界审计结果                                          │
├─────────────────────────────────────────────────────────────┤
│ BaziChart.luck_pillars              存在但未被使用          │
│ BaziChart.branch_clash_map          存在但未被使用          │
│ BaziChart.branch_harm_map           存在但未被使用          │
│ BaziChart.stem_ten_god (Pillar)     缺失                    │
│ BaziChart.day_master_strength       缺失                    │
├─────────────────────────────────────────────────────────────┤
│ ContextAssembler 重新计算项目：                               │
│   1. Ten Gods (4 处)         ❌ 违规                        │
│   2. 地支关系 (多组)          ❌ 违规                        │
│   3. 大运 12 柱               ❌ 违规（第二套引擎）           │
│   4. 流年干支                 ❌ 违规                        │
├─────────────────────────────────────────────────────────────┤
│ 建议方向：                                                    │
│   扩展 BaziChart，让 BAZI 计算所有 deterministic facts       │
│   ContextAssembler 只消费，不计算                           │
└─────────────────────────────────────────────────────────────┘
```

**等待 BOT-MASTER 对以下问题裁决：**
1. Ten Gods、大运、流年应该由哪一层负责计算？
2. 是否扩展 BaziChart 补充缺失字段？
3. ContextAssembler 是否可以保留少量"辅助计算"（如十神映射）？
