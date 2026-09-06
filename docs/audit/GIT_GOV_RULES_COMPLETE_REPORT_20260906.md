# ✅ 顺天Git/Agent治理规则建立完成 - 最终报告

**完成时间**: 2026-09-06 20:40  
**提交**: `787ee0f8`

---

## 一、核心问题诊断

### 1.1 历史问题链

```
审计 → 发现问题 → 裁决 → Agent顺手修改代码 → git add . 
→ commit（混入其他引擎/参考资料）→ 后续Agent以污染commit为基线 
→ 污染被继承 → 代码/审计/裁决之间断层
```

### 1.2 根因分析

**本质问题**: 审计裁决与工程实施没有隔离

- 审计Agent产生了事实、结论、建议
- 但错误地同时实施了代码修改
- 导致commit中混入非本引擎文件
- 后续Agent以污染commit为基线继续工作

**具体表现**:
- 审计commit混入大量参考文件
- 紫微案例、audit_log、de421等被意外加入
- 某些修复实际上不是对应引擎的修改
- 后续Agent又基于污染后的commit继续工作

---

## 二、治理规则建立

### 2.1 三隔离原则

```
原则1: 审计与实施隔离
       裁决 ≠ 修改代码
       审计只产生事实、结论、建议
       实施只产生代码变更

原则2: 引擎边界隔离  
       每个Agent只对自己负责的引擎产生commit
       禁止跨引擎修改
       禁止在引擎commit中混入非本引擎文件

原则3: Commit语义隔离
       一个commit = 一个语义单元
       禁止混合提交不同引擎的变更
       禁止在裁决commit中实施代码修改
```

### 2.2 角色与职责

| 角色 | 职责 | 产出 | 权限 |
|------|------|------|------|
| **审计Agent** | 发现事实、验证契约、评估风险 | 审计报告、证据链 | 只读，禁止修改代码 |
| **裁决Agent** | 评估严重程度、决定修复优先级 | 裁决文档、修复要求 | 只读，禁止修改代码 |
| **工程Agent** | 根据裁决实施修复 | 代码、测试、commit | 只能修改本引擎文件 |
| **治理Agent** | 检查commit边界、拦截违规提交 | 检查报告、拦截记录 | 强制执行边界检查 |

### 2.3 工作流程

```
阶段1: 审计
  ├─ 审计Agent扫描引擎代码
  ├─ 收集证据、验证契约
  ├─ 生成审计报告（只读）
  └─ Commit到GitHub: docs/audit/{engine}/AUDIT_*.md

阶段2: 裁决
  ├─ 裁决Agent评估审计结果
  ├─ 确定P0/P1/P2优先级
  ├─ 生成裁决文档（只读）
  └─ Commit到GitHub: docs/decision/{engine}/ARBITRATION_*.md

阶段3: 实施
  ├─ 工程Agent收到裁决文档
  ├─ Agent开工前报告（BASE COMMIT, BRANCH, ENGINE, ALLOWED PATHS, FORBIDDEN PATHS）
  ├─ 只修改ALLOWED路径下的文件
  ├─ 运行本引擎测试
  ├─ 生成commit（仅包含本引擎文件）
  └─ Pre-commit hook检查边界

阶段4: 验收
  ├─ 治理Agent检查commit内容
  ├─ 确认无越界文件
  ├─ 确认测试通过
  └─ 允许合并到main
```

---

## 三、Git Hooks配置

### 3.1 Pre-commit Hook（边界检查）

**功能**:
- ✅ 检测混合引擎提交
- ✅ 拦截BAZI冻结引擎修改
- ✅ 检查参考资料是否混入
- ✅ 输出详细的检查报告

**测试结果**:

| 测试场景 | 预期结果 | 实际结果 |
|----------|----------|----------|
| 混合引擎提交（BAZI+HELUO） | 拦截 | ✅ 拦截 |
| 单一引擎提交（ZIPING） | 通过 | ✅ 通过 |
| BAZI冻结引擎提交 | 拦截 | ✅ 拦截 |
| 文档提交 | 通过 | ✅ 通过 |

### 3.2 Post-commit Hook（验收提醒）

**功能**:
- ✅ 显示commit信息
- ✅ 识别引擎类型
- ✅ 工程提交提醒验收
- ✅ 审计/裁决提交提醒等待裁决

---

## 四、创建的文件

```
docs/ARCHITECTURE/
├── GIT_GOV_RULES.md          # 顺天Git/Agent治理规则v1.0（557行）
├── BOT_WORKFLOW_SPEC.md      # BOT工作流规范（374行）
└── ENGINE_SUBMISSION_SPEC.md # 引擎独立提交规范（320行）

.git/hooks/
├── pre-commit                # ✅ 引擎边界检查（已测试通过）
├── pre-push                  # ✅ 同步检查（已测试通过）
└── post-commit               # ✅ 完工验收提醒（已测试通过）

scripts/
├── bot-workflow.sh           # 工作流统一入口（341行）
└── bot-selfcheck/
    ├── bot-master.sh         # BOT-MASTER自检
    ├── bot-bazi.sh           # BOT-BAZI自检
    ├── bot-ziping.sh         # BOT-ZIPING自检
    ├── bot-blind.sh          # BOT-BLIND自检
    ├── bot-heluo.sh          # BOT-HELUO自检
    ├── bot-yi.sh             # BOT-YI自检
    ├── bot-time.sh           # BOT-TIME自检
    └── bot-corpus.sh         # BOT-CORPUS自检
```

