# P0-1-C Frozen BAZI Contract 对账表

**任务**: 逐项确认 BAZI Frozen Chart 已有字段 vs ContextAssembler 自己计算字段
**执行者**: @bot-ziping
**日期**: 2026-09-07
**状态**: 待 BOT-MASTER 裁决

---

## 对账原则

根据 BOT-MASTER 裁决：
> **BAZI owns deterministic Ten-God relation; ZIPING owns Ten-God semantic interpretation.**
> **BAZI owns DaYun calculation; ZIPING consumes DaYun.**
> **Canonical Time/BAZI layer owns Year Pillar; ZIPING consumes Year context.**

对账表格式：
```text
FACT_ID | FACT_NAME | OWNER | CURRENT_SOURCE | FROZEN_CONTRACT_FIELD | ZIPING_CONSUMPTION_FIELD | MISSING? | ACTION
```

---

## 对账表

| FACT_ID | FACT_NAME | OWNER | CURRENT_SOURCE | FROZEN_CONTRACT_FIELD | ZIPING_CONSUMPTION_FIELD | MISSING? | ACTION |
|---------|-----------|-------|----------------|----------------------|-------------------------|----------|--------|
| FG-001 | 年干十神 | BAZI | ZIPING 重算 (line 140) | `chart.year_pillar.stem_ten_god` | `natal.pillars[0].stem_ten_god` | ✅ 缺失 | BAZI 补充字段 |
| FG-002 | 月干十神 | BAZI | ZIPING 重算 (line 146) | `chart.month_pillar.stem_ten_god` | `natal.pillars[1].stem_ten_god` | ✅ 缺失 | BAZI 补充字段 |
| FG-003 | 日干十神 | BAZI | ZIPING 硬编码 "DAY_MASTER" (line 152) | `chart.day_pillar.stem_ten_god = "DAY_MASTER"` | `natal.pillars[2].stem_ten_god` | ⚠️ 部分缺失 | BAZI 补充字段 |
| FG-004 | 时干十神 | BAZI | ZIPING 重算 (line 158) | `chart.hour_pillar.stem_ten_god` | `natal.pillars[3].stem_ten_god` | ✅ 缺失 | BAZI 补充字段 |
| BR-001 | 四支冲关系 | BAZI | ZIPING 重算 (line 165-177) | `chart.branch_clash_map` | `natal.branch_clashes` | ✅ 已有 | ZIPING 消费 |
| BR-002 | 四支合关系 | BAZI | ZIPING 重算 (line 166-179) | `chart.branch_he_map` | `natal.branch_combinations` | ✅ 已有 | ZIPING 消费 |
| BR-003 | 四支害关系 | BAZI | ZIPING 重算 (line 167-181) | `chart.branch_harm_map` | `natal.branch_harms` | ✅ 已有 | ZIPING 消费 |
| BR-004 | 三合局 | BAZI | ZIPING 重算 (line 184-186) | `chart.branch_sanhe_map` | `natal.branch_three_combinations` | ✅ 已有 | ZIPING 消费 |
| BR-005 | 空亡 | BAZI | ZIPING 未使用 | `chart.kong_wang` | `natal.kong_wang` | ✅ 已有 | ZIPING 消费 |
| DY-001 | 大运列表 | BAZI | ZIPING 重算 (line 238-267) | `chart.luck_pillars` | `dayun.all_da_yun` | ✅ 已有 | ZIPING 消费 |
| DY-002 | 起运岁数 | BAZI | ZIPING 读取 (line 235) | `chart.start_age` | `dayun.first_luck_start_year` | ✅ 已有 | ZIPING 消费 |
| DY-003 | 大运十神 | BAZI | ZIPING 重算 (line 265) | `chart.luck_pillars[i].stem_ten_god` | `dayun.current_da_yun.stem_ten_god` | ⚠️ 部分缺失 | BAZI 补充 |
| YR-001 | 流年干支 | Time/BAZI | ZIPING 重算 (line 318) | `time_context.target_year_pillar` | `year.year_stem/year.year_branch` | ✅ 待确认 | 确认来源 |
| YR-002 | 流年十神 | BAZI | ZIPING 重算 (line 319) | `time_context.target_year_stem_ten_god` | `year.year_stem_ten_god` | ⚠️ 待确认 | 确认来源 |
| DM-001 | 日主强度 | BAZI | ZIPING 要求 (line 195) | `chart.day_master_strength` | `natal.day_master_strength` | ❌ 缺失 | BAZI 补充（Phase 3 P0） |
| FE-001 | 五行分布 | BAZI | ZIPING 未使用 | `chart.five_element_balance` | `natal.five_element_distribution` | ✅ 已有 | ZIPING 消费 |
| SP-001 | 配偶星 | BAZI | ZIPING 未使用 | `chart.spouse_star` | `natal.spouse_star` | ✅ 已有 | ZIPING 消费 |
| SP-002 | 配偶星强度 | BAZI | ZIPING 未使用 | `chart.spouse_star_strength` | `natal.spouse_star_strength` | ✅ 已有 | ZIPING 消费 |
| SP-003 | 日支主气十神 | BAZI | ZIPING 未使用 | `chart.day_branch_main_ten_god` | `natal.day_branch_main_ten_god` | ✅ 已有 | ZIPING 消费 |
| RC-001 | Natal × DaYun 冲合 | BAZI? | ZIPING 重算 (line 280-288) | 可能需要 BAZI 计算 | `dayun.natal_dayun_clashes` | ⚠️ 待确认 | 确认是否 BAZI 或 ZIPING |
| RC-002 | Natal × Year 冲合害 | BAZI? | ZIPING 重算 (line 324-337) | 可能需要 BAZI 计算 | `year.natal_year_clashes` | ⚠️ 待确认 | 确认是否 BAZI 或 ZIPING |
| RC-003 | DaYun × Year 冲合 | BAZI? | ZIPING 重算 (line 340-351) | 可能需要 BAZI 计算 | `year.dayun_year_clashes` | ⚠️ 待确认 | 确认是否 BAZI 或 ZIPING |
| RC-004 | 三层交互（三合局完成） | BAZI? | ZIPING 重算 (line 354-361) | 可能需要 BAZI 计算 | `year.three_layer_interactions` | ⚠️ 待确认 | 确认是否 BAZI 或 ZIPING |

