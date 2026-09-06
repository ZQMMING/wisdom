# 顺天项目 Git / Agent 治理规则 v1.0

**生效时间**: 2026-09-06  
**适用范围**: 所有Agent、所有引擎、所有审计和裁决活动

---

## 一、核心原则（铁律）

### 1.1 三隔离原则

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

### 1.2 问题链与根因

**历史问题链**:
```
审计 → 发现问题 → 裁决 → Agent顺手修改代码 → git add . 
→ commit（混入其他引擎/参考资料）→ 后续Agent以污染commit为基线 
→ 污染被继承 → 代码/审计/裁决之间断层
```

**根因**: 审计裁决与工程实施没有隔离

---

## 二、角色与职责

### 2.1 角色定义

| 角色 | 职责 | 产出 | 权限 |
|------|------|------|------|
| **审计Agent** | 发现事实、验证契约、评估风险 | 审计报告、证据链 | 只读，禁止修改代码 |
| **裁决Agent** | 评估严重程度、决定修复优先级 | 裁决文档、修复要求 | 只读，禁止修改代码 |
| **工程Agent** | 根据裁决实施修复 | 代码、测试、commit | 只能修改本引擎文件 |
| **治理Agent** | 检查commit边界、拦截违规提交 | 检查报告、拦截记录 | 强制执行边界检查 |

### 2.2 Agent职责矩阵

```
┌─────────────────────────────────────────────────────────────────┐
│                        顺天治理架构                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    │
│   │  审计Agent   │    │  裁决Agent   │    │  治理Agent   │    │
│   │  (只读)      │───▶│  (只读)      │    │  (检查)      │    │
│   └──────────────┘    └──────────────┘    └──────┬───────┘    │
│                                                  │             │
│                                          ┌───────▼───────┐    │
│                                          │  工程Agent    │    │
│                                          │  (实施)       │    │
│                                          └───────┬───────┘    │
│                                                  │             │
│                                    ┌─────────────┼─────────┐  │
│                                    ↓             ↓         ↓  │
│                              ┌─────────┐  ┌─────────┐ ┌────────┐│
│                              │ BAZI    │  │ ZIPING  │ │ ZIWEI  ││
│                              │ (冻结)  │  │ 引擎    │ │ 引擎   ││
│                              └─────────┘  └─────────┘ └────────┘│
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 三、工作流规范

### 3.1 标准工作流程

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
  ├─ Agent开工前报告（见3.2节）
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

### 3.2 Agent开工报告模板

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

---

## 执行计划

1. {步骤1}
2. {步骤2}
3. {步骤3}

---

**报告人**: {Agent名称}  
**状态**: ⏳ 等待执行
```

### 3.3 Agent完工报告模板

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

### 删除文件
```
{文件路径} - {删除原因}
```

---

## 边界检查

- [ ] 仅修改ALLOWED路径下的文件
- [ ] 未触碰FORBIDDEN路径
- [ ] 测试全部通过
- [ ] 无意外文件进入commit

---

**报告人**: {Agent名称}  
**状态**: ✅ 完成，等待验收
```

---

## 四、Commit规范

### 4.1 Commit格式

```
{PREFIX}: {Engine} - {任务类型} - {变更摘要}

