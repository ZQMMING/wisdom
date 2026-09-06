# P0-1-C Boundary Decision Contract

**任务**: 定义 BAZI / Temporal / ZIPING 三层边界 Contract
**执行者**: @bot-ziping
**日期**: 2026-09-07
**状态**: 待 BOT-MASTER 最终裁决

---

## 一、架构原则（已裁决）

### 1.1 BAZI 职责

```text
BAZI Frozen Canonical Chart
├── 四柱（年/月/日/时）
├── 日主
├── 十神确定性关系（pillar.stem_ten_god）
├── 地支关系（branch_clash_map / branch_he_map / branch_harm_map / branch_sanhe_map / branch_sanxing_map）
├── 大运列表（luck_pillars）
├── 起运岁数（start_age）
├── 空亡（kong_wang）
├── 五行分布（five_element_balance）
├── 配偶星（spouse_star / spouse_star_strength）
└── 日支主气十神（day_branch_main_ten_god）
```

### 1.2 Temporal Engine 职责

```text
Temporal Context（由 TimeEngine 提供）
├── target_year_pillar（流年干支）
├── target_year_stem_ten_god（流年十神）
└── 时间层确定性事实
```

### 1.3 ZIPING 职责

```text
ZIPING ContextAssembler
├── 消费 BAZI Frozen Chart
├── 消费 Temporal Context
├── 组装 Natal / DaYun / Year Context
├── Feature Extraction
├── Rule Evaluation
└── Judgment（旺衰/格局/用神/十神语义/事件判断）
```

### 1.4 禁止事项

```text
❌ ZIPING 不得重新计算 BAZI-owned deterministic facts
❌ ZIPING 不得重新计算 Temporal-owned deterministic facts
❌ BAZI 不得计算诊断性 facts（如 day_master_strength）
❌ Temporal Engine 不得计算命理诊断
```

---

## 二、BAZI Frozen Chart Contract

### 2.1 Pillar 类（需扩展）

```python
@dataclass(frozen=True)
class Pillar:
    heavenly_stem: str
    earthly_branch: str
    
    # ❌ 当前缺失，需 BAZI 补充
    stem_ten_god: str = ""  # 年干十神/月干十神/时干十神
    
    # ✅ 已有或即将补充
    hidden_stems: list = field(default_factory=list)
    main_qi: str = ""
```

### 2.2 BaziChart 类（已有字段确认）

```python
@dataclass(frozen=True)
class BaziChart:
    # 四柱
    year_pillar: Pillar           # ✅ 已有
    month_pillar: Pillar          # ✅ 已有
    day_pillar: Pillar            # ✅ 已有
    hour_pillar: Pillar           # ✅ 已有
    day_master: str               # ✅ 已有
    
    # 大运（需扩展 LuckPillar）
    luck_pillars: list            # ✅ 已有，但需补充 stem_ten_god
    
    # 起运
    start_age: float = 0.0        # ✅ 已有
    
    # 地支关系（已有）
    branch_clash_map: dict = field(default_factory=dict)   # ✅ 已有
    branch_harm_map: dict = field(default_factory=dict)    # ✅ 已有
    branch_he_map: dict = field(default_factory=dict)      # ✅ 已有
    branch_sanhe_map: dict = field(default_factory=dict)   # ✅ 已有
    branch_sanxing_map: dict = field(default_factory=dict) # ✅ 已有
    kong_wang: tuple = field(default_factory=tuple)        # ✅ 已有
    
    # 日主强度（⚠️ 争议字段）
    # BOT-MASTER 裁决：day_master_strength 是诊断结果，不是 BAZI 确定性事实
    # → 不得加入 BaziChart
    
    # 其他（已有，ZIPING 未使用）
    five_element_balance: dict = field(default_factory=dict)
    spouse_star: dict = field(default_factory=dict)
    spouse_star_strength: str = "weak"
    day_branch_main_ten_god: str = ""
```

### 2.3 LuckPillar 类（需扩展）

```python
@dataclass(frozen=True)
class LuckPillar:
    index: int
    heavenly_stem: str
    earthly_branch: str
    
    # ❌ 当前缺失，需 BAZI 补充
    stem_ten_god: str = ""
    
    start_age: float
    end_age: float
    start_year: int
    end_year: int
    is_current: bool = False
```

