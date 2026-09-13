# Source 录入规范 v7（预审修订版）
> 预审编号：PRE-2026-0913-010
> 状态：CONDITIONAL_REJECT → 修订中
> 依据：V2.2.2 FINAL §39/§45/Appendix D/L + 第七轮预审意见

---

## 一、版本信息

| 字段 | 值 |
|------|-----|
| 规范版本 | v7.0.0 |
| 生效状态 | NOT_APPROVED |
| 适用阶段 | Phase 3+ |
| 基准 Schema | shared_schema/source.schema.json |
| 基准 Enum | Enum Registry |

---

## 二、六部经典层级映射表（修订 v4）

### 2.1 各经典实际结构

| 经典 | 实际层级结构 | PATH_CODE 示例 | 状态 |
|------|-------------|----------------|------|
| 《渊海子平》 | book→volume→pian→passage | `V-V01/P-LUN_TIAN_GAN` | ✅ 已裁定 |
| 《子平真诠》 | book→volume→chapter→passage | `V-V01/C-01` | ✅ 已裁定 |
| 《滴天髓》 | book→lun→pian→passage | `L-TONGSHEN/P-TIAN_DAO` | ⚠️ GAP-DTS-001（命名待裁定：lun/gang/bu） |
| 《穷通宝鉴》 | book→volume→pian→passage | `V-V00/P-LUN_MU`（卷首）/ `V-V01/P-LUN_JIA_MU`（卷一） | ⚠️ GAP-QTBJ-002（层级待裁定） |
| 《三命通会》 | book→volume→pian→passage | `V-V01/P-LUN_WUXING_SHENGCHENG` | ✅ 已裁定 |
| 《神峰通考》 | book→volume→lei→passage | `V-V01/L-BINGYAO_SHUO_LEI` | ✅ 已裁定 |

### 2.2 source_id 格式（修订 v5）

**禁止在 source_id 中使用中文字符，改为 ASCII 路径编码，PATH_CODE 必须带层级前缀：**

```
格式：<BOOK>-<PATH_CODE>-<PSS>

PATH_CODE = 以层级前缀标识的路径段，段间用 "/" 分隔：
  层级前缀：
    V-  = volume（卷）
    L-  = lun（论，滴天髓/穷通宝鉴）
    C-  = chapter（章，子平真诠）
    P-  = pian（篇）
    L-  = lei（类，神峰通考）※ 与 lun 同前缀，按经典注册表区分

示例：
  YHZP:  V-V01/P-LUN_TIAN_GAN
  PZZQ:  V-V01/C-01
  DTS:   L-TONGSHEN/P-TIAN_DAO
  QTBJ:  V-V00/P-LUN_MU（卷首）或 V-V01/P-LUN_JIA_MU（卷一）
  SMTH:  V-V01/P-LUN_WUXING_SHENGCHENG
  SFTK:  V-V01/L-BINGYAO_SHUO_LEI

PSS = 三位数字段落索引
source_id 完整示例：
  YHZP-V-V01/P-LUN_TIAN_GAN-P007
  PZZQ-V-V01/C-01-P042
  DTS-L-TONGSHEN/P-TIAN_DAO-P128
  SFTK-V-V01/L-BINGYAO_SHUO_LEI-P089
```

**拼音统一规则（消除歧义）：**
- 使用全大写拼音，多音节词内部用下划线分隔
- "说类" 统一编码为 `SHUO_LEI`（不用 `SHULEI`）
- "天干" 编码为 `TIAN_GAN`，"天道" 编码为 `TIAN_DAO`，靠 PATH_CODE 上下文层级前缀区分
- 层级前缀（V-/L-/C-/P-）保证每段可独立解码，无歧义拆解

### 2.3 PATH_CODE 映射规则

```
PATH_CODE 段 = <层级前缀>-<ASCII 编码>
  "卷一"         → "V-V01"
  "论天干"       → "P-LUN_TIAN_GAN"
  "第四章"       → "C-04"
  "通神论"       → "L-TONGSHEN"
  "天道"         → "P-TIAN_DAO"
  "论木"         → "L-LUN_MU"
  "病药说类"     → "L-BINGYAO_SHUO_LEI"
```

**中文名称保留在 source_location.path[] 中，不作为 source_id 的一部分。**

**PATH_CODE 不得在运行时动态生成。必须注册到《六部经典批准版本目录注册表》并逐条写死后方可使用。**

