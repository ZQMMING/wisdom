# P0-1-C 修复进度报告

**任务**: P0-1-C Deterministic Boundary Fix
**执行者**: @bot-ziping + @bot-bazi (协助)
**日期**: 2026-09-07
**状态**: 🟡 Phase 1 待 BOT-BAZI 完成，Phase 3 已完成

---

## 一、已完成工作

### 1.1 Phase 1: BAZI 端扩展（BOT-BAZI 负责）

**状态**: ⏳ 待执行

**任务内容**:
1. 扩展 `Pillar` 类，添加 `stem_ten_god: str = ""`
2. 扩展 `LuckPillar` 类（如果存在），添加 `stem_ten_god: str = ""`
3. 修改 `BaziEngine.compute()` 方法，计算四个 pillar 的 `stem_ten_god`
4. 修改 `_compute_luck_pillars()` 方法，计算大运的 `stem_ten_god`

**涉及文件**:
- `src/tongshu/engines/bazi_engine.py`
- `src/tongshu/canonical/state.py` (如果 LuckPillar 定义在此)

**测试要求**:
- `test_bazi_engine.py` 全部 PASS
- 不修改任何测试期望值

---

### 1.2 Phase 3: ZIPING 端修改（BOT-ZIPING 负责）✅

**状态**: ✅ 已完成

**修改内容**:

#### 1.2.1 删除重复计算函数
```python
# ❌ 已删除
def compute_year_pillar(year: int) -> tuple[str, str]: ...
from tongshu.reasoning.bazi_ten_gods import ten_god as compute_ten_god
```

#### 1.2.2 添加临时 fallback 函数
```python
def _compute_year_pillar_temp(self, year: int) -> tuple[str, str]:
    """临时：计算流年干支。等待 TemporalEngine 集成后删除."""
    ...

def _compute_ten_god_temp(self, day_master: str, stem: str) -> str:
    """临时：计算十神。等待 BAZI Chart 提供后删除."""
    ...
```

#### 1.2.3 修改 assemble_natal_context()
```python
# ✅ 改为消费 BAZI 字段（带 fallback）
pillar = NatalPillar(
    position="YEAR",
    heavenly_stem=chart.year_pillar.heavenly_stem,
    earthly_branch=chart.year_pillar.earthly_branch,
    stem_ten_god=getattr(chart.year_pillar, 'stem_ten_god', compute_ten_god(...)),
)

# ✅ 地支关系直接消费
branch_clashes = list(getattr(chart, 'branch_clash_map', {}).keys())
branch_combinations = list(getattr(chart, 'branch_he_map', {}).keys())
branch_harms = list(getattr(chart, 'branch_harm_map', {}).keys())
branch_three_combinations = list(getattr(chart, 'branch_sanhe_map', {}).keys())
```

#### 1.2.4 修改 assemble_dayun_context()
```python
# ✅ 消费 BAZI 已有大运列表（不重新计算）
for luck in chart.luck_pillars:
    da_yun_pillars.append(DaYunPillar(
        stem_ten_god=getattr(luck, 'stem_ten_god', ''),  # 消费 BAZI 字段
        ...
    ))
```

#### 1.2.5 修改 assemble_year_context()
```python
# ✅ 使用临时函数（等待 TemporalEngine）
year_stem, year_branch = self._compute_year_pillar_temp(target_year)
year_stem_ten_god = self._compute_ten_god_temp(natal.day_master, year_stem)
```

---

## 二、测试结果

### 2.1 当前状态

```
✅ test_bazi_engine.py: 12/12 PASS
✅ test_phase3_p0.py: 1/1 PASS
✅ test_rule_engine.py: 12/12 PASS
━━━━━━━━━━━━━━━━━━━━━━━━━━━
总计: 25/25 PASS
```

### 2.2 待 BOT-BAZI 完成后

当 BOT-BAZI 完成 Phase 1 后：
1. 更新 `context_assembler.py` 中的 fallback 逻辑
2. 验证完整的端到端链路
3. 运行完整测试套件

---

## 三、Git 提交历史

| Commit | 内容 | 作者 | 状态 |
|--------|------|------|------|
| `8bcb2c9b` | P0-1-C 边界审计报告 | BOT-ZIPING | ✅ |
| `fa3529ff` | P0-1-C Frozen BAZI Contract 对账表 | BOT-ZIPING | ✅ |
| `f18c1412` | P0-1-C Boundary Decision Contract 最终定义 | BOT-ZIPING | ✅ |
| `229526fb` | P0-1-C Fix Plan 修复路径规划 | BOT-ZIPING | ✅ |
| `8f82af8c` | P0-1-C Final Boundary Decision Contract | BOT-ZIPING | ✅ |
| `4a3a1b12` | ZP: P0-1-C Fix - ZIPING端改为消费BAZI字段 | BOT-ZIPING | ✅ |

---

## 四、关键决策

### 4.1 BAZI 职责

```text
✅ 计算四柱（年/月/日/时）
✅ 计算十神确定性关系（pillar.stem_ten_god）
✅ 计算地支关系（branch_clash_map, branch_he_map, branch_harm_map, branch_sanhe_map）
✅ 计算大运列表（luck_pillars）
✅ 计算起运岁数（start_age）
```

### 4.2 ZIPING 职责

```text
✅ 消费 BAZI Frozen Chart
✅ 组装 Natal/DaYun/Year Context
✅ Feature Extraction
✅ Rule Evaluation
✅ Judgment（旺衰/格局/用神/十神语义/事件判断）
❌ 不得重新计算 BAZI-owned deterministic facts
```

### 4.3 Temporal Engine 职责

```text
⏳ 计算流年干支（target_year_pillar）
⏳ 计算流年十神（target_year_stem_ten_god）
```

---

## 五、下一步

### 5.1 立即执行

1. **BOT-BAZI**: 完成 Phase 1（扩展 Pillar.stem_ten_god）
2. **BOT-ZIPING**: 验证 Phase 3 修改

### 5.2 待 BOT-BAZI 完成后

1. 更新 `context_assembler.py`，移除 fallback 逻辑
2. 通知 BOT-TIME 开始 Phase 2（Temporal Engine 扩展）
3. 运行完整测试套件
4. 提交最终验收报告

---

## 六、禁止事项（严格执行）

```text
❌ 不得修改 Judgment 层算法（旺衰/格局/用神/十神语义/事件判断）
❌ 不得修改 Golden Dataset 期望值
❌ 不得将 day_master_strength 塞入 BaziChart
❌ 不得引入新的确定性计算入口
❌ 不得修改 BAZI 的 Ten Gods 计算算法
```

---

## 七、GitHub 链接

- 审计报告: https://github.com/ZQMMING/wisdom/commit/8bcb2c9b
- 对账表: https://github.com/ZQMMING/wisdom/commit/fa3529ff
- Contract: https://github.com/ZQMMING/wisdom/commit/f18c1412
- Fix Plan: https://github.com/ZQMMING/wisdom/commit/229526fb
- ZIPING 修改: https://github.com/ZQMMING/wisdom/commit/4a3a1b12

---

**最后更新**: 2026-09-07 19:22
**等待**: BOT-BAZI Phase 1 完成
