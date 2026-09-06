# Git / Agent 治理规则

**确立时间**: 2026-09-06  
**版本**: v2.0  
**状态**: 已生效

---

## 核心原则（不可违反）

```
审计 ≠ 修改
裁决 ≠ 代码提交
每个Agent只对自己的引擎负责
禁止混合提交多个引擎代码
```

---

## 历史教训（问题链分析）

```text
审计
 ↓
发现问题
 ↓
裁决
 ↓
Agent 顺手修改代码 ← ❌ 这是污染源
 ↓
git add .
 ↓
commit
 ↓
其他引擎 / 参考资料 / 审计资产一起进入 commit
 ↓
后续 Agent 以这个 commit 为基线
 ↓
污染被继承
 ↓
现在出现代码、审计、裁决之间断层
```

---

## 正确流程（硬隔离模型）

```
                         main
                          │
                 ┌────────┼────────┐
                 │        │        │
               BAZI     ZIPING   ZIWEI
                 │        │        │
              Agent A  Agent B  Agent C
                 │        │        │
               commit   commit   commit
```

**每个Engine独立Commit，互不干扰：**

```
                    AUDIT
                      │
          ┌───────────┼───────────┐
          ↓           ↓           ↓
        BAZI        ZIPING       ZIWEI
       verdict      verdict      verdict
          │           │           │
          ↓           ↓           ↓
       implementation only
```

---

## 七大引擎边界

### 1. BOT-BAZI（八字排盘）
```
ALLOWED:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/time/**
  - tests/test_bazi*
  - tests/test_time*
  - docs/bots/BOT-BAZI/**

FORBIDDEN:
  - src/tongshu/engines/ziwei/**
  - src/tongshu/engines/heluo/**
  - src/tongshu/engines/yi/**
  - src/tongshu/engines/blind/**
  - src/tongshu/reasoning/**
```

### 2. BOT-ZIPING（子平辨层）
```
ALLOWED:
  - src/tongshu/engines/zi_ping_engine.py
  - src/tongshu/reasoning/**
  - tests/test_phase3*
  - tests/test_yi/**
  - docs/bots/BOT-ZIPING/**

FORBIDDEN:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/ziwei/**
  - src/tongshu/engines/heluo/**
  - src/tongshu/engines/yi/**
  - src/tongshu/engines/blind/**
```

### 3. BOT-BLIND（盲派）
```
ALLOWED:
  - src/tongshu/engines/blind_bazi_engine.py
  - tests/test_blind*
  - docs/bots/BOT-BLIND/**

FORBIDDEN:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/ziwei/**
  - src/tongshu/engines/heluo/**
  - src/tongshu/engines/yi/**
```

### 4. BOT-ZIWEI（紫微斗数）
```
ALLOWED:
  - src/tongshu/engines/ziwei_engine.py
  - src/tongshu/engines/ziwei/**
  - tests/test_ziwei*
  - docs/bots/BOT-ZIWEI/**

FORBIDDEN:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/zi_ping_engine.py
  - src/tongshu/engines/heluo/**
  - src/tongshu/engines/yi/**
  - src/tongshu/engines/blind/**
```

### 5. BOT-HELUO（河洛理数）
```
ALLOWED:
  - src/tongshu/engines/heluo/**
  - tests/test_heluo*
  - docs/bots/BOT-HELUO/**

FORBIDDEN:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/ziwei/**
  - src/tongshu/engines/yi/**
  - src/tongshu/engines/blind/**
```

### 6. BOT-YI（易经卦象）
```
ALLOWED:
  - src/tongshu/engines/yi/**
  - tests/yi/**
  - docs/bots/BOT-YI/**

FORBIDDEN:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/ziwei/**
  - src/tongshu/engines/heluo/**
  - src/tongshu/engines/blind/**
```

### 7. BOT-CORPUS（五部经典）
```
ALLOWED:
  - data/classics/**
  - data/evidence/**
  - src/tongshu/corpus/**
  - tests/test_corpus*
  - tests/test_full_classification.py
  - docs/bots/BOT-CORPUS/**

FORBIDDEN:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/ziwei/**
  - src/tongshu/engines/heluo/**
  - src/tongshu/engines/yi/**
  - src/tongshu/engines/blind/**
  - cases/golden/
```

---

## Commit 语义规则

### 正确示例
```
fix: BAZI P0-1 Solar term boundary fix
```
**应只包含**:
```
src/tongshu/engines/bazi/jd_converter.py
tests/test_bazi_boundary.py
docs/bots/BOT-BAZI/PHASE_N_REPORT.md
```

