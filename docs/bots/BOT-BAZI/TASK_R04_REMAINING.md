# BOT-BAZI 任务单: Bazi Core 剩余 P0/P1 修复

**任务来源**: BOT-MASTER 对 b97e5c07 的仲裁裁决
**目标文件**: `src/tongshu/engines/bazi_engine.py`
**当前状态**: R-04-P0-B PASS, 但 R-04 = CONDITIONAL CLOSED, BASIC_VALIDATED = NO

---

## 问题清单（按严重性排序）

### 🔴 P0-1: 全球时区硬编码 Asia/Shanghai

**位置**: `_compute_with_sxtwl()` 内多处

```python
# 当前 (错误):
jieqi_dt = jd_to_datetime(jieqi_jd)
birth_dt = datetime(solar_term_year, solar_term_month, solar_term_day,
                    civil_hour, civil_minute, civil_second,
                    tzinfo=ZoneInfo("Asia/Shanghai"))  # ← 硬编码北京
```

**问题**: 
- 用户 Profile Contract 是 `birth_date + timezone`，不是固定中国时区
- `America/New_York / Europe/Berlin / Asia/Singapore` 等应保留用户 civil timezone
- 现有测试覆盖多个 timezone，但主要验证 TimeResolver 层，未验证 BaziEngine 节气比较真正使用了这些 timezone

**修复要求**:
1. 从调用层传入 `birth_timezone: ZoneInfo` 参数
2. `birth_dt` 构造使用传入的 timezone，而非硬编码 Shanghai
3. 节气瞬间 `jieqi_dt` 需要与 birth_dt 在同一 timezone 下比较（或都转 UTC 后比较）

---

### 🔴 P0-2: 全球时区 × 节气边界 × 23:00 换日 × 真太阳时 四维正交测试

**要求**: 新增测试覆盖以下正交场景

**测试矩阵设计**:
```
维度1: 时区 = [Asia/Shanghai, America/New_York, Europe/Berlin, Asia/Singapore, Australia/Sydney]
维度2: 节气 = [立春, 惊蛰, 清明, 立夏, 立秋, 白露, 立冬, 大雪]
维度3: 时间 = [22:30, 23:00, 23:30, 23:59, 00:01]
维度4: 真太阳时 = [无修正, +30min, -45min, +2h]

核心验证点:
A. 同一个 UTC 节气瞬间，在不同 timezone 的 civil 表示不同
B. 出生时间的 civil datetime 与节气 instant 在同一 timezone 下比较
C. 日柱/时柱的 effective_date/effective_hour 逻辑不受影响
D. 23:00 换日场景在所有时区下正确
```

**测试用例示例**:
```python
@pytest.mark.parametrize("tz_name", [
    "Asia/Shanghai", "America/New_York", "Europe/Berlin",
    "Asia/Singapore", "Australia/Sydney"
])
def test_solar_term_boundary_across_timezones(tz_name):
    """验证立春边界在多个时区下判断正确"""
    tz = ZoneInfo(tz_name)
    # 构造场景: 出生时间在当地时区的立春前后
    ...
```

---

### 🟠 P1-1: `true_solar_datetime` 参数语义污染

**位置**: `compute()` 调用 `_compute_with_sxtwl()` 处

```python
# 当前 (错误):
four_pillars = self._compute_with_sxtwl(year, month, day, hour, minute, second,
                                        true_solar_datetime=birth_datetime,  # ← birth_datetime 是 civil，不是 true solar
                                        birth_datetime=birth_datetime,
                                        civil_date=civil_date)
```

**问题**:
- `birth_datetime` 是 civil datetime（用户输入的钟表时间）
- 参数名 `true_solar_datetime` 暗示它是真太阳时转换后的结果
- 下游引擎（紫微、河洛、盲派）接入时可能误用此参数作为真太阳时
- 造成四个时间对象语义混乱：`birth_civil_datetime`、`true_solar_datetime`、`solar_term_datetime`、`effective_datetime`

**修复要求**:
1. 重命名参数 `true_solar_datetime` → `birth_civil_datetime` 或直接移除（因为已有 `birth_datetime`）
2. 如果真太阳时需要，应在上游 TimeResolver 层完成转换，产出独立的 `true_solar_datetime` 对象
3. 在函数注释中明确四个时间对象的职责边界

---

### 🟡 P1-2: 月柱 day_idx 与 civil_date 的关系需契约证明

**位置**: `_compute_with_sxtwl()` 内

```python
# 年柱/月柱节气判断用 civil_date:
solar_term_year, solar_term_month, solar_term_day = civil_date.year, civil_date.month, civil_date.day

# 但 day_idx 用 view (effective_date):
day_idx = sxtwl.fromSolar(view_year, view_month, view_day)  # view = effective_date
```

**问题**: 
- `day_idx` 用于 `getMonthGZ()`（获取月柱干支）
- 月柱节气边界比较使用 `civil_date`
- 需证明：当 birth 在 23:00-00:00 且发生换日时，`view_date`（已换日）和 `civil_date`（原始日期）的节气质差不会导致月柱取错

**修复要求**:
1. 在代码中添加契约说明注释，解释为什么 `day_idx` 可以用 `view_date` 而节气比较用 `civil_date`
2. 补充边界测试覆盖：换日 + 节气边界同时发生的情况

---

## 执行要求

1. **不修改算法逻辑本体**：保持 R-04-P0-B 已修好的修复方向
2. **单独 commit**：每个问题独立 commit，不混合提交
3. **测试先行**：先写 failing test，再修代码
4. **边界说明**：每个修复需注明解决的仲裁条目（P0-1/P0-2/P1-1/P1-2）

---

## 验收标准

- [ ] 全球时区不再硬编码 Shanghai
- [ ] 四维正交测试通过（至少 5 timezone × 8 节气 × 5 时间点 = 200 用例）
- [ ] `true_solar_datetime` 参数语义清理
- [ ] 月柱 day_idx 契约说明补全
- [ ] 129/129 boundary 保持 PASS
- [ ] 新增测试全部 PASS

---

## 禁止事项

- ❌ 不修改四柱计算核心算法
- ❌ 不修改 Golden Dataset
- ❌ 不引入新依赖
- ❌ 不修改其他引擎代码

---

**报告格式**:
- CHANGED FILES
- NEW TESTS
- COMMIT HASH
- 验证结果（测试 PASS 数）
