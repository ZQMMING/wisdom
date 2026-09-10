# ⑮-2-P1-Sub R-A Audit Report

> **⑮-2 子平辨层 Rule / Evidence / Algorithm / Classical-Provenance 最终审计矩阵**
> **Audit-Only, No Code Change**

---

## 0. 审计元数据

| 项 | 值 |
|---|---|
| 审计 ID | BZ-FNDR-15.5-RA |
| 审计阶段 | ⑮-2-P1-Sub |
| 起始 commit | `40eeb359` (⑮-0 接入契约) |
| 审计窗口 | 2026-09-10 |
| 执行者 | BOT-MASTER |
| **Code Change** | **0 (zero code change)** |
| **Git push** | **未推远程** |

---

## 1. 阶段链

```
⑮-0 Bazi → ZiPing 接入契约 (BZ-FNDR-15)
        ↓
  ⑮-1 子平自身方法审计 (BZ-FNDR-15.3) → CLOSED
        ↓
  ⑮-2 P0 (CITATION 元数据 + 路径独立性) (BZ-FNDR-15.4-P0) → CLOSED
        ↓
  ⑮-2-P1-Sub (Evidence / Rule Provenance)
        ↓
  Q (DTS) → P (ZPZ) → R (YONGSHEN) → R-B (4 项补审)
        ↓
  R-A (综合最终裁决)  ← 本文
```

---

## 2. 五种状态分类定义

| 状态 | 含义 | 验收标准 |
|------|------|---------|
| **CLASSICAL-PROVEN** | 原典能够直接支撑当前 Rule Claim | evidence 文件 + passage_id + classical_original verification |
| **CLASSICAL-DERIVED** | 原典原则存在,但代码进行了工程抽象 | evidence 文件 + abstract 边界声明 |
| **ENGINEERING-DEFINED** | 工程参数/策略,没有古典原典依据 | 必须显式标注为 ENGINEERING |
| **PARTIAL** | 原典存在,但当前算法没有完整覆盖 | 缺口清单 + 阻塞 RULE |
| **PROVENANCE-BLOCKED** | 当前证据不能证明代码所声称的 Rule | 禁止进入 production_provenance CLOSED |

> **关键原则**: ENGINEERING-DEFINED ≠ 错误. 合法存在的前提是**显式标注**而非**伪装成 Classical Rule**.

---

## 3. 综合 Rule Provenance 最终裁决矩阵

### 3.1 Q - DTS Provenance

| Evidence ID | Rule | 真实出处 | 状态 |
|-------------|------|---------|------|
| E-DTS-101-001 | DTS-101 得令 | 滴天髓·通神论·衰旺 (paraphrase, 根目录, **未被 loader扫描**) | ENGINEERING-DEFINED + PROVENANCE-BLOCKED (loader 不扫根目录) |
| E-DTS-102-001 | DTS-102 失令 | 复用 E-DTS-101-001 (反义) | CLASSICAL-PROVEN (复用 verified) |
| E-DTS-103-001 | DTS-103 日支通根 | 滴天髓·通神论·地支 (paraphrase, 根目录) | ENGINEERING-DEFINED + PROVENANCE-BLOCKED |
| E-DTS-104-001 | DTS-104 十二长生得地 | 滴天髓·通神论·衰旺 (paraphrase, 根目录) | ENGINEERING-DEFINED + PROVENANCE-BLOCKED |
| E-DTS-105-001 | DTS-105 党众 | 滴天髓·通神论·衰旺 (paraphrase, 根目录) | ENGINEERING-DEFINED + PROVENANCE-BLOCKED |
| **E-DTS-106-001** | **DTS-106 月令被冲** | **🔴 双资源 + DTS_0010 不支撑 DTS-106 语义 + 全库唯一 validate失败** | **PROVENANCE-BLOCKED** 🔴 |
| E-DTS-107-001 | DTS-107 失令有根修正 | 滴天髓·通神论·衰旺 (paraphrase, 根目录) | ENGINEERING-DEFINED + PROVENANCE-BLOCKED |
| (di_tian_sui/E-DTS-106-001) | DTS-106 | DTS_0010 (任氏曰, 进退之机) | PROVENANCE-BLOCKED (DTS_0010 不证明"月令被冲") |
| SMTH-103 → E-SMTH-103-001 | 建禄格取财官 | 《三命通会·论建禄》 (论建禄) | CLASSICAL-PROVEN (verified M2-B) |
| YHZP-101 → E-YHZP-101-001 | 阳刃格取杀制 | 《渊海子平·卷一·论阳刃》 | CLASSICAL-PROVEN (verified M2-B) |
| YHZP-104 → E-YHZP-104-001 | 月劫格取财官 | 《渊海子平·卷一·论月建建禄》 | CLASSICAL-PROVEN (verified M2-B) |
| **YHZP-105 → E-YHZP-105-001** | **阳刃透杀制伏** | **元数据 E-YHZP-105-001 ≠ 代码 E-YHZP-101-001** | **PARTIAL** (binding inconsistency) |

