# 子平引擎独立审计报告（P0）

**审计范围**: 子平引擎全链（不涉及河洛、紫薇、盲派）  
**审计日期**: 2026-09-05  
**审计原则**: 先查排盘入口和数据契约，再向后审计

---

## 执行摘要

| 层级 | 文件 | 状态 | 关键发现 |
|------|------|------|---------|
| API 入口 | `api/app.py` | ✅ | ReadingRequest 接收 hour + optional minute |
| TimeResolver | `time/resolver.py` | ✅ | 真太阳时计算完整，保留 minute |
| L1 事实层 | `time/calculation_context.py` | ⚠️ | bazi_view 只传 hour |
| Adapter | `engines/bazi_adapter.py` | 🔴 | 未传递 birth_datetime |
| BaziEngine | `engines/bazi_engine.py` | 🔴 | 月柱检查硬编码 minute=0，大运只有3个 |
| Canonical | `models/canonical_bazi.py` | 🔴 | 缺少 birth_datetime 字段 |
| 测试 | `tests/test_p27g*.py` | ⚠️ | 测试通过但覆盖不完整 |

**Calculation Freeze: 🔴 HOLD**

---

## 一、入口层 Audit

### 1.1 ReadingRequest 输入契约

```python
# src/tongshu/api/app.py:108
class ReadingRequest(BaseModel):
    birth_date: str           # YYYY-MM-DD ✅
    hour: int                 # 0-23 ✅
    birth_minute: Optional[int]  # 0-59, None=时辰中点 ✅
    gender: str               # male/female ✅
    location: Optional[str]
    timezone: Optional[str]
```

**✅ 契约完整**

### 1.2 TimeResolver 接收 minute

```python
# src/tongshu/engines/time/resolver.py:88
def resolve(self, *, birth_date: date, hour: int, minute: Optional[int], ...)
```

**✅ 正确接收 minute**

---

## 二、历法权威层 Audit

### 2.1 ResolvedBirthInstant L1 事实层

```python
# src/tongshu/engines/time/calculation_context.py:83
class ResolvedBirthInstant:
    effective_date: date
    effective_hour: int
    effective_minute: int       # ✅ 有分钟
    solar_datetime: datetime    # ✅ 有完整真太阳时
    civil_datetime: datetime    # ✅ 有完整墙钟时间
```

**✅ L1 事实层完整**

### 2.2 CalculationContext 视图投影 🔴

```python
# src/tongshu/engines/time/calculation_context.py:236
@property
def bazi_view(self) -> tuple[int, int, int, int]:
    return (
        self.effective_date.year,
        self.effective_date.month,
        self.effective_date.day,
        self.effective_hour,  # ← 🔴 只有 hour，minute 丢失！
    )
```

**🔴 问题 P1：bazi_view 只传 hour**

这是时间链断裂的核心位置。

---

## 三、适配器层 Audit 🔴

### 3.1 BaziAdapter 当前实现

```python
# src/tongshu/engines/bazi_adapter.py:33-45
def compute(self, ctx: CalculationContext, gender: Literal["male", "female"] = "male") -> BaziChart:
    view = ctx.bazi_view
    return self._engine.compute(view, gender=gender, skip_late_zi=True)
```

**🔴 问题 P2：未传递完整 birth_datetime**

缺少：
- `birth_datetime=ctx.true_solar_datetime`
- 无法让 BaziEngine 获得精确时间

---

## 四、BaziEngine 层 Audit 🔴

### 4.1 compute 方法签名 ✅

```python
# src/tongshu/engines/bazi_engine.py:748-753
def compute(self, solar_date, gender, skip_late_zi=False, birth_datetime=None):
```

**✅ 已支持 birth_datetime 参数（H18）**

### 4.2 _compute_with_sxtwl 月柱边界检查 🔴

