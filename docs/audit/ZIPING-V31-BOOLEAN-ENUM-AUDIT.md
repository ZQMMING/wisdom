# ZIPING V3.1 布尔算法 + 枚举 深度核证审计报告

> 日期: 2026-09-12
> 方法: 一代理一本典籍（PZZQ/DTS/QTBJ/YHZP/SMTH），逐条对照本典原文裁定
> 状态: 所有已知 WRONG 项已修正，GREEN 标记 = 生产代码已验证与原文一致

---

## 核心发现汇总

| 级别 | 问题 | 根因 | 修正状态 |
|------|------|------|----------|
| **P0** | B1-LING | 得令方向倒置 | `relation(month_el, day_el)` | → `relation(day_el, month_el)` | ✅ 已修 |
| **High** | B9-002 | 土库燥湿矛盾 | CHEN 同时归 DRY/WET | `_DRY={XU,WEI}`, `_WET={CHOU,CHEN}` | ✅ 已修 |
| **High** | QTBJ-B9-001 | 调候表春秋 fail-closed | 仅匹配 COLD/HOT | 扩展匹配所有二维组合 | ✅ 已修 |
| **Medium** | B3-GUANDAI | 冠带/养误降 RESIDUAL | 渊海 YHZP_0282 列「吉」 | → ROOTING | ✅ 已修 |
| **High** | STRENGTH-011 | 得令不旺需根失效 | 原要求 eff_root_exists | 改为仅需 opposing_exists | ✅ 已修 |
| **High** | STRENGTH-013 | 身弱需对立存在 | 原要求 opposing_exists | 删除对立条件 | ✅ 已修 |
| **Medium** | STRENGTH-014 | 中和需月令前提 | 原要求 month_support or shi_ling | 改为仅帮身+对立并存 | ✅ 已修 |

---

## 各典籍裁定详情

### A-PZZQ《子平真诠》（sa-0-43963f1b）

| ID | 问题 | 裁定 | 严重度 |
|----|------|------|--------|
| LING-001 | 得令定义 | **CORRECT** - "书云,得时俱为旺论,失时便作衰看" | INFO |
| LING-002 | 节气交界活看 | **UNVERIFIED** - 需引入"进气/退气" | LOW |
| QING-002 | 清浊混杂条件 | **UNVERIFIED** - 官伤/印财相克未覆盖 | LOW |

### A-DTS《滴天髓》（sa-0-dts）

| ID | 问题 | 裁定 | 严重度 |
|----|------|------|--------|
| B5 | 党众帮身/对立 | **CORRECT** - 同我+生我=帮身，我生+我克+克我=对立 | INFO |
| B6 | 身强弱六态 | **CORRECT** - 体用扶抑，得令不旺/失令不弱 | INFO |
| **B9** | **寒暖燥湿二维** | **WRONG** → 已修 | **HIGH** |
| B13 | 节气四时边界 | **CORRECT** - 黄经交节 + 三候司令 | INFO |

**B9 根因**: 原代码将 天道寒暖×地道燥湿 简化为两个独立二元 flag，春秋直接 fail-closed，缺土库燥湿结构。

### A-QTBJ《穷通宝鉴》（sa-1-qtbj）

| ID | 问题 | 裁定 | 严重度 |
|----|------|------|--------|
| QTBJ-B9-001 | 春秋 fail-closed | **WRONG** → 已修 | **HIGH** |
| QTBJ-B9-002 | 土库燥湿矛盾 | **WRONG** → 已修 | MEDIUM |
| QTBJ-B10-001 | 调候优先级 | **CORRECT** - 专用/先用=PRIMARY，次取=SECONDARY | LOW |
| QTBJ-B10-002 | 三级优先级 | **UNVERIFIED** - 三并场景(五月辛金) | LOW |

**B9-002 根因**: `_DRY_EARTH_BRANCHES={"XU","CHEN"}` 与 `_WET_EARTH_BRANCHES={"CHOU","CHEN"}` 共 CHEN 导致逻辑矛盾。穷通原文「辰有伏水(湿)，戌有藏火(燥)，丑有隐金(湿)，未有匿木/带火(燥)」→ 正确应为 DRY={XU,WEI} WET={CHOU,CHEN}。

### A-YHZP《渊海子平》（sa-0-yhzp）