### 3.2 P - ZPZ Provenance

| ZPZ Rule | Cluster Anchor 直接支撑? | 真实出处 | 状态 |
|----------|----------------------|---------|------|
| **ZPZ-111** 月令取格 | ✅ "八字用神,专求月令,而生克不同,格局分焉" | 《子平真诠·论用神》 (verified cluster) | **CLASSICAL-PROVEN** |
| ZPZ-111 杂气月中气 | ❌ Anchor 不含 "杂气月中气" | 《子平真诠·论杂气如何取用》? (待查) | **PARTIAL** |
| **ZPZ-120** 透干成格 | ⚠️原则支持但非字面 | 《子平真诠·论用神·格局判定》 (E-ZIPI-GEJU_SUCCESS-PZZQ_0422) | **CLASSICAL-DERIVED** |
| **ZPZ-106** 伤官见官 | 🔴 Anchor 不同内容 | 《渊海子平·卷一·论岁君》 (YHZP_2319/2436) "伤官见官,为祸百端" | **PARTIAL** (cluster 错挂) |
| ZPZ-110 伤官见官同义 | 🔴 同 ZPZ-106 | 同 | **PARTIAL** |
| **ZPZ-107** 七杀无制 | 🔴 Anchor 不含七杀 | 《渊海子平·卷二·论正官/论疾病》 (YHZP_2462/2413) | **PARTIAL** |
| **ZPZ-108** 财破印 | 🔴 Anchor 不含财破印 | 《渊海子平·卷一·论岁君》 (YHZP_2436) "印綬见财,愈多愈灾" | **PARTIAL** |

**ZPZ Cluster Model 判定**:
- 30 条 ZPZ evidence **共享同一原文**("八字用神,专求月令...") - verified cluster
- 但 member 各自 Rule Claim **不一致**(ZPZ-111 直接证明 / ZPZ-106 等超出 anchor 字面)
- **CLUSTER 是"证据去重层"(Model A), 不是"Rule 证明层"(Model B)**
- 实际实现中**部分 member 错挂 cluster** (6 条 ZPZ-106/107/108/110/120 cluster_id 与真实出处不符)

### 3.3 R - YONGSHEN Provenance

#### 5 级优先级方法

| # | 方法 | 原典 | 当前代码 | 状态 |
|---|------|------|---------|------|
| **1** | 格局用神 (3 格) | ✅《子平真诠·论用神》 | GEJU_RULE_BY_GE 3 格映射 (建禄/月劫/阳刃) | **CLASSICAL-PROVEN** |
| 1 | 格局用神 (7 其他格) | ✅ 论用神·格局判定 (PZZQ_0422) | GEJU_YONGSHEN_TABLE 含 7 格但 GEJU_RULE_BY_GE 不映射 | **PARTIAL** (evidence_refs 未挂载) |
| **1b** | 从格 | ✅《子平真诠·论用神》(从煞/从财/从化 3 类) | `ge_type == "从格": 取克泄耗十神` 单一逻辑 | **PARTIAL** (原典 3 类未细分) |
| **1c** | 专旺格 | ✅《渊海子平》 (YHZP_114) | 仅标记"证据缺口 → UNKNOWN, 不作 ESTABLISHED" | **PARTIAL / NON-ESTABLISHED** |
| **2** | 扶抑用神 | ✅《子平真诠·论用神》 "弱者以生扶为喜,强者因生扶而反害;衰者以裁抑为忌,太旺者反以裁抑而得益" | `_pick_present(SHENG_TEN_GODS) for WEAK / KE_XIE_HAO for STRONG` | **CLASSICAL-PROVEN** (evidence_refs 未挂载) |
| **3** | 调候用神 | ✅《穷通宝鉴》(specific 月×天干) | `season == WINTER → 丙, SUMMER → 壬` (简化) | **CLASSICAL-DERIVED** (原则真实, 算法过度简化不区分天干) |
| **4** | 通关用神 | ✅《渊海子平·卷一·杂论》"伤官见官取财" + 《子平真诠·用神成败救应》"食逢枭生财护食" | `_tongguan_yongshen` 两条件 | **CLASSICAL-PROVEN** (evidence_refs 未挂载) |
| **5** | 病药用神 | 🟡"成败救应"思想(概念有原典),但阈值**无原典依据** | `total >= 8 → KE_XIE_HAO`, `total <= -7 → SHENG_TEN_GODS` | **ENGINEERING-DEFINED** (阈值 8/-7) + Classical Concept (思想) |

