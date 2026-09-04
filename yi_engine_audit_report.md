# 易经解卦引擎审计报告

**审计时间：** 2026-09-03  
**目标目录：** `E:\shuntian\src\tongshu\engines\yi\`  
**测试目录：** `E:\shuntian\tests\test_yi*.py`, `E:\shuntian\tests\yi\`

---

## 一、文件清单 + 职责

| 文件 | 大小 | 层级 | 职责 |
|------|------|------|------|
| `__init__.py` | 1KB | — | 模块导出，不重复定义模型 |
| `models.py` | 3.5KB | 全局 | 共享数据模型：HexagramSymbol, LineSymbol, ClassicalText, ImageExpansion, InterpretationInput/Output |
| `classical_text.py` | 27KB | **层C** | 经典原文检索：64卦卦辞/彖辞/大象辞（周易原文），支持别名解析和KbLoader覆盖 |
| `yao_ci_data.py` | 53KB | **层B** | 爻辞数据：384条爻辞（64卦×6爻），支持多格式爻位名解析 |
| `hexagram_symbol.py` | 7KB | **层A** | 卦象结构解析：八卦五行/符号映射、64卦SIXTY_FOUR_MAP、体用生克、错综互卦计算 |
| `line_symbol.py` | 3.2KB | **层B** | 爻象关系计算：当位/中位/承乘比应/元堂解析，纯逻辑无AI介入 |
| `image_expansion.py` | 1.8KB | **层D** | 象义展开：5层证据等级，禁止跨级跳跃输出 |
| `evidence_producer.py` | 5.4KB | 输出层 | YiEvidenceProducer：从卦/爻结果提取EngineEvidence纯事实列表（V13 §五硬约束） |
| `fupeirong_loader.py` | 6KB | 数据加载 | 傅佩荣64卦8维断言（时运/财运/家宅等） |
| `gua_four_dim_loader.py` | 9.6KB | 数据加载 | 64卦四维验证数据（卦辞/大象/白话/人间道/占卜道） |
| `master_wisdom_loader.py` | 8.9KB | 知识补充 | 南怀瑾/曾仕强易经哲学观点库（17个主题） |
| `yao_ci_meanings.py` | 208KB | 数据 | 爻辞释义扩展数据（未在测试中直接引用） |

**不在本目录的核心文件：**
- `interpreter.py` 位于 `src/tongshu/yi/interpreter.py`（7.5KB）—— YiInterpretationEngine 实现
- `yi/__init__.py` / `yi/schema.py` / `yi/adapter.py` —— Yi架构契约层

---

## 二、测试通过率

### 根目录测试（按任务要求）
```
cd E:\shuntian && python -m pytest tests/test_yi_interpreter.py tests/test_yi_hexagram.py -v --tb=short
```
**结果：27 passed，0 failed，0 errors** ✅

### tests/yi/ 子目录全量测试
```
python -m pytest tests/yi/ -v --tb=short
```
**结果：45 passed，1 failed，4 errors**

| 状态 | 测试文件 | 说明 |
|------|---------|------|
| ✅ 45 passed | `test_yi_e2e.py`, `test_yi_forward_validation.py`部分, `test_p0_classical_text.py`, `test_p0_interpretation_unified.py` | 核心引擎逻辑正常 |
| ❌ 1 failed | `test_yi_forward_validation.py::TestGoldenDatasetIntegrity::test_no_golden_dataset_modification` | 路径硬编码为 `D:/today/backend/src/tongshu/golden`，当前环境不存在 |
| ⚠️ 4 errors | `test_p0_compute_stage_heluo.py`（setUpClass失败）| 依赖 `D:\today\docs\rule.schema.json` 文件不存在（路径硬编码） |

**注：** 4个ERROR和1个FAILED均为测试路径硬编码问题（硬编码 `D:/today/...`），非引擎代码bug。

---

## 三、数据完整性验证

### 爻辞数据（YAO_CI）
```
Hexagrams: 64 ✅
Total yao lines: 384 ✅ (64 × 6 = 384)
Missing/incorrect line counts: 0 ✅
```

### 卦辞/彖辞/大象辞数据（_CLASSICAL_TEXTS）
```
Hexagrams: 64 ✅
All 3 slot types (gua_ci, tuan_ci, da_xiang_ci): present ✅
```

### 一致性校验
- `YAO_CI` keys ⊆ `_CLASSICAL_TEXTS` keys：完全一致 ✅
- 别名映射（`_HEXAGRAM_ALIASES` 和 `_HEXAGRAM_VARIANTS`）：均覆盖64卦 ✅
- `_KB_TEXTS`（运行时KbLoader覆盖）：当前为空字典（无外部知识库数据），回退到内嵌数据 ✅

**结论：384爻辞完整，64卦卦辞/彖辞/大象辞完整。**

---

## 四、V13架构合规性检查

### 4.1 原文vs解释分离 ✅

| 约束 | 实现状态 |
|------|---------|
| 层C（classical_text.py）不介入AI | ✅ 纯数据查询，无LLM调用 |
| 层B（yao_ci_data.py）不介入AI | ✅ 纯数据查询 |
| 层A（hexagram_symbol.py）不介入AI | ✅ 纯逻辑计算 |
| 解释逻辑独立（interpreter.py） | ✅ YiInterpretationEngine 在独立路径 |
| EngineEvidence 只保留事实 | ✅ evidence_producer.py 不生成 direction/polarity/strength |

### 4.2 YiInterpretationEngine 合规性 ✅

```python
# 禁止术语表（已实现）
FORBIDDEN_TERMS = frozenset({
    "大凶", "凶兆", "化解", "必败", "定数", "宿命",
    "改运", "转运", "趋吉避凶", "命理", "风水",
    "五行缺", "冲煞", "刑克", "犯太岁",
})
```

- 不生成 `fortune_score` / `luck_score` ✅
- 输出 `YiInterpretation` 包含 `state/opportunity/risk/remediation/action` ✅
- `check_forbidden_terms()` 方法已实现 ✅
- 置信度仅记录不参与决策 ✅

### 4.3 架构分层 ✅

```
层A: hexagram_symbol.py     → HexagramSymbol（数据）
层B: line_symbol.py          → LineSymbol（逻辑计算）
层B: yao_ci_data.py          → 爻辞原文（数据）
层C: classical_text.py       → 卦辞/彖辞/大象辞（数据）
层D: image_expansion.py      → ImageExpansion（5层象义）
输出: evidence_producer.py   → YiEvidenceProducer（纯事实证据）
解释: tongshu/yi/interpreter.py → YiInterpretationEngine（关系式解释）
```

---

## 五、问题清单

### P0（阻塞性问题）

| # | 问题 | 位置 | 影响 |
|---|------|------|------|
| 1 | `interpreter.py` 路径不一致 | `src/tongshu/engines/yi/` 无此文件，实际在 `src/tongshu/yi/interpreter.py` | 模块导入路径混乱，新开发者易困惑 |
| 2 | 测试路径硬编码 `D:/today/...` | `test_p0_compute_stage_heluo.py`, `test_yi_forward_validation.py` | 在新环境无法运行 |

### P1（重要问题）

| # | 问题 | 位置 | 建议 |
|---|------|------|------|
| 1 | `HEXAGRAM_FULL_DATA` 空字典 | `hexagram_symbol.py:24` | 注释说明"简化版暂不编号"，但未填充数据，影响 `get_hexagram_symbol()` 的 `hexagram_number` 字段 |
| 2 | `GUA_SEQUENCE` 编号错误 | `hexagram_symbol.py:36-48` | 序号不连续（缺11,12,21,30,31等），与标准文王卦序不符 |
| 3 | `yao_ci_data.py` 来源标注不规范 | 多处 `source` 字段含重复字符如 `"周易·同人卦·六二二"` | 应为 `"周易·同人卦·六二"`，数据清洗问题 |
| 4 | `_get_hu_gua()` 返回空字符串 | `hexagram_symbol.py:154-157` | 互卦计算未实现，仅占位 |

### P2（建议改进）

| # | 问题 | 建议 |
|---|------|------|
| 1 | 缺少小象辞（xiao xiang ci）数据 | `ClassicalText` 模型有 `xiao_xiang_ci` 字段但无数据 |
| 2 | `image_expansion.py` 第3-5层未实现 | 当前只生成L1/L2，L3-L5为空 |
| 3 | 爻位名标准化可增强 | 支持更多变体（如"上一"→"上九"） |

---

## 六、改进建议

### 短期（可立即修复）

1. **统一 interpreter.py 路径**：将 `src/tongshu/yi/interpreter.py` 迁移到 `src/tongshu/engines/yi/interpreter.py`，或在 `engines/yi/__init__.py` 中添加重导出
2. **修复测试路径硬编码**：使用 `Path(__file__).resolve().parents[N]` 动态计算路径
3. **清洗 yao_ci_data.py 来源标注**：修正 `"周易·同人卦·六二二"` → `"周易·同人卦·六二"` 等重复字符

### 中期（架构完善）

4. **实现互卦计算**：`_get_hu_gua()` 需补充二三四爻/三四五爻提取逻辑
5. **填充 HEXAGRAM_FULL_DATA**：按文王卦序完整编号（或从标准数据源导入）
6. **补充小象辞数据**：完成 `ClassicalText.xiao_xiang_ci` 字段的数据覆盖

### 长期（数据质量）

7. **引入外部校验**：与权威周易数据库（如国学网、汉典）交叉验证384爻辞准确性
8. **添加数据版本标记**：在 `yao_ci_data.py` 和 `classical_text.py` 顶部添加数据来源版本
9. **实现 L3-L5 象义扩展**：完成 `image_expansion.py` 第3-5层的数据构建

---

## 七、总结

| 维度 | 状态 | 评分 |
|------|------|------|
| 数据完整性（64卦×6爻） | ✅ 384/384 完整 | 100% |
| 测试通过率（核心） | ✅ 27/27 passed | 100% |
| 测试通过率（全量） | ⚠️ 45/50（5个路径问题） | 90% |
| V13架构合规 | ✅ 原文/解释分离清晰 | 符合 |
| 代码质量 | ⚠️ 路径不一致、数据标注瑕疵 | 75% |

**整体评估：易经解卦引擎核心功能正常，数据完整，V13架构约束基本遵守。主要问题集中在测试路径硬编码和模块组织不规范，建议优先修复P0问题。**