---

## 五、Commit格式规范

### 5.1 前缀对照表

| 前缀 | 引擎/职责 | 示例 |
|------|-----------|------|
| G: | Governance治理 | `G: Governance - 建立Git治理规则` |
| P: | BAZI八字排盘 | `P: BAZI - 修复日柱计算` |
| ZP: | ZIPING子平 | `ZP: ZIPING - P0-1修复 ContextAssembler` |
| BL: | BLIND盲派 | `BL: BLIND - 新增做功链解析` |
| H: | HELUO河洛 | `H: HELUO - 修复节候卦计算` |
| Y: | YI易经 | `Y: YI - 新增梅花易数起卦` |
| T: | TIME时间计算 | `T: TIME - 修复真太阳时` |
| C: | CORPUS语料库 | `C: CORPUS - 新增滴天髓原文` |
| E: | Evidence证据 | `E: Evidence - 新增E-YHZP-001` |
| A: | Audit审计 | `A: AUDIT - ZIPING Phase 2报告` |
| D: | Decision裁决 | `D: DECISION - ZIPING P0-1裁决` |

### 5.2 Commit内容规范

**正确示例**:
```
ZP: ZIPING - P0-1修复 - ContextAssembler不再重新调用BAZI
```
内容:
- `src/tongshu/reasoning/zi_ping_context_assembler.py` ✅
- `tests/test_ziping_context.py` ✅
- `docs/audit/ziping/AUDIT-P0-1.md` ✅

**错误示例**（混合提交）:
```
fix: 修复ZIPING并顺手更新其他引擎
```
内容:
- `src/tongshu/reasoning/zi_ping_context_assembler.py` ✅
- `src/tongshu/engines/bazi_engine.py` ❌（BAZI已冻结）
- `src/tongshu/engines/ziwei_engine.py` ❌（不是本引擎）
- `docs/audit/ziwei/紫微案例.bsp` ❌（参考资料不应进入commit）

---

## 六、Agent开工/完工报告模板

### 6.1 开工报告