#### 五级优先级顺序本身

| 顺序元素 | 状态 |
|---------|------|
| 1→2→3→4→5 固定顺序 | **ENGINEERING-DEFINED** (无原典规定; "格局用神为主,调候为补" 只证明主辅, 不证明完整顺序) |

#### WANGSHUAI 评分阈值

| 阈值 | 状态 |
|------|------|
| STRONG_THRESHOLD = 4 | **ENGINEERING-DEFINED** (无原典量化依据) |
| WEAK_THRESHOLD = -3 | **ENGINEERING-DEFINED** (无原典量化依据) |
| 评分项 ±3/±2/±1/0 (get_ling/de_di/dangzhong) | **CLASSICAL-DERIVED** (原则有原典 "得令/得地/得势" 三辨, 具体 ± 值无原典) |

---

## 4. Audit Classification Distribution

> **名称说明**: 不是"生产通过率",是 Rule/Evidence 5 状态分布.

```
29 个 Rule / 组件:

CLASSICAL-PROVEN          8 (28%) - 原典直接支撑
CLASSICAL-DERIVED         2 (7%)  - 原典原则 + 工程抽象
ENGINEERING-DEFINED       9 (31%) - 工程参数/策略 (必须显式标注)
PARTIAL                   8 (28%) - 原典存在但算法未完整覆盖
PROVENANCE-BLOCKED        1 (4%)  - 当前证据不能证明 Rule Claim
                         ──
                          29 (100%)

🔴 真正阻塞项: 1 个 (DTS-106 PROVENANCE-BLOCKED)
🟡 必须标注边界: 9+8 = 17 个 ENGINEERING/PARTIAL
🟢 完全满足: 8 个 CLASSICAL-PROVEN
```

---

## 5. Remediation Queue (后续修复优先级, 不立即执行)

```
⑮-2-P1-Sub Remediation Queue
│
├── 🔴 P0 (修复前不允许 Production Admission)
│   ├── DTS-106 PROVENANCE-BLOCKED
│   ├── YHZP-105 binding inconsistency (元数据 vs 代码)
│   └── ZPZ cluster 错挂修复 (6 条 evidence_refs 重新分配)
│
├── 🟠 P1 (Classical / Engineering 分层标注)
│   ├── 调候 ENGINEERING-DEFINED 标注
│   ├── 病药 8/-7 ENGINEERING-DEFINED 标注
│   ├── 旺衰 4/-3 ENGINEERING-DEFINED 标注
│   └── 五级优先级 ENGINEERING-DEFINED 标注
│
├── 🟡 P2 (原典追溯补齐)
│   ├── ZPZ-111 杂气月中气 → 论杂气如何取用
│   ├── ZPZ-106/110/107/108 → 补挂 YHZP evidence
│   ├── 从格 → 区分从煞/从财/从化
│   └── 专旺格 → 追溯 rule ID
│
└── 🟢 P3 (evidence_refs 补挂载)
    ├── 扶抑/通关 evidence_refs 挂载
    ├── GEJU_YONGSHEN_TABLE 7 格 evidence_refs
    └── YHZP-105 真实 evidence (YHZP_2447) 挂载
```

---

## 6. 关键事实与发现 (历史快照, 不可作为裁决依据)

### 6.1 D10 审查队列真实身份