### 2.4 经典层级注册表（已裁定）

| 经典 | 层级映射 | PATH_CODE 编码规则 | 裁定依据 |
|------|---------|-------------------|----------|
| YHZP | book→volume→pian→passage | `V-<VOL>/P-<PIAN_ASCII>` | 原典搜索结果确认，五卷五篇结构 |
| PZZQ | book→volume→chapter→passage | `V-<VOL>/C-<NUM>` | 原典搜索结果确认，四十八章分五卷 |
| DTS | book→lun→pian→passage | `L-<LUN_ASCII>/P-<PIAN_ASCII>` | 见GAP-DTS-001（命名待裁定：lun/gang/bu） |
| QTBJ | book→volume→pian→passage | `V-<VOL>/P-<PASSAGE_PATH>` | 卷首=V00（五行论），卷一至卷四=V01-V04（天干论）⚠️ GAP-QTBJ-002 |
| SMTH | book→volume→pian→passage | `V-<VOL>/P-<PIAN_ASCII>` | 原典搜索结果确认，十二卷篇结构 |
| SFTK | book→volume→lei→passage | `V-<VOL>/L-<LEI_ASCII>` | 原典搜索结果确认，类为同级并列 |

**《穷通宝鉴》详细裁定（v7 新增）：**

```
卷首（独立 volume V00，五行论体系）：
  V-V00/P-LUN_MU      → 论木
  V-V00/P-LUN_HUO     → 论火
  V-V00/P-LUN_TU      → 论土
  V-V00/P-LUN_JIN     → 论金
  V-V00/P-LUN_SHUI    → 论水

卷一至卷四（天干论体系）：
  V-V01/P-LUN_JIA_MU  → 论甲木
  V-V02/P-LUN_YI_MU   → 论乙木
  V-V03/P-LUN_BING_HUO → 论丙火
  V-V04/P-LUN_DING_HUO → 论丁火
```

**注意**：卷首“论木”与卷一“论甲木”为不同层级的 PATH_CODE，前者属于五行论体系，后者属于天干论体系。

**《神峰通考》详细裁定（v7 新增）：**

“病药说类”、“雕枯旺弱四病说类”、“损益生长四药说类”在目录中为**同级并列**关系，均为卷一下的独立 `lei`。

```
SFTK-V-V01/L-BINGYAO_SHUO_LEI-P001
SFTK-V-V01/L-DIAOKU_WANGRUO_SI_BING-P001
SFTK-V-V01/L-SUNYI_SHENGCHANG_SI_YAO-P001  ← 原文写作"损益生长四药说类"，编码使用 SHENGCHANG
```

### 2.5 层级结构 GAP 项（v7 修订）

**GAP-QTBJ-001（穷通宝鉴 层级结构）→ CLOSED**

已裁定：卷首=V00（五行论体系），卷一至卷四=V01-V04（天干论体系）。详见 §2.4。

**GAP-SFTK-001（神峰通考 "类"的层级关系）→ CLOSED**

已裁定："病药说类"、"雕枯旺弱四病说类"、"损益生长四药说类"为同级并列，非父子关系。详见 §2.4。

**GAP-QTBJ-002（穷通宝鉴 细层级结构）→ OPEN（待 Human Architect 裁定）**

- 问题：卷首"论五行"下，"五行总论"与"论木"并列；卷一"论甲木"下，"甲木总论"与"三春甲木"并列
- 待裁定：① "论五行"/"论甲木"是否为独立 `lun` 层 ② "五行总论"/"甲木总论"是否与季节篇并列
- 两种可能方案：
  - 方案A（两级）：`V-V00/P-LUN_MU` / `V-V01/P-LUN_JIA_MU`（当前裁定）
  - 方案B（三级）：`V-V00/L-WUXING/P-LUN_MU` / `V-V01/L-LUN_JIA_MU/P-SAN_CHUN_JIA_MU`
- 状态：OPEN，blocked_phase=Phase 3
- 建议 Human Architect 对照已批准版本逐条裁定后写入注册表

**GAP-DTS-001（滴天髓 纲层命名）→ OPEN（待 Human Architect 终审）**

