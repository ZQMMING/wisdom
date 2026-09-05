# P2.7-H18-FIX: Minute/Second Jieqi Boundary Fix

## 任务目标
根据用户裁决，在 `84b0668` 基础上补充分钟级节气边界硬测试，验证 minute/second 贯穿整条链且月柱边界正确。

## 发现的根本问题

### JD 基准不一致 Bug
`sxtwl` 库存在两个不同的 JD 基准：
- `getJieQiJD()` 返回基于北京时间的 JD（特殊处理）
- `toJD(Time)` 返回基于 UTC 的标准 JD

两者差值约 0.5 天（12小时），导致之前的比较逻辑完全错误。

**证据：**
```python
jieqi_jd = sxtwl.fromSolar(2024, 2, 4).getJieQiJD()  # 2460345.1853370667
jd_utc = sxtwl.toJD(utc_time)                         # 2460344.3520023148
jd_bj = sxtwl.toJD(beijing_time)                      # 2460344.6853356482

jieqi_jd - jd_utc = 0.8333...  # 约20小时差异
jieqi_jd - jd_bj = 0.5000...   # 约12小时差异
```

## 修复内容

### 1. `src/tongshu/engines/bazi_engine.py`

**修改 `_compute_with_sxtwl()` 方法：**

```python
# 修复前（错误）
t = sxtwl.Time()
t.Y, t.M, t.D = year, month, day
t.h, t.m, t.s = hour, minute, float(second)
birth_jd = sxtwl.toJD(t)  # UTC基准

if birth_jd < jieqi_jd:   # 与getJieQiJD()的BJ基准比较 → 错误！
    ...

# 修复后（正确）
from tongshu.engines.time.jd_converter import jd_to_datetime
jieqi_dt = jd_to_datetime(jieqi_jd)  # 转换为naive datetime（北京时间）

birth_dt = datetime(year, month, day, hour, minute, int(second))  # naive datetime

if birth_dt < jieqi_dt:  # 同类型比较，正确！
    ...
```

### 2. `tests/test_p27g_minute_second_jieqi_boundary.py`（新建）

创建了 **13 个硬边界测试**，覆盖：

| 测试类 | 测试数 | 覆盖场景 |
|--------|--------|----------|
| `TestMonthPillarBoundary` | 3 | 立春前后真太阳时边界 |
| `TestStartAgeTargetJie` | 3 | 顺排/逆排目标节、中气排除 |
| `TestSameJieqiDay` | 3 | 节气日真太阳时前后边界 |
| `TestProductionPipelinePreservesTime` | 3 | minute 贯穿整条链 |
| `TestMinutePrecisionImpact` | 1 | 同一节气日不同分钟 |

**关键测试发现：**
- 立春 2024-02-04 04:26:53
- 输入 04:55 → true_solar=04:26:47（仍在立春前6秒）
- 输入 04:59 → true_solar=04:30:47（立春后3分54秒）
- 经度校正约 -14分钟，EoT 约 -8分钟，总校正约 -22分钟

## 测试结果

```
$ python -m pytest tests/test_p27g*.py -q
73 passed in 1.63s
```

### 测试覆盖矩阵

| 场景 | 状态 | 说明 |
|------|------|------|
| 立春前月柱 | ✅ | CHOU 月正确 |
| 立春后月柱 | ✅ | YIN 月正确 |
| 真太阳时边界 | ✅ | minute 影响月柱判断 |
| 顺排目标节 | ✅ | 找未来最近节 |
| 逆排目标节 | ✅ | 找过去最近节 |
| 中气排除 | ✅ | 雨水等中气不作为目标 |
| 同一节气日 | ✅ | 前后真太阳时月柱不同 |
| minute 贯穿链 | ✅ | 从 Adapter 到 Engine 未丢失 |
| CanonicalBaziChart | ✅ | 包含 birth_datetime |

## 验证清单

| # | 检查项 | 状态 |
|---|--------|------|
| 1 | `_compute_with_sxtwl` 使用 naive datetime 比较 | ✅ |
| 2 | `jd_to_datetime` 返回北京时间（验证立春 04:26:53） | ✅ |
| 3 | 真太阳时校正被正确传递到 Engine | ✅ |
| 4 | 节气前后 minute 差异导致不同月柱 | ✅ |
| 5 | 大运数量仍为 10 个 | ✅ |
| 6 | 起运年龄计算使用完整 minute/second | ✅ |

## Calculation Freeze 门禁评估

| 门禁 | 状态 | 说明 |
|------|------|------|
| BirthInput | 🟢 | |
| TimeResolver | 🟢 | |
| 真太阳时 | 🟢 | |
| Adapter 时间传递 | 🟢 | |
| minute/second | 🟢 | 实现并验证 |
| 月柱边界正确性 | 🟢 | 已修复 JD 基准 bug |
| 起运算法 | 🟢 | 包含 minute/second |
| 大运数量 | 🟢 | 10个 |
| 测试覆盖 | 🟢 | 73/73 |
| **Calendar Authority** | 🟡 | 需 H19 Ground Truth 验证 |
| **Calculation Freeze** | 🟡 | 需用户最终裁决 |

## 待办事项

1. **H19: Calendar/Bazi Ground Truth Closure**
   - 建立可验证的预期答案表
   - 每个字段（出生时间、真太阳时、目标节、月柱、起运年龄）必须有明确来源或数学推导

2. **用户裁决**
   - 是否进入 Calculation Freeze？
   - 是否需要继续 H19 Ground Truth 工作？

## 提交记录

- 修复本地提交（未推送 GitHub）：`84b0668` + 本次修复
- 测试文件：`tests/test_p27g_minute_second_jieqi_boundary.py`

---

**修复日期**: 2026-07-11  
**修复者**: @bazi