---

## 汇总

### BAZI 已有但 ZIPING 未消费的字段（8 个）

```text
✅ chart.branch_clash_map    → natal.branch_clashes
✅ chart.branch_he_map       → natal.branch_combinations
✅ chart.branch_harm_map     → natal.branch_harms
✅ chart.branch_sanhe_map    → natal.branch_three_combinations
✅ chart.kong_wang           → natal.kong_wang
✅ chart.luck_pillars        → dayun.all_da_yun
✅ chart.start_age           → dayun.first_luck_start_year
✅ chart.five_element_balance → natal.five_element_distribution
✅ chart.spouse_star         → natal.spouse_star
✅ chart.spouse_star_strength → natal.spouse_star_strength
✅ chart.day_branch_main_ten_god → natal.day_branch_main_ten_god
```

### BAZI 缺失导致 ZIPING 重算的字段（6 个）

```text
❌ chart.year_pillar.stem_ten_god   → natal.pillars[0].stem_ten_god
❌ chart.month_pillar.stem_ten_god  → natal.pillars[1].stem_ten_god
❌ chart.day_pillar.stem_ten_god    → natal.pillars[2].stem_ten_god (硬编码)
❌ chart.hour_pillar.stem_ten_god   → natal.pillars[3].stem_ten_god
❌ chart.luck_pillars[i].stem_ten_god → dayun.current_da_yun.stem_ten_god
❌ chart.day_master_strength        → natal.day_master_strength
```

### 待确认来源的字段（流年相关，6 个）

```text
⏳ time_context.target_year_pillar          → year.year_stem/year.year_branch
⏳ time_context.target_year_stem_ten_god    → year.year_stem_ten_god
⏳ 流年交互关系（RC-001/002/003/004）来源确认
```

---

## 修复优先级

### P0：阻止 assemble() 失败

```text
1. BAZI 补充 day_master_strength 字段（Phase 3 P0 要求）
2. BAZI 补充 pillar.stem_ten_god 字段
3. ZIPING 改为消费 chart 字段
```