```python
# src/tongshu/engines/bazi_engine.py:858-861
t = sxtwl.Time()
t.Y, t.M, t.D = year, month, day
t.h, t.m, t.s = hour, 0, 0.0  # ← 🔴 minute 硬编码为 0
birth_jd = sxtwl.toJD(t)
```

**🔴 问题 P3：月柱边界检查丢失 minute 精度**

影响场景：
```
节气：2024-02-04 04:26:53（立春）
出生：04:27:00（节气后 7秒）

当前算法：t.m=0 → birth_jd = 04:00:00 < 04:26:53
结果：错误使用前一月柱（应为立春后月柱）
```

### 4.3 _calc_start_age 起运算法 ✅

```python
# src/tongshu/engines/bazi_engine.py:942-976
def _calc_start_age(self, year, month, day, hour, minute, second, direction):
    birth_dt = datetime(year, month, day, hour, minute, second)  # ✅ H18
```

**✅ H18 修复：支持 minute/second**

### 4.4 _compute_luck_pillars 大运算法 🔴

```python
# src/tongshu/engines/bazi_engine.py:1058
for decade in range(1, 4):  # ← 🔴 只有3个大运！
    ...
    luck_pillars.append(lp)
```

**🔴 问题 P4：大运数量应为10个，当前只有3个**

验证：
```python
>>> c.luck_pillars
[BaziChart.luck_pillars[0], BaziChart.luck_pillars[1], BaziChart.luck_pillars[2]]
>>> len(c.luck_pillars)
3  # 应为 10
```

---

## 五、Canonical Contract Audit 🔴

### 5.1 BaziChart 定义 ✅

```python
# src/tongshu/engines/bazi_engine.py:232
class BaziChart:
    ...
    birth_datetime: Optional[datetime] = None  # ✅ H18 添加
```

**✅ BaziChart 有 birth_datetime 字段**

### 5.2 CanonicalBaziChart 定义 🔴

```python
# src/tongshu/models/canonical_bazi.py:48-54
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

**🔴 问题 P5：CanonicalBaziChart 缺少 birth_datetime**

### 5.3 from_bazi_chart 转换方法 🔴

```python
# src/tongshu/models/canonical_bazi.py:69-77
@classmethod
def from_bazi_chart(cls, chart: "BaziChart") -> "CanonicalBaziChart":
    return cls(
        year_pillar=chart.year_pillar,
        month_pillar=chart.month_pillar,
        day_pillar=chart.day_pillar,
        hour_pillar=chart.hour_pillar,
        day_master=chart.day_master,
        gender=chart.gender,
        start_age=chart.start_age,
        # ❌ 未传递 birth_datetime
    )
```

**🔴 问题 P6：from_bazi_chart 未传递 birth_datetime**

---

## 六、测试 Audit

### 6.1 当前测试状态

```
60 passed in 1.98s
```

### 6.2 测试覆盖分析

| 测试文件 | 数量 | 状态 | 问题 |
|---------|------|------|------|
| test_p27g_fix_hour_precision.py | 35 | ✅ | 仅测试小时级 |
| test_p27g_h17p0_jieqi_algorithm.py | 9 | ✅ | 无分钟级边界 |
| test_p27g_luck_pillar_algorithm.py | 16 | ⚠️ | 大运验证宽松 |
| **总计** | **60** | | |

### 6.3 测试缺口 🔴

**T1：大运数量测试不严格**

```python
# tests/test_p27g_luck_pillar_algorithm.py:245
def test_luck_pillar_count(self):
    """大运数量验证（当前实现为3柱用于测试）"""  # ← 注释承认只验证3柱
    ...
    assert len(chart.luck_pillars) >= 3  # ← 宽松验证
```

**T2：分钟级节气边界测试缺失**

```python
# 应测试但缺失：
# 节气：2024-02-04 04:26:53（立春）
# 出生：04:25:00 → 应使用前一月柱
# 出生：04:27:00 → 应使用当前月柱
```

---

## 七、时间链断裂分析

### 当前时间流

```
API (hour=4, minute=27)
    ↓ ReadingRequest
