# P0-3.0 五经 Corpus 辨证工程化裁决

**裁决日期**: 2026-08-30
**裁决目标**: 利用 FOR-BAZI 五经 Corpus 做候选检索，以现有原书资料/Evidence 做交叉验证，最终把五经辨证工程化
**核心原则**: 先做 Corpus Adapter + Corpus Audit + Evidence Candidate Retrieval，不要一上来继续堆旺衰规则

---

## 一、裁决背景

### 1.1 当前状态

经过 P0-2.9 系列审计，项目已建立：
- ✅ CanonicalState 数据结构（facts/relations/classical_states/qualifiers/unresolved_reasons/provenance）
- ✅ CanonicalStateProducer（从 BaziChart 生产 CanonicalState）
- ✅ DTS 旺衰 10 个 Primitive（DTS-WS-001~010，基于《滴天髓阐微·十七、衰旺》原典）
- ✅ DTS 旺衰 6 条关系规则（REL-001~006）
- ✅ Signal 适配器（基础层 Signal → CanonicalSignal）
- ✅ 旧评分路径调用图审计 + 迁移计划

### 1.2 核心问题

当前辨证工程化的瓶颈：
1. **证据来源单一**：目前主要依赖《滴天髓阐微·十七、衰旺》单一章节
2. **五经未系统利用**：FOR-BAZI 五经 Corpus（滴天髓/子平真诠/穷通宝鉴/三命通会/渊海子平）已结构化，但未接入辨证工程
3. **候选检索能力缺失**：没有工具能根据辨证概念（如"得时""有根""调候"）从五经中自动检索候选证据
4. **交叉验证能力缺失**：没有机制能将 FOR-BAZI Corpus 的候选证据与现有原书资料（完整原典补充/五部经典完整数据）做交叉验证

### 1.3 裁决方向

**不是**继续"凭经验写身强身弱算法"。

**而是**：
1. 建立 Corpus Adapter — 统一读取五经 JSON，提供标准化访问接口
2. 建立 Corpus Audit — 审计五经数据的完整性、质量、覆盖度
3. 建立 Evidence Candidate Retrieval — 根据辨证概念从五经中自动检索候选证据
4. 建立 Cross-Validation — 将候选证据与现有原书资料做交叉验证
5. 最终将五经辨证工程化 — 每一条辨证规则都有五经候选证据 + 交叉验证结果

---

## 二、FOR-BAZI 五经 Corpus 现状

### 2.1 数据位置

- **主目录**: `D:/today/Canonical-Mining/FOR-BAZI五书JSON/`
- **辅助数据**: `D:/today/Canonical-Mining/五部经典完整数据/`（完整全文MD + 段落数据JSON）
- **原始原典**: `D:/today/Canonical-Mining/完整原典补充/`（原始TXT文件）

### 2.2 文件清单

| 文件 | 经典 | 条目数 | 分类 |
|---|---|---|---|
| `di_tian_sui.json` | 滴天髓 | 19 | 十干体性/理法 |
| `ziping_zhenquan.json` | 子平真诠 | - | 格局/用神 |
| `qiongtong_baojian.json` | 穷通宝鉴 | - | 调候用神 |
| `sanming_tonghui.json` | 三命通会 | - | 神煞/格局/十神 |
| `yuanhai_ziping.json` | 渊海子平 | - | 子平基础 |
| `index.json` | 索引 | - | 元数据 |

### 2.3 数据格式（以滴天髓为例）

```json
{
  "source": "滴天髓",
  "version": "2.0",
  "metadata": {
    "author": "京图（传）/ 任铁樵注",
    "total_entries": 19
  },
  "entries": {
    "十干体性_甲": {
      "category": "十干体性",
      "key": "甲",
      "原文": "甲木参天，脱胎要火...",
      "解析": "甲木为纯阳参天之木...",
      "喜忌": "喜：丙丁火...；忌：庚辛金过旺...",
      "出处": "滴天髓·十干体性篇",
      "tags": ["甲", "十干", "体性"]
    }
  }
}
```

### 2.4 数据特点

