# BOT-MASTER 仲裁复核报告: Bazi Core 剩余 P0/P1 修复

**任务单**: `docs/bots/BOT-BAZI/TASK_R04_REMAINING.md`
**执行 Bot**: BOT-BAZI
**复核时间**: 2026-09-09 21:00
**Base commit**: b97e5c07

---

## 一、执行结果总览

| 项目 | 状态 |
|------|------|
| P0-1: 移除硬编码 Asia/Shanghai | ✅ 已完成 |
| P0-2: 四维正交测试 | ✅ 83/83 PASS |
| P1-1: true_solar_datetime 语义清理 | ✅ 重命名为 birth_civil_datetime |
| P1-2: 月柱 day_idx 契约说明 | ✅ 注释已补充 |
| 测试通过率 | ✅ 125/125 PASS |
| boundary 测试 | ✅ 129/129 PASS |

**新增 commits** (4个独立提交):
```
c24ecaa6 [V2 §21 P0 FIX] BAZI R-04-P0-1: 移除硬编码 Asia/Shanghai，支持全球时区
dae00d52 [V2 §21 P0 FIX] BAZI R-04-P0-2: 新增全球时区×节气边界×23:00换日×真太阳时四维正交测试
86ec44ca [V2 §21 P1 FIX] BAZI R-04-P1-1: 清理 true_solar_datetime 参数语义污染
b1a98eff [V2 §21 P1 FIX] BAZI R-04-P1-2: 补充月柱 day_idx 与 civil_date 关系的契约说明
```

---

## 二、逐条代码复核

### ✅ P0-1: 全球时区支持

**改动要点**:
1. `compute()` 提取 `birth_tz = birth_datetime.tzinfo`
2. `_compute_with_sxtwl()` 新增 `birth_tz` 参数
3. 节气比较时：`jieqi_dt.astimezone(tz)` 转换到出生时区后比较
4. `_calc_start_age()` 同样接受 `birth_tz` 参数

**关键代码** (line 955, 986):
```python
tz = birth_tz or ZoneInfo("Asia/Shanghai")  # 安全回退
jieqi_in_tz = jieqi_dt.astimezone(tz)
```

**裁决**: ✅ **通过**。核心逻辑正确：将节气瞬间转出生时区再比较，避免跨时区误判。

---

### ✅ P0-2: 四维正交测试

**测试文件**: `tests/test_bazi_global_timezone.py` (601行)

**覆盖维度**:
- 5时区 × 立春/惊蛰边界 = 10测试
- 5时区 × 23:00换日 = 15测试
- 真太阳时修正按经度 = 3测试
- 5时区 × 8节气矩阵 = 40测试
- 参数语义验证 = 7测试
- 契约文档验证 = 7测试

**测试结果**: 83/83 PASS ✅

---

### ✅ P1-1: 参数语义清理

**改动要点**:
- `true_solar_datetime` → `birth_civil_datetime` (重命名)
- 保留旧参数名向后兼容（`bciv = birth_civil_datetime or true_solar_datetime`）
- 函数注释明确标注废弃

**代码位置**: line 881-896

---

### ✅ P1-2: 契约说明补全

**改动要点**: 在 `_compute_with_sxtwl()` 函数注释中补充：
- `day_idx` 用途：决定干支序号（用 effective_date/view）
- `civil_date` 用途：节气边界判断（用原始 civil 日期）
- 反例说明：civil=02-03 23:30 → effective_date=02-04，若用effective_date判断立春会误判

---

## 三、遗留问题记录

### 🟡 观察项: `_recompute_month_with_datetime()` 死代码

**位置**: line 1021-1070

**状态**: 全仓搜索无生产调用者，确认为历史遗留代码。

**当前行为**: naive datetime 时 fallback 到 Asia/Shanghai

**建议**: 后续可删除，不阻塞当前验收。

---

## 四、验收判定

| 仲裁项 | BOT-MASTER 判定 |
|--------|----------------|
| P0-1 全球时区支持 | ✅ ACCEPT |
| P0-2 四维正交测试 | ✅ 83/83 PASS |
| P1-1 参数语义清理 | ✅ ACCEPT |
| P1-2 契约说明补全 | ✅ ACCEPT |
| 核心算法未改 | ✅ 确认 |
| 测试覆盖完整 | ✅ 125/125 + 129 boundary |

---

## 五、更新状态

```
R-04-P0-B = ✅ PASS (b97e5c07)
R-04-P0-1 = ✅ PASS (c24ecaa6)
R-04-P0-2 = ✅ PASS (dae00d52)
R-04-P1-1 = ✅ ACCEPT (86ec44ca)
R-04-P1-2 = ✅ ACCEPT (b1a98eff)

R-04 = CLOSED ✅
BAZI CALCULATION CORE = READY FOR FREEZE DECISION ⏳
```

**下一步**: 等待用户裁决是否执行 `CALCULATION_FREEZE`。

---

## 六、Commit 链

```
b97e5c07 [V2 §21 P0 FIX] R-04-P0-B: Civil Date / Effective Date 分离
c24ecaa6 [V2 §21 P0 FIX] BAZI R-04-P0-1: 移除硬编码 Asia/Shanghai，支持全球时区
dae00d52 [V2 §21 P0 FIX] BAZI R-04-P0-2: 新增全球时区×节气边界×23:00换日×真太阳时四维正交测试
86ec44ca [V2 §21 P1 FIX] BAZI R-04-P1-1: 清理 true_solar_datetime 参数语义污染
b1a98eff [V2 §21 P1 FIX] BAZI R-04-P1-2: 补充月柱 day_idx 与 civil_date 关系的契约说明
```