- 问题："通神论/六亲论"应命名为 `lun`（论）、`gang`（纲）还是 `bu`（部）？
- 预审建议：选 B（`G-TONGSHEN`，纲）更准确反映两大部分为"纲"级结构
- **状态**：等待 Human Architect 终审裁定，裁定前全文使用 `L-TONGSHEN` 并标注 `⚠️ GAP-DTS-001`
- 裁定后统一全文命名，`ENUM-SOURCE-PATH-LEVEL` 如需增加 `gang` 同步更新

---

## 三、章节切分规则

### 3.1 权威切分基准

**禁止以 Markdown `#` 标题行作为权威切分依据。**

**必须**以 Human Architect 批准的《六部经典批准版本目录注册表》为基准，按各经典自身层级切分。

### 3.2 passage 定义

- 一个 passage = 一个语义完整的经典陈述单元
- 最小单位：一个完整句子（以句号/分号/换行分隔）
- 最大单位：一个完整段落（不跨段落）
- 每个 passage 必须绑定**冻结文件 hash** 与 **行号范围**

---

## 四、ID 体系（修订 v4）

### 4.1 唯一 ID 定义

| ID 类型 | 格式 | 示例 | 职责 |
|---------|------|------|------|
| **source_id** | `<BOOK>-<PATH_CODE>-<PSS>` | YHZP-V-V01/P-LUN_TIAN_GAN-P007 | Source Record 唯一标识（主键，ASCII） |
| **resource_id** | `SRC-<source_id>` | SRC-YHZP-V-V01/P-LUN_TIAN_GAN-P007 | 资源引用标识（与 source_id 一一对应） |

**已删除 passage_id**（v4 中默认等于 source_id，无实际意义）。

**Evidence 引用的是 `source_id + source_location`。**

### 4.2 ID 一一对应规则

```
resource_id = "SRC-" + source_id
```

### 4.3 PATH_CODE 使用规则（v6 新增）

**`PATH_CODE` 在 `source_id` 与 `source_location.path[]` 中的使用规则统一如下：**

| 位置 | 使用形式 | 说明 |
|------|---------|------|
| `source_id` | 完整 PATH_CODE（含 `/` 分隔的层级路径段） | 如 `YHZP-V-V01/P-LUN_TIAN_GAN-P007` |
| `source_location.path[]` | 逐段拆分，每段 = `{"level","code","name"}` | `code` = 该段去掉层级前缀的 ASCII 部分 |

示例：

```
source_id = YHZP-V-V01/P-LUN_TIAN_GAN-P007

source_location.path = [
  {"level": "volume", "code": "V01", "name": "卷一"},
  {"level": "pian",   "code": "LUN_TIAN_GAN", "name": "论天干"}
]
```

**规则：`path[].code` 是 PATH_CODE 各段的无层级前缀部分；`path[].level` 必须与 PATH_CODE 段的层级前缀对应（V→volume, L→lun/lei, C→chapter, P→pian）。Validator 可据此交叉校验 source_id 与 source_location 的一致性。**

---

## 五、Source Record 字段规范（修订 v4）

### 5.1 必需字段

```json
{
  "source_id": "YHZP-V-V01/P-LUN_TIAN_GAN-P007",
  "source_version": "1.0.0",
  "source_hash": "<sha256 of source_text>",
  "text_layer": "ORIGINAL|ANNOTATION|LATER_COMMENTARY|UNVERIFIED",
  "evidence_grade": "A|B|C|D",
  "source_location": {
    "book": "渊海子平",
    "path": [
      {"level": "volume", "code": "V01", "name": "卷一"},
      {"level": "pian", "code": "LUN_TIAN_GAN", "name": "论天干"}
    ],
    "passage": "第一段",
    "line_start": 1,
    "line_end": 15,
    "file_hash": "<sha256 of source file>"
  },
  "resource_id": "SRC-YHZP-V-V01/P-LUN_TIAN_GAN-P007",
  "logical_uri": "source://yhzp/vol1/pian_lun_tian_gan/passage_007",
  "relative_path": "sources/yhzp/vol1_pian_lun_tian_gan/passage_007.md",
  "runtime_resolver": "resource://classic/yhzp/vol1/pian_lun_tian_gan",
  "source_text": "...",
  "provenance": {
    "chain": ["SRC-YHZP-V-V01/P-LUN_TIAN_GAN-P007"],
    "completeness": "COMPLETE",
    "gaps": []
  },
  "handling_status": "NEEDS_REVIEW|SPLIT|RESOLVED",
  "approval_status": "CANDIDATE|PENDING_REVIEW|APPROVED|REJECTED|DEPRECATED",
  "approved_by": null,
  "approved_at": null,
  "created_at": "2026-09-13T00:00:00Z",
  "updated_at": null,
  "metadata": {
    "edition": {
      "type": "通行本",
      "source": null,
      "editor": null,
      "year": null
    },
    "collation_note": null
  }
}
```

