# 子平引擎完整架构审计（P0）—— 基于实际代码

**审计日期**: 2026-09-05  
**审计范围**: 入口 → 历法权威 → 节气 → 年月日时柱 → 换日 → 真太阳时 → Canonical Contract → 测试 → Proven/Frozen  
**原则**: 先查排盘入口和数据契约，再向后审计

---

## 执行摘要

| 审计项 | 状态 | 说明 |
|--------|------|------|
| API 输入契约 | ✅ | ReadingRequest 接收 hour + optional minute |
| TimeResolver 真太阳时 | ✅ | 完整校正链（时区+经度+EoT） |
| L1 事实层 (CalculationContext) | ✅ | effective_minute + solar_datetime 完整 |
| _calc_start_age 起运算法 | ✅ | H18 已支持 minute/second |
| BaziChart birth_datetime | ✅ | H18 已添加字段 |
| **bazi_view 投影** | 🔴 | **只返回 (y,m,d,h)，minute 丢失** |
| **_compute_with_sxtwl** | 🔴 | **硬编码 t.m=0，月柱边界检查不精确** |
| **CanonicalBaziChart 契约** | 🔴 | **缺少 birth_datetime 字段** |
| **大运数量** | 🔴 | **只有3个大运，应为10个** |
| 分钟级边界测试 | 🔴 | 缺失 |
| Calculation Freeze | 🔴 HOLD | 需修复 P0-1 ~ P0-4 |

---

## 一、排盘入口 Audit

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

**✅ API 层契约完整**

### 1.2 TimeResolver 接收 minute

```python
# src/tongshu/engines/time/resolver.py:88
def resolve(self, *, birth_date: date, hour: int, minute: Optional[int], ...)
```

**✅ 接收并保留 minute**

---

## 二、历法权威 Audit

### 2.1 ResolvedBirthInstant L1 事实层

```python
# src/tongshu/engines/time/calculation_context.py:83
class ResolvedBirthInstant:
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

**🔴 问题 P1：bazi_view 只传 hour，minute 在 Adapter 层丢失**

这是时间链断裂的核心位置：
- `ResolvedBirthInstant` 有 `effective_minute`
- `CalculationContext` 继承并保留它
- 但 `bazi_view` 只返回 4-tuple `(y, m, d, h)`

---

## 三、节气算法 Audit

### 3.1 JD 转换器（H17-P0 修复后）✅

```python
# src/tongshu/engines/time/jd_converter.py
def jd_to_datetime(jd: float) -> datetime:
    total_seconds = frac * 86400.0  # sxtwl frac = Beijing Time fraction
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)
    seconds = int(total_seconds % 60)
```

**✅ H17-P0 修复正确：直接转换，无需时区偏移**

### 3.2 节/中气筛选 ✅

```python
# src/tongshu/engines/bazi_engine.py:931
def _is_jie(self, day_obj) -> bool:
    if day_obj.hasJieQi():
        return day_obj.getJieQi() % 2 == 1  # 奇数=节
```

**✅ 正确区分节（奇数）vs 中气（偶数）**

### 3.3 起运算法（H18 修复后）✅

```python
# src/tongshu/engines/bazi_engine.py:942
def _calc_start_age(self, year, month, day, hour, minute, second, direction):
    birth_dt = datetime(year, month, day, hour, minute, second)  # ✅ H18
```

**✅ H18 修复：支持 minute/second**

---

## 四、年月日时柱计算 Audit

### 4.1 _compute_with_sxtwl 🔴

```python
# src/tongshu/engines/bazi_engine.py:858
def _compute_with_sxtwl(self, year, month, day, hour):
    t = sxtwl.Time()
    t.Y, t.M, t.D = year, month, day
    t.h, t.m, t.s = hour, 0, 0.0  # ← 🔴 minute 硬编码为 0
    birth_jd = sxtwl.toJD(t)
```

**🔴 问题 P2：月柱边界检查丢失 minute 精度**

影响场景：
```
节气：2024-02-04 04:26:53
出生：04:27:00（节气后 7秒）

当前：t.m=0 → birth_jd = 04:00:00 < 04:26:53
结果：错误使用前一月柱（应为立春后月柱）
```

### 4.2 日柱、时柱 ✅

```python
# bazi_engine.py:886-890
day_idx = sxtwl.fromSolar(year, month, day)
gz_day = day_idx.getDayGZ()
hour_gz = day_idx.getHourGZ(hour, True)  # 只接受 hour ✅
```

**✅ 日柱、时柱只需 hour，无需 minute**

---

## 五、换日逻辑 Audit ✅

### 5.1 TimeResolver 23:00 换日

```python
# resolver.py:143
if apparent.hour >= DAY_BOUNDARY:  # DAY_BOUNDARY = 23
    effective_date = effective_date + timedelta(days=1)