```markdown
# Agent 开工报告

**时间**: {ISO时间}  
**Agent**: {名称}  
**任务**: {任务描述}  
**裁决依据**: {ARBITRATION_ID}

---

## 环境信息

```
BASE COMMIT: {commit SHA}
BRANCH: {agent/{engine}-{task}}
ENGINE: {引擎名称}
```

## 路径边界

### ALLOWED PATHS（允许修改）
```
src/tongshu/{engine}/**
tests/test_{engine}*.py
docs/audit/{engine}/**
docs/decision/{engine}/**
```

### FORBIDDEN PATHS（禁止修改）
```
src/tongshu/bazi/**
src/tongshu/ziwei/**
src/tongshu/heluo/**
src/tongshu/yi/**
src/tongshu/blind/**
data/classics/**
docs/audit/other-engine/**
docs/decision/other-engine/**
```
```

### 6.2 完工报告

```markdown
# Agent 完工报告

**时间**: {ISO时间}  
**Agent**: {名称}  
**任务**: {任务描述}

---

## 执行结果

```
COMMIT: {commit SHA}
TESTS: {N}/{N} passed
CHANGED FILES: {文件列表}
```

## 文件变更清单

### 修改文件
```
{文件路径} - {变更说明}
```

### 新增文件
```
{文件路径} - {文件说明}
```

---

## 边界检查

- [ ] 仅修改ALLOWED路径下的文件
- [ ] 未触碰FORBIDDEN路径
- [ ] 测试全部通过
- [ ] 无意外文件进入commit
```

---

## 七、违规处理

### 7.1 违规类型

| 类型 | 定义 | 等级 | 处理 |
|------|------|------|------|
| 混合提交 | 一次commit包含多个引擎的代码 | P0 | Block merge，重新提交 |
| 越界修改 | 修改了FORBIDDEN路径下的文件 | P0 | Block merge，重新提交 |
| 冻结引擎 | 修改了BAZI引擎代码 | P0 Critical | Block merge，上报裁决者 |
| 未同步 | commit未推送到GitHub | P1 | 立即push |
| 先执行后裁决 | 未等待裁决就执行变更 | P1 | 回滚变更，重新走裁决流程 |

### 7.2 违规后果

```
首次违规: 警告 + 重新培训
二次违规: 暂停提交权限24小时
三次违规: 上报裁决者仲裁
```

---

## 八、工作顺序固定

### 8.1 正确顺序

```
① GitHub / 本地同步
        ↓
② 建立CLEAN BASELINE
        ↓
③ BAZI已冻结，不再动
        ↓
④ ZIPING独立审计
        ↓
⑤ ZIPING裁决
        ↓
⑥ ZIPING Agent独立修复
        ↓
⑦ ZIPING独立commit
        ↓
⑧ 验收commit
        ↓
⑨ 合并main
        ↓
⑩ 再进入下一个引擎
```

### 8.2 错误顺序（禁止）

```
审计 → 顺手修 → commit → 再审计 → 顺手修其他东西
```

**后果**: 历史断层 + commit污染 + Agent基线漂移

---

## 九、快速参考

### 9.1 提交前自检命令

```bash
# 检查待提交文件
git diff --cached --name-only

# 检查是否包含冻结引擎
git diff --cached --name-only | grep "bazi_engine.py" && echo "❌ 禁止修改BAZI"

# 检查是否混合引擎
git diff --cached --name-only | grep -E "^(src/tongshu/engines/(bazi|ziwei|heluo|blind|yi|time)/)" | cut -d'/' -f4 | sort -u

# 查看commit内容
git show --stat HEAD
```

### 9.2 各引擎ALLOWED PATHS

```bash
# BOT-BAZI（已冻结，禁止修改）
ALLOWED: src/tongshu/engines/bazi_engine.py (只读)
FORBIDDEN: 全部（冻结）

# BOT-ZIPING
ALLOWED: src/tongshu/reasoning/zi_ping*.py, tests/test_ziping*.py
FORBIDDEN: src/tongshu/engines/*, src/tongshu/reasoning/other_*

# BOT-BLIND
ALLOWED: src/tongshu/engines/blind/, tests/test_blind*.py
FORBIDDEN: src/tongshu/engines/other_*, tests/test_other_*

# BOT-HELUO
ALLOWED: src/tongshu/engines/heluo/, tests/test_heluo*.py
FORBIDDEN: src/tongshu/engines/other_*, tests/test_other_*

# BOT-YI
ALLOWED: src/tongshu/engines/meihua.py, src/tongshu/engines/yi/, tests/test_yi*.py
FORBIDDEN: src/tongshu/engines/other_*, tests/test_other_*

# BOT-TIME
ALLOWED: src/tongshu/engines/time/, tests/test_time*.py
FORBIDDEN: src/tongshu/engines/other_*, tests/test_other_*
```

---

## 十、提交历史

```
787ee0f8 G: Governance - 建立顺天Git/Agent治理规则v1.0: 三隔离原则 + 硬边界检查
e34662cd G: Governance - 完成BOT工作流规范建立最终报告
e7446fe5 G: Governance - 完成BOT工作流规范建立总结报告
04f49248 G: Governance - 添加BOT工作流详细规范文档
99a41b91 G: Governance - 完成BOT工作流规范建立报告
d40e6071 G: Governance - 添加8个BOT自检脚本
a2925dc4 G: Governance - 添加BOT工作流统一入口脚本
1739f65a G: Governance - 建立BOT工作流规范: 三条铁律 + 裁决前置流程
```

---

## 十一、GitHub状态

```
Remote: https://github.com/ZQMMING/wisdom
Branch: main
Latest: 787ee0f8 G: Governance - 建立顺天Git/Agent治理规则v1.0
Status: Clean (nothing to commit)
Tests: 35/35 passed
```

---

## 十二、核心要点回顾

### 12.1 三条铁律

```
1. 审计与实施隔离: 裁决 ≠ 修改代码
2. 引擎边界隔离: 每个Agent只修改自己负责的引擎
3. Commit语义隔离: 一个commit = 一个语义单元
```

### 12.2 关键改变

| 之前 | 之后 |
|------|------|
| 审计(commit)混入代码修改 | 审计只产生报告，不修改代码 |
| 一个commit包含多个引擎 | 一个commit只包含一个引擎 |
| 决策和實施没有隔离 | 裁决与实施严格分离 |
| 没有边界检查 | Pre-commit hook强制检查 |
| 基准线被污染 | CLEAN BASELINE，每次审计从干净基线开始 |

### 12.3 验收标准

每次commit必须通过：
- [ ] 仅包含本引擎相关路径
- [ ] 未触碰BAZI（冻结引擎）
- [ ] 未触碰其他引擎代码
- [ ] 未混入参考资料/案例文件
- [ ] 测试全部通过
- [ ] 无意外文件进入commit

---

## 十三、下一步行动

1. **通知所有Agent**: 学习并遵守本治理规则
2. **建立CLEAN BASELINE**: 当前commit `787ee0f8` 作为新基线
3. **开始ZIPING独立审计**: 从clean baseline开始
4. **严格执行边界检查**: 任何违规commit立即block

---

**本规则经裁决者批准后生效，所有Agent必须严格遵守。**