---

## 三、Temporal Context Contract

### 3.1 TemporalContext 类

```python
@dataclass(frozen=True)
class TemporalContext:
    # 流年干支（由 TimeEngine 计算）
    target_year: int
    target_year_pillar: tuple[str, str]  # (stem, branch)
    target_year_stem_ten_god: str
    
    # 其他时间层事实...
```

### 3.2 流年干支归属裁决

```text
裁决：TimeEngine 负责计算流年干支
原因：
1. 流年是时间层的确定性事实，不属于 BAZI 四柱
2. 当前 ZIPING 自己计算的 compute_year_pillar() 是第二套时间计算链
3. 正确架构：TimeEngine → TemporalContext → ZIPING consume
```

---

## 四、ZIPING Derived Context Contract

### 4.1 NatalContext（消费 BAZI，不计算）

```python
@dataclass(frozen=True)
class NatalContext:
    # ✅ 直接读取 BAZI 字段
    day_master: str
    gender: str
    birth_year: int
    
    pillars: list[NatalPillar]  # 从 chart.year_pillar ~ chart.hour_pillar 转换
    
    # ✅ 直接读取 BAZI 已有字段
    branch_clashes: list[str]           # ← list(chart.branch_clash_map.keys())
    branch_combinations: list[str]      # ← list(chart.branch_he_map.keys())
    branch_harms: list[str]             # ← list(chart.branch_harm_map.keys())
    branch_three_combinations: list[str] # ← list(chart.branch_sanhe_map.keys())
    kong_wang: tuple                    # ← chart.kong_wang
    
    # ⚠️ 日主强度：由 ZIPING 诊断层计算，不是 BAZI 字段
    day_master_strength: str = "MISSING"  # ← 由旺衰 Judgment 层计算后注入
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
    natal_dayun_clashes: list[str]      # ← 可保留 ZIPING 计算（派生 Context）
    natal_dayun_combinations: list[str] # ← 可保留 ZIPING 计算（派生 Context）
    
    # 换运期判断
    is_transition_period: bool
    transition_start_year: Optional[int]
    transition_end_year: Optional[int]
    is_pre_luck_period: bool
    first_luck_start_year: Optional[int]
```

### 4.3 YearContext（消费 TemporalContext，不计算）

```python
@dataclass(frozen=True)
class YearContext:
    target_year: int
    year_stem: str
    year_branch: str
    year_stem_ten_god: str
    
    # ✅ 直接读取 TemporalContext 字段
    # 流年干支和十神来自 TimeEngine，不来自 ZIPING 计算
    
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

## 五、ContextAssembler 修改清单

### 5.1 必须删除的代码

```python
# ❌ 删除：ZIPING 自己的 Ten Gods 计算入口
from tongshu.reasoning.bazi_ten_gods import ten_god as compute_ten_god

# ❌ 删除：ZIPING 自己的流年计算函数
def compute_year_pillar(year: int) -> tuple[str, str]:
    ...

# ❌ 删除：ZIPING 自己的地支关系表（如果存在）
BRANCH_CLASH = {...}
BRANCH_COMBINATION = {...}
BRANCH_HARM = {...}
THREE_COMBINATION = {...}
```

### 5.2 必须修改的代码

#### assemble_natal_context()

```python
# ❌ 当前（错误）
pillar = NatalPillar(
    position="YEAR",
    heavenly_stem=chart.year_pillar.heavenly_stem,
    earthly_branch=chart.year_pillar.earthly_branch,
    stem_ten_god=compute_ten_god(chart.day_master, chart.year_pillar.heavenly_stem),  # ❌ 重算
)

# ✅ 修复后
pillar = NatalPillar(
    position="YEAR",
    heavenly_stem=chart.year_pillar.heavenly_stem,
    earthly_branch=chart.year_pillar.earthly_branch,
    stem_ten_god=chart.year_pillar.stem_ten_god,  # ✅ 读取 BAZI 字段
)