**不应包含**:
```
src/tongshu/reasoning/          ← ZIPING引擎
src/tongshu/engines/ziwei/      ← ZIWEI引擎
src/tongshu/engines/heluo/      ← HELUO引擎
data/evidence/blind_seg/        ← BLIND证据
cases/golden/                   ← Golden Dataset
```

---

## 禁止模式

```
❌ 审计 → 顺手修 → commit → 再审计 → 顺手修其他东西
❌ 一个commit包含多个引擎的代码
❌ 裁决文档与代码变更混在一起
❌ 未经边界审计直接合并main
❌ 本地有commit但没推送到GitHub
```

---

## 提交流程（标准化）

```
① GitHub/本地同步
        ↓
② 建立CLEAN BASELINE
        ↓
③ BAZI已冻结，不再动
        ↓
④ ZIPING独立审计
        ↓
⑤ ZIPING裁决（生成docs/decision/*，不产生代码）
        ↓
⑥ ZIPING Agent独立修复（仅限ALLOWED PATHS）
        ↓
⑦ ZIPING独立commit（仅含本引擎代码+测试+文档）
        ↓
⑧ 边界审计（git show --stat, git diff --name-only）
        ↓
⑨ push到GitHub
        ↓
⑩ 验收后合并main
        ↓
⑪ 再进入下一个引擎
```

---

## Agent开工前声明（必须）

```
BASE COMMIT: <sha>
BRANCH: agent/<engine>-<task>
ENGINE: <ENGINE_NAME>
TASK: <description>

ALLOWED PATHS:
  - src/tongshu/engines/<engine>/**
  - tests/<engine>/**
  - docs/bots/BOT-<ENGINE>/**

FORBIDDEN PATHS:
  - src/tongshu/engines/<other_engine>/**
  - data/evidence/<other_evidence>/**
  - cases/golden/
  - backend/
```

---

## Agent完成后报告（必须）

```
CHANGED FILES:
  - src/tongshu/engines/<engine>/xxx.py
  - tests/<engine>/test_xxx.py
  - docs/bots/BOT-<ENGINE>/PHASE_N_REPORT.md

TESTS: X/Y passed

COMMIT: <sha>
```

---

## 边界审计检查

```bash
# 检查commit内容
git show --stat <commit>

# 检查文件变更列表
git diff <base>..<commit> --name-only

# 运行边界审计脚本
bash scripts/audit_commit.sh <commit> <base>

# 验证只有ALLOWED PATHS中的文件
# 如有越界 → BLOCK commit
```

---

## Git Hooks配置

| 钩子 | 路径 | 功能 |
|------|------|------|
| pre-commit | .git/hooks/pre-commit | 阻止Golden Dataset、警告越界 |
| prepare-commit-msg | .git/hooks/prepare-commit-msg | 自动添加`[BOT-<ENGINE>]`前缀 |

---

## 当前Bot状态（2026-09-06）

| Bot | 引擎名称 | 状态 | 通过率 |
|-----|----------|------|--------|
| BOT-BAZI | 八字排盘 | ✅ FROZEN | 141/141 (100%) |
| BOT-ZIPING | 子平辨层 | ⏳ PHASE3 | 进行中 |
| BOT-BLIND | 盲派 | ✅ COMPLETE | 86/86 (100%) |
| BOT-ZIWEI | 紫微斗数 | ✅ COMPLETE | 45/45 (100%) |
| BOT-HELUO | 河洛理数 | ✅ COMPLETE | 26/26 (100%) |
| BOT-YI | 易经卦象 | ✅ COMPLETE | 94/94 (100%) |
| BOT-CORPUS | 五部经典 | ✅ COMPLETE | 26/26 (100%) |
| **总计** | | **100%** | **418/418** |

---

## 验证清单（每次commit前）

- [ ] BASE COMMIT已声明
- [ ] BRANCH命名符合 `agent/<engine>-<task>`
- [ ] 只修改了ALLOWED PATHS中的文件
- [ ] 没有修改Golden Dataset
- [ ] 没有修改其他引擎代码
- [ ] 测试已通过
- [ ] 边界审计通过（git diff --name-only）
- [ ] 裁决文档已生成（docs/decision/*）
- [ ] 已push到GitHub

---

## 参考文档

- SOUL.md: 总控Bot职责与权限
- AGENTS.md: Agent工作协议
- docs/GIT_AGENT_WORKFLOW_CONFIG.md: Git工作流配置
- docs/SHUNTIAN_FINAL_ARCHITECTURE.md: 项目架构

---

**规则确立**: 2026-09-06  
**版本**: v2.0  
**状态**: 已生效

---
*@bot-master*
