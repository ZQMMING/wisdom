# 五引擎架构审计 & Git 同步报告

**时间**: 2026-09-05  
**状态**: 🔴 需要立即处理

---

## 一、当前状态总览

| 维度 | 本地 | origin/main |
|------|------|-------------|
| main 分支 | ahead 2, behind 1 | ahead 1 |
| 未推送 commit | 2 (engine fix) | 0 |
| 未拉取 commit | 0 | 1 (Personal Today page) |
| 未追踪文件 | 1 (ZIWEI_CODE_COMPARISON.md) | - |

---

## 二、五引擎路径独立性审查

### ✅ 1. 子平引擎 (Bazi)
```
src/tongshu/engines/bazi_engine.py        ← 核心计算
src/tongshu/engines/bazi_adapter.py       ← 适配层
src/tongshu/engines/bazi_l1_facts.py      ← L1事实数据
src/tongshu/engines/bazi/                 ← evidence_producer
src/tongshu/models/canonical_bazi.py      ← 模型定义
```
**状态**: ✅ 独立，裁决路径清晰  
**本地改动**: H18-MINUTE-FIX (9d7e789) - JD基准不一致修复 + 13个边界测试

### ✅ 2. 盲派引擎 (Blind)
```
src/tongshu/engines/blind_bazi_engine.py  ← 核心计算
src/tongshu/engines/blind_yingqi.py       ← 应期模块
src/tongshu/engines/blind/                ← palace, workchain, workgraph, evidence_producer
```
**状态**: ✅ 独立，P2.6-E-FIX 已移除 three 越权  
**远端最后**: `fb546dd` P2.6-E-FIX

### ✅ 3. 紫微引擎 (Ziwei)
```
src/tongshu/engines/ziwei_engine.py       ← 核心计算
src/tongshu/engines/ziwei_*.py            ← 10+ 辅助模块
src/tongshu/engines/ziwei/                ← evidence_producer
src/tongshu/models/canonical_bazi.py      ⚠️ 共享依赖
```
**状态**: ⚠️ 基本独立，但需注意 canonical_bazi.py 是共享层  
**远端最后**: `88e1651` Ziwei P0 Fix v2

### ⚠️ 4. 河洛引擎 (Heluo)
```
src/tongshu/engines/heluo/                ← 20+ 文件，完整独立
src/tongshu/engines/heluo_yi_flow.py      ← 与易经共享流程
```
**状态**: ⚠️ **H17-B 污染已被回滚 (9e233e6)，但需确认干净**  
**远端最后**: `9e233e6` P2.7-H18-ROLLBACK

### ✅ 5. 易经引擎 (Yi)
```
src/tongshu/engines/yi/                   ← 10个文件，完整独立
src/tongshu/engines/heluo_yi_flow.py      ← 与河洛共享流程
```
**状态**: ✅ 独立  
**远端最后**: `17d4b4d` P1.2-F

---

## 三、关键发现

### 🔴 问题1: 八字引擎改动污染河洛/易经风险
**已发生**: `7d6002a` P2.7-H17-B 修改了 `heluo/canonical.py` 和 `signal/adapters/heluo_adapter.py`  
**已回滚**: `9e233e6` 恢复了 heluo/canonical.py 并删除了污染文件  
**当前状态**: ✅ 已清理，但需验证回滚彻底性

### 🔴 问题2: 本地 2 个 engine fix 未推送
- `84b0668` P2.7-H18-FIX: Calculation-Time Authority Closure
- `9d7e789` P2.7-H18-MINUTE-FIX: JD基准不一致修复 + 13个边界测试

**影响**: 这些是今天一整天工作的核心修复，必须推送

### 🟡 问题3: 远端 Personal Today page (d164b86) 可能与本地冲突
- 远端新增 8 个 cards 组件
- 修改了 PersonalToday.tsx 和 types/index.ts
- 本地没有这些改动

### 🟡 问题4: assertion_v2 裁决路径过薄
```
src/tongshu/assertion_v2/
├── __init__.py
└── contract.py  ← 仅 9KB，2个文件
```
对比旧的 `assertion/` 目录仍有 3 个文件（admission_registry.py 等）

### 🟡 问题5: 多个工作分支未本地化
远端有但本地缺失的分支：
- `h16-heluo`, `h16-heluo-verification`
- `audit-e001-phase6`
- `master-clean`
- `p0-legacy-purge`

---

## 四、建议执行计划

### 阶段1: 安全同步（立即执行）
```bash
# 1. 先推本地engine fix（这是核心工作）
git push origin main

# 2. 用 rebase 方式拉取远端 Personal Today（减少merge commit）
git pull --rebase origin main
```

### 阶段2: 验证测试
```bash
# 运行全量测试
python -m pytest tests/ -x --tb=short

# 特别关注：
# - bazi 相关测试
# - heluo 相关测试
# - ziwei 相关测试
```

### 阶段3: 架构加固（下次迭代）
1. 在 `assertion_v2/` 建立五引擎独立的 Admission 接口
2. 清理 `assertion/` 旧目录（确认无引用后删除）
3. 创建 `engines/audit/` 目录存放引擎边界审计报告

---

## 五、风险提示

| 风险 | 级别 | 说明 |
|------|------|------|
| Personal Today page 合并冲突 | 🟡 中 | types/index.ts 可能被两边修改 |
| 旧 assertion 残留代码 | 🟢 低 | 需确认无生产引用 |
| heluo/canonical.py 回滚残留 | 🟡 中 | 需验证测试通过 |

---

## 六、下一步行动

**选项A: 立即执行同步**
```bash
git push origin main && git pull --rebase origin main
```

**选项B: 先检查冲突风险**
查看 PersonalToday.tsx 和 types/index.ts 的具体改动差异

**选项C: 先备份再同步**
创建本地备份分支，确认无误后再 push

---

**推荐**: 选项A，因为：
1. 本地 engine fix 是核心修复，不应长期滞后
2. Personal Today page 是前端改动，冲突概率低
3. rebase 方式能保持提交历史整洁
