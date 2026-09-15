# PATCH-002 Concept 语义隔离方案（2026-09-16 · 修订版 v2）

> 依据：PATCH-001 §12/§13 + Human 裁决 2026-09-16（方向成立，证据须逐条重新钉死）
> **修订原因**：v1 报告直接从 OCR 文本提取关键词、未区分 text_layer 与章节语境，违反「证据链只准古书原文逐字」铁律。Human 指出后全量重查。
> 关键升级：**Concept 隔离必须到「章节/Rule 语境」层，不能只到「书籍」层**——滴天髓反局篇内部「印旺」尚分君赖臣生/儿能生母/母慈灭子三种子语境。

---

## 一、同词异义审计（修订版 · 证据逐条钉死）

### 1.1 「印旺」六部证据钉死表（text_layer + 章节 + 可靠等级）

| 引擎 | 章节 | source_id | text_layer | 原文铁证 | 语义 | 状态 |
|---|---|---|---|---|---|---|
| DTS | 六親論·反局 | DTS-045-001 | **ORIGINAL A** | 「君賴臣生理最微，兒能生母洩天機。母慈滅子關頭異」 | 反局总纲（印旺致害） | ✅ 可靠 |
| DTS | 六親論·反局·注 | DTS-045-002 | **ANNOTATION B** | 「木旺謂之慈母，反使火熾而焚滅子」+ 君赖臣/儿能生母细分 | 印旺反局三子语境 | ✅ 可靠（注） |
| DTS | 六親論·何知章·注 | DTS-033-014 | **ANNOTATION B** | 「身弱印輕…元神厚處」（任氏注） | 印轻而有辅=元神厚 | ✅ 可靠（注） |
| DTS | 六親論·何知章 | DTS-033-015 | **UNVERIFIED D** | 「印綬太旺，日主無着落…皆壽歿之人」 | 印太旺→夭 | ⚠️ 待核（非正文对句非注，来源未验） |
| PZZQ | 論用神格局高低 | PZZQ-007-001 | **ORIGINAL A** | 「身強印旺透煞，孤貧…身旺不勞印生」 | 身强印旺反忌 | ✅ 可靠 |
| PZZQ | 論用神格局高低 | PZZQ-007-022 | **ORIGINAL A** | 「身弱逢之，最喜印旺」 | 身弱喜印旺 | ✅ 可靠 |
| QTBJ | 二月丁火 | QTBJ-040-001 | **ORIGINAL A** | 「得印旺殺高大富大貴」 | 调候贵征（特定月干） | ✅ 可靠 |
| QTBJ | 五月戊土 | QTBJ-049-001 | **ORIGINAL A** | 「兩透印旺殺高出將入相」 | 调候贵征（特定月干） | ✅ 可靠 |
| YHZP | 子機賦 | YHZP-138-001 | **ORIGINAL A** | 「身旺印多，喜行財地」 | 身旺印多喜财 | ✅ 可靠 |
| YHZP | 寸金搜髓論 | YHZP-131-001 | **ORIGINAL A** | 「身旺印旺，破財不聚」 | 身旺印旺破财 | ✅ 可靠 |
| SMTH | 卷八·六丁日壬寅時斷 | SMTH-092-007 | **ORIGINAL A** | 「寅午年月身旺，申子辰官旺，亥卯未印旺，俱可言貴」 | 丁巳日壬寅时·年月支三合语境 | ✅ 可靠（网络多源验证） |
| SFTK | 印綬格·補曰 | SFTK-022-010 | **ANNOTATION B**（修正） | 「補曰…印旺遇財乃發」（张楠补注） | 印旺为病财为药 | ⚠️ 注解层，不作 A 级 |
| SFTK | （《崖泉男命赋》引文） | — | **LATER_COMMENTARY** | 「印旺一見財鄉，自然家肥屋潤」 | 印旺见财发（赋文） | ⚠️ 引文归属，不入 Rule |

### 1.2 关键证据修正（v1 错误逐条纠正）

1. **DTS「身弱印輕」**：v1 当 A 级原文 → 实为**何知章·任氏注（ANNOTATION B）**。证据链：注层可作 B 级，**不得作 A 级 Golden**。
2. **DTS「印綬太旺日主無着落」**：v1 当原文 → 实为 DTS-033-015 **UNVERIFIED D**（未验证层）。**待核后才能入证据链**——不能因为「印旺」出现就当原文。
3. **SMTH「亥卯未印旺俱可言貴」**：v1 引错 source_id（072-009）→ 真实出处 **SMTH-092-007（六丁日壬寅時斷·丁巳日壬寅时）**，网络多源（古文岛/汉典古籍/抖音百科）验证一致。语境=**具体日时断语**（丁巳日壬寅时的年月支三合结构），不是泛论。
4. **SFTK「印旺遇財乃發」**：v1 当 A 级原文 → 实为 **SFTK-022-010 補曰（张楠补注，注解层）**；网络查证「印旺一見財鄉」出自**《崖泉男命赋》**（神峰通考引文）。**均不作 A 级**。
5. **SFTK 系统性 text_layer 错误**：176 条「補曰/註/釋」开头条目错标 ORIGINAL/A → **已全量修正为 ANNOTATION/B**（2026-09-16 执行）；91 条「歌/詩」开头登记待批（未机械改）。

