# 顺天项目 BOTS 工作流规范 v2.0

**生效时间**: 2026-09-06  
**适用范围**: 所有 BOT（BOT-MASTER, BOT-BAZI, BOT-ZIPING, BOT-BLIND, BOT-HELUO, BOT-YI, BOT-CORPUS, BOT-TIME）

---

## 一、核心原则

### 1.1 三条铁律

```
铁律1: 独立提交 - 每个 BOT 只能提交自己的引擎部分，禁止污染其他引擎
铁律2: 实时同步 - 所有本地 commit 必须立即同步到 GitHub
铁律3: 裁决前置 - 审计和裁决必须 commit 到 GitHub，等待 GPT 和用户裁决后才能执行
```

### 1.2 BOT 职责矩阵

| BOT | 职责范围 | 代码路径 | 测试路径 | 提交前缀 |
|-----|----------|----------|----------|----------|
| BOT-MASTER | 总调度、治理、证据系统 | `src/tongshu/governance/`, `src/tongshu/assertion/`, `backend/data/evidence/` | `tests/test_*_governance*.py`, `tests/test_*_evidence*.py` | `G:` |
| BOT-BAZI | 八字排盘引擎 | `src/tongshu/engines/bazi_engine.py` | `tests/test_bazi*.py` | `P:` |
| BOT-ZIPING | 子平引擎 | `src/tongshu/reasoning/zi_ping_*.py` | `tests/test_ziping*.py` | `ZP:` |
| BOT-BLIND | 盲派引擎 | `src/tongshu/engines/blind/` | `tests/test_blind*.py` | `BL:` |
| BOT-HELUO | 河洛引擎 | `src/tongshu/engines/heluo/` | `tests/test_heluo*.py` | `H:` |
| BOT-YI | 易经引擎 | `src/tongshu/engines/meihua.py`, `src/tongshu/engines/yi/` | `tests/test_yi*.py`, `tests/test_meihua*.py` | `Y:` |
| BOT-CORPUS | 语料库管理 | `data/classics/`, `docs/bots/*/` | - | `C:` |
| BOT-TIME | 时间计算引擎 | `src/tongshu/engines/time/` | `tests/test_time*.py` | `T:` |

---

## 二、提交工作流

### 2.1 标准提交流程

```
┌─────────────────────────────────────────────────────────────────┐
│  1. 开发/修复代码                                               │
│     ↓                                                          │
│  2. 运行本 BOT 的测试                                           │
│     pytest tests/test_{BOT}*.py -v                            │
│     ↓                                                          │
│  3. 检查是否混合其他引擎文件                                     │
│     git diff --cached --name-only | grep -E "其他引擎路径"     │
│     ↓                                                          │
│  4. 创建 commit（仅包含本 BOT 的文件）                          │
│     git add {本BOT相关文件}                                     │
│     git commit -m "{PREFIX}: {内容}"                          │
│     ↓                                                          │
│  5. 立即推送到 GitHub                                           │
│     git push origin main                                       │
│     ↓                                                          │
│  6. 创建审计/裁决文档并 commit                                  │
│     git add docs/bots/{BOT}/REPORT.md                         │
│     git commit -m "G: {BOT} - {阶段}报告"                     │
│     git push origin main                                       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 禁止行为

```
❌ 禁止跨 BOT 提交代码变更
❌ 禁止本地 commit 不推送 GitHub
❌ 禁止先执行后裁决（必须先 commit 等待裁决）
❌ 禁止混合提交不同引擎的变更
❌ 禁止在 commit message 中隐瞒其他 BOT 的变更
```

---

## 三、GitHub 同步规范

### 3.1 同步要求

| 操作 | 要求 | 执行时机 |
|------|------|----------|
| 代码提交 | 必须同步 | commit 后立即 push |
| 测试更新 | 必须同步 | commit 后立即 push |
| 审计文档 | 必须同步 | commit 后立即 push |
| 裁决报告 | 必须同步 | commit 后立即 push |
| 证据文件 | 必须同步 | 创建/更新后立即 push |

### 3.2 同步检查清单

```bash
# 每次 commit 后执行
git status && echo "---" && git log --oneline -1 && echo "---" && git push origin main
```

### 3.3 失败处理

```bash
# 如果 push 失败，禁止继续开发
if ! git push origin main; then
    echo "❌ 同步失败，停止后续操作"
    echo "请检查网络连接和权限后重试"
    exit 1
