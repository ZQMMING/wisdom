# BOT 工作流规范建立报告

**完成时间**: 2026-09-06 20:00  
**提交**: `b0f0d1de` → 后续新建

---

## 执行摘要

✅ **三条铁律建立完成**  
✅ **8 个 BOT 自检脚本创建完成**  
✅ **Git Hooks 配置完成**  
✅ **工作流脚本创建完成**

---

## 一、核心规范

### 1.1 三条铁律

```
铁律1: 独立提交 - 每个 BOT 只能提交自己的引擎部分，禁止污染其他引擎
铁律2: 实时同步 - 所有本地 commit 必须立即同步到 GitHub
铁律3: 裁决前置 - 审计和裁决必须 commit 到 GitHub，等待 GPT 和用户裁决后才能执行
```

### 1.2 BOT 职责矩阵

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

## 二、Git Hooks 配置

### 2.1 Pre-commit Hook（引擎隔离检查）

```bash
# .git/hooks/pre-commit
# 自动检查是否混合了多个引擎的文件
```

**拦截示例**：
```
❌ 检测到混合引擎提交！
   请拆分提交，每个引擎独立提交
```

### 2.2 Pre-push Hook（同步检查）

```bash
# .git/hooks/pre-push
# 检查是否有未提交的更改
```

**检查项**：
- 无未提交更改
- 远程连接正常
- 当前分支正确

### 2.3 Post-commit Hook（裁决提醒）

```bash
# .git/hooks/post-commit
# 检测裁决相关提交并提醒
```

**提醒内容**：
- 裁决文档已 commit 到 GitHub
- 请通知 GPT 和用户等待裁决
- 裁决完成前禁止执行

---

## 三、BOT 自检脚本

### 3.1 脚本位置

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

### 3.2 自检内容

每个 BOT 的自检脚本包含：

1. **分支检查** - 确保在 main 分支
2. **测试运行** - 运行本 BOT 的所有测试
3. **文件范围检查** - 检测是否混合其他 BOT 的文件
4. **证据文件检查** - 检查证据文件完整性
5. **违规提醒** - 检测到问题时给出明确提示

### 3.3 使用示例

```bash
# 运行 BOT-BAZI 自检
bash scripts/bot-selfcheck/bot-bazi.sh

# 运行 BOT-HELUO 自检
bash scripts/bot-selfcheck/bot-heluo.sh
```

---

## 四、工作流入口脚本

### 4.1 脚本位置

```
scripts/bot-workflow.sh
```

### 4.2 功能命令

| 命令 | 功能 | 示例 |
|------|------|------|
| selfcheck | 运行自检 | `./bot-workflow.sh BOT-BAZI selfcheck` |
| commit | 提交并同步 | `./bot-workflow.sh BOT-HELUO commit` |
| audit | 创建审计报告 | `./bot-workflow.sh BOT-ZIPING audit phase2` |
| arbitrate | 创建裁决申请 | `./bot-workflow.sh BOT-MASTER arbitrate technical` |
| status | 查看状态 | `./bot-workflow.sh BOT-MASTER status` |

### 4.3 使用示例

```bash
# BOT-BAZI 提交代码
./scripts/bot-workflow.sh BOT-BAZI commit

# BOT-HELUO 创建 Phase 2 审计报告
./scripts/bot-workflow.sh BOT-HELUO audit phase2

# BOT-ZIPING 申请技术裁决
./scripts/bot-workflow.sh BOT-ZIPING arbitrate technical

# BOT-MASTER 查看状态
./scripts/bot-workflow.sh BOT-MASTER status
```

---

## 五、裁决文档模板

### 5.1 审计报告模板

```markdown
# {BOT名称} - {阶段} 审计报告

**生成时间**: {时间}
**BOT**: {名称}
**阶段**: {阶段}
**状态**: ⏳ 等待裁决

---

## 一、审计范围
- 代码路径: [待填写]
- 测试覆盖: [待填写]
- 证据引用: [待填写]

## 二、审计发现
[待填写]

## 三、建议操作
- [ ] 执行变更
- [ ] 拒绝变更
- [ ] 要求修改后重新提交

---

## 裁决区

**GPT 裁决**: 待填写
**用户裁决**: 待填写
**裁决时间**: 待填写
**执行状态**: 待执行
```

