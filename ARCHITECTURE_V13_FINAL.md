# 断言层改造最终框架 V13 — 已拍板，不再变更

> 拍板时间：2026-08-28
> 状态：**最终基线，P0-P6按此执行，不再改架构**
> 基于：V11蓝图 + V12方案 + 用户聊天记录工程化设计 + 用户最终拍板补充

---

## 一、不可动摇的硬约束（拍板定死）

1. **不再改引擎** — 子平/盲派/紫微/河洛/易经排盘算法OK，只改中间链路
2. **不再做体系投票** — 互补不比较，不投票、不评分、不多数决、不加权
3. **不让LLM判断** — LLM只负责自然语言表达，不重新算命、不新增断言、不改变direction
4. **不让传统术语直接穿透到用户界面** — 必须经过 Semantic Atom → Modern Concept → Domain → Guidance
5. **EngineEvidence 不能有 polarity/direction** — 只保留事实/数值/结构/位置/时间，方向在Assertion之后才产生
6. **SYSTEM_WEIGHTS彻底删除** — 不保留任何形式的"印证度参考"，避免偷偷变回投票
7. **喜用神走同一条链** — 不另开"喜用神输出系统"，用神事实→Semantic Atom→Mapping→行为指引
8. **AuditFlag冻结** — P0-P4不主动触发反方向审计，等语义原子层稳定后重设计

---

## 二、最终数据链（7层，拍板定死）

```
┌─────────────────────────────┐
│ Deterministic Engine        │
│ 子平/盲派/紫微/河洛/易经    │
└──────────────┬──────────────┘
               │ raw evidence（纯事实）
               ▼
┌─────────────────────────────┐
│ EngineEvidence              │
│ 事实/数值/结构/位置/时间    │
│ （无polarity，无direction） │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ Semantic Atom Layer         │
│ 五行/十神/星曜/四化/卦爻    │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ Canonical Assertion         │
│ domain + semantic + direction│
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ Assertion Cluster           │
│ 同语义证据聚合，不投票       │
│ evidence_count/source_engines│
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ Mapping Layer               │
│ semantic → domain           │
│ element → behavior          │
│ classical → modern          │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ Guidance Composer           │
│ opportunity/caution         │
│ action/avoid                │
└──────────────┬──────────────┘
               ▼
┌─────────────────────────────┐
│ LLM Renderer                │
│ 只负责自然语言表达           │
└─────────────────────────────┘
```

**真正需要重构的就是中间这条：Evidence → Semantic Atom → Assertion → Domain → Guidance**

---

## 三、核心数据结构（拍板定死，P0冻结后不再改）

### 3.1 EngineEvidence（所有引擎统一输出）

```python
class EngineEvidence(BaseModel):
    engine: EngineName          # ZI_PING / BLIND_SCHOOL / ZI_WEI / HE_LUO / YI_JING
    rule_id: str                # 规则ID，稳定不变
    value: Any                  # 原始计算值（事实）
    temporal_scope: TemporalScope  # birth / year / month / day / hour
    attributes: dict[str, Any] = {}  # 附加属性（十神/五行/天干/宫位等）
```

**示例（正确）：**
```json
{
  "engine": "ZI_PING",
  "rule_id": "TEN_GOD_SHANG_GUAN",
  "value": "丙",
  "temporal_scope": "year",
  "attributes": {"ten_god": "伤官", "element": "火", "stem": "丙"}
}
```

**禁止（错误）：**
```json
{"value": "伤官", "polarity": "positive"}  // polarity已废除
```

### 3.2 Canonical Assertion（中间语义资产）

```python
class Assertion(BaseModel):
    assertion_id: str
    subject: str                # case_id
    domain: str                 # CAREER / FINANCE / RELATIONSHIP / ...
    semantic: str               # 语义原子标签（如 OUTPUT_ACTIVATION）
    direction: Literal["supportive", "caution", "neutral"]  # 方向在此层才产生
    intensity: int              # 0-100
    temporal_scope: str
    source_engine: str
    source_rule: str
    evidence: dict              # 追溯到EngineEvidence
```

