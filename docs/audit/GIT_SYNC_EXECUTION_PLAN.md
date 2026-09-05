# Git 同步执行方案

**审计日期**: 2026-09-05  
**状态**: ✅ 审计完成，准备同步

---

## 一、核心发现

### ✅ 五引擎路径独立性：通过

| 引擎 | 核心文件 | Evidence Producer | 测试覆盖 | 状态 |
|------|---------|-------------------|---------|------|
| 子平 | `bazi_engine.py` | `bazi/evidence_producer.py` | 8 files | ✅ 独立 |
| 盲派 | `blind_bazi_engine.py` | `blind/evidence_producer.py` | 4 files | ✅ 独立 |
| 紫微 | `ziwei_engine.py` (+10辅助) | `ziwei/evidence_producer.py` | 12 files | ✅ 独立 |
| 河洛 | `heluo/canonical.py` (+20模块) | `heluo/evidence_producer.py` | 6 files | ✅ 独立 |
| 易经 | `yi/classical_text.py` (+9模块) | `yi/evidence_producer.py` | 5 files | ✅ 独立 |

### ✅ H17-B 污染回滚验证：彻底

- `signal/adapters/heluo_adapter.py` - **已删除** ✅
- `heluo/canonical.py` - **已恢复到 bb33867 (pre-H17-B)** ✅
- 河洛测试 - **24/24 通过** ✅

### 🟡 canonical_bazi.py 状态：正确保留

这是子平引擎的核心模型（非污染），被紫微等引擎作为只读上游接口消费。
- 本地 HEAD: 存在（84b0668 添加了 birth_datetime 字段）
- 远端 main: 存在（a12450e 恢复后）
- **结论**: 这是架构必需，不是污染 ✅

---

## 二、Git 差异详情

### 本地独有（2 commits，必须推送）

```
9d7e789 P2.7-H18-MINUTE-FIX
├── docs/: 添加 8 个审计报告（可暂不推，或单独commit）
├── src/tongshu/engines/bazi_engine.py: JD基准不一致修复
└── tests/: 新增 13 个分钟级节气边界测试

84b0668 P2.7-H18-FIX: Calculation-Time Authority Closure
├── src/tongshu/engines/bazi_adapter.py: 传递 true_solar_datetime
├── src/tongshu/engines/bazi_engine.py: 支持 minute/second
├── src/tongshu/models/canonical_bazi.py: 添加 birth_datetime 字段
└── tests/test_p27g_fix_hour_precision.py: 更新断言
```

### 远端独有（1 commit，可安全拉取）

```
d164b86 Build out full Personal Today page
├── liorin-frontend/src/components/cards/: +8 个新组件
├── liorin-frontend/src/pages/today/PersonalToday.tsx: 重组布局
├── liorin-frontend/src/mock/data.ts: 扩展 mock
└── liorin-frontend/src/types/index.ts: 新增 HeluoPanel/ViewModel 类型
```

### 未追踪文件

```
docs/audit/ZIWEI_CODE_COMPARISON.md  (183 lines)
```

---

## 三、冲突风险评估

| 文件 | 本地改动 | 远端改动 | 冲突风险 |
|------|---------|---------|---------|
| `PersonalToday.tsx` | 基础版本 (93行) | 扩展版本 (106行) | 🟢 低 - rebase 自动合并 |
| `types/index.ts` | 基础版本 (51行) | 扩展版本 (108行) | 🟢 低 - 远端扩展现有类型 |
| 其他 frontend 文件 | 无 | 新增 | 🟢 无冲突 |

**结论**: 预期冲突极少或无冲突，可安全执行 rebase merge。

---

## 四、执行步骤

### 步骤1: 推送本地 engine fix（优先级：高）

```bash
git push origin main
```

**预期结果**: 远端包含 9d7e789 和 84b0668，与本地同步。

### 步骤2: Rebase 拉取远端 Personal Today page

```bash
git pull --rebase origin main
```

**预期结果**: 
- 本地 commit 在 rebase 后成为新 SHA
- Personal Today page 自动应用
- 如有冲突，按报告第三节手动解决

### 步骤3: 提交 ZIWEI_CODE_COMPARISON.md

```bash
git add docs/audit/ZIWEI_CODE_COMPARISON.md
git commit -m "docs: Add Ziwei code comparison audit"
```

### 步骤4: 运行全量测试验证

```bash
python -m pytest tests/ -x --tb=short
```

**预期通过**: 所有引擎测试套件通过。

### 步骤5: 推送最终状态（可选）

```bash
git push origin main
```

---

## 五、分支策略建议

### 立即执行

✅ 保持当前 `main` 分支作为生产路径  
✅ 所有 engine fix 合入 main

### 后续迭代

考虑创建以下分支用于并行工作：

| 分支名 | 用途 | 优先级 |
|--------|------|--------|
| `feat/assertion-v2-heluo` | 河洛引擎独立 Admission 接口 | 中 |
| `feat/assertion-v2-yi` | 易经引擎独立 Admission 接口 | 中 |
| `refactor/canonical-bazi-decouple` | 解耦 canonical_bazi.py 依赖 | 低 |

---

## 六、风险提示

| 风险 | 级别 | 缓解措施 |
|------|------|---------|
| rebase 冲突 | 🟢 低 | 手动编辑 PersonalToday.tsx |
| 旧 assertion 残留 | 🟢 低 | 运行 `grep -r "from src.tongshu.assertion" src/` 验证 |
| heluo 测试遗漏 | 🟢 低 | 已验证 24/24 通过 |

---

## 七、最终状态目标

```
origin/main: d164b86 (Personal Today) + 9d7e789 (H18-MINUTE-FIX) + 84b0668 (Authority Closure)
local/main:  与 origin/main 同步
测试状态:    所有引擎测试套件 PASS
引擎路径:    五引擎完全独立，无交叉污染
```

---

**执行建议**: 按上述步骤顺序执行，每步验证后再进行下一步。