- ✅ **结构化**: 每条都有 category/key/原文/解析/喜忌/出处/tags
- ✅ **原文保留**: 每条都有原典原文
- ✅ **现代解析**: 每条都有现代解析（可作为语义理解参考，但不能作为原典授权）
- ✅ **标签系统**: 每条都有 tags，可用于关键词检索
- ⚠️ **覆盖度待审计**: 各经典条目数、分类覆盖度需审计
- ⚠️ **原文准确性待验证**: FOR-BAZI 的原文需与原始原典（完整原典补充）做交叉验证

---

## 三、执行计划

### 阶段1：Corpus Adapter（适配器）

**目标**: 建立统一的五经 Corpus 访问接口，屏蔽各经典数据格式差异

**交付物**:
- `src/tongshu/corpus/adapter.py` — 五经 Corpus 适配器
- 统一接口：`load_classic(classic_id)`, `get_entry(entry_id)`, `search_by_tag(tag)`, `search_by_keyword(keyword)`, `get_all_categories()`

**核心功能**:
1. 读取 index.json，获取五经元数据
2. 加载各经典 JSON 文件
3. 统一条目访问接口（屏蔽各经典字段差异）
4. 提供基于 tags/category/keyword 的检索接口
5. 提供原文/解析/喜忌/出处的标准化访问

### 阶段2：Corpus Audit（审计）

**目标**: 审计五经 Corpus 的完整性、质量、覆盖度

**交付物**:
- `docs/P0_3_0_CORPUS_AUDIT_REPORT.md` — Corpus 审计报告
- `scripts/p0_3_0_corpus_audit.py` — 审计脚本

**审计项**:
1. **完整性审计**: 每部经典的条目数、分类数、缺失字段
2. **质量审计**: 原文长度分布、解析质量、tags 覆盖度
3. **覆盖度审计**: 辨证概念（得时/有根/调候/格局/十神/刑冲合害等）在五经中的覆盖情况
4. **原文准确性抽样**: 抽样 10 条，与原始原典（完整原典补充）做交叉验证
5. **重复/冲突检测**: 五经之间是否存在重复条目或冲突说法

### 阶段3：Evidence Candidate Retrieval（证据候选检索）

**目标**: 根据辨证概念从五经中自动检索候选证据

**交付物**:
- `src/tongshu/corpus/retrieval.py` — 证据候选检索引擎
- `docs/P0_3_0_EVIDENCE_RETRIEVAL_DEMO.md` — 检索演示（针对 10 个核心辨证概念）

**核心功能**:
1. **概念→关键词映射**: 建立辨证概念到检索关键词的映射表
   - 得时 → ["得时", "得令", "月令", "当令"]
   - 有根 → ["有根", "通根", "根气", "得地"]
   - 调候 → ["调候", "寒暖", "燥湿", "用神"]
   - 格局 → ["格局", "成格", "败格", "救应"]
   - 十神 → ["十神", "比肩", "劫财", "食神", "伤官", "偏财", "正财", "七杀", "正官", "偏印", "正印"]
   - 刑冲合害 → ["刑", "冲", "合", "害", "会"]
2. **多维度检索**: 支持按 tags/category/原文关键词/解析关键词检索
3. **跨经典检索**: 一次检索返回五经中的所有候选证据
4. **候选证据排序**: 按相关度（标签匹配 > 原文匹配 > 解析匹配）排序
5. **候选证据标准化**: 输出统一格式的候选证据（classic/category/key/原文/出处/tags/匹配度）

### 阶段4：Cross-Validation（交叉验证）

**目标**: 将 FOR-BAZI Corpus 的候选证据与现有原书资料做交叉验证

**交付物**:
- `src/tongshu/corpus/validation.py` — 交叉验证引擎
- `docs/P0_3_0_CROSS_VALIDATION_REPORT.md` — 交叉验证报告

**核心功能**:
1. **原文比对**: 将 FOR-BAZI 的原文与原始原典（完整原典补充）做比对
2. **出处验证**: 验证 FOR-BAZI 条目的出处是否准确
3. **多版本比对**: 同一概念在不同版本原典中的表述差异
4. **验证结果分级**: EXACT_MATCH / PARTIAL_MATCH / NOT_FOUND / CONFLICT
5. **验证报告生成**: 生成每条候选证据的交叉验证结果

### 阶段5：五经辨证工程化（远期）