### 3.3 AssertionCluster（证据聚类，不投票）

```python
class AssertionCluster(BaseModel):
    domain: str
    semantic: str
    assertions: list[Assertion]
    evidence_count: int         # 证据覆盖面，不是可信度投票
    source_engines: list[str]   # 哪些引擎提供了证据
    evidence_types: list[str]   # 哪些类型的证据
    expression_strength: int    # 表达强度，基于证据覆盖面
```

### 3.4 Guidance（最终结构化输出）

```python
class Guidance(BaseModel):
    domain: str
    headline: str
    state: str
    opportunities: list[str]
    cautions: list[str]
    actions: list[str]
    avoid: list[str]
    evidence: list[str]         # rule_id 列表，可追溯
```

---

## 四、废除清单（必须删，拍板定死）

| 废除项 | 位置 | 原因 |
|---|---|---|
| `Confidence.CONFLICTED` | assertion/contract.py | V11已废，反方向=算法错误 |
| `SYSTEM_WEIGHTS` | assertion/topics.py | 互补体系无比重，彻底删除不留参考 |
| `_aggregate_directions_weighted` | assertion/topics.py | 加权投票违背互补原则 |
| 规则 `conclusion.direction` / `conclusion.polarity` | data/rules/*.json | 五行/十神本身无吉凶，最根本错误 |
| 紫微 `JI_STARS/XIONG_STARS` 吉凶计数 | assertion/systems.py | 星曜无绝对吉凶 |
| `Signal.direction` / `Signal.polarity` | reasoning/signal_engine.py | 改为语义原子信号 |
| `EngineEvidence.polarity` | 新增schema时就不加入 | 方向在Assertion层才产生 |
| AuditFlag主动触发 | assertion/audit_report.py | P0-P4冻结，不主动调用 |

---

## 五、各引擎本位输出（V11已落地，保持不变）

| 引擎 | 本位领域 | 输出形态 |
|---|---|---|
| 子平 | 旺衰/格局/用神 | 旺衰判定、格局立格、调候用神、扶抑用神 |
| 紫微 | 星曜/宫位/四化 | 命宫主星、12宫细象、四化飞布、大限流年 |
| 盲派 | 做功/应期 | 做功结构、宾主体用、刑冲合害墓库、应期 |
| 河洛 | 卦象/数理 | 先天卦、元堂、后天卦、大运流年卦 |
| 易经 | 决策/占卜 | 卦辞爻辞、人间道指引、决策建议 |

---

## 六、8个人生维度（Mapping Layer投影目标）

| 维度 | 关注内容 |
|---|---|
| 💼 CAREER 事业 | 工作、职业、职位、项目、能力发挥、创业 |
| 💰 FINANCE 财富 | 收入、资产、投资、资源、财务安排 |
| ❤️ RELATIONSHIP 感情 | 恋爱、婚姻、伴侣、亲密关系、情感状态 |
| 🏠 FAMILY 家庭 | 家庭责任、居住、父母、子女、家庭关系 |
| 👥 SOCIAL 人际 | 朋友、合作、人脉、社交、竞争关系 |
| 🧠 GROWTH 成长 | 学习、自我提升、方向定位、能力发展 |
| 🩺 HEALTH 健康 | 生活节奏、作息、压力管理（非诊断，需医学免责） |
| 🎯 DECISION 决策 | 选择、判断、时机、进退、行动建议 |

---

## 七、喜用神走同一条链（拍板定死，不另开系统）

```
子平计算
    ↓
用神事实（EngineEvidence）
    ↓
Semantic Atom（FIRE_SUPPORT / EARTH_SUPPORT / WATER_EXCESS_CONTROL / METAL_RULE_AWARENESS）
    ↓
Mapping Layer
    ↓
ACTION / ENVIRONMENT / BEHAVIOR
    ↓
现代指引
```

**示例：**
- 传统：喜火、土
- 系统内部：FIRE_SUPPORT + EARTH_SUPPORT + WATER_EXCESS_CONTROL + METAL_RULE_AWARENESS
- 用户：增加行动、输出和创造；加强落地、稳定和长期建设；避免过度停留在信息收集和反复思考；面对规则时善用制度，而不是被制度牵制

---

## 八、P1 语义原子知识库目录（拍板定死）

```
data/
└── semantic_atoms/
    ├── five_elements.json      # 五行→现代语义
    ├── ten_gods.json           # 十神→现代语义
    ├── ziwei_stars.json        # 紫微14主星→现代语义
    ├── transformations.json    # 四化→现代语义
    ├── hexagrams.json          # 卦象→现代语义
    ├── yao.json                # 爻辞→现代语义
    ├── he_luo.json             # 河洛特有语义
    └── modern_concepts.json    # 现代概念词典
```

**翻译链：** 传统计算语言 → Semantic Atom → Modern Concept → Domain → Guidance

---

## 九、执行阶段（拍板定死，一级一级递进，不搞其他）

| 阶段 | 内容 | 验收标准 |
|---|---|---|
| **P0** | 接口统一 + 清除旧方向机制 | 见下方P0验收 |
| **P1** | Semantic Atom 知识库建设 | 8个json文件，覆盖核心术语 |
| **P2** | Rules → Semantic Atoms | 136条规则先核心后边缘，rule_id稳定 |
| **P3** | Signal → Semantic Signal | 废除direction/polarity，改为语义原子 |
| **P4** | Assertion Cluster | 加权投票→维度聚合，evidence_count不投票 |
| **P5** | Mapping + Guidance Composer + Renderer | 维度化界面，可解释链，LLM只润色 |
| **P6** | Golden Dataset / 比赛真题 / 真实案例验证 | 3个命例+比赛题+交叉验证 |

---

## 十、P0 验收标准（拍板定死，4条）

### ① 所有引擎都有统一 Adapter
- ZiPingAdapter
- BlindSchoolAdapter
- ZiWeiAdapter
- HeLuoAdapter
- YiJingAdapter
- 不改各引擎内部计算逻辑，只做输出适配

### ② EngineEvidence schema 冻结
- P1-P6不再随意改变schema
- 无polarity，无direction
- rule_id稳定

### ③ 删除旧方向机制
- SYSTEM_WEIGHTS 删除
- aggregate_directions_weighted 删除
- CONFIDENCE.CONFLICTED 删除
- 旧 polarity / direction 吉凶硬编码删除
- AuditFlag冻结（不主动触发）

### ④ Golden Case 能完整追踪
```
case → engine evidence → rule_id → semantic atom → assertion
```
每一个最终断言都能反查来源。

---

## 十一、证据覆盖面（替代投票的唯一表达方式）

以后表达"这个断言有多少体系提供证据"，**只记录**：
- `evidence_count` — 证据数量
- `source_engines[]` — 哪些引擎
- `evidence_types[]` — 哪些类型

**它表示证据覆盖面，不是"可信度投票"。**

禁止：confidence voting / engine score / majority / weighted direction / 任何形式的评分聚合

---

## 十二、LLM Renderer 严格边界（拍板定死）

LLM Prompt 必须限制死：
1. 将结构化指引转换成自然语言
2. 不得重新计算命盘
3. 不得新增任何输入中不存在的断言
4. 不得改变 direction
5. 不得增加"必然""一定""注定"等确定性预测
6. 不得引用未经提供的命理规则
7. 必须保留 opportunity / caution / action 的区别

**AI负责表达，不负责判断。**

---

*文档结束。此为最终基线，P0-P6按此执行，不再改架构。*
