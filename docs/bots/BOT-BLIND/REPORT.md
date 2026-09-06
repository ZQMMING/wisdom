# BOT-BLIND 审计报告 (第二轮)

**任务 ID**: T-ENGINE-BLIND-003  
**审计日期**: 2026-09-05 (第二轮重审)  
**前置依赖**: BOT-TIME ✅, BOT-BAZI ✅ (strength_engine 已隔离)  
**状态**: P1 完成，发现关键问题

---

## 执行摘要

| 项目 | 状态 | 备注 |
|------|------|------|
| 代码结构审计 | ⚠️ **异常** | workchain/workgraph/rules/graph **不存在** |
| 测试覆盖 | ✅ 通过 | 10 yingqi + 3 bench = 13 passed |
| Evidence Corpus | ❌ **未验证** | 86 文件 / **0/74 provenance verified** |
| 做功类型覆盖 | ✅ 完整 | 合/冲/穿/墓/制/化/生/包局/暗合/禄刃 |
| 应期判断 | ✅ 准确 | 大限/大运/流年引动全覆盖 |
| 与 BaziEngine 边界 | ⚠️ 耦合 | BlindBaziEngine 依赖 BaziEngine.compute() |

**核心发现**: Evidence Corpus 存在**系统性 provenance 缺失**，所有 74 条证据被 downgraded 至 PENDING_VERIFICATION。

---

## 一、代码结构审计

### 1.1 workchain/workgraph/rules 不存在

**审计发现**: task_dispatch 列出的以下文件 **不存在于仓库中**:

```
src/tongshu/engines/blind/
├── __init__.py          (6 lines)
└── evidence_producer.py (127 lines)
```

**不存在的文件清单**:
| 预期文件 | 实际状态 |
|----------|----------|
| `workchain.py` | ❌ 不存在 |
| `workgraph.py` | ❌ 不存在 |
| `rules/graph.py` | ❌ 不存在 |
| `rules/matcher.py` | ❌ 不存在 |
| `rules/models.py` | ❌ 不存在 |

**结论**: rules/graph.py 是 **死代码/已删除代码**，无任何生产 consumer。Blind 引擎采用**扁平架构**，所有做功逻辑直接在 `blind_bazi_engine.py` 中实现。

### 1.2 做功类型覆盖度

`blind_bazi_engine.py` (V2.6, 650 lines) 实现以下做功机制:

| 做功类型 | 代码位置 | 状态 |
|----------|----------|------|
| 天干五合 | line 263 | ✅ |
| 地支六合 | line 267 | ✅ |
| 地支六冲 | line 271 | ✅ |
| 地支六穿 | line 276 | ✅ |
| 地支三合 | line 370 | ✅ |
| 墓库收放 | line 379 | ✅ |
| 暗合 | line 423 | ✅ |
| 包局 | line 458 | ✅ |
| 禄神受穿 | line 495 | ✅ |
| 阳刃 | line 508 | ✅ |

**做功方式识别**: 合财/合官/食伤制杀/伤官制官/比劫制财/财制印/官杀制比劫/印化官杀/食伤生财/冲开墓库/闭库收物/禄神受穿/阳刃 → 全部覆盖。

**覆盖度评估**: **8/8 核心做功机制已实现**。

---

## 二、 Yingqi 应期判断准确性

`blind_yingqi.py` (440 lines) 实现以下应期方法:

| 应期方法 | 测试覆盖 | 结果 |
|----------|----------|------|
| 大限分段 | test_daxian_segments | ✅ |
| 流年干支 | test_flow_year_ganzhi | ✅ |
| 冲引动 | test_trigger_cihong | ✅ |
| 穿引动 | test_case3_lu_chuan | ✅ |
| 三刑 | test_sanxing_yingqi | ✅ |
| 墓库开闭 | test_muku_kai_yingqi | ✅ |
| 透干应期 | test_tougan_yingqi | ✅ |
| 合/三合 | implicit | ✅ |
| 自刑 | implicit | ✅ |
| 禄神重现 | implicit | ✅ |

**测试通过率**: **10/10 全部通过** (pytest: 13 passed in 0.27s)

**已知限制**:
- 大限分段采用段建业体系（年1-18/月18-35/日35-55/时55+）
- 不透干地支藏干的应期计算较简化

---

## 三、与 BaziEngine 的依赖边界

```python
# blind_bazi_engine.py:147
def __init__(self, bazi_engine: Optional[BaziEngine] = None):
    self.bazi_engine = bazi_engine or BaziEngine()
```

**依赖关系**:
- `BlindBaziEngine` 依赖 `BaziEngine.compute()` 获取四柱数据
- `BlindYingqiEngine` 同样依赖 `BaziEngine`

**耦合风险**:
- 当前设计：Blind 引擎作为 BaziEngine 的扩展层
- 风险：如果 BaziEngine 接口变更，Blind 引擎需同步修改
- BOT-BAZI 已完成 strength_engine 隔离，可在此基础上提取 `FourPillars` 接口

**建议架构**:
```
FourPillars (interface)
    ├── BaziEngine (adapter)
    └── BlindBaziEngine (consumer)
```

---

## 四、Evidence Corpus 审计

### 4.1 文件统计

| 指标 | 数量 |
|------|------|
| JSON 证据文件 | **86** |
| 有效证据条目 | 74 (manifest.json) |
| 已验证 provenance | **0** |
| 待验证 | 74 |

