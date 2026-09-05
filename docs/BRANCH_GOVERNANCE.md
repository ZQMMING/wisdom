# 顺天项目分支治理协议

> 最后更新: 2026-09-05  
> 协议版本: v1.0

---

## 核心原则

**独立引擎、独立分支、独立审计、独立提交**

```
算 → 辨 → 解
│     │     │
引擎  规则  断言
隔离  隔离  隔离
```

---

## 分支架构

### 主分支 (受保护)

| 分支 | 用途 | 保护级别 |
|------|------|----------|
| `master` | 稳定集成基线 | 🔒 仅接受 merge |
| `main` | GitHub 默认同步 | 🔒 仅接受 merge |

### 引擎特性分支

| 分支 | 引擎 | 负责人 | 用途 |
|------|------|--------|------|
| `feature/ziwei` | 紫微斗数 | Claude | 紫微引擎开发 |
| `feature/ziping` | 子平八字 | OpenCode | 子平引擎开发 |
| `feature/heluo` | 河洛理数 | TBD | 河洛引擎开发 |
| `feature/yi` | 易经 | TBD | 易经引擎开发 |
| `feature/blind` | 盲派 | TBD | 盲派引擎开发 |

### 治理分支

| 分支 | 用途 | 状态 |
|------|------|------|
| `admission-governance-v2` | P2.1 断言准入治理 | 已合并 |
| `audit-e001-phase6` | Phase 6 审计日志 | 已合并 |

---

## 提交规范

### 前缀标识

| 引擎 | 前缀 | 格式 | 示例 |
|------|------|------|------|
| 紫微 | `Z` | `Z{序号}: 描述` | `Z15: 飞星rule匹配实现` |
| 子平 | `P` | `P{序号}{子序号}: 描述` | `P0-14: 立春边界修复` |
| 河洛 | `H` | `H{序号}.{子序号}: 描述` | `H16.1: 独立验证审计` |
| 易经 | `Y` | `Y{序号}: 描述` | `Y1: 卦象解析模块` |
| 盲派 | `BL` | `BL{序号}: 描述` | `BL1: 主客格局引擎` |
| 治理 | `P2.x` | `P2.x-Y: 描述` | `P2.1-F: 外部信任根` |
| 数据 | `D` | `D{序号}: 描述` | `D1: 规则索引更新` |

### 禁止行为

❌ **禁止跨引擎污染**
- 不在 `feature/ziwei` 分支修改 `src/tongshu/engines/bazi/`
- 不在 PR 中混合多个引擎的变更
- 不对应引擎的测试不得混入非本引擎代码

❌ **禁止绕过分支**
- 所有开发必须基于 `feature/*` 分支
- 禁止直接在 `master` 上 commit
- 禁止在 master 上创建临时分支工作

❌ **禁止跳过审计**
- 引擎分支合入 master 必须通过独立审计
- 审计通过后才能触发 merge
- 审计失败必须退回修正

---

## 开发流程

### 单引擎开发

```bash
# 1. 从 master 创建/更新引擎分支
git checkout master && git pull origin master
git checkout feature/ziwei && git rebase master

# 2. 开发引擎功能
git add src/tongshu/engines/ziwei/
git add tests/test_ziwei_*.py
git commit -m "Z15: 飞星rule匹配实现"

# 3. 推送到远程
git push origin feature/ziwei

# 4. 创建 PR (需通过独立审计)
gh pr create --title "Z15: 飞星rule匹配" --body "..."
```

### 引擎分支合入 master

```
前提条件:
✅ 引擎独立测试通过
✅ 无跨引擎污染 (git diff --stat 检查)
✅ 独立审计通过
✅ 无 API 破坏性变更 (或已版本升级)

步骤:
1. 创建 merge commit
   git checkout master
   git merge --no-ff feature/ziwei -m "Z15: 飞星rule匹配 (engine isolation)"

2. 删除已合入的特性分支 (可选)
   git push origin --delete feature/ziwei
```

---

## 引擎目录隔离

```
src/tongshu/engines/
├── ziwei/           # 紫微引擎专属目录
│   ├── evidence_producer.py
│   ├── rules/       # RuleGraph 实现
│   └── z14/         # Z14 同盘异法
├── bazi/            # 子平引擎专属目录
│   └── evidence_producer.py
├── heluo/           # 河洛引擎专属目录
│   ├── hexagram.py
│   └── yi_interpreter.py
├── yi/              # 易经引擎专属目录
│   ├── classical_text.py
│   └── gua_four_dim_loader.py
├── blind/           # 盲派引擎专属目录
│   └── evidence_producer.py
├── time/            # 时间计算共享
│   ├── resolver.py
│   └── solar_time.py
└── canonical/       # 规范状态共享
    └── ...
```

---

## 测试隔离

```
tests/
├── ziwei/           # 紫微测试
│   ├── test_ziwei_engine.py
│   ├── test_ziwei_feixing_*.py
│   └── test_ziwei_z14_*.py
├── bazi/            # 子平测试
│   ├── test_bazi_engine.py
│   └── test_*.py
├── heluo/           # 河洛测试
│   ├── test_heluo_canonical.py
│   └── test_heluo_*.py
├── yi/              # 易经测试
│   └── test_yi_*.py
└── blind/           # 盲派测试
    └── test_blind_*.py
```

---

## 审计协议

### 引擎审计清单

每个引擎分支合入 master 前必须通过:

1. **计算正确性验证**
   - Golden Dataset 比对
   - 边界案例覆盖
   - 历法事实验证

2. **跨引擎污染检查**
   - `git diff --stat master...feature/*` 检查修改范围
   - 确认只修改本引擎相关文件

3. **接口稳定性验证**
   - BaziChart / FrozenZiweiChart 等契约不变
   - 无破坏性 API 变更

4. **证据链完整性**
   - source_rule_ref 正确指向规则文件
   - 原典授权链完整

---

## 决策记录

### D001: 引擎分支隔离 (2026-09-05)
- **问题**: master 混合多个引擎代码，无法独立追踪
- **方案**: 创建 feature/* 分支隔离各引擎开发
- **裁决**: 紫微→feature/ziwei, 子平→feature/ziping, 河洛→feature/heluo, 易经→feature/yi, 盲派→feature/blind
- **状态**: 已执行

### D002: 提交前缀规范 (2026-09-05)
- **问题**: commit 消息无引擎标识，难以追溯
- **方案**: 采用 `Z/P/H/Y/BL/P2.x/D` 前缀体系
- **裁决**: 所有新 commit 必须使用引擎前缀
- **状态**: 生效

---

## 快速参考

```bash
# 查看所有引擎分支状态
git branch -a | grep -E "feature|ziwei|ziping|heluo|yi|blind"

# 查看某个引擎的独有 commits
git log --oneline feature/ziwei --not master

# 检查跨引擎污染
git diff --name-only master...feature/ziwei | grep -v "ziwei"

# 创建新引擎开发分支
git checkout -b feature/<engine> master
```
