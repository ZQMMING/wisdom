# 节气时间 Authority Verification Report (FINAL)

**任务 ID**: T-ENGINE-BAZI-002  
**执行者**: @bot-bazi  
**日期**: 2026-09-05  
**状态**: ⚠️ CRITICAL ISSUE FOUND - 等待裁决

---

## 执行摘要

**发现严重时间基准Bug**: sxtwl库输出的Julian Date (JD) 与 NASA JPL Horizons 权威天文数据存在约8小时差异。

**影响**: 所有节气时间计算错误，影响月柱、年柱、起运岁数等核心计算。

---

## 1. 权威数据对比

### NASA JPL Horizons (官方天文数据源)
来源: Wikipedia引用JPL Horizons On-Line Ephemeris System
- 2024年立春: **08:27 UTC** (2024-02-04 08:27:00)
- 2023年立春: **16:28 UTC** (2023-02-04 16:28:00)

### sxtwl 库输出
```python
JD = 2460345.1853370667  # 2024年立春
# 标准JD转换 → UTC: 2024-02-04 16:26:53
# 标准JD转换 → BJT: 2024-02-05 00:26:53
```

### 新华网报道
- 2024年立春: **北京时间 16:26:53**

### 对比结果

| 来源 | 2024立春 | 与JPL差值 |
|------|----------|-----------|
| NASA JPL Horizons | 08:27 UTC | 基准 |
| sxtwl JD (标准转换) | 16:26 UTC | **+7h59m** ❌ |
| sxtwl JD (BJT转换) | 00:26+1 UTC | **+16h** ❌ |
| 新华网报道 | 16:26 BJT | +8h (实际是UTC) |

---

## 2. 根因分析

### sxtwl JD 格式特殊性

标准儒略日 (JD) 定义：
- 整数部分 = UTC日期
- 小数部分 = UTC时间 (fraction × 86400 = seconds)

但sxtwl库似乎使用了**混合格式**：
- 整数部分 = UTC日期 ✅
- 小数部分 = **北京时间时间** ❌ (非标准)

### 验证证据

```
JD = 2460345.1853370667

整数部分 2460345 → UTC日期 2024-02-04 ✅
小数部分 0.185337 → 直接解读 = 04:26:53
但 16:26:53 (新华网"北京时间") = 08:26:53 UTC (真实UTC)
而 08:27 UTC = NASA JPL权威数据 ✅

结论: sxtwl JD的小数部分实际存储的是北京时间的小时数(16+),
      但被错误地按标准JD公式解读为UTC时间(0.185×24≈4.4小时)
```

### 当前引擎错误

```python
# src/tongshu/engines/time/jd_converter.py (错误实现)
def jd_to_datetime(jd):
    # ...获取整数日期...
    frac = jd - int(jd)
    total_seconds = frac * 86400  # 错误! frac存储的是BJT小时数
    hours = int(total_seconds // 3600)  # 得到4小时而非16小时
```

---

## 3. 影响范围

| 模块 | 影响 | 严重程度 |
|------|------|----------|
| 月柱计算 | 12个节气边界全部错误 | 🔴 P0 |
| 年柱计算 | 立春瞬间判断错误 | 🔴 P0 |
| 起运岁数 | 节气距离计算错误 | 🟡 P1 |
| 时柱计算 | 真太阳时计算基于错误节气 | 🟡 P1 |

---

## 4. 建议修复方案

### 方案A: 修正 jd_converter.py (推荐)

```python
def jd_to_datetime(jd: float) -> datetime:
    """Convert sxtwl JD to Beijing Time datetime.
    
    sxtwl stores solar term times in mixed format:
    - Integer part: UTC date
    - Fractional part: Beijing Time hours (NOT standard JD fraction)
    
    Algorithm:
    1. Extract integer part for UTC date
    2. Extract fractional part and interpret as BJT hours
    3. Combine to form Beijing Time datetime
    """
    JD_EPOCH = 2451545.0
    EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    # 整数部分 → UTC日期
    days_diff = int(jd) - JD_EPOCH
    utc_date = EPOCH_DT + timedelta(days=days_diff)
    
    # 小数部分 → 北京时间小时数
    frac = jd - int(jd)
    bjt_hours = frac * 24  # 0.x → 小时数
    
    # 组合为北京时间
    bjt_dt = datetime(
        utc_date.year, utc_date.month, utc_date.day,
        int(bjt_hours), 0, 0
    )
    
    return bjt_dt
```

### 方案B: 使用独立权威数据源

- NASA JPL Horizons API
- 中国天文年历官方数据
- pysweph/ephem天文库

---

## 5. 测试策略

### 严格遵守BOT-MASTER指示

> "宁可保持 BLOCKED，也不做'测试迎合实现'"

**禁止事项**：
1. ❌ 修改测试期望值
2. ❌ 调整测试脚本适配buggy代码
3. ❌ 创建新的期望值覆盖现有测试

**允许事项**：
1. ✅ 报告发现的问题
2. ✅ 提供分析和建议
3. ✅ 等待Authority裁决

---

## 6. 待裁决问题

1. **时间基准**: 系统应使用UTC还是北京时间作为内部存储？
2. **API输出**: 节气时间API应返回UTC还是BJT？
3. **历史数据**: 如何处理已有的错误时间数据？
4. **数据源**: 是否切换到NASA JPL官方数据源？

---

## 7. 交付物清单

| 文件 | 路径 | 状态 |
|------|------|------|
| 最终报告 | `docs/bots/BOT-BAZI/authority_verification_report_final.md` | ✅ |
| JPL验证脚本 | `scripts/final_jpl_verification.py` | ✅ |
| 权威检查脚本 | `scripts/final_authority_check.py` | ✅ |
| 新华网对比脚本 | `scripts/analyze_xinhua_vs_sxtwl.py` | ✅ |

---

## 8. 下一步行动

1. **冻结**: 不修改任何测试或代码
2. **等待**: BOT-MASTER裁决时间基准方案
3. **修复**: 根据裁决修正 `jd_converter.py`
4. **验证**: 使用NASA JPL数据重新验证

---

**报告完成**: 2026-09-05  
**状态**: ⚠️ BLOCKED - 等待Authority裁决  
**优先级**: P0 (核心计算链)

---
*@bot-bazi*
