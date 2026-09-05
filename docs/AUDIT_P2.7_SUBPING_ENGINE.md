# 子平引擎架构审计（2026-09-05）

## 执行范围
- 时间链：`BirthInput → TimeResolver → BaziAdapter → BaziEngine → BaziChart`
- 数据契约：`CanonicalBaziChart` 类型定义
- 下游消费：是否正确使用时间事实

---

## 审计结果摘要

| 项目 | 状态 | 说明 |
|------|------|------|
| TimeResolver 计算真太阳时 | ✅ | `effective_minute` 正确计算 |
| BaziAdapter 接收 Context | ✅ | 正常接收 `CalculationContext` |
| **BaziAdapter 传递 minute** | 🔴 | **丢失！** 只传 `bazi_view`（无 minute） |
| BaziEngine 接收 solar_date | ✅ | 正常接收 `(year, month, day, hour)` |
| **BaziEngine 内部构造 datetime** | 🔴 | **覆盖！** 用 `hour, 0, 0` 而非 ctx 的 minute |
| `_compute_with_sxtwl` 时间处理 | 🔴 | **t.m = 0** 硬编码，丢失 minute |
| `_calc_start_age` 分钟支持 | ✅ | H18 已支持 minute/second 参数 |
| **CanonicalBaziChart 时间字段** | 🔴 | **缺少 `birth_datetime` 字段** |
| 下游引擎消费 CanonicalBaziChart | ⚠️ | 无法获取精确出生时间 |

---

## 核心问题：时间语义断层

### 问题1：BaziAdapter 丢失 minute

```python
# src/tongshu/engines/time/calculation_context.py:236
@property
def bazi_view(self) -> tuple[int, int, int, int]:
    return (
        self.effective_date.year,
        self.effective_date.month,
        self.effective_date.day,
        self.effective_hour,  # ← 只有 hour！没有 minute
    )
```

**影响**：
- `TimeResolver` 计算出 `effective_minute`（如 30 分）
- `CalculationContext.bazi_view` 只返回 `(2024, 2, 4, 12)`
- `BaziAdapter.compute(ctx)` 调用 `ctx.bazi_view` → minute 丢失
- 下游引擎无法知道准确分钟

### 问题2：BaziEngine 构造 datetime 时强制截断

```python
# src/tongshu/engines/bazi_engine.py:770-773
if birth_datetime is None:
    from datetime import datetime as _dt
    birth_datetime = _dt(year, month, day, hour, 0, 0)  # ← minute 强制为 0
```

**影响**：
- 即使上游有 minute 信息，这里也会丢失
- 月柱边界检查（line 860）也硬编码 `t.m = 0`

### 问题3：_compute_with_sxtwl 硬编码 t.m = 0

```python
# src/tongshu/engines/bazi_engine.py:858-860
t = sxtwl.Time()
t.Y, t.M, t.D = year, month, day
t.h, t.m, t.s = hour, 0, 0.0  # ← 分钟硬编码为 0
birth_jd = sxtwl.toJD(t)
```

**影响**：
- 月柱边界检查只用小时，不使用分钟
- 如果出生时间精确到分钟（如 04:26），算法无法判断是否在节气前

### 问题4：CanonicalBaziChart 缺少时间字段

```python
# src/tongshu/models/canonical_bazi.py
class CanonicalBaziChart:
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar
    day_master: str
    gender: str
    start_age: float
    # ← 没有 birth_datetime 字段！
```

**影响**：
- 下游引擎（盲派、河洛）无法获取精确出生时间
- 只能从 `start_age` 反推，无法验证
- 时间权威链断裂

---

## 时间链现状图

```
┌─────────────────────────────────────────────────────────────────┐
│ BirthInput                                                      │
│   birth_civil_datetime: 2024-02-04 12:30:45 Beijing             │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ TimeResolver.resolve()                                          │
│   effective_datetime: 2024-02-04 12:45:12 (真太阳时)            │
│   effective_date: 2024-02-04                                    │
│   effective_hour: 12                                            │
│   effective_minute: 45  ← 精确计算 ✅                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ CalculationContext                                               │
│   subject: SubjectContext(gender="male")                        │
│   bazi_view: (2024, 2, 4, 12)  ← 只返回 hour，minute丢失 🔴    │
│   effective_minute: 45  ← 存在于 context，但未传递给下游         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ BaziAdapter.compute(ctx)                                        │
│   view = ctx.bazi_view  ← (2024, 2, 4, 12) 无 minute          │
│   engine.compute(view, gender=...)                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ BaziEngine.compute(solar_date=(2024, 2, 4, 12))                │
│   birth_datetime = datetime(2024, 2, 4, 12, 0, 0)  ← minute=0 🔴│
│                                                                   │
│   _compute_with_sxtwl(year, month, day, hour):                  │
│     t.h, t.m, t.s = 12, 0, 0.0  ← 硬编码 minute=0 🔴           │
│                                                                   │
│   _calc_start_age(year, month, day, hour, minute, second):      │
│     参数有 minute/second，但调用方传入 0, 0 🔴                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ BaziChart                                                        │
│   year_pillar, month_pillar, day_pillar, hour_pillar            │
│   start_age: 8.5                                                │
│   birth_datetime: 2024-02-04 12:00:00  ← minute=0 🔴            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ CanonicalBaziChart.from_bazi_chart(chart)                       │
│   year_pillar, month_pillar, day_pillar, hour_pillar            │
│   day_master, gender, start_age                                 │
│   birth_datetime: 未传递！🔴                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

## 影响分析

### 1. 月柱边界计算不精确

如果出生时间在节气前后几分钟：
```
节气时刻：2024-02-04 04:26:53
出生时间：2024-02-04 04:25:00（节气前 1 分 53 秒）

