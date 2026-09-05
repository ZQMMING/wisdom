# P2.7-H18-FIX 修复报告

**提交**: 84b0668  
**日期**: 2026-09-05  
**状态**: ✅ 已本地提交（未推送到 GitHub）

---

## 修复内容

### 1. BaziAdapter 传递完整时间 ✅

**文件**: `src/tongshu/engines/bazi_adapter.py`

```python
return self._engine.compute(
    view,
    gender=gender,
    skip_late_zi=True,
    birth_datetime=ctx.true_solar_datetime,  # ← 新增
)
```

### 2. _compute_with_sxtwl 支持 minute/second ✅

**文件**: `src/tongshu/engines/bazi_engine.py`

```python
def _compute_with_sxtwl(self, year, month, day, hour, minute=0, second=0.0):
    t = sxtwl.Time()
    t.h, t.m, t.s = hour, minute, float(second)  # ← 修复
```

### 3. BaziEngine.compute 提取 minute/second ✅

```python
minute = birth_datetime.minute if birth_datetime is not None else 0
second = birth_datetime.second if birth_datetime is not None else 0
four_pillars = self._compute_with_sxtwl(year, month, day, hour, minute, second)
```

### 4. CanonicalBaziChart 添加 birth_datetime ✅

**文件**: `src/tongshu/models/canonical_bazi.py`

```python
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

### 5. 大运数量修复 ✅

```python
for decade in range(1, 11):  # ← 修复：10个大运
    ...
```

### 6. 测试更新 ✅

```python
# tests/test_p27g_fix_hour_precision.py
assert len(chart.luck_pillars) == 10  # ← 更新断言
```

---

## 修复前后对比

| 项目 | 修复前 | 修复后 |
|------|--------|--------|
| BaziAdapter | 只传 view | 传 view + birth_datetime |
| _compute_with_sxtwl | t.m=0 硬编码 | 接受 minute/second 参数 |
| CanonicalBaziChart | 缺少 birth_datetime | 有 birth_datetime 字段 |
| 大运数量 | 3个 | 10个 |
| 测试 | 60 passed（部分断言错误） | 60 passed |

---

## 验证结果

```
60 passed in 1.22s
```

---

## Calculation Freeze 门禁重新评估

| 项目 | 状态 |
|------|------|
| API 输入契约 | ✅ |
| TimeResolver 真太阳时 | ✅ |
| L1 事实层 | ✅ |
| BaziAdapter 传递时间 | ✅ |
| _compute_with_sxtwl 精度 | ✅ |
| _calc_start_age | ✅ |
| CanonicalBaziChart | ✅ |
| 大运数量 | ✅ |
| 测试覆盖 | ⚠️ 需补充分钟级边界测试 |

**Calculation Freeze**: 🟡 CONDITIONAL PASS（需补充边界测试后可进入 Freeze）

---

## 待补充测试

```python
def test_jieqi_boundary_with_minute():
    """节气前后1分钟的边界案例"""
    # 立春 2024-02-04 04:26:53
    # 出生 04:25:00 → 使用前一月柱
    # 出生 04:27:00 → 使用当前月柱
    pass
```

---

**下一步**: 等待用户裁决是否推送 GitHub 或补充边界测试。