# ❌ 当前（错误）
branch_clashes = []
for i, b1 in enumerate(branches):
    for j, b2 in enumerate(branches):
        if BRANCH_CLASH.get(b1) == b2:
            branch_clashes.append(pair)

# ✅ 修复后
branch_clashes = list(chart.branch_clash_map.keys())  # ✅ 读取 BAZI 字段
```

#### assemble_dayun_context()

```python
# ❌ 当前（错误）：自己计算 12 大运
da_yun_pillars = []
for i in range(12):
    # ... 重新计算 stem/branch/index ...
    da_yun_pillars.append(DaYunPillar(
        stem_ten_god=compute_ten_god(natal.day_master, stem),  # ❌ 重算
    ))

# ✅ 修复后：消费 BAZI 已有大运列表
da_yun_pillars = []
for i, luck_pillar in enumerate(chart.luck_pillars):
    da_yun_pillars.append(DaYunPillar(
        index=i,
        heavenly_stem=luck_pillar.heavenly_stem,
        earthly_branch=luck_pillar.earthly_branch,
        stem_ten_god=luck_pillar.stem_ten_god,  # ✅ 读取 BAZI 字段
        start_age=luck_pillar.start_age,
        end_age=luck_pillar.end_age,
        start_year=luck_pillar.start_year,
        end_year=luck_pillar.end_year,
        is_current=luck_pillar.is_current,
    ))
```

#### assemble_year_context()

```python
# ❌ 当前（错误）
year_stem, year_branch = compute_year_pillar(target_year)  # ❌ 重算
year_stem_ten_god = compute_ten_god(natal.day_master, year_stem)  # ❌ 重算

# ✅ 修复后：从 TemporalContext 读取
year_stem, year_branch = self.temporal_context.target_year_pillar  # ✅ 读取 TimeEngine
year_stem_ten_god = self.temporal_context.target_year_stem_ten_god  # ✅ 读取 TimeEngine
```

### 5.3 允许保留的代码

```python
# ✅ 允许：派生 Context 的交互关系计算
# Natal × DaYun × Year 的冲合害是派生事实，允许 ZIPING 计算
natal_year_clashes = []
for nb in natal_branches:
    if BRANCH_CLASH.get(year_branch) == nb:
        natal_year_clashes.append(f"{year_branch}-{nb}")
```

---

## 六、需要 BAZI 端修改的字段

### 6.1 Pillar.stem_ten_god

```python
# src/tongshu/engines/bazi_engine.py

@dataclass(frozen=True)
class Pillar:
    heavenly_stem: str
    earthly_branch: str
    stem_ten_god: str = ""  # ← 新增
```

### 6.2 LuckPillar.stem_ten_god

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

### 6.3 BaziChart 端计算

```python
# 在 bazi_engine.py 的 compute() 方法中补充：

# 四柱十神
chart.year_pillar = Pillar(
    heavenly_stem=year_stem,
    earthly_branch=year_branch,
    stem_ten_god=ten_god(chart.day_master, year_stem),  # ← 补充
)
chart.month_pillar = Pillar(...)
chart.day_pillar = Pillar(stem_ten_god="DAY_MASTER")  # ← 硬编码
chart.hour_pillar = Pillar(...)

# 大运十神
for i, luck in enumerate(chart.luck_pillars):
    luck.stem_ten_god = ten_god(chart.day_master, luck.heavenly_stem)  # ← 补充
```

---

## 七、需要 TimeEngine 端修改的字段

### 7.1 TemporalContext 新增字段

```python
# src/tongshu/engines/time/temporal_context.py

@dataclass(frozen=True)
class TemporalContext:
    target_year: int
    target_year_pillar: tuple[str, str] = ("", "")  # ← 新增
    target_year_stem_ten_god: str = ""  # ← 新增
```

### 7.2 TimeEngine 计算

```python
# 在 time_engine 的 compute_temporal_context() 中补充：

year_stem, year_branch = compute_year_pillar(target_year)  # ← 统一入口
year_stem_ten_god = ten_god(day_master, year_stem)  # ← 统一入口