### 5.2 source_location 嵌套结构（修订 v5）

**改用 path 数组结构，按经典差异化，消除 null 值。**

**`path[].level` 必须注册为 ENUM-SOURCE-PATH-LEVEL（v6 新增）：**

```
ENUM-SOURCE-PATH-LEVEL: volume | chapter | lun | pian | lei
```

```json
"source_location": {
  "book": "渊海子平",
  "path": [
    {"level": "volume", "code": "V01", "name": "卷一"},
    {"level": "pian", "code": "LUN_TIAN_GAN", "name": "论天干"}
  ],
  "passage": "第一段",
  "line_start": 1,
  "line_end": 15,
  "file_hash": "<sha256>"
}
```

**各经典 path 层级：**

| 经典 | path 层级 | 示例 |
|------|----------|------|
| YHZP | volume→pian | `[{"level":"volume","code":"V01","name":"卷一"}, {"level":"pian","code":"LUN_TIAN_GAN","name":"论天干"}]` |
| PZZQ | volume→chapter | `[{"level":"volume","code":"V01","name":"卷一"}, {"level":"chapter","code":"01","name":"论十干十二支"}]` |
| DTS | lun→pian | `[{"level":"lun","code":"TONGSHEN","name":"通神论"}, {"level":"pian","code":"TIAN_DAO","name":"天道"}]` |
| QTBJ | volume→pian（方案A待裁定） | 卷首：`[{\"level\":\"volume\",\"code\":\"V00\",\"name\":\"卷首\"}, {\"level\":\"pian\",\"code\":\"LUN_MU\",\"name\":\"论木\"}]`；卷一：`[{\"level\":\"volume\",\"code\":\"V01\",\"name\":\"卷一\"}, {\"level\":\"pian\",\"code\":\"LUN_JIA_MU\",\"name\":\"论甲木\"}]` ⚠️ GAP-QTBJ-002 |
| SMTH | volume→pian | `[{"level":"volume","code":"V01","name":"卷一"}, {"level":"pian","code":"LUN_WUXING_SHENGCHENG","name":"论五行生成"}]` |
| SFTK | volume→lei | `[{"level":"volume","code":"V01","name":"卷一"}, {"level":"lei","code":"BINGYAO_SHUO_LEI","name":"病药说类"}]` |

### 5.3 text_layer 与 handling_status 正交关系（修订 v4）

**两者正交，不得混用：**

```
text_layer      = 文本来源层级（ORIGINAL / ANNOTATION / LATER_COMMENTARY / UNVERIFIED）
handling_status = 处理流程状态（NEEDS_REVIEW / SPLIT / RESOLVED）
```

### 5.4 text_layer 与 evidence_grade 强绑定（修订 v4）

**封板 Appendix D：ORIGINAL→A, ANNOTATION→B, LATER_COMMENTARY→C, UNVERIFIED→D。**

**不得突破上限：**

```python
TEXT_LAYER_GRADE_MAP = {
    "ORIGINAL": "A",
    "ANNOTATION": "B",
    "LATER_COMMENTARY": "C",
    "UNVERIFIED": "D"
}
```

### 5.5 provenance.completeness 语义定义（新增，修订 v4）

| 值 | 语义 |
|----|------|
| COMPLETE | provenance chain 完整，无可识别缺口 |
| PARTIAL | provenance chain 基本完整，存在非关键缺口 |
| INCOMPLETE | provenance chain 存在关键缺口，无法追溯 |
| UNKNOWN | provenance 状态未知 |

### 5.6 禁止事项

- ❌ 禁止硬编码绝对路径（D:/ C:/ E:/ /srv/ /home/）
- ❌ 禁止 source_id 含中文字符
- ❌ 禁止未拆分混合文本入库
- ❌ 禁止 APPROVED Source 的 text_layer 为 UNVERIFIED
- ❌ 禁止 evidence_grade 突破 text_layer 对应上限
- ❌ 禁止将 handling_status 与 text_layer 混用

---