TimeResolver.resolve(hour=4, minute=27)
    ↓ solar_datetime=04:27:00, effective_minute=27
ResolvedBirthInstant
    ↓ bazi_view=(y,m,d,4) ← 🔴 minute 在这里丢失！
CalculationContext
    ↓ compute((y,m,d,4), gender)
BaziAdapter
    ↓ _compute_with_sxtwl(y, m, d, hour=4)
BaziEngine
    ↓ t.h, t.m, t.s = 4, 0, 0 ← 硬编码 minute=0
月柱边界检查 ← 可能错误
```

### 起运计算路径（独立且正确）

```
_compute_luck_pillars(birth_datetime=...)
    ↓ _calc_start_age(year, month, day, hour, minute, second, direction)
    ↓ birth_dt = datetime(y,m,d,h,minute,second) ← ✅ H18 正确
起运计算 ✅
```

**关键发现**：起运计算已正确（H18），但月柱计算未闭合（P3）

---

## 八、Calculation Freeze 门禁评估

| 项目 | 状态 | 说明 |
|------|------|------|
| API 输入契约 | ✅ | hour + optional minute |
| TimeResolver 真太阳时 | ✅ | 完整校正链 |
| L1 事实层 | ⚠️ | 有 effective_minute，但 bazi_view 丢失 |
| BaziAdapter | 🔴 | 未传递 birth_datetime |
| _compute_with_sxtwl | 🔴 | 硬编码 t.m=0 |
| _calc_start_age | ✅ | H18 支持 minute/second |
| BaziChart | ✅ | 有 birth_datetime |
| CanonicalBaziChart | 🔴 | 缺少 birth_datetime |
| 大运数量 | 🔴 | 只有3个，应为10个 |
| 分钟级边界测试 | 🔴 | 缺失 |

**最终裁决**：

> **🔴 Calculation Freeze: HOLD**

---

## 九、修复优先级

### P0-1：修复 BaziAdapter 传递完整时间

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

### P0-2：修复 _compute_with_sxtwl 使用 minute

```python
# src/tongshu/engines/bazi_engine.py
def _compute_with_sxtwl(self, year, month, day, hour, minute=0, second=0):
    t = sxtwl.Time()
    t.Y, t.M, t.D = year, month, day
    t.h, t.m, t.s = hour, minute, float(second)  # ← 修复
```

### P0-3：修复 BaziEngine.compute 传递 minute

```python
# src/tongshu/engines/bazi_engine.py
def compute(self, solar_date, gender, skip_late_zi=False, birth_datetime=None):
    year, month, day, hour = solar_date
    minute = birth_datetime.minute if birth_datetime else 0
    second = birth_datetime.second if birth_datetime else 0
    four_pillars = self._compute_with_sxtwl(year, month, day, hour, minute, second)
```

### P0-4：修复 CanonicalBaziChart 契约

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

### P0-5：修复大运数量

```python
# src/tongshu/engines/bazi_engine.py:1058
for decade in range(1, 11):  # ← 修复：10个大运
    ...
```

### P0-6：补充边界测试

```python
def test_jieqi_boundary_with_minute():
    """节气前后1分钟的边界案例"""
    # 立春 2024-02-04 04:26:53
    # 出生 04:25:00 → 使用前一月柱
    # 出生 04:27:00 → 使用当前月柱
    pass
```

---

## 十、结论

**子平引擎存在 3 个核心阻塞点：**

1. **时间链断裂**：minute 在 Adapter 层丢失
2. **月柱边界不精确**：硬编码 t.m=0
3. **大运不完整**：只有3个，应为10个

**修复路径**：完成 P0-1 ~ P0-6 后，再进行 Calculation Freeze Gate。

---

**审计员**: @bazi  
**独立性声明**: 本报告仅审计子平引擎，不涉及河洛、紫薇、盲派引擎。  
**数据来源**: 源代码审计 + 测试执行验证
