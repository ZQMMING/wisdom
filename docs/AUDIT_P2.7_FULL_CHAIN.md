# 子平引擎完整架构审计（2026-09-05）

## 审计范围
按指定顺序：入口 → 历法权威 → 节气 → 年月日时柱 → 换日 → 真太阳时 → Canonical Contract → 测试 → Proven/Frozen

---

## 1. 排盘入口 Audit

### 1.1 API 层输入契约

```python
# src/tongshu/api/app.py:108
class ReadingRequest(BaseModel):
    birth_date: str      # YYYY-MM-DD
    birth_time: str      # HH:MM（无秒）
    gender: str
    location: str        # IANA timezone 或城市名
```

**问题 P1**：API 只接收 `HH:MM`，无秒级精度。

**影响**：
- 输入层已丢失秒信息
- 下游引擎无法获得秒级精度
- 但分钟级仍可用

### 1.2 Profile Gate 验证

```python
# src/tongshu/api/profile.py:41
PROFILE_REQUIRED_FIELDS = (
    "birth_date", "birth_time", "gender",
    "calendar_system", "timezone", "location",
)
```

✅ 契约完整：6 个必填字段

### 1.3 TimeResolver 接收输入

```python
# src/tongshu/engines/time/resolver.py:88
def resolve(self, *, birth_date: date, hour: int, minute: Optional[int], ...)
```

✅ 接收 `hour` + `minute`（可选）
⚠️ `minute=None` 时假设时辰中点（30分）

---

## 2. 历法权威 Audit

### 2.1 CalculationContext 定义

```python
# src/tongshu/engines/time/calculation_context.py:83
@dataclass(frozen=True)
class ResolvedBirthInstant:
    effective_date: date
    effective_hour: int
    effective_minute: int      # ✅ 有分钟
    civil_datetime: Optional[datetime] = None
    solar_datetime: Optional[datetime] = None  # ✅ 有真太阳时
```

✅ L1 事实层包含完整时间信息

### 2.2 视图投影设计

```python
# calculation_context.py:236
@property
def bazi_view(self) -> tuple[int, int, int, int]:
    return (
        self.effective_date.year,
        self.effective_date.month,
        self.effective_date.day,
        self.effective_hour,  # ← 只有 hour！
    )
```

🔴 **问题 P2：bazi_view 丢失 minute**

这是时间链断裂的核心位置：
- `ResolvedBirthInstant` 有 `effective_minute`
- `CalculationContext` 继承并保留它
- 但 `bazi_view` 只返回 4-tuple `(y, m, d, h)`

---

## 3. 节气 Audit

### 3.1 JD 转换器

```python
# src/tongshu/engines/time/jd_converter.py
def jd_to_datetime(jd: float) -> datetime:
    # sxtwl's frac directly represents Beijing Time
    total_seconds = frac * 86400.0
    hours = int(total_seconds // 36400)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
```

✅ H17-P0 修复后正确：直接转换，无需时区偏移

### 3.2 节气筛选逻辑

```python
# bazi_engine.py:935
def _is_jie(self, day_obj) -> bool:
    if day_obj.hasJieQi():
        return day_obj.getJieQi() % 2 == 1  # 奇数=节
```

✅ 正确区分 节（奇数）vs 中气（偶数）

### 3.3 起运算法

```python
# bazi_engine.py:942
def _calc_start_age(self, year, month, day, hour, minute, second, direction):
    birth_dt = datetime(year, month, day, hour, minute, second)  # ✅ H18 修复
```

✅ 支持 minute/second 参数

---

## 4. 年月日时柱 Audit

### 4.1 _compute_with_sxtwl

```python
# bazi_engine.py:858
t = sxtwl.Time()
t.Y, t.M, t.D = year, month, day
t.h, t.m, t.s = hour, 0, 0.0  # ← 🔴 minute 硬编码为 0
birth_jd = sxtwl.toJD(t)
```

🔴 **问题 P3：月柱边界检查丢失 minute**

如果出生时间精确到分钟（如 04:25），当前算法无法判断是否在节气（04:26:53）前。

### 4.2 时柱计算

```python
# bazi_engine.py:889
hour_gz = day_idx.getHourGZ(hour, True)
```

✅ sxtwl 接受 hour 参数，无需 minute（时柱以时辰为单位）

---

## 5. 换日 Audit

### 5.1 Day Boundary Policy

```python
# calculation_context.py:145
if apparent.hour >= DAY_BOUNDARY:  # DAY_BOUNDARY = 23
    effective_date = effective_date + timedelta(days=1)
```

✅ 23:00 换日逻辑正确

### 5.2 BaziAdapter 转发

```python
# bazi_adapter.py:44
view = ctx.bazi_view
return self._engine.compute(view, gender=gender, skip_late_zi=True)
```

✅ 正确使用 `skip_late_zi=True` 避免双重换日

---

## 6. 真太阳时 Audit

### 6.1 TimeResolver 计算链

```python
# resolver.py:116
local_dt = datetime(year, month, day, hour, minute, tzinfo=zone)
utc_offset_min = utc_offset_minutes(local_dt)
longitude_correction = longitude_correction_minutes(loc.longitude, ref_meridian)
eot = round(equation_of_time(birth_date), 2)
apparent = local_dt + timedelta(minutes=total)
```

✅ 真太阳时计算完整：时区偏移 + 经度校正 + 均时差

### 6.2 输出完整性

