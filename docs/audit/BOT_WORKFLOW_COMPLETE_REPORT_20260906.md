# ✅ BOT 工作流规范建立完成报告

**完成时间**: 2026-09-06 20:36  
**提交**: `d40e6071`

---

## 一、执行摘要

✅ **三条铁律建立完成**  
✅ **Git Hooks 配置完成** (pre-commit, pre-push, post-commit)  
✅ **8 个 BOT 自检脚本创建完成**  
✅ **BOT 工作流统一入口创建完成**  
✅ **全部同步到 GitHub**

---

## 二、核心成果

### 2.1 三条铁律

```
铁律1: 独立提交 - 每个 BOT 只能提交自己的引擎部分，禁止污染其他引擎
铁律2: 实时同步 - 所有本地 commit 必须立即同步到 GitHub
铁律3: 裁决前置 - 审计和裁决必须 commit 到 GitHub，等待 GPT 和用户裁决后才能执行
```

### 2.2 BOT 职责矩阵

| BOT | 前缀 | 职责 | 代码路径 |
|-----|------|------|----------|
| BOT-MASTER | G: | 治理、证据、调度 | governance/, assertion/, evidence/ |
| BOT-BAZI | P: | 八字排盘 | bazi_engine.py |
| BOT-ZIPING | ZP: | 子平引擎 | zi_ping*.py |
| BOT-BLIND | BL: | 盲派引擎 | blind/ |
| BOT-HELUO | H: | 河洛引擎 | heluo/ |
| BOT-YI | Y: | 易经引擎 | meihua.py, yi/ |
| BOT-TIME | T: | 时间计算 | time/ |
| BOT-CORPUS | C: | 语料库 | classics/, docs/bots/*/ |

---

## 三、Git Hooks 配置

### 3.1 Pre-commit Hook（引擎隔离检查）

**功能**: 自动检测混合引擎提交

**拦截示例**:
```
=== 引擎隔离检查 ===
文件分布:
  ✓ heluo: 1 files
  ✓ blind: 1 files
  ✓ bazi: 1 files
  ✓ yi: 1 files

❌ 错误: 检测到混合引擎提交！
   请拆分提交，每个引擎独立提交
```

**排除范围**: 
- scripts/ (工作流脚本)
- docs/ (文档)
- node_modules/, __pycache__/, *.pyc

### 3.2 Pre-push Hook（同步检查）

**检查项**:
- 无未提交更改
- 远程连接正常
- 当前分支正确

### 3.3 Post-commit Hook（裁决提醒）

**提醒内容**:
- Commit SHA 和 message
- 如果是裁决相关，提醒等待 GPT 和用户裁决
- 提示裁决文档位置

---

## 四、自检脚本清单

```
scripts/bot-selfcheck/
├── bot-master.sh    # BOT-MASTER 自检
├── bot-bazi.sh      # BOT-BAZI 自检
├── bot-ziping.sh    # BOT-ZIPING 自检
├── bot-blind.sh     # BOT-BLIND 自检
├── bot-heluo.sh     # BOT-HELUO 自检
├── bot-yi.sh        # BOT-YI 自检
├── bot-time.sh      # BOT-TIME 自检
└── bot-corpus.sh    # BOT-CORPUS 自检
```

**每个脚本包含**:
1. 分支检查（必须在 main）
2. 测试运行（本 BOT 的所有测试）
3. 文件范围检查（是否混合其他 BOT 的文件）
4. 证据文件检查（完整性验证）
5. 违规提醒（明确的错误处理和修复指引）

---

## 五、工作流入口脚本

**文件**: `scripts/bot-workflow.sh`

**命令**:
```bash
# 运行自检
./scripts/bot-workflow.sh BOT-BAZI selfcheck

# 提交代码
./scripts/bot-workflow.sh BOT-HELUO commit

# 创建审计报告
./scripts/bot-workflow.sh BOT-ZIPING audit phase2

# 申请裁决
./scripts/bot-workflow.sh BOT-MASTER arbitrate technical

# 查看状态
./scripts/bot-workflow.sh BOT-MASTER status
```

---

## 六、提交流程

### 6.1 标准提交流程

```
┌─────────────────────────────────────────────────────────────────┐
│  1. 开发/修复代码                                               │
│     ↓                                                          │
│  2. 运行自检                                                   │
│     ./scripts/bot-workflow.sh {BOT} selfcheck                  │
│     ↓                                                          │
│  3. 创建 commit（仅包含本 BOT 的文件）                          │
│     git add {本BOT相关文件}                                      │
│     git commit -m "{PREFIX}: {内容}"                           │
│     ↓                                                          │
│  4. 立即推送到 GitHub                                           │
│     git push origin main                                       │
│     ↓                                                          │
│  5. 创建审计/裁决文档并 commit                                  │
│     git add docs/bots/{BOT}/REPORT.md                          │
│     git commit -m "G: {BOT} - {阶段}报告"                      │
│     git push origin main                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 6.2 裁决前置流程

```
任何审计/裁决必须：
1. 先 commit 到 GitHub
2. 通知用户和 GPT 裁决
3. 等待明确批准
4. 才能执行变更
```

---

## 七、禁止行为

```
❌ 禁止跨 BOT 提交代码变更
❌ 禁止本地 commit 不推送 GitHub
❌ 禁止先执行后裁决（必须先 commit 等待裁决）
❌ 禁止混合提交不同引擎的变更
❌ 禁止在 commit message 中隐瞒其他 BOT 的变更
```

---

## 八、违规处理

| 类型 | 定义 | 处理方式 |
|------|------|----------|
| 混合提交 | 一次 commit 包含多个 BOT 的代码 | 拆分 commit，重新验证 |
| 未同步 | commit 未推送到 GitHub | 立即 push，通知相关方 |
| 先执行后裁决 | 未等待裁决就执行变更 | 回滚变更，重新走裁决流程 |
| 越权提交 | 修改了不属于本 BOT 的文件 | 撤销修改，重新提交 |

**后果**:
- 首次违规: 警告 + 重新培训
- 二次违规: 暂停提交权限 24小时
- 三次违规: 上报裁决者仲裁

---

## 九、提交历史

```
d40e6071 G: Governance - 添加 8 个 BOT 自检脚本
a2925dc4 G: Governance - 添加 BOT 工作流统一入口脚本
1739f65a G: Governance - 建立 BOT 工作流规范: 三条铁律 + 裁决前置流程
2e715d66 G: Governance - 完成引擎独立提交规范建立报告
b0f0d1de G: Governance - 建立引擎独立提交规范 + Pre-commit检查
```

---

## 十、GitHub 验证

```
Remote: https://github.com/ZQMMING/wisdom
Branch: main
Latest: d40e6071
Status: Clean (nothing to commit)
Tests: 35/35 passed
```

---

## 十一、使用示例

### 11.1 BOT-BAZI 提交代码

```bash
# 1. 运行自检
bash scripts/bot-selfcheck/bot-bazi.sh

# 2. 查看待提交文件
git status

# 3. 提交（仅包含 bazi 相关文件）
git add src/tongshu/engines/bazi_engine.py tests/test_bazi*.py
git commit -m "P: BaziEngine - 修复日柱计算边界"

# 4. 推送到 GitHub
git push origin main
```

### 11.2 BOT-ZIPING 创建审计报告

```bash
# 1. 运行自检
bash scripts/bot-selfcheck/bot-ziping.sh

# 2. 创建审计报告
./scripts/bot-workflow.sh BOT-ZIPING audit phase2

# 3. 填写审计内容
# 编辑 docs/bots/BOT-ZIPING/AUDIT_PHASE2_*.md

# 4. Commit 并通知裁决
git add docs/bots/BOT-ZIPING/AUDIT_PHASE2_*.md
git commit -m "ZP: ZiPing - Phase 2 审计报告"
git push origin main

# 5. 通知 GPT 和用户等待裁决
```

### 11.3 BOT-MASTER 申请技术裁决

```bash
# 1. 创建裁决申请
./scripts/bot-workflow.sh BOT-MASTER arbitrate technical

# 2. 填写裁决内容
# 编辑 docs/bots/BOT-MASTER/ARBITRATION_TECHNICAL_*.md

# 3. Commit 并通知裁决
git add docs/bots/BOT-MASTER/ARBITRATION_TECHNICAL_*.md
git commit -m "G: BOT-MASTER - 技术裁决申请"
git push origin main

# 4. 等待 GPT 和用户裁决
# 裁决完成后才能执行
```

---

## 十二、规范检查清单

### 12.1 提交前检查

- [ ] 确认在 main 分支
- [ ] 运行本 BOT 的所有测试
- [ ] 检查是否混合其他 BOT 的文件
- [ ] 确认所有更改已 commit
- [ ] 确认 test/ 目录已更新

### 12.2 提交后检查

- [ ] 确认已 push 到 GitHub
- [ ] 确认 GitHub 上能看到新 commit
- [ ] 如果是审计/裁决文档，已通知 GPT 和用户
- [ ] 确认裁决文档已填写完整

### 12.3 裁决前检查

- [ ] 裁决文档已 commit 到 GitHub
- [ ] 已通知 GPT 进行裁决
- [ ] 已通知用户等待裁决
- [ ] 等待明确批准后再执行

---

## 十三、相关文件

| 文件 | 说明 |
|------|------|
| `docs/ARCHITECTURE/BOT_WORKFLOW_SPEC.md` | BOT 工作流规范（详细版） |
| `docs/ARCHITECTURE/ENGINE_SUBMISSION_SPEC.md` | 引擎独立提交规范 |
| `scripts/bot-workflow.sh` | BOT 工作流统一入口 |
| `scripts/bot-selfcheck/*.sh` | 8 个 BOT 自检脚本 |
| `.git/hooks/pre-commit` | 引擎隔离检查钩子 |
| `.git/hooks/pre-push` | 同步检查钩子 |
| `.git/hooks/post-commit` | 裁决提醒钩子 |

---

## 十四、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-09-01 | 初始版本 |
| v2.0 | 2026-09-06 | 增加三条铁律、Git Hooks、自检脚本、工作流入口 |

---

**本规范经裁决者批准后生效，所有 BOT 必须严格遵守。**
