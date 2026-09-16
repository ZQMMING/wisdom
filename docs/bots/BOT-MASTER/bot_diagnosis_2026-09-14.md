# BOT配置问题诊断报告

**诊断时间**: 2026-09-14 18:30  
**诊断人**: BOT-MASTER  
**问题严重性**: P0 - 核心功能缺失

---

## 一、问题总览

### 1.1 当前状态

| 项目 | 状态 | 说明 |
|------|------|------|
| Hermes版本 | v0.21.3 | 最新 |
| bot-master gateway | ✅ running | PID 19828 |
| default gateway | ✅ running | PID 7696 |
| Profile数量 | 3个 | bot-master, bot-bazi, bot-ziwei |
| 缺失SOUL.md | 2个 | bot-bazi, bot-ziwei |
| 缺失config.yaml | 2个 | bot-bazi, bot-ziwei |

### 1.2 核心问题

**我们创建了多个BOT Profile目录，但只配置了一个（bot-master）**。

---

## 二、详细诊断

### 2.1 Profile目录结构

```
~/.hermes/profiles/
├── bot-master/    ✅ 完整配置（SOUL + AGENTS + config）
├── bot-bazi/      ❌ 仅调试脚本，无BOT配置
└── bot-ziwei/     ❌ 仅计算脚本，无BOT配置
```

### 2.2 bot-master 配置检查

| 文件 | 状态 | 大小 |
|------|------|------|
| SOUL.md | ✅ 存在 | 8,115 bytes |
| AGENTS.md | ✅ 存在 | 6,984 bytes |
| config.yaml | ✅ 存在 | 539 bytes |
| personality.md | ⚠️ 缺失 | - |

**配置内容正确**：
```yaml
agent:
  load_soul_identity: true
  skip_context_files: false
workspace:
  primary: "D:/shuntian/"
  enforce_path_check: true
enforcement:
  on_violation: "stop_and_report"
```

### 2.3 bot-bazi 问题

**目录内容**：
- 537个文件（大量调试脚本）
- 无任何BOT配置文件
- 无SOUL.md
- 无AGENTS.md
- 无config.yaml

**问题**：这是"开发工作区"而非"BOT Profile"。

### 2.4 bot-ziwei 问题

**目录内容**：
- 仅3个计算脚本
- 无任何BOT配置文件

**问题**：未完成配置。

---

## 三、根因分析

### 3.1 历史问题

```
2026-09-05 ~ 2026-09-07: BOT批量创建期
├─ 创建了16个profile目录（bot-master/bot-corpus/bot-knowledge/...）
├─ 仅完成bot-master的配置
├─ 其他profile只有空目录或临时脚本
└─ 从未正式初始化这些BOT
```

### 3.2 配置遗漏

根据V2架构设计，应为每个引擎创建：
1. `SOUL.md` - 身份定义
2. `AGENTS.md` - 职责边界
3. `config.yaml` - 运行时配置

**实际完成情况**：
| BOT | SOUL.md | AGENTS.md | config.yaml | Gateway |
|-----|---------|-----------|-------------|---------|
| bot-master | ✅ | ✅ | ✅ | ✅ |
| bot-bazi | ❌ | ❌ | ❌ | ❌ |
| bot-ziwei | ❌ | ❌ | ❌ | ❌ |
| 其他13个 | ❌ | ❌ | ❌ | ❌ |

---

## 四、影响评估

### 4.1 当前影响

- ✅ bot-master gateway正常运行（调度核心）
- ❌ 无法通过Hermes启动其他BOT
- ❌ message_agent工具调用其他BOT会失败
- ⚠️ 所有BOT间协调依赖人工中转

### 4.2 工作流影响

```
正常流程（应有）:
User → BOT-MASTER → message_agent → 各引擎BOT → 回报 → BOT-MASTER

当前流程（实际）:
User → BOT-MASTER（直接执行）或 人工切换profile
```

---

## 五、解决方案

### 方案A：最小化恢复（推荐）

仅配置核心BOT：
1. **bot-master** - 已完整 ✅
2. **bot-bazi** - 基础配置（L0事实层）
3. **bot-ziping** - 子平辨层（当前进行中）

### 方案B：完整恢复

配置全部9个BOT：
- bot-bazi（八字排盘）
- bot-ziping（子平辨层）
- bot-blind（盲派）
- bot-ziwei（紫微）
- bot-heluo（河洛）
- bot-meihua（梅花）
- bot-yi（易经）
- bot-huangli（黄历）
- bot-corpus（五经）

### 方案C：清理废弃目录

删除空profile目录，统一使用单一profile + 多会话模式。

---

## 六、立即行动项

### P0（今天）

1. **确认方案**：选择A/B/C
2. **创建缺失配置**：
   - `profiles/bot-bazi/SOUL.md`
   - `profiles/bot-bazi/config.yaml`
   - `profiles/bot-ziwei/SOUL.md`（如需要）
3. **测试Gateway启动**

### P1（本周）

4. **配置剩余核心BOT**
5. **验证message_agent通信**
6. **更新AGENTS.md治理规则**

---

## 七、附录

### 7.1 相关文件位置

```
~/.hermes/profiles/
├── bot-master/           # ✅ 完整
│   ├── SOUL.md
│   ├── AGENTS.md
│   └── config.yaml
├── bot-bazi/             # ❌ 空目录
└── bot-ziwei/            # ❌ 空目录

~/.hermes/
├── config.yaml           # 主配置（feishu已配置）
├── logs/
│   └── gateway.log       # 无日志（可能未启用）
└── bots.yaml             # 不存在
```

### 7.2 正确配置模板

```yaml
# config.yaml示例
agent:
  load_soul_identity: true
  skip_context_files: false

workspace:
  primary: "D:/shuntian/"
  enforce_path_check: true

enforcement:
  on_violation: "stop_and_report"
```

---

**诊断结论**：BOT配置不完整是导致"一直出问题"的根本原因。建议立即选择方案A进行最小化恢复。

**下一步**：等待用户确认方案，然后执行配置。
