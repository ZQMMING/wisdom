# 子平引擎提交链条整理（P0 独立审计）

**审计员**: @bazi  
**日期**: 2026-09-05  
**分支**: main → origin/main

---

## 一、子平引擎提交链条

### 核心修复链（H17-P0 + H18）

```
8cbb530  P2.7-H17-P0: Fix _calc_start_age() algorithm
         ↓ 修复：range(0,33)，_is_jie() 节筛选，方向一致性
9b86aaa  P2.7-H17-P0: Fix JD converter timezone bug
         ↓ 修复：UTC→北京时间转换
c8c3757  P2.7-H17-P0: Fix JD converter with correct simple algorithm
         ↓ 修复：sxtwl frac 直接转换北京时间
eb568f4  P2.7-H18: Fix Calculation-Time Authority
         ↓ 修复：BaziChart birth_datetime + _calc_start_age minute/second
a12450e  P2.7-H18-FIX: Restore canonical_bazi.py to pre-H17-B state
         ↓ 修复：回滚意外删除的 canonical_bazi.py
```

### 已回滚的污染提交

```
7d6002a  P2.7-H17-B: Canonical Bazi Integration — Heluo consumes CanonicalBaziChart
         ← 此提交被回滚（污染河洛引擎）
9e233e6  P2.7-H18-ROLLBACK: Revert H17-B Heluo pollution from bazi agent
         ← 回滚 7d6002a
```

---

## 二、当前状态评估

### ✅ 已通过的项目

| 项目 | Commit | 说明 |
|------|--------|------|
| 起运算法（节筛选） | 8cbb530 | range(0,33) + _is_jie() 奇数筛选 |
| JD 转换（北京时间） | c8c3757 | frac 直接转换，无需时区偏移 |
| 起运分钟级支持 | eb568f4 | _calc_start_age(year,month,day,hour,minute,second) |
| BaziChart 时间字段 | eb568f4 | birth_datetime 字段已添加 |
| 方向一致性检查 | 8cbb530 | 顺排只找未来节，逆排只找过去节 |

### 🔴 未通过的项目

| 问题 | 位置 | 影响 |
|------|------|------|
| **bazi_view 丢失 minute** | `calculation_context.py:236` | Adapter 层时间链断裂 |
| **月柱边界 t.m=0** | `bazi_engine.py:860` | 节气前后分钟级判断错误 |
| **Canonical 缺少 birth_datetime** | `canonical_bazi.py` | 下游引擎无法验证时间 |
| **大运只有 3 个** | `bazi_engine.py:1058` | range(1,4) 应为 range(1,11) |

---

## 三、代码审计详情

### 3.1 bazi_view 投影问题 🔴

**文件**: `src/tongshu/engines/time/calculation_context.py:236`

```python
@property
def bazi_view(self) -> tuple[int, int, int, int]:
    return (
        self.effective_date.year,
        self.effective_date.month,
        self.effective_date.day,
        self.effective_hour,  # ← 只有 hour！
    )
```

**问题**: `effective_minute` 存在于 L1 事实层，但在 bazi_view 投影中丢失。

**影响**:
```
TimeResolver 输出: effective_minute=27
    ↓
bazi_view 输出: (y,m,d,4)  ← minute 丢失
    ↓
BaziAdapter 收到: 只有 hour
```

### 3.2 _compute_with_sxtwl 硬编码问题 🔴

**文件**: `src/tongshu/engines/bazi_engine.py:858-861`

```python
t = sxtwl.Time()
t.Y, t.M, t.D = year, month, day
t.h, t.m, t.s = hour, 0, 0.0  # ← minute 硬编码为 0
birth_jd = sxtwl.toJD(t)
```

**问题**: 月柱边界检查丢失 minute 精度。

**影响场景**:
```
节气: 2024-02-04 04:26:53 (立春)
出生: 04:27:00 (节气后 7秒)

当前算法: t.m=0 → birth_jd = 04:00:00 < 04:26:53
结果: 错误使用前一节月柱（应为立春后月柱）
```

### 3.3 CanonicalBaziChart 契约不完整 🔴

**文件**: `src/tongshu/models/canonical_bazi.py`

```python
@dataclass(frozen=True)
class CanonicalBaziChart:
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar
    day_master: str
    gender: str
    start_age: float
    # ❌ 缺少 birth_datetime 字段
```

**问题**: 下游引擎无法验证出生时间的准确性。

### 3.4 大运数量问题 🔴

**文件**: `src/tongshu/engines/bazi_engine.py:1058`

```python
for decade in range(1, 4):  # ← 只有 3 个
    ...
```

**问题**: 大运应为 10 个，当前只有 3 个。

---

## 四、时间链断裂分析

### 当前数据流

```
ReadingRequest(hour=4, minute=27)
    ↓
TimeResolver.resolve(hour=4, minute=27)
    ↓
ResolvedBirthInstant(effective_minute=27, solar_datetime=04:27:00)
    ↓
CalculationContext.true_solar_datetime=04:27:00 ✅
    ↓
bazi_view=(y,m,d,4) ← 🔴 minute 丢失
    ↓
BaziAdapter.compute(view)  ← 🔴 未传递 birth_datetime
    ↓
BaziEngine._compute_with_sxtwl(y,m,d,hour=4)  ← 🔴 t.m=0
    ↓
月柱边界检查 ← 可能错误
```