### 1.3 滴天髓反局内部细分（Human 裁决核心证据）

DTS-045-002 任氏注（ANNOTATION B）明示三种「印旺」反局子语境：

| 子概念 | 注文 | 判定 |
|---|---|---|
| 君賴臣生 | 「木浮水泛，土止水則生木…皆君賴臣也」 | 印旺需他行制化救 |
| 兒能生母 | 「木被金傷，火尅金則生木…皆兒能生母」 | 食伤救印 |
| 母慈滅子 | 「木旺謂之慈母，反使火熾而焚滅子」 | 印旺过甚反害（**印旺致害**） |

**结论**：同一「印旺」（DTS 反局篇），内部三种子语境——概念隔离必须下沉到 **章节·Rule 语境** 层。

## 二、Concept 隔离机制（修订版：下沉到章节语境）

### 2.1 concept_id 命名升级

```
v1（书籍层）：CONCEPT-<BOOK>-<CONCEPT>
        ↓
v2（章节·Rule 语境层）：CONCEPT-<BOOK>-<CHAPTER>-<CONCEPT>[-<SUBCONCEPT>]
```

示例：
- `CONCEPT-DTS-FANJU-YINWANG-MUCI_MIEZI`（母慈灭子）
- `CONCEPT-DTS-FANJU-YINWANG-JUNLAI_CHENSHENG`（君赖臣生）
- `CONCEPT-DTS-HEZHIZHANG-YINQING`（何知章·印轻·任注）
- `CONCEPT-PZZQ-YONGSHEN-GEJU-YINWANG`（真诠·论用神格局高低·印旺）

### 2.2 concept_registry.json schema（v2）

```json
{
  "concept_id": "CONCEPT-DTS-FANJU-YINWANG-MUCI_MIEZI",
  "book": "滴天髓",
  "engine": "DI_TIAN_SUI",
  "chapter": "六親論·反局",
  "concept": "印旺·母慈滅子",
  "text_layer": "ORIGINAL",
  "evidence_grade": "A",
  "semantic_domain": "反局·印旺致害",
  "state_domain": "CONDITION_STATE",
  "source_ids": ["DTS-045-001", "DTS-045-002"],
  "rule_ids": [],
  "text_evidence": "「母慈滅子關頭異」「木旺謂之慈母，反使火熾而焚滅子」",
  "version": "1.0.0",
  "status": "PENDING"
}
```

字段铁律：
- `text_layer` / `evidence_grade`：**必须与 source 一致**（注层=ANNOTATION/B，正文=ORIGINAL/A，未验证=D）
- `chapter`：必填（章节语境隔离）
- `source_ids`：证据链逐条绑定
- 注层证据的 concept 必须显式标 `text_layer=ANNOTATION`，**不得伪装 ORIGINAL**

### 2.3 引擎执行约束（v2）

1. 派生概念规则必须带 `concept_id`（含章节层级），未注解 → FAIL_CLOSED
2. **同书同词不同章节 = 不同 concept**（如 DTS 反局印旺 ≠ 何知章印轻）
3. 证据等级 A/B/D 分别入 Golden 的等级权重，**D 级（UNVERIFIED）不得入规则**

## 三、8 条印系 Rule → **暂停（Human 裁决）**

不准开发。原因：证据未全部钉死（DTS-033-015 待核、SFTK 注解层、引文归属）。
确认路径：

```
Source → Evidence → Concept → Enum → Rule → Golden
```

每步必须 Human 审批。当前仅完成 Source→Evidence→Concept 审计（本报告）。

## 四、待办（下一批）

- [ ] DTS-033-015「印綬太旺日主無着落」版本核验（UNVERIFIED → 定层）
- [ ] SFTK 91 条「歌/詩」开头 text_layer 待批
- [ ] 三命通会「亥卯未印旺」已钉死（SMTH-092-007）——可作 B/A 级候选
- [ ] 身旺身弱/财官/清浊/化神/从格 概念下一批审计（同法：章节语境 + text_layer 钉死）
- [ ] concept_registry.json 创建（v2 schema）待 Human 批准

## 五、本次执行记录（2026-09-16）

1. SFTK source：176 条注解错标 → ANNOTATION/B 全量修正 ✅
2. PATCH-002 报告 v2 重写（证据钉死表）✅
3. SMTH-092-007 网络多源验证（古文岛/汉典古籍/抖音百科）✅
4. 测试 257 passed ✅