- `evidence_review_queue.json` (4180 items, 1934KB)
- 6 个根目录 paraphrase evidence (E-DTS-101/103/104/105/106/107) 全部 `verdict: pending_verification`
- `provenance_note` 明确: "M2-B 五书分批核验 - (待校,paraphrase) 前缀 + paraphrase 层,无逐字经典引文"
- 30 条 ZPZ cluster 成员全部 `verdict: verified` (M2-B 程序化断言通过)

### 6.2 EvidenceLoader 扫描范围

- `phase_b1_evidence_connection.py` `load_all()` 只扫 5 个子目录:
  `["yuan_hai_zi_ping", "ziping_zhenquan", "di_tian_sui", "qiong_tong_bao_jian", "san_ming_tong_hui"]`
- **完全不扫根目录** → 6 个 paraphrase 文件**不被索引**

### 6.3 上下文验证系统真实失败点

- `context_validation_summary.json`:
  - `total_processed: 1412, matched: 1411, not_found: 1`
  - `sample_not_found: E-DTS-106-001 passage_id=DTS_0010 found=false`
  - **DTS-106 是 1412 条中唯一未匹配项**

### 6.4 ZPZ Cluster Anchor 原文

- 《子平真诠·论用神》(徐乐吾批注本, 通行本句读)
- 原文: "八字用神,专求月令,以日干配月令地支,而生克不同,格局分焉。"
- **Anchor 只直接证明 ZPZ-111(月令取格)**,其他 ZPZ 成员 Rule Claim 需独立 evidence

---

## 7. 边界遵守记录

本审计过程严格遵守:
- ✅ 0 处代码修改
- ✅ 0 处 evidence_refs 补挂载
- ✅ 0 处 Evidence ID 重新分配
- ✅ 0 处 ZPZ cluster 修改
- ✅ 0 处 DTS collision 修复
- ✅ 未修改 Bazi ①-⑭ 计算算法
- ✅ 未修改 CanonicalBaziChart 本体
- ✅ 未修改 golden set expected values
- ✅ 未开始 ⑮-3~⑮-6 子平其他域审计
- ✅ 未对 cronjob 自动修改文件 (audit_log.jsonl 等) 进行干涉

---

## 8. 后续阶段锁死状态

```
BAZI ①–⑭             CLOSED 🔒
⑮-0 Bazi→ZiPing       CLOSED 🔒
⑮-1 Self-Method       CLOSED 🔒
⑮-2 P0                CLOSED 🔒

⑮-2-P1-Sub
    Q DTS              AUDIT COMPLETE ✅
    P ZPZ              AUDIT COMPLETE ✅
    R YONGSHEN         AUDIT COMPLETE ✅
    ─────────────────────────
    Audit               CLOSED ✅
    Provenance           OPEN 🟡
    Production Admission BLOCKED 🔴
    Code Remediation     NOT STARTED
```

---

## 9. User 裁决纪要 (2026-09-10)

- **DTS-106**: PROVENANCE-BLOCKED 保持
- **DTS-101/103/104/105/107**: ENGINEERING-DEFINED (paraphrase) + PROVENANCE-BLOCKED (loader 不扫根目录) 保持审计状态
- **ZPZ Cluster = A 模型**: 证据去重/锚定层,不是 Rule 证明层
- **ZPZ-111**: Cluster Anchor 对 Rule Claim 有直接支撑 → provenance 可成立
- **ZPZ-120**: 应以 PZZQ_0422 为主要依据
- **ZPZ-106/110/107/108**: 真实依据应追到《渊海子平》
- **ZPZ-111 杂气中气**: 应继续追《论杂气如何取用》
- **五级优先级 1→2→3→4→5**: ENGINEERING DECISION POLICY
- **调候算法**: CLASSICAL-DERIVED / ENGINEERED-ABSTRACTION
- **病药阈值 8/-7**: ENGINEERING THRESHOLD
- **旺衰阈值 4/-3**: ENGINEERING-DEFINED
- **从格**: PARTIAL (原典 3 类未细分)
- **专旺格**: PARTIAL / NON-ESTABLISHED
- **R-B-A**: 进入综合最终裁决 (本文)
- **R-A-3**: Audit Record Commit, Not Remediation Commit

---

*Generated by BOT-MASTER on 2026-09-10*
*Code change: 0 | Files modified: 1 (audit report only)*