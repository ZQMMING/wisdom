# 顺天项目分支策略与治理架构

## 核心原则

**算 → 辨 → 解** 严格分层，引擎独立提交不交叉污染

```
算 (Calculation)        → BaziCalc / ZiweiCalc / HeluoCalc     确定性计算层
辨 (Signal/Judgment)    → Feature Extraction / Rule Matching   状态/关系层
解 (Assertion)          → Assertion Admission / Evidence        断言结论层
```

---

## 分支策略

### 主分支 (保护)
| 分支 | 用途 | 保护规则 |
|------|------|----------|
| `master` | 稳定集成 | 只接受 merge，禁止直接 push |
| `main` | GitHub 默认 | 同 master |

### 引擎开发分支 (独立)
| 分支 | 引擎 | 负责人 | 状态 |
|------|------|--------|------|
| `ziwei` | 紫微斗数 | Claude | ✅ 已存在 |
| `ziping` | 子平八字 | OpenCode | ✅ 已存在 |
| `blind` | 盲派 | TBD | ✅ 已存在 |
| `heluo` | 河洛理数 | TBD | ✅ 已存在 |
| `yi` | 易经 | TBD | ✅ 已存在 |

### 治理分支
| 分支 | 用途 | 状态 |
|------|------|------|
| `admission-governance-v2` | P2.1 断言准入治理 | ✅ 已存在 |
| `audit-e001-phase6` | Phase 6 审计 | ✅ 已存在 |

---

## 提交规范

### 引擎开发提交
```
Z10: ZiweiMethodProfile methodology contract
Z11: ZiweiPalaceResolution palace resolution layer
Z12: ZiweiRuleGraph rule matching engine
Z13: FeixingRuleGraph + dayu.py stub cleanup
Z14: 同盘异法验收 — 四派独立证据收集与隔离验证
```

### 治理提交
```
P2.1-F: Immutable External Trust Root
P2.1-G: Admission Atomicity
P2.1-H: Fail-Closed Enforcement
```

### 数据提交
```
H16.1: 河洛独立验证审计
H17: Correct P0/P1/P2 priority definition
```

---

## 引擎目录结构

```
src/tongshu/engines/
├── bazi/           # 八字核心计算
├── ziwei/          # 紫微引擎
│   ├── z14/        # Z14 同盘异法
│   └── rules/      # RuleGraph
├── heluo/          # 河洛引擎
├── yi/             # 易经引擎
├── blind/          # 盲派引擎
├── time/           # 时间解析
└── canonical/      # 规范状态 (共享)
```

---

## 决策记录

### D001: 引擎隔离架构 (2026-09-05)
- **问题**: 历史 commit 混合多个引擎开发
- **方案**: 按引擎创建独立分支
- **裁决**: 紫微→ziwei, 子平→ziping, 盲派→blind, 河洛→heluo, 易经→yi
- **状态**: 已执行

---

## 工作流

```
1. 从 master 创建引擎分支
   git checkout -b ziwei origin/master

2. 开发引擎功能
   git commit -m "Z15: 新增飞星rule匹配"

3. 提交到引擎分支
   git push origin ziwei

4. 通过 PR 合并回 master
   - 必须通过独立审计
   - 必须有测试覆盖
   - 必须无跨引擎污染
```
