# P0-1-C Boundary Decision Contract（最终版）

**任务**: 定义 BAZI / Temporal / ZIPING 三层边界
**执行者**: @bot-ziping
**日期**: 2026-09-07
**状态**: 待 BOT-MASTER 最终签字

---

## 一、架构原则（BOT-MASTER 裁决）

### 1.1 核心原则

```text
输入 → BAZI Frozen Canonical Chart → ZIPING Context Assembler → ZIPING Diagnosis
                    ↑                                          ↓
              确定性事实                                    命理判断
              (Ten-God/Branch/DaYun)                      (旺衰/格局/用神)
```

### 1.2 各层职责

| 层级 | 职责 | 禁止事项 |
|------|------|----------|
| **BAZI** | 计算四柱、十神关系、地支关系、大运列表、起运岁数 | 不得计算诊断性事实（如 day_master_strength） |
| **Temporal** | 计算流年干支、时间层确定性事实 | 不得计算命理诊断 |
| **ZIPING** | 消费 Canonical Facts，组装 Context，执行 Feature Extraction、Rule Evaluation、Judgment | 不得重新计算 BAZI/Temporal 的确定性事实 |

### 1.3 边界规则

```text
✅ BAZI owns deterministic Ten-God relation
✅ ZIPING owns Ten-God semantic interpretation
✅ BAZI owns DaYun calculation
✅ ZIPING consumes DaYun
✅ Temporal Engine owns Year Pillar
✅ ZIPING consumes Year context
```

---

## 二、BAZI Frozen Chart Contract

### 2.1 Pillar 类（需扩展）

```python
@dataclass(frozen=True)
class Pillar:
    heavenly_stem: str
    earthly_branch: str
    stem_ten_god: str = ""  # ← BAZI 计算，ZIPING 消费
    hidden_stems: list = field(default_factory=list)
    main_qi: str = ""
```

### 2.2 LuckPillar 类（需扩展）

```python
@dataclass(frozen=True)
class LuckPillar:
    index: int
    heavenly_stem: str
    earthly_branch: str
    stem_ten_god: str = ""  # ← BAZI 计算，ZIPING 消费
    start_age: float
    end_age: float
    start_year: int
    end_year: int
    is_current: bool = False
```

### 2.3 BaziChart 类（已有字段确认）

```python
@dataclass(frozen=True)
class BaziChart:
    # 四柱
    year_pillar: Pillar           # ✅ 已有，需补充 stem_ten_god
    month_pillar: Pillar          # ✅ 已有，需补充 stem_ten_god
    day_pillar: Pillar            # ✅ 已有，需补充 stem_ten_god（硬编码 "DAY_MASTER"）
    hour_pillar: Pillar           # ✅ 已有，需补充 stem_ten_god
    day_master: str               # ✅ 已有
    
    # 大运
    luck_pillars: list[LuckPillar]  # ✅ 已有，需补充 stem_ten_god
    
    # 起运
    start_age: float = 0.0        # ✅ 已有
    
    # 地支关系（BAZI 已计算）
    branch_clash_map: dict        # ✅ 已有
    branch_harm_map: dict         # ✅ 已有
    branch_he_map: dict           # ✅ 已有
    branch_sanhe_map: dict        # ✅ 已有
    branch_sanxing_map: dict      # ✅ 已有
    kong_wang: tuple              # ✅ 已有
    
    # 其他（BAZI 已计算，ZIPING 未使用）
    five_element_balance: dict
    spouse_star: dict
    spouse_star_strength: str
    day_branch_main_ten_god: str
```

### 2.4 day_master_strength 裁决

```text
❌ 不得加入 BaziChart
原因：日主强度是诊断结果，不是确定性事实
正确位置：ZIPING 旺衰 Judgment 层计算后返回
```

---

## 三、Temporal Context Contract

### 3.1 TemporalContext 类（需扩展）

```python
@dataclass(frozen=True)
class TemporalContext:
    target_year: int
    target_year_pillar: tuple[str, str] = ("", "")  # ← Temporal Engine 计算
    target_year_stem_ten_god: str = ""  # ← Temporal Engine 计算（或 BAZI 计算后传入）
```

### 3.2 流年干支归属

```text
裁决：Temporal Engine 负责
原因：
1. 流年是时间层的确定性事实
2. 不应属于 BAZI 四柱（四柱是出生时冻结的）
3. 不应由 ZIPING 自己计算（第二套时间链）
```

### 3.3 TimeEngine 计算逻辑

