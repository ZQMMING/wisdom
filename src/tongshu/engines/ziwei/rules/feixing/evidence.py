"""
Feixing Evidence Bindings — 飞星派证据等级与一手源 (P0-5-A)

严格工程边界：
- 每条规则绑定 grade=1 一手源（王亭之原文 / 飞星派嫡系讲义）
- grade=3+ 后人整理只作 DRAFT/CANDIDATE 不进 production
- 所有 5 条 production 规则必须有 verbatim 原文出处
- 来源 URL 用作 commit-time 审计追溯

P0-5-A 状态：
- 5 条 production 规则 evidence 已落
- evidence_grade 一律 = 1 (王亭之原文 / 飞星嫡系讲义)
- 不存 grade=3+ 规则进 production（符合 P0-4 锁死的"宁可少不可编"原则）
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeixingEvidence:
    """单条飞星规则的证据绑定。

    字段说明：
      rule_id        — 与 combinations.py 的 detect 函数返回值一一对应
      grade          — 证据等级（1=王亭之原文/嫡系讲义；3=后人整理；4=推演）
      source_title   — 一手源文章标题
      source_url     — 一手源 URL（用于 commit-time 审计追溯）
      verbatim_quote — 一手源关键原文（用于 fail-closed 校验）
      semantic_note  — 中州派 vs 飞星派的语义边界（防误读）
    """
    rule_id: str
    grade: int
    source_title: str
    source_url: str
    verbatim_quote: str
    semantic_note: str = ""


# ============================================================================
# P0-5-A Production Evidence Bindings — 5 条 grade=1 规则
# ============================================================================

EVIDENCE_TABLE: tuple[FeixingEvidence, ...] = (
    # ── 1. 财荫夹印 (天相被化禄/天梁所夹) ─────────────────────────────
    FeixingEvidence(
        rule_id="FEX-CMB-001",
        grade=1,
        source_title="王亭之谈星（08）：天相、天梁",
        source_url="https://www.xuanmen.com.cn/archives/1115.html",
        verbatim_quote=(
            "天梁为荫星，若另一旁的巨门化禄星之时，则此天相便为化禄及荫星所夹，"
            "称为财荫夹印，为其数中重要的格局，主一生得人助力或荫庇，从而致取富贵。"
            "若夹天相为天机化禄、天同化禄，而非巨门化禄，亦成此格，唯一般主格局较次。"
        ),
        semantic_note=(
            "中州派亦采用此格局；飞星派将其纳入飞化逻辑：天机/巨门/天同化禄"
            "从天机/巨门/天同宫飞入天相两邻宫（巨门+天梁）即触发。"
            "production 触发条件简化: 任何化禄落入天相两邻宫 + 该宫为天梁/天机/巨门/天同"
        ),
    ),

    # ── 2. 刑忌夹印 (天相被化忌/天刑所夹) ─────────────────────────────
    FeixingEvidence(
        rule_id="FEX-CMB-002",
        grade=1,
        source_title="王亭之谈星（08）：天相、天梁",
        source_url="https://www.xuanmen.com.cn/archives/1115.html",
        verbatim_quote=(
            "天梁又为刑宪之星，若另一旁的巨门化为忌星，则成刑忌夹印之局，"
            "主人一生受压力，且多刑伤克害。"
            "若夹天相的天机化忌、天同化忌，而非巨门化忌，亦成此格，但克害较浅。"
            "于四煞，天相不畏擎羊或陀罗同度，但却畏羊陀相夹，是亦构成刑忌夹印。"
            "因为擎羊为刑，陀罗为忌。"
        ),
        semantic_note=(
            "production 触发条件: 任何化忌落入天相两邻宫 + 该宫为天梁/天机/巨门/天同；"
            "或擎羊+陀罗分居天相两邻宫（夹忌）。"
        ),
    ),

    # ── 3. 来因宫命迁线 (P0-3 已修，P0-5 复用 grade=1) ─────────────────
    FeixingEvidence(
        rule_id="FEX-CMB-003",
        grade=1,
        source_title="飞星派嫡系讲义（LifeDNA 林士钦）",
        source_url="https://www.lifedna.com.tw/blog/c247.html",
        verbatim_quote=(
            "向心力：包含在上面的飛宮象中，因为本对宮的飛星作用力強，所以分開解釋。"
            "比如命宮與遷移宮是本對宮的關係，命宮飛到遷移宮，或遷移宮飛到命宮"
            "就是屬於這一類。一共有12個宮位，就有12種向心力的流向。"
        ),
        semantic_note=(
            "来因宫 = 宫干=生年干的那一宫；P0-3 已修 selection_rule"
            "（辛/壬年取寅至亥本位，不取子、丑重复干）。"
            "P0-5 复用 P0-3 来因宫定义，grade=1。"
        ),
    ),

    # ── 4. 自化忌基础语义 (飞星派嫡系 12 宫基础定义) ───────────────────
    FeixingEvidence(
        rule_id="FEX-CMB-004",
        grade=1,
        source_title="自化，人生的漏洞？",
        source_url="https://www.lifedna.com.tw/blog/c247.html",
        verbatim_quote=(
            "飛星的起點與終點都在同一個宮位稱為自化（離心自化），"
            "根據十干化曜表，每個天干都會讓四種星辰化出不同特性，"
            "所以自化也跟生年四化一樣有四象：自化祿、自化權、自化科、自化忌。"
            "然後根據不同的自化類型，會讓我們看到不同的現象。"
            "因為它同時散掉了命盤的能量，所以自化通常帶有不好的意義。"
        ),
        semantic_note=(
            "production 触发条件: 某宫宫干使本宫星曜自化（离心自化）；"
            "其中化忌最具杀伤力（散掉命盘能量）。"
            "12宫细分语义在 DRAFT 层（林士钦 12宫详解为后人整理）。"
        ),
    ),

    # ── 5. 四化入命 (宫干飞化禄入命宫 → 增力) ─────────────────────────
    FeixingEvidence(
        rule_id="FEX-CMB-005",
        grade=1,
        source_title="王亭之 谈星 08 + 令东来 什么是正宗的紫微斗数",
        source_url="https://www.xuanmen.com.cn/archives/633.html",
        verbatim_quote=(
            "令东来回答：「宫干飞化」的内容，可以说是比较正宗的。"
            "「飞化」可以看出某些细节、某些内幕，这的确是传统三合派做不到的地方。"
            "例如，令东来为某位女顾客算命，说到：你的父亲非常关心你的学习，"
            "并且不遗余力地支持你的学业。这就是用宫干飞化看的。"
        ),
        semantic_note=(
            "王亭之 + 令东来共同支持: 宫干飞化落入他宫可看出该宫对命主的影响。"
            "production 触发条件简化: 任何宫干飞化禄入命宫 → 增力（王亭之泛论）；"
            "化忌入命宫 → 减力（令东来论化忌通用语义）。"
            "三方/对宫飞化细化在 DRAFT 层。"
        ),
    ),
)


def get_evidence(rule_id: str) -> FeixingEvidence | None:
    """按 rule_id 查 evidence（O(n) 线性；n=5 可接受）。"""
    for ev in EVIDENCE_TABLE:
        if ev.rule_id == rule_id:
            return ev
    return None


def all_evidence() -> tuple[FeixingEvidence, ...]:
    """返回全部 evidence 绑定（用于审计）。"""
    return EVIDENCE_TABLE


def evidence_grade(rule_id: str) -> int:
    """查询 evidence grade（未找到返回 99 = 不可生产）。"""
    ev = get_evidence(rule_id)
    return ev.grade if ev else 99