**目标**: 在 Corpus Adapter + Audit + Retrieval + Cross-Validation 基础上，将五经辨证工程化

**核心原则**:
- 每一条辨证规则都必须有五经候选证据
- 每一条候选证据都必须有交叉验证结果
- 原典明确（EXACT_MATCH）→ CLASSICAL_EXPLICIT
- 原典隐含（PARTIAL_MATCH）→ CLASSICAL_IMPLICIT
- 原典未找到（NOT_FOUND）→ REASONABLE_HYPOTHESIS 或 ENGINEERING_DERIVED
- 原典冲突（CONFLICT）→ SOURCE_CONTESTED，需人工裁决

---

## 四、执行顺序（严格）

```
阶段1: Corpus Adapter（必须先做）
    ↓
阶段2: Corpus Audit（基于Adapter）
    ↓
阶段3: Evidence Candidate Retrieval（基于Adapter + Audit）
    ↓
阶段4: Cross-Validation（基于Retrieval）
    ↓
阶段5: 五经辨证工程化（远期，基于前四阶段）
```

**禁止**:
- ❌ 禁止跳过 Adapter 直接做检索
- ❌ 禁止跳过 Audit 直接信任 Corpus 数据
- ❌ 禁止跳过 Cross-Validation 直接把候选证据当原典授权
- ❌ 禁止一上来继续堆旺衰规则而不做证据基础建设

---

## 五、验收标准

### 阶段1 验收
- [ ] Corpus Adapter 可加载全部 5 部经典 + index
- [ ] 统一接口可访问每条的原文/解析/喜忌/出处/tags
- [ ] 支持按 tags/category/keyword 检索
- [ ] 单元测试覆盖核心功能

### 阶段2 验收
- [ ] 生成 Corpus 审计报告
- [ ] 每部经典的条目数/分类数/缺失字段已统计
- [ ] 辨证概念覆盖度已分析
- [ ] 至少 10 条原文抽样与原始原典做了交叉验证

### 阶段3 验收
- [ ] 证据候选检索引擎可工作
- [ ] 建立至少 10 个核心辨证概念的关键词映射
- [ ] 一次检索可返回五经中的所有候选证据
- [ ] 候选证据按相关度排序
- [ ] 生成检索演示文档

### 阶段4 验收
- [ ] 交叉验证引擎可工作
- [ ] 验证结果分级（EXACT_MATCH/PARTIAL_MATCH/NOT_FOUND/CONFLICT）
- [ ] 生成交叉验证报告
- [ ] 至少 20 条候选证据完成交叉验证

---

## 六、项目治理原则（持续生效）

1. **算准→辨准→解准** — 算层是地基，算错则全错
2. **FROZEN≠PROVEN CORRECT** — 代码冻结不等于计算正确
3. **P6-CALC 仍是最高优先级** — 计算完整性审计不能停
4. **禁止五行计分→强弱** — 禁止 strength_score / root_score
5. **原典授权≠条件成立≠断事结论授权** — 三层必须分离
6. **整体旺衰保持 UNRESOLVED** — 除非有明确原典授权的综合规则
7. **合理≠原典证明** — FOR-BAZI 的解析是现代解释，不能作为原典授权
8. **候选证据≠原典授权** — 候选证据必须经过交叉验证才能升级授权等级

---

## 七、最终裁决

| 项 | 裁决 |
|---|---|
| 执行方向 | 🟢 PASS（先做 Corpus Adapter + Audit + Retrieval，不堆旺衰规则） |
| 数据基础 | 🟢 PASS（FOR-BAZI 五经 Corpus 已结构化，位置明确） |
| 阶段1 Corpus Adapter | ⏳ 待执行 |
| 阶段2 Corpus Audit | ⏳ 待执行 |
| 阶段3 Evidence Candidate Retrieval | ⏳ 待执行 |
| 阶段4 Cross-Validation | ⏳ 待执行 |
| 阶段5 五经辨证工程化 | 🔴 远期（基于前四阶段） |
| 禁止堆旺衰规则 | 🔒 强制 |

**最终裁决**: 🟢 PASS，可以开始执行阶段1。

**核心要求**: 先把"有原书可交叉验证"真正变成工程能力，再谈辨证规则工程化。