return TemporalContext(
    target_year=target_year,
    target_year_pillar=(year_stem, year_branch),  # ← 补充
    target_year_stem_ten_god=year_stem_ten_god,  # ← 补充
)
```

---

## 八、day_master_strength 裁决

### BOT-MASTER 裁决

> **日主强度不能作为一个未经证明的 BAZI pseudo-fact 塞回 Chart。**
> 真正的架构应该是：
> ```
> BAZI Canonical Facts
>         ↓
> ZIPING Feature Extraction
>         ↓
> 旺衰诊断
> ```

### 正确实现

```python
# ❌ 错误：在 BAZI 端计算并注入
chart.day_master_strength = compute_strength(chart)  # ← 禁止

# ✅ 正确：在 ZIPING 旺衰 Judgment 层计算
class WANGSHUAIJudgment:
    def judge(self, chart: BaziChart, natal: NatalContext) -> JudgmentConclusion:
        # 旺衰算法：得令 + 得地 + 得势 + 寒暖燥湿 + 生克制化 + 结构条件
        # 返回 STRONG / WEAK / MODERATE
        pass

# ContextAssembler 不要求 day_master_strength
# 而是由 Judgment 层计算后注入到诊断结果中
```

---

## 九、执行顺序（待 BOT-MASTER 裁决后）

### Phase 1：BAZI 端补充字段

```text
1. BAZI Engine: Pillar.stem_ten_god
2. BAZI Engine: LuckPillar.stem_ten_god
3. BAZI Engine: compute() 补充计算
```

### Phase 2：TimeEngine 端补充字段

```text
4. TimeEngine: TemporalContext.target_year_pillar
5. TimeEngine: TemporalContext.target_year_stem_ten_god
6. TimeEngine: compute_temporal_context() 补充计算
```

### Phase 3：ZIPING 端改为消费

```text
7. ContextAssembler: 删除 compute_ten_god()
8. ContextAssembler: 删除 compute_year_pillar()
9. ContextAssembler: 删除 BRANCH_CLASH/HARM/COMBINATION 表
10. ContextAssembler: assemble_natal_context() 改为消费 chart 字段
11. ContextAssembler: assemble_dayun_context() 改为消费 chart.luck_pillars
12. ContextAssembler: assemble_year_context() 改为消费 temporal_context 字段
```

### Phase 4：测试验证

```text
13. 运行 test_phase3_p0.py
14. 运行 test_bazi_engine.py
15. 运行 test_rule_engine.py
16. 验证 assemble() 不再失败
```

---

## 十、当前状态

```
┌─────────────────────────────────────────────────────────────┐
│ P0-1-C Boundary Decision Contract                          │
├─────────────────────────────────────────────────────────────┤
│ BAZI Frozen Chart Contract: 定义完成                        │
│ Temporal Context Contract: 定义完成                         │
│ ZIPING Derived Context Contract: 定义完成                   │
│ day_master_strength 裁决: 暂不批准塞入 BAZI                 │
├─────────────────────────────────────────────────────────────┤
│ 等待 BOT-MASTER 对以下事项裁决：                             │
│ 1. Contract 是否完整？                                      │
│ 2. 是否可以开始 Phase 1 修复？                               │
│ 3. 是否有遗漏或错误？                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 十一、禁止事项确认

### ❌ 以下操作在本次修复中禁止

1. **不得修改 Judgment 层算法**（旺衰/格局/用神/十神语义/事件判断）
2. **不得修改 Golden Dataset 期望值**
3. **不得修改 BAZI Engine 的确定性计算逻辑**（只补充字段）
4. **不得引入新的确定性计算入口**（只消费已有字段）
5. **不得将 day_master_strength 塞入 BaziChart**

### ✅ 允许的操作

1. 扩展 Pillar / LuckPillar 类，添加 stem_ten_god 字段
2. 扩展 TemporalContext 类，添加 target_year_pillar / target_year_stem_ten_god
3. 修改 BaziEngine.compute()，补充上述字段的计算
4. 修改 TimeEngine.compute_temporal_context()，补充流年计算
5. 修改 ContextAssembler，改为消费上述字段
6. 删除 ContextAssembler 中的重复计算代码

---

**等待 BOT-MASTER 对 P0-1-C Boundary Decision Contract 的最终裁决。**