```python
def compute_temporal_context(self, birth_chart: BaziChart, target_year: int) -> TemporalContext:
    # 流年干支计算（统一入口）
    year_stem, year_branch = compute_year_pillar(target_year)
    
    # 流年十神（由 BAZI 的 ten_god 函数计算）
    year_stem_ten_god = ten_god(birth_chart.day_master, year_stem)
    
    return TemporalContext(
        target_year=target_year,
        target_year_pillar=(year_stem, year_branch),
        target_year_stem_ten_god=year_stem_ten_god,
    )
```

---

## 四、ZIPING Derived Context Contract

### 4.1 NatalContext（消费 BAZI，不计算）

```python
@dataclass(frozen=True)
class NatalContext:
    day_master: str
    gender: str
    birth_year: int
    
    pillars: list[NatalPillar]  # 从 chart 转换
    
    # ✅ 直接读取 BAZI 字段
    branch_clashes: list[str]           # ← list(chart.branch_clash_map.keys())
    branch_combinations: list[str]      # ← list(chart.branch_he_map.keys())
    branch_harms: list[str]             # ← list(chart.branch_harm_map.keys())
    branch_three_combinations: list[str] # ← list(chart.branch_sanhe_map.keys())
    kong_wang: tuple                    # ← chart.kong_wang
    
    # ⚠️ day_master_strength 不在此处，由旺衰 Judgment 层计算后注入
```

### 4.2 DaYunContext（消费 BAZI，不计算）

```python
@dataclass(frozen=True)
class DaYunContext:
    current_da_yun: DaYunPillar
    previous_da_yun: Optional[DaYunPillar]
    next_da_yun: Optional[DaYunPillar]
    all_da_yun: list[DaYunPillar]
    
    # ✅ 直接读取 BAZI 字段
    # all_da_yun = [LuckPillar → DaYunPillar] 转换
    
    # ⚠️ 交互关系（派生 Context）
    natal_dayun_clashes: list[str]      # ← ZIPING 可以计算
    natal_dayun_combinations: list[str] # ← ZIPING 可以计算
```

### 4.3 YearContext（消费 TemporalContext）

```python
@dataclass(frozen=True)
class YearContext:
    target_year: int
    year_stem: str                      # ← 读取 temporal_context.target_year_pillar[0]
    year_branch: str                    # ← 读取 temporal_context.target_year_pillar[1]
    year_stem_ten_god: str              # ← 读取 temporal_context.target_year_stem_ten_god
    
    # 交互关系（派生 Context，允许 ZIPING 计算）
    natal_year_clashes: list[str]
    natal_year_combinations: list[str]
    natal_year_harms: list[str]
    natal_year_fuyin: list[str]
    dayun_year_clashes: list[str]
    dayun_year_combinations: list[str]
    dayun_year_fuyin: list[str]
    three_layer_interactions: list[str]
```

---

## 五、交互关系归属（三层拆分）

### 5.1 第一层：Canonical Relation（BAZI-owned）

```text
四柱本身的冲合害刑三合
大运本身的干支和十神
→ BAZI 计算，ZIPING 消费
```

### 5.2 第二层：Temporal Context Assembly（ZIPING-owned）

```text
Natal × DaYun 的冲合
Natal × Year 的冲合害
DaYun × Year 的冲合
三层交互（三合局完成等）
→ ZIPING 可以计算（这是派生 Context）
```

### 5.3 第三层：Diagnosis（ZIPING-owned）

```text
某流年冲夫妻宫
某大运与原局形成某结构
某三层结构触发某事件条件
→ ZIPING 诊断层
```

---

## 六、ContextAssembler 修改清单

### 6.1 必须删除的代码

```python
# ❌ Line 37: import
from tongshu.reasoning.bazi_ten_gods import ten_god as compute_ten_god

# ❌ Line 111-117: 流年计算函数
def compute_year_pillar(year: int) -> tuple[str, str]:
    ...

# ❌ Line 120-121: 天干地支表（如果与 BAZI 重复）
HEAVENLY_STEMS = [...]
EARTHLY_BRANCHES = [...]

# ❌ Line 165-186: 地支关系重算
branch_clashes = []
for i, b1 in enumerate(branches):
    for j, b2 in enumerate(branches):
        if BRANCH_CLASH.get(b1) == b2:
            branch_clashes.append(pair)
```

### 6.2 必须修改的代码

#### assemble_natal_context()

```python
# ❌ 当前（错误）
pillar = NatalPillar(
    stem_ten_god=compute_ten_god(chart.day_master, chart.year_pillar.heavenly_stem),
)

# ✅ 修复后
pillar = NatalPillar(
    stem_ten_god=chart.year_pillar.stem_ten_god,  # ← 读取 BAZI 字段
)

# ❌ 当前
branch_clashes = []
for i, b1 in enumerate(branches):
    for j, b2 in enumerate(branches):
        if BRANCH_CLASH.get(b1) == b2:
            branch_clashes.append(pair)

# ✅ 修复后
branch_clashes = list(chart.branch_clash_map.keys())  # ← 读取 BAZI 字段
```

