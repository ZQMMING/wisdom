# 引擎隔离整理方案

## 现状分析

### 分支状态
```
origin/master (781 commits) - 当前主分支
├── origin/ziwei (74 commits beyond master) - 紫微引擎 + 文档审计
├── origin/ziping (74 commits beyond master) - 子平引擎 + 文档审计
├── origin/heluo (相同 HEAD) - 河洛引擎
└── origin/yi (相同 HEAD) - 易经引擎
```

### 问题
1. **master 混合了所有引擎代码** - 无法独立追踪单个引擎变更
2. **ziwei/ziping 分支有额外 74 commits** - 主要是 docs/audit 内容
3. **历史 commit 交叉污染** - 无法清晰区分哪个 commit 属于哪个引擎

---

## 整理方案

### 方案 A: 保持 monorepo，按引擎记录 commit 范围
```
优点: 代码集中，便于跨引擎集成测试
缺点: 无法独立推送到引擎专属分支
```

### 方案 B: 创建引擎特性分支 (推荐)
```
从 master 分叉，按引擎创建开发分支
- feature/ziwei   - 紫微引擎开发
- feature/ziping  - 子平引擎开发
- feature/heluo   - 河洛引擎开发
- feature/yi      - 易经引擎开发
- feature/blind   - 盲派引擎开发

工作流程:
1. 在 feature/ziwei 上开发紫微引擎
2. PR 合并回 master (需通过独立审计)
3. 其他引擎开发者不影响紫微工作
```

### 方案 C: 完全拆分仓库
```
wisdom-zziwei, wisdom-ziping, wisdom-heluo, wisdom-yi, wisdom-blind
每个仓库独立维护，通过 submodule 或独立 CI 集成
```

---

## 执行计划 (推荐方案 B)

### Step 1: 创建引擎特性分支
```bash
# 从 master 创建各引擎分支
git checkout -b feature/ziwei origin/master
git checkout -b feature/ziping origin/master
git checkout -b feature/heluo origin/master
git checkout -b feature/yi origin/master
git checkout -b feature/blind origin/master
git checkout master
```

### Step 2: 标记引擎 commit 范围
```bash
# 为每个引擎标记相关 commits
git log --oneline --grep="Z\|ziwei" > ziwei_commits.txt
git log --oneline --grep="ziping\|bazi" > ziping_commits.txt
git log --oneline --grep="heluo" > heluo_commits.txt
git log --oneline --grep="yi\|易经" > yi_commits.txt
git log --oneline --grep="blind\|盲派" > blind_commits.txt
```

### Step 3: 清理远程分支
```bash
# 删除过时的引擎分支 (已合并到 master 的)
git push origin --delete ziwei  # 如已无新开发
git push origin --delete ziping
```

### Step 4: 更新 PR 流程
- 所有引擎开发必须在 feature/* 分支上进行
- PR 必须通过对应引擎的独立测试
- 跨引擎变更需要特殊审批

---

## Commit 标记规范

### 引擎标识前缀
| 引擎 | 前缀 | 示例 |
|------|------|------|
| 紫微 | `Z` | `Z15: 飞星rule匹配` |
| 子平 | `P` | `P0-14: 立春边界修复` |
| 河洛 | `H` | `H16.1: 独立验证` |
| 易经 | `Y` | `Y1: 卦象解析` |
| 盲派 | `BL` | `BL1: 主客格局` |
| 治理 | `P2.x` | `P2.1-F: 外部信任根` |
| 数据 | `D` | `D1: 规则索引更新` |

### 禁止行为
- ❌ 不在引擎特性分支外修改引擎代码
- ❌ 不在 PR 中混合多个引擎变更
- ❌ 不在 master 直接 commit

---

## 下一步

需要确认：
1. 选择方案 A/B/C？
2. 是否需要保留 ziwei/ziping 等远程分支？
3. 是否需要为每个引擎创建独立的 CI 流水线？