当前算法：
  t.h, t.m, t.s = 4, 0, 0.0  ← minute=0
  birth_jd = 04:00:00 < 04:26:53 → 使用前一月柱 ❌

正确算法：
  t.h, t.m, t.s = 4, 25, 0.0  ← 使用实际 minute
  birth_jd = 04:25:00 < 04:26:53 → 使用前一月柱 ✅
```

虽然当前边界案例较少，但**契约不闭合**。

### 2. 起运计算缺少分钟精度

当前 `start_age` 计算使用 `minute=0`，如果有分钟级边界案例会不准确。

### 3. 下游引擎无法获取精确时间

`CanonicalBaziChart` 没有时间字段，下游引擎无法：
- 验证起运计算是否正确
- 自己做高精度起运计算
- 处理边界案例

---

## 修复建议

### 优先级 P0-1：传递 minute 到 BaziEngine

**修改点1：BaziAdapter**
```python
# src/tongshu/engines/bazi_adapter.py
def compute(self, ctx: CalculationContext, gender: str) -> BaziChart:
    view = ctx.bazi_view
    # H18-FIX: 传递完整时间信息
    birth_datetime = ctx.solar_datetime  # 或构造完整 datetime
    return self._engine.compute(
        view, 
        gender=gender, 
        skip_late_zi=True,
        birth_datetime=birth_datetime,  # ← 传递完整时间
    )
```

**修改点2：BaziEngine.compute()**
```python
def compute(self, solar_date, gender, skip_late_zi=False, birth_datetime=None):
    year, month, day, hour = solar_date
    
    # H18-FIX: 优先使用传入的完整 datetime
    if birth_datetime is None:
        birth_datetime = datetime(year, month, day, hour, 0, 0)
    
    # 传递 minute/second 给子方法
    four_pillars = self._compute_with_sxtwl(
        year, month, day, hour, 
        minute=birth_datetime.minute,  # ← 新增参数
        second=birth_datetime.second,  # ← 新增参数
    )
```

**修改点3：_compute_with_sxtwl()**
```python
def _compute_with_sxtwl(self, year, month, day, hour, minute=0, second=0):
    # ...
    t = sxtwl.Time()
    t.Y, t.M, t.D = year, month, day
    t.h, t.m, t.s = hour, minute, float(second)  # ← 使用传入值
    # ...
```

### 优先级 P0-2：CanonicalBaziChart 添加时间字段

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
    birth_datetime: Optional[datetime] = None  # ← 新增
```

---

## 测试验证计划

### 1. 边界案例测试
```python
def test_jieqi_boundary_with_minute():
    """节气前后1分钟的边界案例"""
    # 出生：2024-02-04 04:25:00（立春 04:26:53 前 1分53秒）
    # 应使用前一月柱
    pass

def test_jieqi_boundary_after_minute():
    """节气后1分钟的边界案例"""
    # 出生：2024-02-04 04:27:00（立春后 7秒）
    # 应使用当前月柱
    pass
```

### 2. 端到端验证
```python
def test_full_chain_preserves_minute():
    """验证完整链路保留 minute 信息"""
    ctx = resolver.resolve(
        birth_date=date(2024, 2, 4),
        hour=4, minute=25,  # 节气前
        location="beijing"
    )
    chart = adapter.compute(ctx, gender="male")
    assert chart.birth_datetime.minute == 25  # ← 验证传递
    pass
```

---

## 结论

**Calculation Freeze 条件未满足**：

1. ✅ 算法正确性：已验证（H17-P0, H18）
2. ❌ 时间权威闭合：**未完成**（minute 在 Adapter 层丢失）
3. ❌ Canonical 契约完整：**未完成**（缺少 birth_datetime）
4. ❌ 边界案例验证：**未完成**（分钟级节气边界未测试）

**下一步行动**：
- P0-1：修复 BaziAdapter 传递 minute
- P0-2：修复 CanonicalBaziChart 添加时间字段
- P0-3：补充分钟级边界测试

**冻结门禁**：以上三项完成前，不允许进入 Calculation Freeze。
