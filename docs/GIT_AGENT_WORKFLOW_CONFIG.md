# Git / Agent 工作流配置

**确立时间**: 2026-09-06  
**版本**: v1.2  
**状态**: 已配置并生效

---

## 三大核心原则

### 原则1: 独立Commit（不污染其他引擎）
```
每个Agent只修改自己的引擎代码
禁止一个commit包含多个引擎的代码
边界审计：git diff --name-only 验证
```

### 原则2: 本地+GitHub同步
```
所有commit必须push到GitHub
本地与远程保持同步
禁止只有本地commit没有远程
```

### 原则3: 审计/裁决先提交，等待裁决后执行
```
审计文档 → commit → GitHub
裁决文档 → commit → GitHub
等待User/GPT裁决 → 确认后才能执行代码修改
```

---

## GitHub配置

**Remote**: `https://github.com/ZQMMING/wisdom.git`  
**认证**: Token已配置  
**Current Branch**: `main`

### 验证连接 ✅
```bash
git ls-remote origin
# 输出: bdc6294ec5fcd6757d54827243584e1ec72ac15b HEAD
#       bdc6294ec5fcd6757d54827243584e1ec72ac15b refs/heads/main
```

---

## Git Hooks配置

### 1. pre-commit钩子
**路径**: `.git/hooks/pre-commit`  
**功能**: 
- 阻止提交Golden Dataset
- 警告backend目录修改
- 检查其他引擎代码变更

### 2. prepare-commit-msg钩子
**路径**: `.git/hooks/prepare-commit-msg`  
**功能**:
- 自动检测分支名 `agent/<engine>-*`
- 自动添加commit前缀 `[BOT-<ENGINE>]`

**示例**:
```bash
# 分支: agent/ziping-p0-fix
# 提交: "Fix ContextAssembler fail-closed"
# 结果: "[BOT-ZIPING]
# Fix ContextAssembler fail-closed"
```

---

## Bot工作区配置

### BOT-BAZI
```yaml
engine: bazi
allowed_paths:
  - src/tongshu/engines/bazi/**
  - tests/test_bazi*
  - tests/test_time*
  - docs/bots/BOT-BAZI/**
forbidden_paths:
  - src/tongshu/engines/ziwei/**
  - src/tongshu/engines/heluo/**
  - src/tongshu/engines/yi/**
  - src/tongshu/engines/blind/**
  - data/evidence/ziwei/
  - data/evidence/heluo/
  - cases/golden/
branch_pattern: agent/bazi-*
commit_format: "[BOT-BAZI] <description>"
status: FROZEN ✅
```

### BOT-ZIPING
```yaml
engine: ziping
allowed_paths:
  - src/tongshu/engines/zi_ping_engine.py
  - src/tongshu/reasoning/**
  - tests/test_phase3*
  - tests/test_yi/**
  - docs/bots/BOT-ZIPING/**
forbidden_paths:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/ziwei/**
  - src/tongshu/engines/heluo/**
  - src/tongshu/engines/yi/**
  - src/tongshu/engines/blind/**
  - data/evidence/ziwei/
  - cases/golden/
branch_pattern: agent/ziping-*
commit_format: "[BOT-ZIPING] <description>"
status: PHASE3 ⏳
```

### BOT-ZIWEI
```yaml
engine: ziwei
allowed_paths:
  - src/tongshu/engines/ziwei_engine.py
  - src/tongshu/engines/ziwei/**
  - tests/test_ziwei*
  - docs/bots/BOT-ZIWEI/**
forbidden_paths:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/zi_ping_engine.py
  - src/tongshu/engines/heluo/**
  - src/tongshu/engines/yi/**
  - src/tongshu/engines/blind/**
  - data/evidence/blind_seg/
  - cases/golden/
branch_pattern: agent/ziwei-*
commit_format: "[BOT-ZIWEI] <description>"
status: COMPLETE ✅
```

### BOT-HELUO
```yaml
engine: heluo
allowed_paths:
  - src/tongshu/engines/heluo/**
  - tests/test_heluo*
  - docs/bots/BOT-HELUO/**
forbidden_paths:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/ziwei/**
  - src/tongshu/engines/yi/**
  - src/tongshu/engines/blind/**
  - data/evidence/blind_seg/
  - cases/golden/
branch_pattern: agent/heluo-*
commit_format: "[BOT-HELUO] <description>"
status: COMPLETE ✅
```

### BOT-YI
```yaml
engine: yi
allowed_paths:
  - src/tongshu/engines/yi/**
  - tests/yi/**
  - docs/bots/BOT-YI/**
forbidden_paths:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/ziwei/**
  - src/tongshu/engines/heluo/**
  - src/tongshu/engines/blind/**
  - data/evidence/ziwei/
  - cases/golden/
branch_pattern: agent/yi-*
commit_format: "[BOT-YI] <description>"
status: COMPLETE ✅
```

### BOT-BLIND
```yaml
engine: blind
allowed_paths:
  - src/tongshu/engines/blind_bazi_engine.py
  - tests/test_blind*
  - docs/bots/BOT-BLIND/**
forbidden_paths:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/ziwei/**
  - src/tongshu/engines/heluo/**
  - src/tongshu/engines/yi/**
  - data/evidence/ziwei/
  - cases/golden/
branch_pattern: agent/blind-*
commit_format: "[BOT-BLIND] <description>"
status: COMPLETE ✅
```

