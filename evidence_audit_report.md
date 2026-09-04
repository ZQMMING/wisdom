# 古籍证据体系审计报告

**审计时间**: 2026-09-03  
**目标目录**: `E:\shuntian\src\tongshu\classic_evidence\`, `E:\shuntian\data\evidence\`, `E:\shuntian\dataset\golden_v1\`

---

## 1. 证据数据来源清单

| 来源目录 | 文件数 | 格式特征 | 状态 |
|---------|--------|---------|------|
| `data/evidence/blind_seg/` | 86 | 极简（仅evidence_id） | ⚠️ 占位符 |
| `data/evidence/di_tian_sui/` | 44 | 完整结构 | ✅ |
| `data/evidence/ziping_zhenquan/` | 32 | 完整结构 | ✅ |
| `data/evidence/yuan_hai_zi_ping/` | 119 | 完整结构 | ✅ |
| `data/evidence/qiong_tong_bao_jian/` | 1,233 | 完整结构 | ✅ |
| `data/evidence/san_ming_tong_hui/` | 37 | 完整结构 | ✅ |
| `data/evidence/reports/` | - | 报告 | - |
| **合计** | **1,644** | - | - |

**golden_cases.json**: 50个案例，518个事件，含A/B两轮语义标注

---

## 2. 各引擎 evidence_producer 职责

| 引擎 | 文件路径 | PREFIX | 职责 |
|------|---------|--------|------|
| BaziEngine | `engines/bazi/evidence_producer.py` | ZP | 四柱天干地支、十神、地支关系、桃花、五行失衡 |
| BlindEngine | `engines/blind/evidence_producer.py` | BL | 宾主判定、体用分析、做功结构、透干十神 |
| HeLuoEngine | `engines/heluo/evidence_producer.py` | HL | 天数地数、先天卦、元堂、后天卦、卦象结构 |
| YiEngine | `engines/yi/evidence_producer.py` | YI | 卦名、卦辞、爻位、爻辞 |
| ZiweiEngine | `engines/ziwei/evidence_producer.py` | ZW | 星曜分布、宫位、三方四正、四化、借星 |

**古典五经证据代理** (classic_evidence/)：
- `dts_agent.py` → 滴天髓：旺衰气势辨证
- `pzzq_agent.py` → 子平真诠：格局成败辨证
- `qtbj_agent.py` → 穷通宝鉴：调候寒暖辨证
- `smth_agent.py` → 三命通会：关系转化辨证
- `yhzp_agent.py` → 渊海子平：基础语义辨证

---

## 3. Golden Cases 字段完整性检查

### golden_cases.json 字段结构
```json
{
  "case_id": "GOLDEN-XXX",
  "gender": "male/female",
  "birth_date": "YYYY-MM-DD",
  "birth_hour": 0-23,
  "source_type": "historical",
  "events": [
    {
      "date": "YYYY-MM-DD",
      "category": "EXAM/JOB_CHANGE/PARENT_DEATH/...",
      "severity": 1-5,
      "description": "...",
      "evidence_grade": "A/B"
    }
  ]
}
```

### 缺失的字段建议
| 字段 | 用途 | 优先级 |
|------|------|--------|
| `timing_precision` | 时间精确度 (exact/approximate) | 中 |
| `source_citation` | 事件出处文献 | 高 |
| `cause_analysis` | 命理因果分析备注 | 低 |

### 语义标注文件 (annotations_round_a/b.json)
- 包含 `direction` 字段：`supportive`, `neutral`, `caution`
- 这些是**标注层的语义方向**，不是Evidence的polarity — **合规**

---

## 4. V13架构合规性检查

### Evidence不能有polarity ✓
- 所有1,644个证据文件均**无 polarity 字段**
- Golden cases events 也**无 polarity 字段**
- 标注文件的 `direction` 是注释层语义，非证据层

### 数据一致性
| 检查项 | 结果 |
|--------|------|
| `source_locator` 完整性 | ⚠️ 1,638个文件缺失字段 |
| `citation.original_text` 非空 | ⚠️ 91个文件为空 |
| `edition_id` 存在率 | 仅73/1638 (4.5%) |
| `source_layer` 分布 | classical_original:129, paraphrase:43, engineering_seed:11, MISSING:1455 |
| `evidence_strength` 分布 | primary:99, secondary:52, tertiary:32, MISSING:1455 |

---

## 5. 发现的问题

### 🔴 严重问题

1. **blind_seg 占位符文件**
   - 86个文件仅含 `{"evidence_id": "..."}` 空壳
   - 无任何 provenance、citation、source_locator
   - 需填充或清理

2. **source_locator 缺失严重**
   - 1,638个文件缺少 `classic`, `section`, `paragraph`, `passage_id`, `source_hash` 等字段
   - 违反 V13 完整 provenance 要求

### 🟡 中等问题

3. **citation.original_text 缺失**
   - 91个文件（主要是blind_seg）原文引用为空

4. **edition_id 覆盖率极低**
   - 仅4.5%文件有edition_id
   - 影响版本追溯

5. **source_layer / evidence_strength 大量MISSING**
   - 1,455个文件缺少这两个字段
   - 影响证据分级

### 🟢 轻微问题

6. **Golden Cases 缺少 source_citation**
   - 事件未标注出处文献，不利于溯源

7. **classic_evidence agents 的 _load_classic_entries() 均为 TODO**
   - 5个agent文件均未实现数据加载逻辑

---

## 6. 改进建议

| 优先级 | 建议 |
|--------|------|
| P0 | 清理或填充 blind_seg 86个空壳文件 |
| P0 | 补全 source_locator 必填字段 (classic, section, paragraph, passage_id, source_hash) |
| P1 | 为所有证据文件补充 citation.original_text |
| P1 | 实现各 agent 的 `_load_classic_entries()` 方法 |
| P1 | 补充 edition_id 和 source_layer / evidence_strength |
| P2 | Golden Cases 增加 source_citation 字段 |
| P2 | 统一时间戳格式（UTC ISO 8601 vs 本地时间） |

---

**审计结论**: 核心数据结构符合V13规范（无polarity），但**数据质量存在严重缺口**，特别是 provenance 链不完整。blind_seg占位符和source_locator缺失是最大风险点。