## 六、text_layer 分类标准（修订 v4）

### 6.1 正式 APPROVED 限制

**APPROVED Source 的 text_layer 必须 ∈ {ORIGINAL, ANNOTATION, LATER_COMMENTARY}**

NEEDS_REVIEW 是 handling_status，不是 text_layer。

### 6.2 分类规则

| text_layer | 判定标准 | evidence_grade | APPROVED 允许 |
|------------|---------|----------------|---------------|
| ORIGINAL | 作者本人原文 | A | ✓ |
| ANNOTATION | 作者正式注解 | B | ✓ |
| LATER_COMMENTARY | 后世解释/现代标点整理 | C | ✓（需标注 edition） |
| UNVERIFIED | 无法判定来源 | D | ✗（仅 CANDIDATE 阶段） |

### 6.3 现代标点本判定（细化 v4）

| 情况 | text_layer | evidence_grade | 处理方式 |
|------|------------|----------------|---------|
| 仅点校、标点、排版，未改动字词语义 | ORIGINAL | A | 必须记录 edition/editor/collation_note |
| 整理者改动字词、增删按语 | LATER_COMMENTARY | C | 拆分后单独入库 |
| 白话翻译 | LATER_COMMENTARY | C | 拆分后单独入库 |
| 无法判定 | UNVERIFIED | D | 进入 Gap Report |

---

## 七、混合文本强制拆分（修订 v4）

### 7.1 handling_status 定义

```
handling_status ∈ {NEEDS_REVIEW, SPLIT, RESOLVED}

NEEDS_REVIEW: 混合文本待处理
SPLIT: 已拆分为多个 Source Record
RESOLVED: 处理完成
```

### 7.2 拆分流程

```
Step 1: 识别混合段落（原文+注解混排）
Step 2: 按文本类型拆分 → 多个 text_layer
Step 3: 分别生成 Source Record（每条有独立 source_id，handling_status=SPLIT）
Step 4: 无法拆分 → Gap Report（gap_type=MIXED_TEXT_UNSPLIT, handling_status=NEEDS_REVIEW）
Step 5: 不得强行入库 UNVERIFIED 混合文本
```

---

## 八、Enum Registry 绑定（修订 v4）

### 8.1 已注册枚举

| Enum ID | 值域 | 说明 |
|---------|------|------|
| ENUM-SOURCE-TEXT-LAYER | ORIGINAL/ANNOTATION/LATER_COMMENTARY/UNVERIFIED | Source 文本层 |
| ENUM-EVIDENCE-GRADE | A/B/C/D | Evidence 质量等级 |
| ENUM-SOURCE-PROVENANCE-COMPLETENESS | COMPLETE/PARTIAL/INCOMPLETE/UNKNOWN | Provenance 完整性（含语义定义） |
| ENUM-SOURCE-APPROVAL-STATUS | CANDIDATE/PENDING_REVIEW/APPROVED/REJECTED/DEPRECATED | 审批状态 |
| ENUM-SOURCE-HANDLING-STATUS | NEEDS_REVIEW/SPLIT/RESOLVED | 处理状态 |
| ENUM-SOURCE-PATH-LEVEL | volume/chapter/lun/pian/lei | source_location.path[].level 层级枚举（v6 新增） |
| ENUM-SOURCE-EDITION-TYPE | 通行本/善本/校勘本/影印本/辑佚本/白话全译/评注本/丛书本 | 版本类型（仅 edition.type 字段受控） |

### 8.2 edition 分层描述（修订 v4）

**edition 不再使用简单字符串，改为分层描述结构：**

```json
"edition": {
  "type": "通行本|善本|校勘本|影印本|辑佚本|白话全译|评注本|丛书本",
  "source": "故宫珍本丛刊|四库存目|钦定四库全书|武陵精装版|...",
  "editor": "徐乐吾|任铁樵|...",
  "year": "2012"
}
```

- `type`：注册为 ENUM-SOURCE-EDITION-TYPE
- `source`/`editor`/`year`：自由文本，由 Human Architect 逐条签核

---

## 九、Portable Path / Runtime Resolver（修订 v4）

### 9.1 resource_id

```
格式：SRC-<source_id>
示例：SRC-YHZP-V-V01/P-LUN_TIAN_GAN-P007
```

**注意**：`resource_id = "SRC-" + source_id`，source_id 含 `/` 分隔符，resource_id 亦保留。

