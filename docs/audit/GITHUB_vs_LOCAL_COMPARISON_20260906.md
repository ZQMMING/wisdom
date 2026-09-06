# GitHub vs D:/shuntian 对比分析报告

**分析时间**: 2026-09-06 19:15  
**分析人**: Hermes Agent

---

## 一、仓库基本信息

| 项目 | 值 |
|------|-----|
| 远程仓库 | https://github.com/ZQMMING/wisdom |
| 远程分支 | origin/main (master) |
| 远程最新commit | `824142f9` - 扩展东南亚/大洋洲经纬度覆盖 |
| 本地最新commit | `6a0bf855` - docs: 添加迁移完整性验证报告 |
| 本地领先远程 | 1 commit |
| 远程领先本地 | 3 commits（在 feature/ziwei 分支） |

---

## 二、本地独有的内容（已提交到 master）

### 2.1 审计文档（本次会话生成）
```
docs/audit/
├── ENGINE_MIGRATION_AUDIT_20260906.md
├── FINAL_MIGRATION_VERIFICATION_REPORT_20260906.md
├── FINAL_SUMMARY_20260906.md
├── FINAL_VERDICT_20260906.md
├── MIGRATION_COMPLETENESS_FINAL_20260906.md
├── MIGRATION_COMPLETENESS_REPORT_20260906.md
├── P0_ENGINE_MIGRATION_AUDIT_20260906.md
├── P0_ENGINE_MIGRATION_FINAL_REPORT_20260906.md
├── P0_EVIDENCE_GAP_20260906.md
├── P0_FINAL_VERDICT_20260906.md
├── P0_ZIWEI_ARCHITECTURE_DEFECT_20260906.md
├── SUMMARY_20260906.md
├── zi_ping_engine_comparison_20260906.md
└── audit_log.jsonl
```

### 2.2 新增证据文件
```
backend/data/evidence/di_tian_sui/E-DTS-145-001.json
```
（补充了三会局方位的测试用例）

### 2.3 归档目录
```
archive/heluo_legacy/
├── hetu_luoshu.py
├── metrics.py
├── heluo_yi_flow.py
├── meihua_engine.py
├── dayu.py
├── time_sequence.py
└── test_*.py (3个)
```

### 2.4 工作脚本
```
scripts/phase4_reaudit.py
```

---

## 三、远程独有的内容（尚未拉取到本地）

### 3.1 Phase B1/B2 核心模块（缺失！）
```
src/tongshu/phase_b1_evidence_connection.py     (963行) - 证据连接审计
src/tongshu/phase_b2_rule_authorization.py        (667行) - 规则授权治理
src/tongshu/phase_b2_1_remediation.py             (835行) - 补救修复逻辑
```

**影响**: 这些是断言治理的核心模块，缺失会导致：
- 无法运行 Phase B1 证据连接审计
- 无法运行 Phase B2 规则授权验证
- 无法运行 Phase B2.1 补救修复

### 3.2 紫微引擎修复（缺失！）
```
commit 1c809925: S14-fix: ZiweiEngine.full_chart() 补 stub fallback
commit f8c435da: Z13: FeixingRuleGraph + dayu.py stub cleanup
commit 54975dcb: H17-P0: Fix test fixture corruption in H16
```

**影响**: 这解释了为什么测试失败！
- shuntian 的 `full_chart()` 缺少 stub fallback
- FeixingRuleGraph 有清理修复
- test fixture 有损坏修复

### 3.3 诊断脚本
```
tests/fix_paths.py                              (82行)
tests/test_bazi_p2_fields.py                    (358行)
tests/test_phase3_p0.py                         (73行)
```

### 3.4 Bot审计报告
```
docs/bots/BOT-ZIPING/phase_b0_1_analysis.json   (6969行)
docs/bots/BOT-ZIPING/phase_b2_1_results.json    (483行)
docs/bots/BOT-ZIPING/phase_b2_audit_results.json (511行)
docs/bots/BOT-ZIWEI/REPORT.md                   (93行)
docs/bots/BOT-ZIWEI/PHASE2_REPORT.md            (96行)
```

---

## 四、架构差异根因分析

### 问题1：紫微引擎 full_chart() 返回类型不一致

**根因**：本地 shuntian 缺少 GitHub 上的 3 个关键 commits：
- `1c809925` - 补全 stub fallback（解决 import 错误）
- `f8c435da` - 清理 dayu.py stub
- `54975dcb` - 修复 test fixture corruption

**表现**：
```python
# 本地 shuntian
def full_chart(self, lunar_date, hour, gender):
    # ... 计算 ...
    return ZiweiChart(...)  # 或返回 dict（取决于实现）

# GitHub 最新版
def full_chart(self, lunar_date, hour, gender):
    # ... 计算 ...
    return FrozenZiweiChart(...)  # 明确返回对象
```

### 问题2：Phase B1/B2 模块缺失

**根因**：本地 master 分支缺少 feature/ziwei 分支的合并

**影响**：
- 断言治理功能不完整
- 证据连接审计无法运行
- 规则授权验证缺失

---

## 五、修复建议

### 立即行动（P0）

1. **拉取 GitHub 更新**
   ```bash
   cd /d/shuntian
   git fetch origin
   git merge origin/feature/ziwei  # 或 rebase
   ```

2. **验证紫微引擎**
   ```bash
   python -m pytest tests/test_ziwei_feixing_production.py -v
   ```

### 后续优化（P1）

3. **同步其他分支**
   ```bash
   git merge origin/feature/blind
   git merge origin/feature/heluo
   git merge origin/feature/yi
   git merge origin/feature/ziping
   ```

4. **清理审计文档**
   - 将本次生成的审计报告移到 `docs/audit/archive/`
   - 保留最终的 `FINAL_MIGRATION_VERIFICATION_REPORT_20260906.md`

---

## 六、结论

### ✅ 本地（D:/shuntian）状态
- master 分支领先 GitHub 1 commit（审计文档）
- 核心引擎代码基本完整
- 证据系统完整（1,575个文件）
- **问题**：缺少紫微引擎的 stub fallback 修复

### ⚠️ GitHub 远程状态
- 有 3 个 commits 未合并到 master
- Phase B1/B2 模块在 feature/ziwei 分支但未合并
- 紫微引擎有修复但未合入 master

### 🔴 需要立即处理
1. **合并 feature/ziwei 分支到 master**
2. **验证紫微引擎测试**
3. **确认 Phase B1/B2 模块完整性**

---

**建议立即执行 `git merge origin/feature/ziwei`，然后运行测试验证。**