#### assemble_dayun_context()

```python
# ❌ 当前（错误）：自己计算 12 大运
da_yun_pillars = []
for i in range(12):
    stem_idx = (month_stem_idx + 1 + i) % 10
    branch_idx = (month_branch_idx + 1 + i) % 12
    da_yun_pillars.append(DaYunPillar(
        stem_ten_god=compute_ten_god(natal.day_master, stem),
    ))

# ✅ 修复后：消费 BAZI 已有大运
da_yun_pillars = []
for luck in chart.luck_pillars:
    da_yun_pillars.append(DaYunPillar(
        index=luck.index,
        heavenly_stem=luck.heavenly_stem,
        earthly_branch=luck.earthly_branch,
        stem_ten_god=luck.stem_ten_god,  # ← 读取 BAZI 字段
        start_age=luck.start_age,
        end_age=luck.end_age,
        start_year=luck.start_year,
        end_year=luck.end_year,
        is_current=luck.is_current,
    ))
```

#### assemble_year_context()

```python
# ❌ 当前（错误）
year_stem, year_branch = compute_year_pillar(target_year)
year_stem_ten_god = compute_ten_god(natal.day_master, year_stem)

# ✅ 修复后：从 TemporalContext 读取
year_stem, year_branch = temporal_context.target_year_pillar
year_stem_ten_god = temporal_context.target_year_stem_ten_god
```

### 6.3 允许保留的代码

```python
# ✅ 允许：派生 Context 的交互关系计算
natal_year_clashes = []
for nb in natal_branches:
    if BRANCH_CLASH.get(year_branch) == nb:  # ← ZIPING 可以计算派生关系
        natal_year_clashes.append(f"{year_branch}-{nb}")
```

---

## 七、禁止事项（严格执行）

```text
❌ 不得修改 Judgment 层算法（旺衰/格局/用神/十神语义/事件判断）
❌ 不得修改 Golden Dataset 期望值
❌ 不得修改 BAZI Engine 的确定性计算逻辑（只补充字段）
❌ 不得引入新的确定性计算入口
❌ 不得将 day_master_strength 塞入 BaziChart
❌ 不得修改 BAZI 的 Ten Gods 计算算法
❌ 不得让 ZIPING 重新计算 BAZI-owned 或 Temporal-owned 确定性事实
```

---

## 八、执行顺序

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

## 九、验收标准

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

## 十、当前状态

```
┌─────────────────────────────────────────────────────────────┐
│ P0-1-C Boundary Decision Contract                           │
├─────────────────────────────────────────────────────────────┤
│ BAZI Frozen Chart Contract: 定义完成                        │
│ Temporal Context Contract: 定义完成                         │
│ ZIPING Derived Context Contract: 定义完成                   │
│ day_master_strength 裁决: 暂不批准塞入 BAZI                 │
│ 流年干支归属: Temporal Engine                               │
│ 交互关系归属: 三层拆分（Canonical/Temporal/Diagnosis）       │
├─────────────────────────────────────────────────────────────┤
│ 下一步：                                                    │
│ 1. BOT-MASTER 签字批准 Contract                             │
│ 2. 通知 BOT-BAZI 开始 Phase 1                               │
│ 3. 通知 BOT-TIME 开始 Phase 2                               │
│ 4. BOT-ZIPING 等待 Phase 1+2 完成后开始 Phase 3             │
└─────────────────────────────────────────────────────────────┘
```

---

## 十一、Commit 历史

| Commit | 内容 | 状态 |
|--------|------|------|
| `8bcb2c9b` | P0-1-C 边界审计报告 | ✅ 已完成 |
| `fa3529ff` | P0-1-C Frozen BAZI Contract 对账表 | ✅ 已完成 |
| `f18c1412` | P0-1-C Boundary Decision Contract 最终定义 | ✅ 已完成 |
| `229526fb` | P0-1-C Fix Plan 修复路径规划 | ✅ 已完成 |
| 待执行 | BAZI 端扩展（Phase 1） | ⏳ 等待裁决 |
| 待执行 | Temporal Engine 扩展（Phase 2） | ⏳ 等待裁决 |
| 待执行 | ZIPING 端修改（Phase 3） | ⏳ 等待裁决 |

---

**等待 BOT-MASTER 最终签字后开始执行。**
