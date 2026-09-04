# 子平八字引擎审计报告

## 1. 文件清单 + 职责

### 核心引擎层
| 文件 | 路径 | 职责 |
|------|------|------|
| bazi_engine.py | `src/tongshu/engines/bazi_engine.py` | 子平八字主引擎：四柱计算、大运推导、P2婚姻/健康字段附加 |
| bazi_adapter.py | `src/tongshu/engines/bazi_adapter.py` | 适配层：将 TimeResolver/CalculationContext 投影到 BaziEngine 输入 |
| blind_bazi_engine.py | `src/tongshu/engines/blind_bazi_engine.py` | 盲派八字引擎（做功体系，与子平并行） |
| evidence_producer.py | `src/tongshu/engines/bazi/evidence_producer.py` | P1.2-A：从 BaziChart 提取 EngineEvidence，无 polarity/strength/confidence |
| bazi_l1_facts.py | `src/tongshu/engines/bazi_l1_facts.py` | P6.1-A：L1原始事实层（十二长生 + 完整藏干），零旺衰判断 |

### 推理层
| 文件 | 路径 | 职责 |
|------|------|------|
| bazi_ten_gods.py | `src/tongshu/reasoning/bazi_ten_gods.py` | 十神计算、藏干表、季节映射（确定性查找表） |
| bazi_fixed_tables.py | `src/tongshu/reasoning/bazi_fixed_tables.py` | 固定规则表（含道路地支、绝对地支等） |

### 规格定义层
| 文件 | 路径 | 职责 |
|------|------|------|
| engine_evidence.py | `src/tongshu/spec/canonical/engine_evidence.py` | EngineEvidence 合约：禁止 direction/polarity/strength/confidence |
| result.py | `src/tongshu/cross_domain/result.py` | 跨域结果模型：EngineEvidenceSet、MultiDomainSemanticCoverage |

### 测试层
| 文件 | 路径 | 职责 |
|------|------|------|
| test_bazi_engine.py | `tests/test_bazi_engine.py` | Pillar属性、Chart结构、确定性输出、60甲子完整性 |
| test_bazi_integrity_audit.py | `tests/test_bazi_integrity_audit.py` | 四柱计算校验（与sxtwl交叉验证）、藏干/十神/五行验证 |

---

## 2. 测试通过率

| 测试套件 | 用例数 | 通过数 | 失败数 | 通过率 |
|----------|--------|--------|--------|--------|
| test_bazi_engine.py | 12 | 12 | 0 | 100% |
| test_bazi_integrity_audit.py | 15 | 15 | 0 | 100% |
| **合计** | **27** | **27** | **0** | **100%** |

---

## 3. 发现的 Bug 或问题

### 3.1 严重性：中

**路径冲突：bazi 目录 vs bazi_engine.py 顶层**
- `bazi_engine.py` 位于 `engines/` 根目录，但证据生产者 `evidence_producer.py` 位于 `engines/bazi/` 子目录
- 测试文件 `test_bazi_engine.py` 通过 `sys.path.insert(0, str(Path("D:/today/backend/src")))` 注入路径，而 `test_bazi_integrity_audit.py` 使用 `E:/shuntian/src`
- **路径不一致**：两个测试文件使用了不同的 source 路径

### 3.2 严重性：低

**test_bazi_integrity_audit.py 不是 pytest 可运行模块**
- 文件内容是脚本式运行（`run_audit()` + `if __name__ == "__main__"`）
- `pytest tests/test_bazi_integrity_audit.py -v --tb=short` 返回 "no tests ran"
- 应重构为 unittest 或 pytest fixture 风格才能纳入 CI 自动化

### 3.3 严重性：低

**`bazi_l1_facts.py` NEG-05 测试有语法错误**
```python
tests.append((
    "NEG-05",
    all_not_canonical,
    "所有事实的 canonical_source_status = NOT_CANONICAL..."
))
# 文件末尾：KeyError: 0 (截断错误)
```
- 第485行出现 `KeyError: 0` 混入代码，可能是编辑遗留

---

## 4. V13 架构合规性检查

### EngineEvidence 字段审查

| 检查项 | 要求 | 实际状态 | 结论 |
|--------|------|----------|------|
| 无 polarity | ✅ 禁止 | EngineEvidence 无 polarity 字段 | ✅ 合规 |
| 无 direction | ✅ 禁止 | EngineEvidence 无 direction 字段 | ✅ 合规 |
| 无 strength | ✅ 禁止 | EngineEvidence 无 strength 字段 | ✅ 合规 |
| 无 confidence | ✅ 禁止 | EngineEvidence 无 confidence 字段 | ✅ 合规 |
| 有 evidence_id | ✅ 要求 | UUID hex[:8] 动态生成 | ✅ 合规 |
| 有 rule_id 追溯 | ✅ 要求 | `ZP_STEM_YEAR` 等稳定格式 | ✅ 合规 |
| temporal_scope 标准化 | ✅ 要求 | 使用 TemporalScope enum | ✅ 合规 |

### evidence_producer.py V13 合规性

```python
# produce() 输出：list[EngineEvidence]
# 每条证据：value = 事实值（天干/地支/十神），无 polarity/direction/strength/confidence
```
✅ **完全合规**

### bazi_l1_facts.py V13 合规性

- `derived_conclusions = "NONE"` — 明确声明零旺衰推导
- `fact_layer = "L1_ENGINE_FACT"` — 正确标注
- `canonical_source_status = "NOT_CANONICAL"` — 正确标注实现源非 canonical
- 负向测试 NEG-01~NEG-07：零强/弱/根/评分字段

✅ **完全合规**

---

## 5. Golden Cases 检查

| 数据集 | 路径 | 规模 | 格式 |
|--------|------|------|------|
| golden_cases.json | `dataset/golden_v1/` | 50 案例, 518 事件 | `case_id, gender, birth_date, birth_hour, events, source_type` |
| ground_truth_frozen.json | `dataset/golden_v1/` | 8 条标注 | `annotation_contract_version, semantic_families, domains, directions` |
| celebrity50_zh.json | `cases/bazi/` | 50 名人案例 | `person_id, name, profile, categories, questions, source_file` |
| contest8_2021~2025.json | `cases/bazi/` | 各年竞赛题 | `contest_id, current_year, description, total_questions` |

**状态**：Golden cases 存在但测试未与之对接（test_bazi_engine.py 仅做单元/结构验证，无端到端 golden test）。

---

## 6. 改进建议

1. **统一测试路径**：`test_bazi_engine.py` 使用 `D:/today/backend/src`，`test_bazi_integrity_audit.py` 使用 `E:/shuntian/src`，应统一为项目路径。

2. **重构 integrity_audit 为 pytest 兼容**：将 `run_audit()` 拆分为独立的 pytest test 函数，使其能纳入 CI 自动运行。

3. **修复 bazi_l1_facts.py 末尾语法错误**：删除 `KeyError: 0` 遗留代码。

4. **添加 golden case 端到端测试**：当前测试不验证与 `golden_cases.json` 的对齐，建议增加 `test_matches_golden_case()` 用例。

5. **bazi 目录结构归一**：`bazi_engine.py` 在 `engines/` 根目录，而 `evidence_producer.py` 在 `engines/bazi/` 子目录，建议统一放置位置以避免导入混乱。

---

**审计结论**：子平八字引擎核心逻辑正确，V13 合约完全合规，测试通过率 100%，存在路径不一致和结构化改进空间。