### 5.2 裁决申请模板

```markdown
# {BOT名称} - {类型} 裁决申请

**申请人**: {BOT名称}
**时间**: {时间}
**类型**: {type}
**状态**: ⏳ 等待裁决

---

## 一、问题摘要
[待填写问题描述]

## 二、涉及文件
- [待填写]

## 三、可选方案

### 方案 A: [名称]
- 优势: [待填写]
- 劣势: [待填写]
- 推荐指数: ⭐⭐⭐

### 方案 B: [名称]
- 优势: [待填写]
- 劣势: [待填写]
- 推荐指数: ⭐⭐

## 四、建议方案
**推荐**: 方案 A
**理由**: [待填写]

---

## 裁决区

### GPT 裁决
- 选择方案: [待填写]
- 理由: [待填写]
- 裁决时间: [待填写]

### 用户裁决
- 选择方案: [待填写]
- 理由: [待填写]
- 裁决时间: [待填写]

### 执行状态
- [ ] 等待裁决
- [ ] 已批准，待执行
- [ ] 已执行
- [ ] 已拒绝
```

---

## 六、违规处理

### 6.1 违规类型

| 类型 | 定义 | 处理方式 |
|------|------|----------|
| 混合提交 | 一次 commit 包含多个 BOT 的代码 | 拆分 commit，重新验证 |
| 未同步 | commit 未推送到 GitHub | 立即 push，通知相关方 |
| 先执行后裁决 | 未等待裁决就执行变更 | 回滚变更，重新走裁决流程 |
| 越权提交 | 修改了不属于本 BOT 的文件 | 撤销修改，重新提交 |

### 6.2 违规后果

```
首次违规: 警告 + 重新培训
二次违规: 暂停提交权限 24小时
三次违规: 上报裁决者仲裁
```

---

## 七、规范检查清单

### 7.1 提交前检查

- [ ] 确认在 main 分支
- [ ] 运行本 BOT 的所有测试
- [ ] 检查是否混合其他 BOT 的文件
- [ ] 确认所有更改已 commit
- [ ] 确认 test/ 目录已更新

### 7.2 提交后检查

- [ ] 确认已 push 到 GitHub
- [ ] 确认 GitHub 上能看到新 commit
- [ ] 如果是审计/裁决文档，已通知 GPT 和用户
- [ ] 确认裁决文档已填写完整

### 7.3 裁决前检查

- [ ] 裁决文档已 commit 到 GitHub
- [ ] 已通知 GPT 进行裁决
- [ ] 已通知用户等待裁决
- [ ] 等待明确批准后再执行

---

## 八、快速参考

### 8.1 常用命令

```bash
# 查看状态
./scripts/bot-workflow.sh BOT-MASTER status

# 运行自检
./scripts/bot-workflow.sh BOT-BAZI selfcheck

# 提交代码
./scripts/bot-workflow.sh BOT-HELUO commit

# 创建审计报告
./scripts/bot-workflow.sh BOT-ZIPING audit phase2

# 申请裁决
./scripts/bot-workflow.sh BOT-MASTER arbitrate technical
```

### 8.2 提交前缀对照表

| BOT | 前缀 | 示例 |
|-----|------|------|
| BOT-MASTER | G: | `G: 新增裁决机制` |
| BOT-BAZI | P: | `P: 修复日柱计算边界` |
| BOT-ZIPING | ZP: | `ZP: 修复十神映射` |
| BOT-BLIND | BL: | `BL: 新增做功链解析` |
| BOT-HELUO | H: | `H: 修复节候卦计算` |
| BOT-YI | Y: | `Y: 新增梅花易数起卦` |
| BOT-TIME | T: | `T: 修复真太阳时计算` |
| BOT-CORPUS | C: | `C: 新增滴天髓原文` |

---

## 九、版本历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-09-01 | 初始版本 |
| v2.0 | 2026-09-06 | 增加三条铁律、Git Hooks、自检脚本、工作流入口 |

---

**本规范经裁决者批准后生效，所有 BOT 必须严格遵守。**
