# 盲派引擎代码审计报告（修正版）

**审计时间**: 2026-09-14  
**审计范围**: `src/tongshu/engines/blind*.py` 及相关测试  
**审计标准**: 《盲派生产规则.txt》V1-FINAL + V3.3/V3.4规范  
**重要说明**: 盲派是独立体系，不适用V2.2.2（六部经典引擎规范）

---

## 一、审计概览

| 项目 | 状态 |
|------|------|
| 核心文件 | ✅ 存在 |
| 测试覆盖率 | ✅ 93 passed |
| Golden测试 | ✅ 21 passed |
| 证据链 | ✅ 59条 |
| 规范合规 | ✅ V1-FINAL/V3.4 |

---

## 二、盲派规范版本演进

| 版本 | 日期 | 主要变更 |
|------|------|----------|
| V1-FINAL | 基础 | 94节生产规则（§1-94） |
| V3.0 | 2026-08 | 做功六方式、体用宾主 |
| V3.1 | 2026-09 | 做功归因（谁在做功） |
| V3.2 | 2026-09 | 六域施工+效率联动 |
| V3.3 | 2026-09 | L1e事件结构（§60-64） |
| V3.4 | 2026-09 | L2解层+事实吉凶判定 |
| V3.4.3 | 2026-09 | 宾主易位·官星投墓修复 |

**当前版本**: V3.4.3

---

## 三、代码规模

### 源代码（5,970行）