### BOT-CORPUS
```yaml
engine: corpus
allowed_paths:
  - data/classics/**
  - data/evidence/**
  - src/tongshu/corpus/**
  - tests/test_corpus*
  - tests/test_full_classification.py
  - docs/bots/BOT-CORPUS/**
forbidden_paths:
  - src/tongshu/engines/bazi/**
  - src/tongshu/engines/ziwei/**
  - src/tongshu/engines/heluo/**
  - src/tongshu/engines/yi/**
  - src/tongshu/engines/blind/**
  - cases/golden/
branch_pattern: agent/corpus-*
commit_format: "[BOT-CORPUS] <description>"
status: COMPLETE ✅
```

---

## 标准工作流程

### 阶段1: 审计提交（等待裁决）

```bash
# 1. 创建审计分支
git checkout -b agent/<engine>-audit-<date>

# 2. 执行审计，生成文档
# 产出：docs/audit/<engine>/PHASE_N_REPORT.md
# 产出：docs/decision/<engine>/DECISION_N.md

# 3. 提交审计文档（不提交代码）
git add docs/audit/<engine>/
git add docs/decision/<engine>/
git commit -m "Phase N audit report"
# 自动添加前缀: [BOT-<ENGINE>]

# 4. 推送到GitHub
git push origin agent/<engine>-audit-<date>

# 5. 等待User/GPT裁决
# （此阶段不执行任何代码修改）
```

### 阶段2: 裁决确认

```markdown
## 裁决记录

| 项目 | 裁决 |
|------|------|
| P0-1 | 接受，需修复 |
| P1-1 | 接受，需优化 |
| P2-1 | 记录，暂不修复 |

裁决时间: 2026-09-06
裁决人: User
```

### 阶段3: 代码修复提交

```bash
# 1. 基于最新main创建修复分支
git checkout main
git pull origin main
git checkout -b agent/<engine>-fix-<date>

# 2. 执行代码修复（仅限allowed_paths）
# 修改：src/tongshu/engines/<engine>/...
# 修改：tests/<engine>/...

# 3. 运行测试验证
pytest tests/<engine>/ -v

# 4. 提交代码变更
git add src/tongshu/engines/<engine>/
git add tests/<engine>/
git commit -m "Fix P0-1: <description>"
# 自动添加前缀: [BOT-<ENGINE>]

# 5. 边界审计（必须）
bash scripts/audit_commit.sh HEAD main
# 确认只有本引擎文件

# 6. 推送到GitHub
git push origin agent/<engine>-fix-<date>
```

### 阶段4: 合并验证

```bash
# 1. PR合并后同步
git checkout main
git pull origin main

# 2. 验证所有测试通过
pytest tests/ -v

# 3. 进入下一个引擎
```

---

## 边界审计脚本

**路径**: `scripts/audit_commit.sh`  
**用法**: `bash scripts/audit_commit.sh [commit] [base]`

**功能**:
- 检查commit是否包含其他引擎代码
- 检查是否修改Golden Dataset
- 检查是否修改Evidence数据（非CORPUS引擎）
- 输出审计结果，越界则BLOCK

---

## Git Hooks位置

| 钩子 | 路径 | 功能 |
|------|------|------|
| pre-commit | .git/hooks/pre-commit | 阻止越界提交 |
| prepare-commit-msg | .git/hooks/prepare-commit-msg | 自动添加Bot前缀 |

---

## 当前状态（2026-09-06）

| Bot | 状态 | 最新Commit | 远程同步 |
|-----|------|------------|----------|
| BOT-BAZI | ✅ FROZEN | f9616c17 | ✅ 已同步 |
| BOT-ZIPING | ⏳ PHASE3 | 进行中 | - |
| BOT-ZIWEI | ✅ COMPLETE | 待确认 | 待推送 |
| BOT-HELUO | ✅ COMPLETE | 待确认 | 待推送 |
| BOT-YI | ✅ COMPLETE | 待确认 | 待推送 |
| BOT-BLIND | ✅ COMPLETE | 待确认 | 待推送 |
| BOT-CORPUS | ✅ COMPLETE | 待确认 | 待推送 |

---

## 待执行任务

### 遗留测试文件清理（待裁决）

```bash
# 建议操作
mkdir -p tests/deprecated
mv tests/test_audit_draft_mappings.py tests/test_c12_c13.py tests/deprecated/
mv tests/test_ziwei_feixing_*.py tests/test_ziwei_rule_graph.py tests/test_ziwei_z14_same_chart.py tests/deprecated/
```

**理由**: 这些测试引用已删除的代码，持续产生错误。

---

## 验收清单

- [x] Git Hooks已配置（pre-commit, prepare-commit-msg）
- [x] 边界审计脚本已创建（scripts/audit_commit.sh）
- [x] GitHub Remote已配置并验证
- [x] Bot工作区配置已固化
- [ ] 所有Bot已知晓新工作流
- [ ] 遗留测试文件清理（待裁决）

---

**配置确立**: 2026-09-06  
**版本**: v1.2  
**状态**: 已生效

---
*@bot-master*