### 9.2 logical_uri

```
格式：source://<book_lower>/<path_slug>/passage_<n>
示例：source://yhzp/vol1/pian_lun_tian_gan/passage_007
```

### 9.3 relative_path

```
格式：sources/<book_lower>/<path_slug>_passage_<n>.md
示例：sources/yhzp/vol1_pian_lun_tian_gan_passage_007.md
```

### 9.4 runtime_resolver

```
格式：resource://classic/<book_code>/<path>
示例：resource://classic/yhzp/vol1/pian_lun_tian_gan
```

---

## 十、时间戳字段（修订 v4）

### 10.1 必需时间戳

```json
{
  "created_at": "2026-09-13T00:00:00Z",
  "updated_at": null,
  "approved_at": null
}
```

### 10.2 状态迁移对应时间戳

| 状态迁移 | 更新时间戳 |
|---------|-----------|
| CREATED → CANDIDATE | created_at |
| CANDIDATE → PENDING_REVIEW | updated_at |
| PENDING_REVIEW → APPROVED | approved_at |
| APPROVED → DEPRECATED | updated_at |

---

## 十一、Human Architect 审批流程（修订 v4）

### 11.1 审批字段

```json
{
  "approval_status": "APPROVED",
  "approved_by": "Human Architect Name",
  "approved_at": "2026-09-13T12:00:00Z",
  "approval_note": "逐条核对原文，text_layer 分类正确",
  "edition_verified": true,
  "hash_verified": true,
  "grade_check": "A=ORIGINAL ✓"
}
```

### 11.2 审批记录

- 每条 Source 记录审批人与审批时间
- 审批批次记录版本号
- 拒绝的 Source 记录原因并归档

---

## 十二、Phase 0 关系说明

本规范适用于 **Phase 3（Source Registry）** 及之后的正式录入。

Phase 0 仅建立基础设施（shared_schema/shared_types/validators），不涉及 Source 数据。

本规范与 shared_schema/source.schema.json 绑定，字段变更需同步更新。

---

## 十三、阻断项检查清单（v7）

### 第五轮阻断项（已全部修复）
- [x] source_id 改为 ASCII 路径编码 + 层级前缀（V-/L-/C-/P-）
- [x] source_location 改为嵌套 path[] 结构，注册 ENUM-SOURCE-PATH-LEVEL
- [x] edition 改为分层描述（type+source+editor+year）
- [x] 删除 passage_id

### 第六轮阻断项（已全部修复）
- [x] GAP-QTBJ-001 直接裁定（卷首V00+卷一至卷四V01-V04）
- [x] GAP-SFTK-001 直接裁定（同级并列）
- [x] provenance.chain 同步 v6 格式
- [x] resource_id §9.1 示例同步 v6 格式

### 第八轮阻断项（已修复）
- [x] 文件重命名为 source_spec_v7.md（原文件名仍为 v6）
- [x] §2.1 表格 QTBJ 层级结构改为 book→volume→pian→passage
- [x] §2.2 QTBJ 示例同步 §2.4 裁定（P-LUN_MU / P-LUN_JIA_MU）
- [x] §5.2 表格 QTBJ 行同步 GAP-QTBJ-001 CLOSED 状态
- [x] §2.4 SFTK "生长" 笔误澄清
- [x] GAP-DTS-001 全文标注待裁定，使用 L-TONGSHEN 暂代
- [x] QTBJ 细层级裁定标记为 GAP-QTBJ-002（OPEN），待 Human Architect 裁定

### 保留项（v4 已确认）
- [x] evidence_grade ≤ text_layer 对应上限（硬绑定）
- [x] D 级证据不得用于正式 APPROVED Rule
- [x] NEEDS_REVIEW 作为 handling_status，不是 text_layer
- [x] APPROVED Source 的 text_layer 限制为 {ORIGINAL, ANNOTATION, LATER_COMMENTARY}
- [x] Portable path / runtime resolver
- [x] source_id 唯一性（ASCII 编码）
- [x] source_id / resource_id 职责区分 + 一一对应
- [x] Human Architect 审批栏
- [x] 时间戳字段（created_at/updated_at/approved_at）
- [x] Enum Registry 绑定（7个枚举）
- [x] 与 Phase 0 关系说明

---

*BOT-CORPUS 修订 | 第八轮预审处理 | 待 Human Architect 终审*