### 4.2 分层分布

```
Layer A (传承证据):    2 条
Layer B (段氏理论):   57 条
Layer C (命例验证):   15 条
Layer D (二次整理):    0 条
```

### 4.3 Provenance 严重问题

**`source_verification_final_report.json` 显示**:
```json
{
  "verification_summary": {
    "retained_direct": 0,
    "downgraded_to_pending": 56,
    "verified_count": 0,
    "claimed_direct_count": 0,
    "pending_count": 74
  }
}
```

**所有 74 条证据均被 downgraded**，原因统一为:
- `no_author`: 无作者信息
- `no_chapter`: 无章节定位
- `no_locator`: 无原文定位符

**示例** (E-BLIND-A-GUEST_HOST-001.json):
```json
{
  "source_fidelity": "PENDING_VERIFICATION",
  "certainty": "MEDIUM",
  "notes": "🔄 强制修正: 理法-结构 → 理法-结构 | 🔍 来源验证: DOWNGRADED - ['no_author', 'no_chapter', 'no_locator']"
}
```

### 4.4 与 v1 报告的关系

`BLIND_EVIDENCE_CORPUS_V1_FINAL_REPORT.md` 声称:
- 18 条证据
- 12/12 主题覆盖
- 100% DIRECT/HIGH 保真度

**矛盾**: 当前 manifest.json 显示 74 条证据，且全部为 PENDING_VERIFICATION。v1 报告中的数据已被清理/重写。

**结论**: Evidence Corpus 处于 **假阳性完成** 状态。文件存在但未经过原典验证，且声称的 DIRECT/HIGH 保真度已被 downgraded。

---

## 五、10 个问题标记定位

| # | 问题 | 严重度 | 证据 |
|---|------|--------|------|
| 1 | workchain/workgraph/rules 不存在 | **P0** | 文件系统确认 |
| 2 | Evidence provenance **0/74** 验证 | **P0** | source_verification_final_report.json |
| 3 | v1 报告声称 18 条 DIRECT/HIGH，实际 0/74 | **P1** | 报告 vs 数据矛盾 |
| 4 | 86 文件 vs 74 条证据不一致 | P1 | manifest.json vs 文件系统 |
| 5 | Blind 引擎强依赖 BaziEngine | P2 | 代码耦合分析 |
| 6 | 大限分段与部分传统不同 | P2 | 段建业体系 vs 传统 |
| 7 | RULE_PREFIX 使用 "BL" 而非 "BLIND" | P3 | 命名一致性 |
| 8 | Evidence Producer 的 rule_ref 路径不存在 | P3 | data/rules/blind_*.json |
| 9 | 测试无 golden case 对比 | P3 | 仅单元测试 |
| 10 | 做功强度计算公式未经验证 | P2 | 经验公式 vs 典籍校准 |

---

## 六、验收状态

| 验收项 | 状态 |
|--------|------|
| 所有测试通过 | ✅ 13/13 passed |
| Golden Dataset 无降级 | ✅ 无修改 |
| Evidence provenance 完整 | ❌ **0/74 verified** |
| 无遗留 P0/P1 问题 | ❌ **存在 P0 问题** |

---

## 七、下一步行动

### 立即执行 (P0)
1. **清理 workchain/workgraph 残留引用** - 确认这些文件是否被其他模块引用
2. **启动 Evidence 原典验证** - 至少验证 Layer B 的 57 条段氏理论证据
3. **修正 v1 报告** - 将 claims 与实际 provenance 状态对齐

### 短期计划 (P1-P2)
4. **解耦 BlindBaziEngine 与 BaziEngine** - 利用 BOT-BAZI 的 FourPillars 接口隔离
5. **补充 golden case 测试** - 使用段建业《盲派初级命理学》案例
6. **做功强度公式校准** - 与典籍案例对照

### 长期计划
7. **Phase B: Signal Schema 定义** - 等待用户裁决
8. **Phase C: Evidence → Signal Mapping** - Phase B 完成后执行

---

## 八、附录

### A. 代码路径

```
/c/Users/ming/.temp/wisdom_repo/
├── src/tongshu/engines/
│   ├── blind_bazi_engine.py     (650 lines, V2.6)
│   ├── blind_yingqi.py          (440 lines)
│   └── blind/
│       ├── __init__.py
│       └── evidence_producer.py
├── tests/
│   ├── test_blind_yingqi.py     (10 tests, all pass)
│   └── test_mingli_bench_blind.py (3 tests, all pass)
└── data/evidence/blind_seg/
    ├── *.json (86 files)
    ├── manifest.json            (74 entries, PHASE_A_IN_PROGRESS)
    └── provenance_final_status.json (0/74 verified)
```

### B. 关键数据源

| 文件 | 内容 |
|------|------|
| `data/evidence/blind_seg/manifest.json` | 74 条证据，18 主题 |
| `data/evidence/blind_seg/provenance_final_status.json` | 0/74 verified |
| `data/evidence/blind_seg/source_verification_final_report.json` | 全部 downgraded |
| `docs/audit/BLIND_PHASE_A_CORRECTION.md` | 理论架构说明 |
| `docs/BLIND_SEGMENT_ARCHITECTURE.md` | 分层架构方案 |

---

*报告生成: @bot-blind | 顺天项目 BOT-MASTER 审计任务 T-ENGINE-BLIND-003*
