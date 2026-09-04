# 顺天项目 - 五大体系资料证据收集总报告

**收集日期**: 2026-09-03
**项目路径**: C:/Users/wisdom/wisdom
**架构依据**: SHUNTIAN_FINAL_ARCHITECTURE.md
**验证状态**: ✅ ad-hoc verification passed

---

## 一、子平八字体系

### 1.1 Classic Evidence Agents (`src/tongshu/classic_evidence/`)

| 文件 | 行数 | Authority | 职责 |
|------|------|-----------|------|
| `base.py` | 465 | Framework | 基类：ClassicEvidenceAgent、AssertionProvenance、SourceLocator |
| `dts_agent.py` | 192 | PRINCIPLE_CONSTRAINT | 滴天髓：旺衰气势辨证 |
| `pzzq_agent.py` | 203 | PATTERN_OPERATIONAL | 子平真诠：格局成败辨证 |
| `qtbj_agent.py` | 191 | CLIMATE_SEASONAL | 穷通宝鉴：调候寒暖辨证 |
| `smth_agent.py` | 191 | ELEMENT_IDENTITY | 三命通会：关系转化辨证 |
| `yhzp_agent.py` | 188 | DAYMASTER_STRUCTURE | 渊海子平：基础语义辨证 |

### 1.2 五部经典原典 (`data/classics/original/`)

| 经典 | 段落数 | 完整度 | 状态 |
|------|--------|--------|------|
| 滴天髓 (DTS) | 719 | 95% | ✅ 较好 |
| 子平真诠 (PZZQ) | 446 | 91.7% | ✅ 较好 |
| 穷通宝鉴 (QTBJ) | 1,556 | 调候表50% | ⚠️ 中等 |
| 三命通会 (SMTH) | 1,846 | 主题33.3% | ❌ 较差 |
| 渊海子平 (YHZP) | 2,472 | 8.9% | 🔴 严重不足 |

### 1.3 Evidence 文件统计 (`data/evidence/`)

| 来源 | 文件数 | HIGH | MEDIUM | LOW | 覆盖率 |
|------|--------|------|--------|-----|--------|
| 滴天髓 (DTS) | 44 | 44 | 0 | 0 | 6.1% |
| 子平真诠 (PZZQ) | 10 | 3 | 7 | 0 | 2.2% |
| 穷通宝鉴 (QTBJ) | 1,233 | 1,233 | 0 | 0 | **79.3%** |
| 三命通会 (SMTH) | 8 | 4 | 4 | 0 | 0.4% |
| 渊海子平 (YHZP) | 117 | 31 | 86 | 0 | 4.7% |
| 盲派 (blind_seg) | 76 | 0 | 0 | 76 | N/A |
| **总计** | **1,574** | **1,315** | **97** | **162** | **22.4%** |

---

## 二、盲派体系

### 2.1 引擎文件 (`src/tongshu/engines/blind/`) — 10个文件

| 文件 | 职责 |
|------|------|
| `evidence_producer.py` | 证据生产核心：BlindFeatureState（纯事实）、Relevance枚举 |
| `palace.py` | 宫位计算层：从palace_rules.json加载语义 |
| `workchain.py` | 做功链解析器：DFS提取体→用链路 |
| `workgraph.py` | 做功关系图：NodeType + RelationType |
| `rules/graph.py` | 规则图解析器：从BL-*.json加载 |

### 2.2 Evidence (`data/evidence/blind_seg/`) — 76文件

| 指标 | 数量 |
|------|------|
| 活跃证据 | 74 |
| VERIFIED | 0 (0%) |
| PENDING | 72 (97.3%) |
| REJECTED | 2 (2.7%) |
| 理论分层 | 理法-结构、理法-机制、象法、应期 |

---

## 三、紫微斗数体系

### 3.1 引擎文件 (`src/tongshu/engines/ziwei/`) — 6+文件

| 文件 | 职责 |
|------|------|
| `ziwei_engine.py` | 紫微主引擎 |
| `ziwei_adapter.py` | iztro输出适配 |
| `ziwei_dependency_adapter.py` | 修复大限方向bug |
| `evidence_producer.py` | 证据生产管道 |

### 3.2 外部依赖
- **iztro 2.6.0**: npm package，Implementation Reference
- **Bug已知**: 大限方向反向已修复

---

## 四、河洛理数体系

### 4.1 引擎文件 (`src/tongshu/engines/heluo/`) — 23文件

