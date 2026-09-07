# 顺天 V2 验收状态总览

> 更新: 2026-09-08 | 依据: V2验收和生产准入规范 (E0-E10)
> 原则: 如实标注，不虚标。测试通过 ≠ 计算验证通过 ≠ 生产准入。

## 一、九引擎验收矩阵

|| 引擎 | E0 Contract | E1 Unit | E2 Alg | E3 Boundary | E4 Negative | E5 Golden | E6 Reg | E7 Integ | E8 Trace | E9 Audit | E10 | 测试数 | 生命周期 |
||------|:-----------:|:-------:|:------:|:-----------:|:-----------:|:---------:|:------:|:--------:|:--------:|:--------:|:---:|:------:|----------|
|| BAZI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⏳ | COND | 19+44 | FROZEN+Canonical修复 |
|| ZIPING | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ | ⚠️ | ✅ | ⚠️ | ⏳ | COND | 21 | 算法就绪/接线完成 |
|| BLIND | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ⏳ | ⏳ | COND | 101 | 证据74/74✅ strength修复 |
|| ZIWEI | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ⚠️ | ✅ | ⏳ | ⏳ | COND | 96 | Golden 80/80 (100%) |
|| HELUO | ✅ | ✅ | ✅ | 🔄 | 🔄 | ✅ | ⚠️ | ✅ | ⏳ | ⏳ | COND | 59+13 | E3/E4派发中 |
|| MEIHUA | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ⏳ | COND | 191 | E3/E4/E5✅ 输入校验修复 |
|| YIJING | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⏳ | ⏳ | COND | 113 | E3/E4/E5✅ |
|| HUANGLI | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ⚠️ | ❌ | ⏳ | COND | 52 | E3/E4/E5✅ |
|| CORPUS | ✅ | ✅ | N/A | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ✅ | ⏳ | ⏳ | COND | 25 | 4,089条注册待核验 |

图例: ✅ PASS | ⚠️ PARTIAL | ❌ FAIL | ⏳ PENDING | 🔄 派发中

## 二、本轮修复的真实缺陷（代码级验证）

| 引擎 | 缺陷 | 修复 | commit |
|------|------|------|--------|
| BAZI Canonical | CrossDomainResult无法JSON序列化 + Schema缺失 | 递归to_dict + schema创建 | 474e5e11 |
| MEIHUA | cast_by_numbers(1.5,3) KeyError非TypeError | isinstance校验 | b9ef6e25 |
| MEIHUA | 时辰数/动爻公式错误(历史) | 公式修复 | 4f46cd40 |
| BLIND | CanonicalSignal缺strength标准输入崩溃 | 7处补确定性值 | b7675d92 |
| YI | yao_ci 48处双后缀 | 数据修复 | 0df0d893 |

## 三、P0/P1 问题汇总

### P0（阻塞生产准入）
| 引擎 | 问题 | 责任 | 状态 |
|------|------|------|------|
| ~~ZIPING~~ | ~~零生产调用方~~ | BOT-ZIPING | ✅ 已解决 (d3cd7fba) |
| BLIND | Golden Set未建立 | BOT-BLIND | 🔺 待派发（证据74/74已完成） |
| BLIND | ~~证据0/74 provenance待验~~ | BOT-BLIND | ✅ 74/74 SEMANTIC_MATCH（待User确认口径） |
| MEIHUA | ~~Golden Set未建立~~ | BOT-MEIHUA | ✅ 30案例 (b9ef6e25) |
| MEIHUA | Adapter未接入 + 无证据目录 | BOT-MEIHUA | 待办 |
| HUANGLI | ~~Golden Set未建立~~ | BOT-HUANGLI | ✅ 38案例 (7ebdf8dd) |
| HUANGLI | 生产路径未接入 | BOT-HUANGLI | 待办 |

### P1
| 引擎 | 问题 | 责任 | 状态 |
|------|------|------|------|
| ZIWEI | ZW-004证据不足 + Chart Hash未建 | BOT-ZIWEI | 待办 |
| HELUO | E3/E4边界+负向测试 | BOT-HELUO | 🔄 派发中 (proc_03938e1f5c8e) |
| YIJING | ~~Golden Set未建~~ | BOT-YI | ✅ 20案例 (0df0d893) |
| CORPUS | 5,604条UNVERIFIED证据 | BOT-CORPUS | 长期（人工原典核验） |
| BAZI | E8 Production Trace待验证 | BOT-BAZI | 待办 |

## 四、V2验收顺序进度

```
BAZI FOUNDATION → ✅ FROZEN + Canonical修复 (474e5e11)
Canonical State → ✅ 契约测试44/44 (Phase 4通过)
ZIPING → ✅ 算法就绪+接线完成 (d3cd7fba)
MANGPAI → ⚠️ 代码✅+证据✅+strength修复; Golden Set待建
ZIWEI → ✅ Golden 80/80执行100% (ea5700f7)
HELUO → ⚠️ E5✅; E3/E4派发中
MEIHUA → ✅ 算法修复+E3/E4/E5 (b9ef6e25); Adapter待接入
YIJING → ✅ E3/E4/E5 (0df0d893)
HUANGLI → ✅ E3/E4/E5 (7ebdf8dd); 当日卦+通书匹配验证通过
CORPUS → ⚠️ 4,089条注册完成; 核验长期
Cross-Engine Baseline → ✅ 5引擎hash快照+污染检测 (e6464c23)
```

## 五、Cross-Engine Contamination（Phase 5）

**baseline工具**: `scripts/cross_engine_baseline.py`（e6464c23）
- 5引擎hash快照: ziwei/meihua/huangli/blind/heluo
- 首次实证: blind修复后其他4引擎hash全部不变 ✅
- 已修复PYTHONHASHSEED顺序噪声（set→list排序规范化）
- 用法: 引擎变更后 `--check`，其他引擎必须OK

## 六、待User裁决

1. **BLIND证据验证标准**: SEMANTIC_MATCH（现代《段氏理象学》语义匹配+原文摘录）74/74 — 是否接受为验证通过？
2. **越界提交**: BOT-YI `0df0d893`混入BLIND文件、BOT-BAZI `7db31fb0`混入frontend-case — 已记录，历史不重写，成果保留
3. **frontend-case在途文件**: 被7db31fb0提前commit，前端负责人需确认