```

**✅ 正确：23:00-23:59 属于次日**

### 5.2 BaziAdapter 转发 ✅

```python
# bazi_adapter.py:44
view = ctx.bazi_view
return self._engine.compute(view, gender=gender, skip_late_zi=True)
```

**✅ 使用 skip_late_zi=True 避免双重换日**

---

## 六、真太阳时 Audit ✅

### 6.1 TimeResolver 计算链

```python
# resolver.py:116-127
local_dt = datetime(year, month, day, hour, minute, tzinfo=zone)
utc_offset_min = utc_offset_minutes(local_dt)
longitude_correction = longitude_correction_minutes(loc.longitude, ref_meridian)
eot = round(equation_of_time(birth_date), 2)
apparent = local_dt + timedelta(minutes=total)
```

**✅ 真太阳时计算完整**

---

## 七、Canonical Contract Audit

### 7.1 BaziChart ✅

```python
# bazi_engine.py:232
class BaziChart:
    ...
    birth_datetime: Optional[datetime] = None  # ✅ H18 添加
```

**✅ BaziChart 有 birth_datetime 字段**

### 7.2 CanonicalBaziChart 🔴

```python
# canonical_bazi.py:48-54
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

**🔴 问题 P3：CanonicalBaziChart 缺少 birth_datetime**

### 7.3 转换方法 🔴

```python
# canonical_bazi.py:56-77
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

**🔴 问题 P4：from_bazi_chart 未传递 birth_datetime**

---

## 八、大运时间轴 Audit 🔴

### 8.1 当前实现

```python
# bazi_engine.py:1058
for decade in range(1, 4):  # 只有3个大运！
    ...
    luck_pillars.append(lp)
```

**🔴 问题 P5：大运循环只有 range(1, 4)，只生成3个大运**

验证：
```python
>>> c.luck_pillars
[BaziChart.luck_pillars[0], BaziChart.luck_pillars[1], BaziChart.luck_pillars[2]]
>>> len(c.luck_pillars)
3  # 应为 10
```

### 8.2 缺少时间信息

```python
# BaziChart.luck_pillars 只包含 Pillar 对象
# 没有 start_age, end_age, start_date, end_date
```

**🔴 问题 P6：大运缺少时间轴信息**

---

## 九、测试 Audit

### 9.1 当前测试状态

```
60 passed (test_p27g*.py)
```

### 9.2 测试覆盖分析

| 测试文件 | 数量 | 状态 |
|---------|------|------|
| test_p27g_fix_hour_precision.py | 35 | ✅ 通过 |
| test_p27g_h17p0_jieqi_algorithm.py | 9 | ✅ 通过 |
| test_p27g_luck_pillar_algorithm.py | 16 | ⚠️ 通过但验证不完整 |
| test_heluo_canonical.py | 13 | ✅ 通过 |

### 9.3 测试缺口

**🔴 T1：大运数量测试不严格**

```python
# tests/test_p27g_luck_pillar_algorithm.py:245
def test_luck_pillar_count(self):
    """大运数量验证（当前实现为3柱用于测试）"""  # ← 注释承认只验证3柱
    ...
    assert len(chart.luck_pillars) >= 3  # ← 宽松验证
```

**🔴 T2：分钟级节气边界测试缺失**

```python
# 应测试但缺失：
# 节气：2024-02-04 04:26:53
# 出生：04:25:00 → 应使用前一月柱
# 出生：04:27:00 → 应使用当前月柱
```

---

## 十、时间链断裂分析

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

**关键发现**：起运计算已正确（H18），但月柱计算未闭合（P2）

---

## 十一、Calculation Freeze 门禁评估

| 项目 | 状态 | 说明 |
|------|------|------|
| API 输入契约 | ✅ | hour + optional minute |
| TimeResolver 真太阳时 | ✅ | 完整校正链 |
| L1 事实层 | ✅ | effective_minute + solar_datetime |
| **bazi_view 投影** | 🔴 | **只传 hour** |
| **_compute_with_sxtwl** | 🔴 | **硬编码 t.m=0** |
| _calc_start_age | ✅ | H18 支持 minute/second |
| BaziChart | ✅ | 有 birth_datetime |
| **CanonicalBaziChart** | 🔴 | **缺少 birth_datetime** |
| **大运数量** | 🔴 | **只有3个，应为10个** |
| 分钟级边界测试 | 🔴 | 缺失 |

### 最终裁决

**🔴 Calculation Freeze: HOLD**

根本原因：时间链在 Adapter 层断裂，minute 信息丢失，导致：
1. 月柱边界检查不精确（minute=0）
2. 大运数量不完整（只有3个）
3. Canonical 契约不完整（缺少 birth_datetime）

---

## 十二、修复优先级

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

## 结论

**Calculation Freeze 必须 HOLD 直到完成 P0-1 ~ P0-6 修复。**

主要阻塞点：
1. **时间链断裂**：minute 在 Adapter 层丢失
2. **月柱边界不精确**：硬编码 t.m=0
3. **大运不完整**：只有3个，应为10个
4. **Canonical 契约不完整**：缺少 birth_datetime

修复完成后，再进行 Calculation Freeze Gate。