### 起运计算路径（独立且正确）

```
_compute_luck_pillars(birth_datetime=...)
    ↓
_calc_start_age(year, month, day, hour, minute, second, direction)
    ↓
birth_dt = datetime(y,m,d,h,minute,second)  ← ✅ H18 正确
    ↓
起运计算 ✅
```

---

## 五、测试覆盖分析

### 当前测试状态

```
60 passed in 1.51s
```

### 测试缺口

| 测试类型 | 状态 | 说明 |
|---------|------|------|
| 小时级精度测试 | ✅ | test_p27g_fix_hour_precision.py (35 tests) |
| 节气边界测试 | ✅ | test_p27g_h17p0_jieqi_algorithm.py (9 tests) |
| 大运算法测试 | ⚠️ | test_p27g_luck_pillar_algorithm.py (16 tests) |
| **分钟级节气边界** | 🔴 | **缺失** |
| **大运数量验证** | 🔴 | **只验证 ≥3，未验证 =10** |

### 大运测试不严格

```python
# tests/test_p27g_luck_pillar_algorithm.py:245
def test_luck_pillar_count(self):
    """大运数量验证（当前实现为3柱用于测试）"""  # ← 注释承认只验证3柱
    ...
    assert len(chart.luck_pillars) >= 3  # ← 宽松验证
```

---

## 六、修复优先级

### P0-1: 修复 BaziAdapter 传递完整时间

```python
# src/tongshu/engines/bazi_adapter.py
def compute(self, ctx: CalculationContext, gender: str) -> BaziChart:
    view = ctx.bazi_view
    return self._engine.compute(
        view,
        gender=gender,
        skip_late_zi=True,
        birth_datetime=ctx.true_solar_datetime,  # ← 新增
    )
```

### P0-2: 修复 _compute_with_sxtwl 使用 minute

```python
# src/tongshu/engines/bazi_engine.py
def _compute_with_sxtwl(self, year, month, day, hour, minute=0, second=0):
    t = sxtwl.Time()
    t.Y, t.M, t.D = year, month, day
    t.h, t.m, t.s = hour, minute, float(second)  # ← 修复
```

### P0-3: 修复 BaziEngine.compute 传递 minute

```python
# src/tongshu/engines/bazi_engine.py
def compute(self, solar_date, gender, skip_late_zi=False, birth_datetime=None):
    year, month, day, hour = solar_date
    minute = birth_datetime.minute if birth_datetime else 0
    second = birth_datetime.second if birth_datetime else 0
    four_pillars = self._compute_with_sxtwl(year, month, day, hour, minute, second)
```

### P0-4: 修复 CanonicalBaziChart 契约

```python
# src/tongshu/models/canonical_bazi.py
@dataclass(frozen=True)
class CanonicalBaziChart:
    # ... existing fields ...
    birth_datetime: Optional[datetime] = None  # ← 新增

    @classmethod
    def from_bazi_chart(cls, chart: "BaziChart"):
        return cls(
            # ... existing fields ...
            birth_datetime=chart.birth_datetime,  # ← 传递
        )
```

### P0-5: 修复大运数量

```python
# src/tongshu/engines/bazi_engine.py:1058
for decade in range(1, 11):  # ← 修复：10个大运
    ...
```

### P0-6: 补充边界测试

```python
def test_jieqi_boundary_with_minute():
    """节气前后1分钟的边界案例"""
    # 立春 2024-02-04 04:26:53
    # 出生 04:25:00 → 使用前一月柱
    # 出生 04:27:00 → 使用当前月柱
    pass
```

---

## 七、Calculation Freeze 裁决

| 项目 | 状态 | 说明 |
|------|------|------|
| 起运算法 | ✅ | H17-P0 + H18 已修复 |
| JD 转换 | ✅ | H17-P0 已修复 |
| 时间链闭合 | 🔴 | Adapter 层丢失 minute |
| 月柱边界精度 | 🔴 | t.m=0 硬编码 |
| Canonical 契约 | 🔴 | 缺少 birth_datetime |
| 大运数量 | 🔴 | 只有3个 |
| 测试覆盖 | 🔴 | 缺少分钟级边界 |

**最终裁决**:

> **🔴 Calculation Freeze: HOLD**
>
> 需完成 P0-1 ~ P0-6 修复后，再进行 Calculation Freeze Gate。

---

## 八、独立性声明

- 本报告仅审计**子平引擎**（zi_ping）
- 不涉及河洛（heluo）、紫薇（ziwei）、盲派（blind）引擎
- 所有发现均为子平层内部问题
- 下游引擎（河洛/紫薇/盲派）应在子平冻结后独立审计

---

**审计完成时间**: 2026-09-05  
**下次行动**: 等待用户裁决是否推进 P0-1 ~ P0-6 修复