fi
```

---

## 四、审计与裁决流程

### 4.1 裁决前置原则

```
任何审计、裁决、治理决策必须：
1. 先 commit 到 GitHub
2. 通知用户和 GPT 裁决
3. 等待明确批准
4. 才能执行变更
```

### 4.2 裁决文档模板

```markdown
# {BOT名称} - {阶段} - 裁决申请

**申请人**: {BOT名称}  
**时间**: {ISO时间}  
**状态**: ⏳ 等待裁决

---

## 变更摘要
- 涉及文件: {文件列表}
- 变更类型: {新增/修改/删除}
- 影响范围: {仅本BOT / 跨BOT影响}

## 审计结果
- 测试覆盖: {X/Y PASS}
- 证据验证: {evidence_id} VERIFIED
- 架构合规: {符合/违规}

## 建议操作
- 操作类型: {执行/拒绝/修改}
- 理由: {详细说明}

---

## 裁决区

**GPT裁决**: {待填写}  
**用户裁决**: {待填写}  
**裁决时间**: {待填写}  
**执行状态**: {待执行/已执行/已拒绝}
```

### 4.3 执行门槛

```
✅ 允许执行的条件：
1. 裁决文档已 commit 到 GitHub
2. GPT 裁决为 APPROVE
3. 用户裁决为 APPROVE
4. 无未解决的 P0 问题

❌ 禁止执行的情况：
1. 裁决文档未 commit
2. 裁决状态为 PENDING/REJECTED
3. 存在未解决的 P0 问题
4. 跨 BOT 变更未经联合裁决
```

---

## 五、Git 钩子配置

### 5.1 Pre-commit 检查（已安装）

```bash
# .git/hooks/pre-commit
# 检查引擎隔离
```

### 5.2 Pre-push 检查

```bash
#!/bin/bash
# .git/hooks/pre-push

echo "=== Pre-push 检查 ==="

# 1. 检查是否有未提交的更改
if [ -n "$(git diff --name-only)" ]; then
    echo "❌ 有未提交的更改，请先 commit"
    exit 1
fi

# 2. 检查当前分支
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    echo "⚠️  警告: 当前不在 main 分支"
fi

# 3. 检查远程连接
if ! git ls-remote origin HEAD > /dev/null 2>&1; then
    echo "❌ 无法连接到 GitHub，请检查网络"
    exit 1
fi

echo "✅ Pre-push 检查通过"
exit 0
```

### 5.3 Post-commit 通知

```bash
#!/bin/bash
# .git/hooks/post-commit

echo "=== Post-commit 通知 ==="
echo "Commit: $(git rev-parse --short HEAD)"
echo "Message: $(git log -1 --pretty=%s)"
echo ""
echo "⚠️  请立即执行 git push origin main 同步到 GitHub"
echo "⚠️  如果是审计/裁决文档，请通知 GPT 和用户等待裁决"
```

---

## 六、BOT 自检清单

### 6.1 提交前自检

```bash
#!/bin/bash
# bot-self-check.sh

BOT_NAME=$1
BOT_PATH=$2

echo "=== ${BOT_NAME} 提交前自检 ==="

# 1. 检查是否有未提交的更改
if [ -n "$(git diff --name-only ${BOT_PATH})" ]; then
    echo "⚠️  检测到未提交的更改:"
    git diff --name-only ${BOT_PATH}
    echo "请先完成所有更改"
    exit 1
fi

# 2. 检查测试
echo "运行 ${BOT_NAME} 测试..."
pytest tests/test_${BOT_NAME}*.py -v --tb=short
TEST_RESULT=$?

if [ $TEST_RESULT -ne 0 ]; then
    echo "❌ 测试失败，禁止提交"
    exit 1