PREFIX对照表:
G:  - Governance（治理、规范、工具）
P:  - BAZI引擎
ZP: - ZIPING引擎  
BL:  - BLIND引擎
H:  - HELUO引擎
Y:  - YI引擎
T:  - TIME引擎
C:  - CORPUS语料库
E:  - Evidence证据文件
A:  - Audit审计报告（只读）
D:  - Decision裁决文档（只读）
```

### 4.2 Commit内容规范

**正确示例**:
```
ZP: ZIPING - P0-1修复 - ContextAssembler不再重新调用BAZI
```
内容:
- `src/tongshu/reasoning/zi_ping_context_assembler.py`
- `tests/test_ziping_context.py`
- `docs/audit/ziping/AUDIT-P0-1.md`

**错误示例**（混合提交）:
```
fix: 修复ZIPING并顺手更新其他引擎
```
内容:
- `src/tongshu/reasoning/zi_ping_context_assembler.py` ✅
- `src/tongshu/engines/bazi_engine.py` ❌（BAZI已冻结）
- `src/tongshu/engines/ziwei_engine.py` ❌（不是本引擎）
- `docs/audit/ziwei/紫微案例.bsp` ❌（参考资料不应进入commit）

### 4.3 Commit边界检查

每次commit必须通过以下检查：

```bash
# 1. 检查是否混合引擎文件
git diff --cached --name-only | grep -E "^(src/tongshu/engines/(bazi|ziwei|heluo|blind|yi|time)/)" 

# 2. 检查是否包含非引擎代码（除了本引擎）
git diff --cached --name-only | grep -v -E "^((src/tongshu/(engines|reasoning)/{engine}|tests/test_{engine}|docs/(audit|decision)/{engine}))"

# 3. 检查是否包含冻结引擎（BAZI）
git diff --cached --name-only | grep "bazi_engine.py" && echo "❌ 禁止修改冻结引擎"
```

---

## 五、Git Hooks增强

### 5.1 Pre-commit Hook（边界检查）

```bash
#!/bin/bash
# 顺天Git治理 - 引擎边界检查

echo "=== 顺天Git治理检查 ==="
echo ""

# 获取当前commit message
MSG=$(git log -1 --pretty=%s 2>/dev/null || echo "")

# 解析引擎前缀
ENGINE=""
case "$MSG" in
    G:*) ENGINE="governance" ;;
    P:*) ENGINE="bazi" ;;
    ZP:*) ENGINE="ziping" ;;
    BL:*) ENGINE="blind" ;;
    H:*) ENGINE="heluo" ;;
    Y:*) ENGINE="yi" ;;
    T:*) ENGINE="time" ;;
    C:*) ENGINE="corpus" ;;
    E:*) ENGINE="evidence" ;;
    A:*) ENGINE="audit" ;;
    D:*) ENGINE="decision" ;;
esac

# 获取暂存文件
FILES=$(git diff --cached --name-only 2>/dev/null)

if [ -z "$FILES" ]; then
    echo "✅ 无暂存文件"
    exit 0
fi

# 排除文档/脚本/tests目录
FILTERED=$(echo "$FILES" | grep -v -E "^(scripts/|docs/|tests/|\.git/|node_modules/)" || true)

if [ -z "$FILTERED" ]; then
    echo "✅ 非引擎代码提交，跳过边界检查"
    exit 0
fi

# 检查BAZI冻结
if echo "$FILTERED" | grep -q "bazi_engine.py"; then
    echo "❌ 严重违规: BAZI引擎已冻结，禁止修改！"
    echo "   发现文件: $(echo "$FILES" | grep 'bazi_engine.py')"
    exit 1
fi

# 统计各引擎文件
declare -A ENGINE_COUNT
ENGINE_PATHS=(
    "ziwei_engine.py:ziwei"
    "heluo/:heluo"
    "blind/:blind"
    "meihua.py:yi"
    "yi/:yi"
    "time/:time"
    "reasoning/zi_ping:ziping"
)

for entry in "${ENGINE_PATHS[@]}"; do
    IFS=':' read -r path name <<< "$entry"
    count=$(echo "$FILTERED" | grep -c "$path" || true)
    if [ "$count" -gt 0 ]; then
        ENGINE_COUNT[$name]=$count
    fi
done

# 输出统计
echo "文件分布:"
for engine in "${!ENGINE_COUNT[@]}"; do
    echo "  ✓ $engine: ${ENGINE_COUNT[$engine]} files"
done