```python
# calculation_context.py:86
class ResolvedBirthInstant:
    civil_datetime: Optional[datetime] = None   # 墙钟
    solar_datetime: Optional[datetime] = None   # 真太阳时 ✅
    effective_minute: int  # ✅ 有分钟
```

✅ L1 事实层完整保留所有时间信息

---

## 7. Canonical Contract Audit

### 7.1 BaziChart 定义

```python
# bazi_engine.py:219
@dataclass(frozen=True)
class BaziChart:
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar
    day_master: str
    luck_pillars: list
    start_age: float = 0.0
    birth_datetime: Optional[datetime] = None  # ✅ H18 添加
```

✅ H18 已添加 `birth_datetime` 字段

### 7.2 CanonicalBaziChart 定义

```python
# canonical_bazi.py:30
@dataclass(frozen=True)
class CanonicalBaziChart:
    year_pillar: Pillar
    month_pillar: Pillar
    day_pillar: Pillar
    hour_pillar: Pillar
    day_master: str
    gender: str
    start_age: float
    # ❌ 缺少 birth_datetime 字段！
```

🔴 **问题 P4：CanonicalBaziChart 缺少 birth_datetime**

这是下游引擎无法验证时间准确性的根本原因。

### 7.3 转换契约

```python
# canonical_bazi.py:69
def from_bazi_chart(cls, chart: "BaziChart") -> "CanonicalBaziChart":
    return cls(
        year_pillar=chart.year_pillar,
        # ...
        start_age=chart.start_age,
        # ❌ 未传递 birth_datetime
    )
```

🔴 **问题 P5：from_bazi_chart 未传递 birth_datetime**

---

## 8. 测试 Audit

### 8.1 现有测试覆盖

| 测试文件 | 测试数 | 覆盖范围 |
|---------|--------|---------|
| test_p27g_fix_hour_precision.py | 35 | 小时级精度 |
| test_p27g_h17p0_jieqi_algorithm.py | 9 | 节气边界 |
| test_p27g_luck_pillar_algorithm.py | 16 | 大运算法 |
| test_heluo_canonical.py | 13 | 河洛集成 |

**总计：60 passed**

### 8.2 缺失的测试

🔴 **测试缺口 T1**：分钟级节气边界测试

```python
# 应测试但缺失的案例：
# 节气：2024-02-04 04:26:53
# 出生：2024-02-04 04:25:00（节气前 1分53秒）→ 应使用前一月柱
# 出生：2024-02-04 04:27:00（节气后 7秒）→ 应使用当前月柱
```

🔴 **测试缺口 T2**：端到端时间链测试

```python
# 应测试但缺失：
# TimeResolver → CalculationContext → BaziAdapter → BaziEngine → BaziChart
# 验证 minute 在整条链中不丢失
```

---

## 9. Proven/Frozen 状态评估

### 当前状态

| 组件 | 状态 | 说明 |
|------|------|------|
| API 输入契约 | ✅ | birth_date + birth_time (HH:MM) |
| TimeResolver 计算 | ✅ | 真太阳时 + 经度校正 + EoT |
| CalculationContext L1 | ✅ | 完整时间事实层 |
| bazi_view 投影 | 🔴 | 只传 hour，minute 丢失 |
| _compute_with_sxtwl | 🔴 | 硬编码 t.m = 0 |
| _calc_start_age | ✅ | 支持 minute/second |
| BaziChart | ✅ | 有 birth_datetime 字段 |
| CanonicalBaziChart | 🔴 | 缺少 birth_datetime 字段 |
| 分钟级边界测试 | 🔴 | 缺失 |

### Calculation Freeze 门禁

```
❌ 不满足冻结条件：

1. 时间链未闭合：minute 在 Adapter 层丢失
2. Canonical 契约不完整：缺少 birth_datetime
3. 边界测试不充分：分钟级节气边界未验证
```

---

## 修复优先级

### P0-1：修复 BaziAdapter 传递完整时间

```python
# src/tongshu/engines/bazi_adapter.py
def compute(self, ctx: CalculationContext, gender: str) -> BaziChart:
    view = ctx.bazi_view
    # H18-FIX: 传递完整 solar_datetime
    return self._engine.compute(
        view,
        gender=gender,
        skip_late_zi=True,
        birth_datetime=ctx.solar_datetime,  # ← 新增
    )
```

### P0-2：修复 _compute_with_sxtwl 使用 minute

```python
# src/tongshu/engines/bazi_engine.py
def _compute_with_sxtwl(self, year, month, day, hour, minute=0, second=0):
    # ...
    t = sxtwl.Time()
    t.Y, t.M, t.D = year, month, day
    t.h, t.m, t.s = hour, minute, float(second)  # ← 修复
```

### P0-3：修复 CanonicalBaziChart 契约

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

### P0-4：补充边界测试

```python
def test_jieqi_boundary_with_minute():
    """节气前后1分钟的边界案例"""
    # 立春 2024-02-04 04:26:53
    # 出生 04:25:00 → 使用前一月柱
    # 出生 04:27:00 → 使用当前月柱
    pass
```

---

## 结论

**Calculation Freeze：HOLD**

根本原因：时间链在 Adapter 层断裂，minute 信息丢失，导致：
1. 月柱边界检查不精确（minute=0）
2. 起运计算可能偏差（虽然当前案例少）
3. 下游引擎无法验证时间准确性

建议：先完成 P0-1 ~ P0-4 修复，再进行 Calculation Freeze Gate。