fi

echo "✅ 测试通过"

# 3. 检查引擎隔离
echo "检查引擎隔离..."
STAGED_FILES=$(git diff --cached --name-only)
OTHER_ENGINE=$(echo "$STAGED_FILES" | grep -E "^(?!.*${BOT_NAME}).*(ziwei|heluo|blind|bazi|yi|meihua)")

if [ -n "$OTHER_ENGINE" ]; then
    echo "❌ 检测到混合引擎提交:"
    echo "$OTHER_ENGINE"
    exit 1
fi

echo "✅ 引擎隔离检查通过"

# 4. 检查裁决文档
if [[ "$*" == *"audit"* || "$*" == *"裁决"* ]]; then
    echo "⚠️  检测到裁决相关提交"
    echo "请确保已创建裁决文档并 commit"
    echo "请通知 GPT 和用户等待裁决"
fi

echo "=== 自检完成 ==="
```

---

## 七、违规处理

### 7.1 违规类型

| 类型 | 定义 | 处理方式 |
|------|------|----------|
| 混合提交 | 一次 commit 包含多个 BOT 的代码 | 拆分 commit，重新验证 |
| 未同步 | commit 未推送到 GitHub | 立即 push，通知相关方 |
| 先执行后裁决 | 未等待裁决就执行变更 | 回滚变更，重新走裁决流程 |
| 越权提交 | 修改了不属于本 BOT 的文件 | 撤销修改，重新提交 |

### 7.2 违规后果

```
首次违规: 警告 + 重新培训
二次违规: 暂停提交权限 24小时
三次违规: 上报裁决者仲裁
```

---

## 八、快速参考

### 8.1 常用命令

```bash
# BOT-MASTER: 总调度
git add src/tongshu/governance/ backend/data/evidence/
git commit -m "G: 治理模块 - 新增裁决机制"
git push origin main

# BOT-BAZI: 八字排盘
git add src/tongshu/engines/bazi_engine.py tests/test_bazi*.py
git commit -m "P: BaziEngine - 修复日柱计算边界"
git push origin main

# BOT-ZIPING: 子平
git add src/tongshu/reasoning/zi_ping*.py tests/test_ziping*.py
git commit -m "ZP: ZiPing - 修复十神映射"
git push origin main

# BOT-BLIND: 盲派
git add src/tongshu/engines/blind/ tests/test_blind*.py
git commit -m "BL: BlindEngine - 新增做功链解析"
git push origin main

# BOT-HELUO: 河洛
git add src/tongshu/engines/heluo/ tests/test_heluo*.py
git commit -m "H: HeluoEngine - 修复节候卦计算"
git push origin main

# BOT-YI: 易经
git add src/tongshu/engines/meihua.py src/tongshu/engines/yi/ tests/test_yi*.py tests/test_meihua*.py
git commit -m "Y: YiEngine - 新增梅花易数起卦"
git push origin main

# BOT-CORPUS: 语料库
git add data/classics/ docs/bots/*/
git commit -m "C: Corpus - 新增滴天髓原文"
git push origin main

# BOT-TIME: 时间计算
git add src/tongshu/engines/time/ tests/test_time*.py
git commit -m "T: TimeEngine - 修复真太阳时计算"
git push origin main
```

### 8.2 状态查询

```bash
# 查看所有 BOT 的最新提交
git log --oneline --all --grep="^G:\|^P:\|^ZP:\|^BL:\|^H:\|^Y:\|^C:\|^T:" -20

# 检查各 BOT 的测试状态
pytest tests/test_bazi*.py tests/test_blind*.py tests/test_heluo*.py tests/test_ziwei*.py tests/test_yi*.py -v --tb=no

# 检查 GitHub 同步状态
git status && git log --oneline origin/main..HEAD
```

---

## 九、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-09-01 | 初始版本 |
| v2.0 | 2026-09-06 | 增加三条铁律、GitHub同步规范、裁决前置流程 |

---

**本规范经裁决者批准后生效，所有 BOT 必须严格遵守。**