# 检查是否混合
ENGAGE_COUNT=${#ENGINE_COUNT[@]}
if [ $ENGAGE_COUNT -eq 0 ]; then
    echo "✅ 非引擎代码提交，跳过边界检查"
    exit 0
fi

if [ $ENGAGE_COUNT -gt 1 ]; then
    echo ""
    echo "❌ 严重违规: 检测到混合引擎提交！"
    echo "   请拆分提交，每个引擎独立提交"
    echo ""
    echo "涉及引擎:"
    for engine in "${!ENGINE_COUNT[@]}"; do
        echo "   - $engine: ${ENGINE_COUNT[$engine]} files"
    done
    echo ""
    echo "正确做法:"
    echo "  1. git reset HEAD"
    echo "  2. git add {单个引擎相关文件}"
    echo "  3. git commit -m \"{PREFIX}: {Engine} - {任务}\""
    echo "  4. git push origin main"
    exit 1
fi

echo ""
echo "✅ 引擎边界检查通过"
exit 0
```

### 5.2 Post-commit Hook（验收提醒）

```bash
#!/bin/bash
# 顺天Git治理 - 完工验收提醒

echo "=== 顺天Git治理 - 完工验收 ==="
echo ""

# 获取最新commit信息
COMMIT=$(git log -1 --pretty=format:"%h" 2>/dev/null)
MSG=$(git log -1 --pretty=format:"%s" 2>/dev/null)
TIME=$(git log -1 --pretty=format:"%ci" 2>/dev/null)

echo "Commit: $COMMIT"
echo "Message: $MSG"
echo "Time: $TIME"
echo ""

# 解析引擎前缀
ENGINE=""
case "$MSG" in
    G:*) ENGINE="governance" ;;
    P:*) ENGINE="bazi" ;;
    ZP:*) ENGINE="ziping" ;;
    BL:*) ENGINE="blind" ;;
    H:*) ENGINE="heluo" ;;
    Y:*) ENGINE="yi" ;;
    T:*) ENGINE="time" ;;
    C:*) ENGINE="corpus" ;;
    E:*) ENGINE="evidence" ;;
    A:*) ENGINE="audit" ;;
    D:*) ENGINE="decision" ;;
esac

echo "识别引擎: $ENGINE"
echo ""

# 如果是工程提交，提醒验收
if [[ "$MSG" =~ ^(P:|ZP:|BL:|H:|Y:|T:|C:) ]]; then
    echo "⚠️  工程提交 detected，需要验收："
    echo ""
    echo "1. 检查commit内容："
    echo "   git show --stat $COMMIT"
    echo "   git diff $(git rev-parse HEAD~1)..$COMMIT --name-only"
    echo ""
    echo "2. 确认无越界文件"
    echo "3. 确认测试通过"
    echo "4. 确认可以合并到main"
    echo ""
fi

echo "✅ Commit完成"
```

---

## 六、验收标准

### 6.1 Commit验收检查清单

```bash
# 验收命令
git show --stat <commit>
git diff <base>..<commit> --name-only

# 检查项
- [ ] 仅包含本引擎相关路径
- [ ] 未触碰BAZI（冻结引擎）
- [ ] 未触碰其他引擎代码
- [ ] 未混入参考资料/案例文件
- [ ] 测试全部通过
- [ ] 无意外文件进入commit
```

### 6.2 验收不通过的处理

```
如果发现违规commit：

1. 立即block merge
2. 通知相关Agent重新提交
3. 记录违规事件到audit_log
4. 分析根因，完善检查规则
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

### 7.2 违规记录

所有违规事件必须记录到：
```
docs/audit/governance/ViolationLog.md
```

---

## 八、快速参考

### 8.1 各引擎ALLOWED PATHS

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

### 8.2 提交前自检命令

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

---

## 九、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v0.1 | 2026-09-06 | 初始版本，建立三隔离原则 |
| v1.0 | 2026-09-06 | 正式定稿，增加Agent开工/完工报告模板 |

---

**本规则经裁决者批准后生效，所有Agent必须严格遵守。**