| 文件 | 行数 | 功能 |
|------|------|------|
| blind_bazi_engine.py | 2,544 | 主引擎（V3.4.3） |
| blind_interpretation.py | 834 | 解读层 |
| blind_judgment.py | 347 | L2解层（V3.4） |
| blind_themes.py | 394 | 主题分类 |
| blind_yingqi.py | 666 | 应期引擎 |
| blind/*.py (9文件) | 1,185 | 子模块 |
| **合计** | **5,970** | |

### 测试代码（1,118行）

| 测试文件 | 行数 | 用例数 |
|----------|------|--------|
| test_blind_golden.py | 237 | 21 |
| test_blind_rule_compliance.py | 240 | 22 |
| test_blind_integration_bazi.py | 134 | 9 |
| test_blind_yingqi.py | 151 | 14 |
| test_blind_themes.py | 99 | 12 |
| test_mingli_bench_blind.py | 105 | 4 |
| test_blind_signal_regression.py | 89 | 5 |
| test_blind_negative.py | 63 | 6 |
| **合计** | **1,118** | **93** |

---

## 四、规范合规性检查

### 4.1 L1e事件结构（V3.3 §60-64）

| 规则ID | 域 | 输出枚举 | 实现状态 |
|--------|------|----------|----------|
| EVT-MARRIAGE-001 | 婚姻 | HARMONIOUS/CHALLENGED/BROKEN/UNDETERMINED | ✅ |
| EVT-WEALTH-001 | 财富 | DIRECTED_AND_ESTABLISHED/PRESENT_UNTAKEN等 | ✅ |
| EVT-OFFICIAL-001 | 官贵 | CONTROLLED_AND_CLEAN/UNCONTROLLED等 | ✅ |
| EVT-OCCUPATION-001 | 职业 | 12类枚举 | ✅ |
| EVT-BODY-001 | 身体 | LU_UNDER_ATTACK/YANG_REN_CLASHED等 | ✅ |

### 4.2 L2解层（V3.4）

| 组件 | 状态 |
|------|------|
| BlindJudgmentEngine | ✅ 已实现 |
| JDGDirection枚举 | ✅ AUSPICIOUS/IN_AUSPICIOUS/WARNING/NEUTRAL/UNDETERMINED |
| RESPONSE_ACTION_SEMANTICS | ✅ 14种动作语义 |
| BLIND-DJ-001~012证据 | ✅ 12条核心证据 |

### 4.3 做功强弱（V1-FINAL §38）

| 枚举 | 实现状态 |
|------|----------|
| LARGE/MEDIUM/SMALL/NONE | ✅ WK_EFFICIENCY |
| 大贵/中贵/小贵/平常/贫贱 | ✅ WORK_LEVEL |

### 4.4 做功归因（V3.1）

| 组件 | 状态 |
|------|------|
| GONGSHEN_ROLE枚举 | ✅ GONGSHEN/XIENSHEN/NULL |
| attribution字段 | ✅ 谁在做功/是否为我所用 |

---

## 五、证据链审计

### 证据目录：`data/evidence/blind_seg/`

| 类别 | 文件数 | 状态 |
|------|--------|------|
| WORK_METHOD | 6 | ✅ |
| WORK_TARGET | 5 | ✅ |
| WORK_RELATION | 4 | ✅ |
| WORK_EFFICIENCY | 3 | ✅ |
| GUEST_HOST | 5 | ✅ |
| BODY_USE | 6 | ✅ |
| IMAGE | 6 | ✅ |
| POWER_PARTY | 5 | ✅ |
| YING_QI | 5 | ✅ |
| EMPTY_USELESS | 6 | ✅ |
| COMPLEX_WORK | 3 | ✅ |
| **总计** | **59** | ✅ |

### 元数据文件

```
manifest.json                    # 总索引
provenance_final_status.json     # 来源状态
provenance_rules.json            # 来源规则
source_verification_*.json       # 来源验证报告（59条全核证）
reclassification_matrix.json     # 重新分类矩阵
```

---

## 六、测试结果

```bash
python -m pytest tests/test_blind_*.py -v
```

**结果**：
```
==================== 93 passed, 7 subtests passed in 0.90s ====================
```

### 测试覆盖详情

| 测试类 | 用例数 | 状态 |
|--------|--------|------|
| TestBlindGoldenSet | 21 | ✅ |
| TestBlindBaziIntegration | 9 | ✅ |
| TestBlindNegative | 6 | ✅ |
| TestBlindRuleCompliance | 22 | ✅ |
| TestBlindSignalRegression | 5 | ✅ |
| TestBlindThemes | 12 | ✅ |
| TestBlindYingqi | 14 | ✅ |
| TestMingliBenchBlind | 4 | ✅ |

---

## 七、架构独立性检查

### 7.1 盲派 vs 子平独立

```python
# blind_bazi_engine.py L15-24: 架构铁律
# 盲派引擎与子平引擎是【完全独立】的两个引擎：
#   - 唯一共同消费层 = 八字排盘引擎输出的基础事实
#   - 盲派引擎【禁止】import / 消费 / 复用子平辨层任何东西
```

**检查结果**：
- ✅ 仅导入 `BaziChart`（L0事实层）
- ❌ 未导入 `ziping_v3.*`
- ❌ 未导入 `yongshen.py`
- ❌ 未导入格局/用神/调候模块

### 7.2 禁止事项检查

| 禁止项 | 检查结果 |
|--------|----------|
| 使用百分比/评分 | ✅ 无（全枚举） |
| 使用比较算子`> < >= <=` | ✅ 无（布尔/枚举） |
| LLM参与计算 | ✅ 无 |
| 跨引擎依赖 | ✅ 无 |
| 绝对路径硬编码 | ✅ 无 |

---

## 八、风险项

### 低风险项

1. **单文件过大**: `blind_bazi_engine.py` 2,544行，接近建议上限
   - 影响：维护成本略高
   - 建议：可考虑拆分，但非P0

2. **版本演进快**: V3.0→V3.4.3仅一个月
   - 影响：历史版本可能未全部文档化
   - 状态：V3.4.3是当前稳定版

### 无需处理

- 无违规导入
- 无违禁符号
- 无架构违规

---

## 九、结论

| 维度 | 评级 |
|------|------|
| 代码结构 | ✅ PASS |
| 规范合规 | ✅ PASS（V1-FINAL/V3.4） |
| 测试覆盖 | ✅ PASS（93 cases） |
| 证据链 | ✅ PASS（59条） |
| 架构独立 | ✅ PASS |

**综合评定**：**BASIC_VALIDATED** ✅

**适用规范**: 《盲派生产规则.txt》V1-FINAL + V3.3/V3.4规范  
**不适用**: V2.2.2（六部经典引擎规范）

---

## 十、附录

### A. 规范文件清单

```
docs/v2/盲派生产规则.txt                          # 主规范（V1-FINAL）
docs/v2/盲派V3.3_L1e事件结构_布尔规则校对验证.md # L1e事件结构
docs/v2/盲派V3.4_L2解层_事实吉凶判定引擎.md      # L2解层
docs/v2/盲派V3.4.1_布尔规则枚举深挖排查报告.md   # 枚举深挖
docs/v2/盲派9例对齐验证_V3.4.3.md               # 最新验证
docs/v2/盲派全链路自我审计报告_V3.4.2.md        # 自我审计
docs/v2/盲派规则V1-FINAL_修订_WORK_EFFICIENCY.md # 做功效率修订
docs/v2/盲派规则_VERIFY-BLIND-001-030_全量核证报告.md # 证据核证
```

### B. 测试文件清单

```
tests/test_blind_golden.py              # 21 cases
tests/test_blind_integration_bazi.py    # 9 cases
tests/test_blind_negative.py            # 6 cases
tests/test_blind_rule_compliance.py     # 22 cases
tests/test_blind_signal_regression.py   # 5 cases
tests/test_blind_themes.py              # 12 cases
tests/test_blind_yingqi.py              # 14 cases
tests/test_mingli_bench_blind.py        # 4 cases
```

---

**审计员**: BOT-MASTER  
**日期**: 2026-09-14  
**版本**: V1.1（修正：盲派独立规范，不适用V2.2.2）