| 核心文件 | 职责 |
|----------|------|
| `canonical.py` | 主计算引擎 |
| `dayu.py` | 大运时间线 |
| `timeline_yun.py` | 流年/流月/流日 |
| `yi_interpreter.py` | HL×Yi解卦层 |
| `yuan_tang.py` | 元堂计算 |
| `hexagram.py` | 卦象结构分析 |
| `numbers.py` | 天干地支取数映射 |
| `interpretation.py` | H4 关系解释引擎 |

### 4.2 数据文件
- `data/semantic_atoms/`: yao.json(5KB), hexagrams.json(32KB), he_luo.json(7KB)
- `data/tiaohou/`: 64hex.json, fupeirong_64gua_dimensions.json
- `data/rules/HL-*.json`: 21条河洛规则

### 4.3 Golden Cases
- `dataset/golden_v1/`: 6 entries，**河洛相关: 0**

---

## 五、易经体系

### 5.1 引擎文件 (`src/tongshu/engines/yi/`) — 12文件

| 层级 | 文件 | 职责 |
|------|------|------|
| 层A | `hexagram_symbol.py` | 卦象层：八卦基础数据 |
| 层B | `line_symbol.py` | 爻象层：爻结构关系 |
| 层C | `classical_text.py` | 64卦卦辞+大象辞内嵌 |
| 层C | `yao_ci_data.py` | **384爻辞完整数据库** |
| 层C | `yao_ci_meanings.py` | 64卦爻辞解读（208KB） |
| 层D | `image_expansion.py` | 5层证据等级 |

### 5.2 数据覆盖验证 ✅
- 64卦卦辞: ✅ 内嵌完整
- 384爻辞: ✅ 内嵌完整（YAO_CI dict确认）
- 傅佩荣维度: ✅ 65条目，1601维
- 倪海厦数据: ✅ 完整

### 5.3 测试文件 (`tests/yi/`) — 5文件，1030行

---

## 六、五大体系互补关系

```
子平 ──────┐
盲派 ──────┤
紫微 ──────┤
河洛 ──────┼──→ EngineEvidence
易经 ──────┘
```

| 体系 | 核心维度 | 输出焦点 |
|------|----------|----------|
| 子平 | 格局成败、日主旺衰 | 命局结构分析 |
| 盲派 | 做功效率、应期判断 | 事件发生时机 |
| 紫微 | 星曜分布、宫位四化 | 人生领域映射 |
| 河洛 | 数/时/位/卦动态 | 时序变化结构 |
| 易经 | 卦爻辞解释层 | 哲理指引 |

---

## 七、改进建议

### P0（立即处理）
1. 🔴 **补充渊海子平缺失123篇** - 原典覆盖率仅8.9%
2. 🔴 **补全三命通会10个主题** - 主题覆盖率仅33.3%
3. 🔴 **修复测试路径硬编码** - 177个测试错误

### P1（重要）
4. ⚠️ **验证72个盲派证据原文** - 目前100% PENDING
5. ⚠️ **完成Phase 2语义归一化** - 生成semantic_authority_registry.json
6. ⚠️ **完成Phase 3 Feature/Signal Mapping**

### P2（优化）
7. 清理86个根目录未归类文件
8. 添加河洛专属Golden Cases
9. 创建yao_ci_data.py供heluo引用（需确认路径）

---

## 八、产出文件清单

| 文件 | 大小 | 说明 |
|------|------|------|
| `MATERIALS_COLLECTION_SUMMARY.md` | 10.9KB | 本报告 |
| `materials_collection_final.json` | 10.5KB | 结构化JSON |
| `data/evidence/evidence_catalog.json` | 6.7KB | 子平证据总目录 |
| `盲派资料目录清单.json` | 6.1KB | 盲派引擎+证据清单 |
| `heluo_material_inventory.json` | 6.4KB | 河洛引擎+数据清单 |
| `yi_material_catalog.json` | 2.7KB | 易经引擎+数据清单 |

---

## 九、验证结果

```
============================================================
VERIFICATION RESULTS
============================================================
Output files: 6/6 valid ✅
Evidence files (E-*): 1,574 ✅
Classic passages: 10 JSON + 5 MD ✅
Yi YAO_CI: 64 hexagrams, 384 yao ci lines ✅
============================================================
Status: ad-hoc verification PASSED
============================================================
```

---

*收集完成 - 所有五大体系资料证据已整理完毕*