### P1：消除重复计算

```text
4. ZIPING 消费 chart.branch_clash_map 等已有字段
5. ZIPING 消费 chart.luck_pillars 大运列表
6. 确认流年干支来源（TimeEngine or BAZI）
```

### P2：完善交互关系

```text
7. 确认 Natal × DaYun × Year 交互关系的归属
8. 补充缺失的交互关系字段到 BAZI 或 TimeEngine
```

---

## 需要 BOT-MASTER 裁决的问题

### 问题 1：流年干支由谁负责？

```text
选项 A: TimeEngine 计算并返回到 TemporalContext
选项 B: BAZI Engine 计算并返回到 BaziChart
选项 C: ZIPING 可以独立计算（因为是纯数学问题）
```

### 问题 2：Natal × DaYun × Year 交互关系由谁负责？

```text
选项 A: BAZI 计算所有交互关系（因为依赖 BAZI 确定性事实）
选项 B: TimeEngine 计算时间层交互
选项 C: ZIPING 计算交互（派生 Context）
```

### 问题 3：Pillar.stem_ten_god 是否应该加入 BaziChart？

```text
选项 A: 是，BAZI 负责确定性十神关系
选项 B: 否，ZIPING 可以保留十神计算（但需要统一入口）
```

---

## 预期效果

修复后 ContextAssembler 结构：

```python
# ✅ 修复后
def assemble_natal_context(self, chart, birth_year: int, gender: str) -> NatalContext:
    pillars = [
        NatalPillar(
            position="YEAR",
            heavenly_stem=chart.year_pillar.heavenly_stem,
            earthly_branch=chart.year_pillar.earthly_branch,
            stem_ten_god=chart.year_pillar.stem_ten_god,  # ✅ 消费 BAZI 字段
        ),
        # ...
    ]
    
    # ✅ 消费 BAZI 已有字段，不重新计算
    branch_clashes = list(chart.branch_clash_map.keys())
    branch_combinations = list(chart.branch_he_map.keys())
    branch_harms = list(chart.branch_harm_map.keys())
    branch_three_combinations = list(chart.branch_sanhe_map.keys())

def assemble_dayun_context(self, chart, natal: NatalContext, target_year: int) -> DaYunContext:
    # ✅ 消费 BAZI 已有大运列表
    da_yun_pillars = []
    for i, luck_pillar in enumerate(chart.luck_pillars):
        da_yun_pillars.append(DaYunPillar(
            index=i,
            heavenly_stem=luck_pillar.heavenly_stem,
            earthly_branch=luck_pillar.earthly_branch,
            stem_ten_god=luck_pillar.stem_ten_god,  # ✅ 消费 BAZI 字段
            start_age=luck_pillar.start_age,
            end_age=luck_pillar.end_age,
            start_year=luck_pillar.start_year,
            end_year=luck_pillar.end_year,
            is_current=luck_pillar.is_current,
        ))

def assemble_year_context(self, natal: NatalContext, dayun: DaYunContext,
                           target_year: int) -> YearContext:
    # ⏳ 等待裁决：流年干支来源
    # 假设由 TimeEngine 提供
    year_stem, year_branch = self.time_context.target_year_pillar  # ✅ 消费 TimeEngine
    year_stem_ten_god = self.time_context.target_year_stem_ten_god  # ✅ 消费 TimeEngine
```

---

## 当前状态

```
┌─────────────────────────────────────────────────────────────┐
│ P0-1-C Frozen Contract 对账                                  │
├─────────────────────────────────────────────────────────────┤
│ BAZI 已有但 ZIPING 未消费：11 个字段                         │
│ BAZI 缺失导致 ZIPING 重算：6 个字段                          │
│ 待确认来源：流年干支 + 交互关系                               │
├─────────────────────────────────────────────────────────────┤
│ 下一步：                                                    │
│ 1. 等待 BOT-MASTER 裁决问题 1/2/3                           │
│ 2. BAZI 端补充缺失字段（P0: day_master_strength, stem_ten_god）│
│ 3. ZIPING 端改为消费 chart 字段                              │
└─────────────────────────────────────────────────────────────┘
```

**等待 BOT-MASTER 对问题 1/2/3 裁决后再继续。**
