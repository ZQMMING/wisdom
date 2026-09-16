# 盲派引擎代码审计报告

**审计时间**: 2026-09-14  
**审计范围**: `src/tongshu/engines/blind*.py` 及相关测试  
**审计标准**: 《盲派生产规则.txt》V1-FINAL + V3.3/V3.4规范  
**重要说明**: 盲派是独立体系，不适用V2.2.2（V2.2.2仅适用于六部经典引擎）

---

## 一、代码规模

### 1.1 源代码结构（14个文件，5,970行）

| 文件 | 行数 | 大小 | 功能 |
|------|------|------|------|
| `blind_bazi_engine.py` | 2,544 | 148 KB | 主引擎（宾主/体用/做功） |
| `blind_interpretation.py` | 834 | 60 KB | 解读层 |
| `blind_judgment.py` | 347 | 24 KB | L2解层（V3.4） |
| `blind_themes.py` | 394 | 24 KB | 主题分类 |
| `blind_yingqi.py` | 666 | 36 KB | 应期引擎 |
| `blind/` 子目录 | 1,185 | 140 KB | 9个模块文件 |
| **源代码小计** | **5,970** | **~432 KB** | |

### 1.2 测试代码（8个文件，1,118行）

| 测试文件 | 行数 | 用例数 |
|----------|------|--------|
| `test_blind_golden.py` | 237 | 21 |
| `test_blind_rule_compliance.py` | 240 | 22 |
| `test_blind_integration_bazi.py` | 134 | 9 |
| `test_blind_yingqi.py` | 151 | 14 |
| `test_blind_themes.py` | 99 | 12 |
| `test_mingli_bench_blind.py` | 105 | 4 |
| `test_blind_signal_regression.py` | 89 | 5 |
| `test_blind_negative.py` | 63 | 6 |
| **测试小计** | **1,118** | **93** |

### 1.3 证据数据

| 类型 | 数量 | 大小 |
|------|------|------|
| 证据文件 | 59条 | 499 KB |
| 元数据 | 5个 | ~50 KB |
| **证据小计** | **64个文件** | **~549 KB** |

### 1.4 规范文档

| 类型 | 数量 | 大小 |
|------|------|------|
| 规范文件 | 14个 | 171 KB |
| **文档小计** | **14个文件** | **~171 KB** |

### 1.5 总规模汇总

```
┌─────────────────────────────────────┐
│  源代码：    5,970 行   ~432 KB     │
│  测试代码：  1,118 行    ~56 KB     │
│  证据数据：      64 个文件  ~549 KB │
│  规范文档：      14 个文件  ~171 KB │
├─────────────────────────────────────┤
│  合计：     ~7,088 行    ~1.27 MB  │
└─────────────────────────────────────┘
```

---

## 二、规范体系

### 2.1 独立规范（非V2.2.2）

盲派有自己独立的规范体系，**不适用V2.2.2**：

| 规范 | 版本 | 内容 |
|------|------|------|
| 《盲派生产规则.txt》 | V1-FINAL | 94节生产规则（§1-94） |
| L1e事件结构 | V3.3 | §60-64五域规则 |
| L2解层 | V3.4 | 事实吉凶判定引擎 |
| 做功归因 | V3.1 | 谁在做功/是否为我所用 |
| 做功效率 | V1-FINAL §38 | 四档枚举 |

**当前版本**：V3.4.3

### 2.2 V2.2.2适用范围

V2.2.2仅适用于六部经典引擎：
- L2A: YHZP 渊海子平
- L2B: PZZQ 子平真诠
- L2C: DTS 滴天髓
- L2D: QTBJ 穷通宝鉴
- L2E: SMTH 三命通会
- L3: SFTK 神峰通考

**盲派是独立体系，有自己的规范演进路径（V3.0→V3.4.3）**

---

## 三、架构合规性检查

### 3.1 导入链路验证

```python
# blind_bazi_engine.py L31-36（合法导入）
from ..engines.bazi_engine import BaziEngine, BaziChart, STEM_ELEMENT...
from ..signal.canonical_signal import CanonicalSignal, SourceEngine...
from ..reasoning.bazi_ten_gods import ten_god, BRANCH_HIDDEN_STEMS...
```