| ID | 问题 | 裁定 | 严重度 |
|----|------|------|--------|
| B3-GROWTH | 十二长生结构态 | **CORRECT** - 只出事实不推身强 | INFO |
| B3-DIWANG-LINGUAN-CHANGSHENG | 帝旺/临官/长生 | **CORRECT** - 三位归有根 | INFO |
| **B3-GUANDAI-YANG** | **冠带/养 归 RESIDUAL** | **WRONG** → 已修 | **MEDIUM** |
| B3-JUE-TAI-SI | 绝/胎/死 | **UNVERIFIED** - 胎位无渊海原文支撑 | LOW |
| B4-JIANLU-LINGUAN | 建禄=临官 | **CORRECT** - YHZP_0548 甲禄在寅 | INFO |
| B4-YANGREN-DIWANG | 阳刃=帝旺 | **CORRECT** - YHZP_0548 卯为阳刃 | INFO |
| B4-ZHONGWANG-SET | 重根判定 | **CORRECT** - 三位均有渊海支撑 | INFO |
| B12-CHONGXING-KAIKU | 冲刑开库 | **CORRECT** - YHZP_0320/0323/2463 | INFO |
| **B12-HE-BI-KU** | **合闭库** | **UNVERIFIED** - YHZP 全库 0 命中 | MEDIUM |

**B3-GUANDAI-YANG 根因**: YHZP_0282「遇帝旺、临官、禄马、贵人、生、养、冠带、库者吉」，冠带/养与帝旺临官长生同列「吉」，不应归 RESIDUAL(余气)。

**B12-HE-BI-KU**: 渊海原文「合」只作合绊/合起(如阳刃冲合、印多合)，无「合闭库」条文。

### A-SMTH《三命通会》（sa-2-smth）

| ID | 问题 | 裁定 | 严重度 |
|----|------|------|--------|
| B12-STORE_BRANCHES | 墓库定义 | **CORRECT** - 辰/戌/丑/未四位 | INFO |
| B13-节气边界 | 四季归类 | **CORRECT** - 立春/立夏/立秋/立冬为界 | INFO |
| B14-建禄格 | 建禄定义 | **UNVERIFIED** - 需人元透干方可成格 | MEDIUM |

---

## 已修正代码清单

### 修正 1: LING 方向 P0 倒置
- **文件**: `judgment.py` L45
- **根因**: `relation(month_el, day_el)` 以月支视角，应为日主视角
- **修正**: `relation(day_el, month_el)` → 日主对月支的生克

### 修正 2: 土库燥湿矛盾 B9-002
- **文件**: `judgment_ext.py` L29-31
- **根因**: CHEN 同时归入 DRY 和 WET 集合
- **修正**: `_DRY={"XU","WEI"}`, `_WET={"CHOU","CHEN"}`

### 修正 3: 十二长生冠带/养误降 B3
- **文件**: `judgment.py` `_GROWTH_STATE`
- **根因**: RESIDUAL 降级违背 YHZP_0282「吉」组
- **修正**: 冠带/养 → ROOTING(有根)

### 修正 4: 调候表匹配扩展 QTBJ-B9-001
- **文件**: `judgment_ext.py` `judge_climate` / `judge_yong`
- **根因**: 仅匹配 COLD/HOT，春秋 fail-closed
- **修正**: 允许状态为 COLD_WET/COLD_DRY/HOT_WET/HOT_DRY/WET/DRY/MIXED 时查表

### 修正 5: 身强弱六态 PZZQ 修正
- **文件**: `judgment.py` `judge_strength`
- **STRENGTH-011**: 删除 `not eff_root_exists` 条件 — 滴天髓「春木虽强，金太重而木亦危」，得令+对立即不旺
- **STRENGTH-013**: 删除 `and opposing_exists` 条件 — 子平真诠「秋木虽弱，木根深而木亦强」，弱不依赖对立
- **STRENGTH-014**: 删除 `(month_support or shi_ling)` 前提 — 子平真诠「有情有力无力之间」，中和核心是帮身+对立并存

---

## 待后续裁决项（UNVERIFIED/Low）

以下项无明确原文矛盾，但细节需 User 裁决:

1. **LING-002**: 节气交界是否引入进气/退气因子？
2. **QING-002**: 清浊是否应覆盖官伤/印财相克？
3. **QTBJ-B10-002**: 调候优先级是否扩展至三级(主/次/三并)？
4. **B3-JUE-TAI-SI**: 胎位是否归 EXTINCT？
5. **B12-HE-BI-KU**: 合闭库是否有其他典籍支撑？
6. **B14-建禄格**: 是否需人元透干判定？

---

## 测试状态

```
29/29 tests PASS
ARCH-001~018: 全 PASS
5案例端到端: 通过
```

---

## Commit 记录

- `0fc154f2`: B1/B9/B3 修复（已 Push）
- 本轮新增: B9-002(土库) + QTBJ-B9-001(调候扩展)
