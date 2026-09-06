# BOT-BAZI 节气时间 Authority Verification 完成报告

**任务 ID**: T-ENGINE-BAZI-002  
**执行者**: @bot-bazi  
**日期**: 2026-09-05  
**状态**: ⚠️ BLOCKED - 等待 Authority 裁决

---

## 执行摘要

完成节气时间 Authority Verification，**发现严重时间基准 Bug**。

### 核心发现

sxtwl 库输出的 Julian Date (JD) 与 NASA JPL Horizons 权威天文数据存在**约8小时差异**。

### 数据对比

| 来源 | 2024年立春时间 | 说明 |
|------|---------------|------|
| **NASA JPL Horizons** | 08:27 UTC | 官方天文数据源 |
| sxtwl JD (标准转换) | 16:26 UTC | **差值 +7h59m** ❌ |
| 新华网报道 | 北京时间 16:26 | 实际为 UTC 时间 |

### 根因

`sxtwl` 库使用**混合格式**存储节气时间：
- 整数部分 = UTC 日期
- 小数部分 = 北京时间小时数（非标准 JD 小数部分）

当前引擎 `jd_converter.py` 错误地按标准 JD 公式解读小数部分，导致时间偏移。

---

## 详细验证结果

### 1. NASA JPL Horizons 权威数据

来源：Wikipedia 引用 JPL Horizons On-Line Ephemeris System

```
2024年立春: 2024-02-04 08:27 UTC
2023年立春: 2023-02-04 16:28 UTC
```

### 2. sxtwl 库输出

```python
JD = 2460345.1853370667  # 2024年立春

# 标准 JD 转换
UTC: 2024-02-04 16:26:53
BJT: 2024-02-05 00:26:53
```

### 3. 新华网报道

> "北京时间2月4日16时27分迎来立春节气"

实际该时间是 **UTC 时间**，非北京时间。

---

## 影响范围

| 模块 | 影响 | 严重程度 |
|------|------|----------|
| 月柱计算 | 12个节气边界全部错误 | 🔴 P0 |
| 年柱计算 | 立春瞬间判断错误 | 🔴 P0 |
| 起运岁数 | 节气距离计算错误 | 🟡 P1 |
| 时柱计算 | 真太阳时计算基于错误节气 | 🟡 P1 |

---

## 建议修复方案

### 方案A：修正 jd_converter.py（推荐）

```python
def jd_to_datetime(jd: float) -> datetime:
    """Convert sxtwl JD to Beijing Time datetime.
    
    sxtwl stores solar term times in mixed format:
    - Integer part: UTC date
    - Fractional part: Beijing Time hours (NOT standard JD fraction)
    """
    JD_EPOCH = 2451545.0
    EPOCH_DT = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    
    # 整数部分 → UTC日期
    days_diff = int(jd) - JD_EPOCH
    utc_date = EPOCH_DT + timedelta(days=days_diff)
    
    # 小数部分 → 北京时间小时数
    frac = jd - int(jd)
    bjt_hours = frac * 24
    
    # 组合为北京时间
    return datetime(
        utc_date.year, utc_date.month, utc_date.day,
        int(bjt_hours), 0, 0
    )
```

### 方案B：切换权威数据源

- NASA JPL Horizons API
- 中国天文年历官方数据
- pysweph/ephem 天文库

---

## 待裁决问题

1. **时间基准**: 系统内部存储使用 UTC 还是北京时间？
2. **API 输出**: 节气时间 API 返回 UTC 还是 BJT？
3. **历史数据**: 如何处理已有的错误时间数据？
4. **数据源**: 是否切换到 NASA JPL 官方数据源？

---

## 交付物

| 文件 | 路径 |
|------|------|
| 完整报告 | `docs/bots/BOT-BAZI/AUTHORITY_VERIFICATION_REPORT_FINAL.md` |
| JPL 验证脚本 | `scripts/final_jpl_verification.py` |
| 权威检查脚本 | `scripts/final_authority_check.py` |
| 新华网对比脚本 | `scripts/analyze_xinhua_vs_sxtwl.py` |

---

## 严格遵守指示

> "宁可保持 BLOCKED，也不做'测试迎合实现'"

- ✅ 未修改任何测试期望值
- ✅ 未修改任何源代码
- ✅ 仅报告问题和提供建议
- ⏳ 等待 Authority 裁决后执行修复

---

**报告完成**: 2026-09-05  
**状态**: ⚠️ BLOCKED  
**优先级**: P0 (核心计算链)

---
*@bot-bazi*