**检查结果**：
- ✅ 仅导入 L0事实层（BaziChart, STEM_ELEMENT）
- ✅ 仅导入信号层（CanonicalSignal）
- ✅ 仅导入通用十神规则
- ❌ 未导入 `ziping_v3.*`
- ❌ 未导入 `yongshen.py`
- ❌ 未导入格局/用神/调候模块

### 3.2 核心概念实现

| 概念 | 枚举/类 | 实现状态 |
|------|---------|----------|
| 宾主 | `BlindBaziResult.guest_host` | ✅ |
| 体用 | `TI_TEN_GODS/YONG_TEN_GODS` | ✅ |
| 做功方法 | `BlindWorkMethod` (5种) | ✅ |
| 做功效率 | `WK_EFFICIENCY` (4档) | ✅ |
| 功神角色 | `GONGSHEN_ROLE` | ✅ |
| 事件状态 | `marriage_state/wealth_state等` | ✅ |
| 吉凶方向 | `JDGDirection` | ✅ |

---

## 四、测试结果

```bash
python -m pytest tests/test_blind*.py -v
```

**结果**：
```
==================== 93 passed, 7 subtests passed in 0.90s ====================
```

**测试覆盖**：
- Golden: 21 cases ✅
- Integration: 9 cases ✅
- Rule Compliance: 22 cases ✅
- Yingqi: 14 cases ✅
- Themes: 12 cases ✅
- Signal Regression: 5 cases ✅
- Negative: 6 cases ✅
- Benchmark: 4 cases ✅

---

## 五、证据链审计

### 5.1 证据目录结构

```
data/evidence/blind_seg/
├── E-BLIND-WORK_METHOD-*.json     (6条)
├── E-BLIND-WORK_TARGET-*.json     (5条)
├── E-BLIND-WORK_RELATION-*.json   (4条)
├── E-BLIND-WORK_EFFICIENCY-*.json (3条)
├── E-BLIND-GUEST_HOST-*.json      (5条)
├── E-BLIND-BODY_USE-*.json        (6条)
├── E-BLIND-IMAGE-*.json           (6条)
├── E-BLIND-POWER_PARTY-*.json     (5条)
├── E-BLIND-YING_QI-*.json         (5条)
├── E-BLIND-EMPTY_USELESS-*.json   (6条)
├── E-BLIND-COMPLEX_WORK-*.json    (3条)
├── manifest.json                  # 总索引
├── provenance_*.json              # 来源元数据
└── source_verification_*.json     # 验证报告
```

**总计**：59条证据文件

### 5.2 证据来源等级

| 等级 | 定义 | 示例 |
|------|------|------|
| A (PRIMARY_TRADITION) | 段建业原书原文 | 《盲派初级命理学》 |
| B (SYSTEMATIZED) | 段氏系统化理论 | 《段氏理象学》 |
| C (CASE_EVIDENCE) | 命例验证 | 《盲派命理-案例资料集》 |
| D (DERIVED) | 后人整理 | 二手分析 |

---

## 六、风险项

### 6.1 低风险项

1. **单文件规模**：`blind_bazi_engine.py` 2,544行，接近建议上限（2,500行）
   - 影响：维护成本略高
   - 建议：未来可考虑拆分为 `blind_core.py` + `blind_work.py`

2. **版本演进快**：V3.0→V3.4.3仅一个月
   - 影响：历史版本可能未全部文档化
   - 状态：V3.4.3是当前稳定版

### 6.2 无风险项

- ❌ 无违规导入
- ❌ 无违禁符号
- ❌ 无架构违规
- ❌ 无测试失败

---

## 七、结论

| 维度 | 评级 |
|------|------|
| 代码结构 | ✅ PASS |
| 规范合规 | ✅ PASS（V1-FINAL/V3.4） |
| 测试覆盖 | ✅ PASS（93 cases） |
| 证据链 | ✅ PASS（59条） |
| 架构独立 | ✅ PASS |
| **综合评定** | **BASIC_VALIDATED** ✅ |

---

## 八、附录

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

### B. 关键提交记录

```
commit: V3.4.3 宾主归因升级
commit: V3.4 L2解层事实吉凶判定
commit: V3.3 L1e事件结构五域
commit: V3.2 六域施工+效率联动
commit: V3.1 做功归因（谁在做功）
commit: V3.0 做功六方式统一
```

---

**审计员**: BOT-MASTER  
**日期**: 2026-09-14  
**版本**: V1.0
