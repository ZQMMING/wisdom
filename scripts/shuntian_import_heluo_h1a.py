# -*- coding: utf-8 -*-
"""H1-A 河图/洛书 研究性入库。

范围:河洛理数(HELUO-LISHU)书/章节/passage/evidence/rule/algorithms/golden/链。
纪律(HL_H1_KICKOFF_AND_RULINGS.md):
  - 印刷版(故宫珍本B)到位前,passage/evidence 恒 PENDING;rule 恒 DRAFT。
  - 本次为"研究性入库"(允许),不升格 verified。
  - golden 为 HL-G-R-xxxx(研究级),禁标 GOLDEN_VERIFIED。

幂等:全部 ON CONFLICT DO UPDATE;JSON 注册表按 id 去重追加。
用法: PYTHONPATH=src python scripts/shuntian_import_heluo_h1a.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "backend" / "src"))

import psycopg2.extras  # noqa: E402
from tongshu.db.config import get_dsn  # noqa: E402

KB = REPO_ROOT / "backend" / "data" / "knowledge"

BOOK_ID = "HELUO-LISHU"

# ---------------------------------------------------------------------------
# 数据定义(H1-A)
# ---------------------------------------------------------------------------
BOOK = {
    "book_id": BOOK_ID, "title": "河洛理数", "edition": "识典古籍电子本 NA09030(研究底稿;印刷版基准=故宫珍本B待核)",
    "author": "陈抟(旧题)", "era": "宋代(旧题陈抟著/邵雍述,明史应选校订)",
    "source_type": "classical_text", "version": "1.0.0", "status": "review",
    "pinned_edition_id": "EDITION-HELUO-LISHU-NA09030", "short_name": "HL",
    "aliases": ["HELUO", "河洛理数"],
}

EDITION = {
    "edition_id": "EDITION-HELUO-LISHU-NA09030", "book_id": BOOK_ID,
    "title": "河洛理数(识典古籍电子本 NA09030,研究底稿)", "pinned": True,
    "commentator": "明·史应选 校订", "commentary_scope": "陈抟著/邵雍述原文 + 明史应选重订",
    "basis": "识典古籍 NA09030 电子化;OCR 未对锁定印刷版(故宫珍本B)逐字复核",
    "basis_verification": "pending_verification",
    "layer_structure": {"classical_original": "陈抟著/邵雍述原文", "commentary": "明史应选重订",
                        "paraphrase": "归一化解读"},
    "excludes": [], "source_type": "classical_text",
    "verification_status": "verified", "status": "review",
    "version": "1.0.0", "note": "研究底稿版本(识典NA09030 lineage=Spec Owner 裁定①识典F 逐字对照研究底稿);身份=公开书目事实;文本未对印刷版复核→basis_verification=pending;印刷版到位后锁新 EDITION 条目",
}

CHAPTERS = [
    {"chapter_id": "HELUO-LISHU-01", "book_id": BOOK_ID, "sequence": 1, "title": "序 大易源流",
     "status": "review", "verification_status": "pending_verification"},
    {"chapter_id": "HELUO-LISHU-02", "book_id": BOOK_ID, "sequence": 2, "title": "河图运行次序",
     "status": "review", "verification_status": "pending_verification"},
    {"chapter_id": "HELUO-LISHU-03", "book_id": BOOK_ID, "sequence": 3, "title": "说河图篇",
     "status": "review", "verification_status": "pending_verification"},
    {"chapter_id": "HELUO-LISHU-04", "book_id": BOOK_ID, "sequence": 4, "title": "洛书运行次序",
     "status": "review", "verification_status": "pending_verification"},
    {"chapter_id": "HELUO-LISHU-05", "book_id": BOOK_ID, "sequence": 5, "title": "说洛书篇",
     "status": "review", "verification_status": "pending_verification"},
    {"chapter_id": "HELUO-LISHU-06", "book_id": BOOK_ID, "sequence": 6, "title": "八卦取象",
     "status": "review", "verification_status": "pending_verification"},
]

# passage: (passage_id, chapter_id, chapter_name, original_text, locator, paraphrase)
PASSAGES = [
    ("P-HL-001", "HELUO-LISHU-01", "序 大易源流",
     "河洛理数卷之一,华山希夷先生陈抟著,康节尧夫先生邵雍述,明覃怀史应选念冲甫重订。一八卦之书,始于伏羲,有画无文,先天之易也。一六十四卦重于文王,卦下有辞,后天之易也。……系辞十传,乃吾夫子所著,兼先后二天而总括之,是谓中天之易也。",
     "识典NA09030 chapter/1m8od60nhc1me 卷之一首(OCR,PENDING)",
     "(待校,paraphrase)《河洛理数》卷之一题署:陈抟著/邵雍述/明史应选重订;述先天(伏羲有画无文)/后天(文王六十四卦系辞)/中天(孔子系辞十传兼总先后天)三易框架。"),
    ("P-HL-002", "HELUO-LISHU-02", "河图运行次序",
     "河图之序,自北而东,左旋而相生。然对待之位,则北方一六水克南方巳午火,西方四九金克东方三八木,而相克者寓乎相生之中,盖造化之理,生而不克,则生者无从而裁制,其河图生克之妙,有如此乎?",
     "识典NA09030 chapter/1m8od60nhc1me(OCR,PENDING)",
     "(待校,paraphrase)河图数序自北而东左旋相生;对待之位(一六北水克二七南火、四九西金克三八东木)相克寓于相生,故河图主生中含制。"),
    ("P-HL-003", "HELUO-LISHU-03", "说河图篇",
     "天一生水,地六成之;地二生火,天七成之;天三生木,地八成之;地四生金,天九成之;天五生土,地十成之。……龙马负图之初,有点,一白六黑,在背近尾,七白二黑,在背近头,三白八黑在背之左,九白四黑在背之右,五白十黑在背之中。羲皇与大挠氏定以:一六在下,合于北而生水,亥子属焉;二七在上,合于南而生火,巳午属焉;三八在左,合于东而生木,寅卯属焉;四九在右,合于西而生金,申酉属焉;五十在中为土,而辰戌丑未属焉。此八字地支之数所由始也。",
     "识典NA09030 chapter/1m8od60nhc1me(OCR,PENDING;校'王火'='生火','昨酒'='申酉')",
     "(待校,paraphrase)河图生成数:天一生水地六成之/地二生火天七成之/天三生木地八成之/地四生金天九成之/天五生土地十成之;地支五行归属=亥子水(一六)、巳午火(二七)、寅卯木(三八)、申酉金(四九)、辰戌丑未土(五十)。此八字地支取数之源。"),
    ("P-HL-004", "HELUO-LISHU-04", "洛书运行次序",
     "洛书之序,自北而西,右转而相克。然对待之位,则东南四九金生西北一六水,东北三八木生西南二七火,而相生者已寓乎相克之中……",
     "识典NA09030 chapter/1m8od60nhc1me(OCR,PENDING)",
     "(待校,paraphrase)洛书数序自北而西右转相克;对待之位(四九金生一六水、三八木生二七火)相生寓于相克,故洛书主克中含生。"),
    ("P-HL-005", "HELUO-LISHU-05", "说洛书篇",
     "夫河龟负书者,非龟也,乃大龟也。其背所有之文……戴九履一,左三右七,二四为肩,六八为足,五十居中。……以一白近尾为坎,二黑在右肩属坤,三绿属震,四碧在左肩属巽,六白近右足属乾,七赤在右属兑,八白近左足属艮,九紫近头属离。五数居中,以维八方,八卦繇是生焉。此神龟出洛之表象也。",
     "识典NA09030 chapter/1m8od60nhc1me(OCR,PENDING)",
     "(待校,paraphrase)洛书九宫方位:戴九履一/左三右七/二四为肩/六八为足/五十居中;配卦=一坎二坤三震四巽五中六乾七兑八艮九离,八卦由此生。"),
    ("P-HL-006", "HELUO-LISHU-06", "八卦取象",
     "乾三连,坤六断,震仰盂,艮覆碗,离中虚,坎中满,兑上缺,巽下断。……乾宫:乾为天、天风姤、天山遁、天地否……",
     "识典NA09030 chapter/1m8od60nhc1me(OCR,PENDING)",
     "(待校,paraphrase)八卦卦象口诀:乾三连坤六断震仰盂艮覆碗离中虚坎中满兑上缺巽下断;并载乾宫所属(乾为天/天风姤/天山遁/天地否等)。"),
]

# claims: (claim_id, passage_id, claim_text)  — evidence.claim_id 的 FK 锚点
CLAIMS = [
    ("CLAIM-HL-001", "P-HL-001", "河洛理数题署为陈抟著/邵雍述/明史应选校订(provenance)"),
    ("CLAIM-HL-002", "P-HL-002", "河图之序自北而东左旋相生,对待之位相克寓乎相生"),
    ("CLAIM-HL-003", "P-HL-003", "河图生数成数:天一生水地六成之…天五生土地十成之;地支归属亥子水一六…辰戌丑未土五十"),
    ("CLAIM-HL-004", "P-HL-004", "洛书之序自北而西右转相克,对待之位相生寓乎相克"),
    ("CLAIM-HL-005", "P-HL-005", "戴九履一左三右七二四为肩六八为足五十居中;一白坎…九紫离,八卦由此生"),
    ("CLAIM-HL-006", "P-HL-006", "八卦取象:乾三连坤六断震仰盂艮覆碗离中虚坎中满兑上缺巽下断"),
]

# evidence: (evidence_id, claim_id, original_text, interpretation)
EVIDENCE = [
    ("E-HL-001", "CLAIM-HL-001",
     "河洛理数卷之一,华山希夷先生陈抟著,康节尧夫先生邵雍述,明覃怀史应选念冲甫重订。",
     "书卷端题署原文;作为版本/作者归属证据,不涉及算法。"),
    ("E-HL-002", "CLAIM-HL-002",
     "河图之序,自北而东,左旋而相生。然对待之位,则北方一六水克南方巳午火,西方四九金克东方三八木,而相克者寓乎相生之中……",
     "河图运行方向与生克关系;HL-01 方位/数序依据。"),
    ("E-HL-003", "CLAIM-HL-003",
     "天一生水,地六成之;地二生火,天七成之;天三生木,地八成之;地四生金,天九成之;天五生土,地十成之。……一六在下,合于北而生水,亥子属焉;二七在上,合于南而生火,巳午属焉;三八在左,合于东而生木,寅卯属焉;四九在右,合于西而生金,申酉属焉;五十在中为土,而辰戌丑未属焉。此八字地支之数所由始也。",
     "河图数系统(HL-01)与地支取数(C-03)的直接原文依据;单者/双者由 C-04 承接。"),
    ("E-HL-004", "CLAIM-HL-004",
     "洛书之序,自北而西,右转而相克。然对待之位,则东南四九金生西北一六水,东北三八木生西南二七火,而相生者已寓乎相克之中……",
     "洛书运行方向与生克;HL-02 方位/数序依据。"),
    ("E-HL-005", "CLAIM-HL-005",
     "戴九履一,左三右七,二四为肩,六八为足,五十居中。……一白近尾为坎,二黑在右肩属坤,三绿属震,四碧在左肩属巽,六白近右足属乾,七赤在右属兑,八白近左足属艮,九紫近头属离。五数居中,以维八方,八卦繇是生焉。",
     "洛书九宫(HL-02)与依洛书取卦(C-05)的直接原文依据。"),
    ("E-HL-006", "CLAIM-HL-006",
     "乾三连,坤六断,震仰盂,艮覆碗,离中虚,坎中满,兑上缺,巽下断。",
     "八卦卦象符号学基础(HL-07 相荡成卦的卦象前提)。"),
]

# rules: (rule_id, passage_id, rule_text, condition, result)
RULES = [
    ("RL-HL-001", "P-HL-003", "河图方位数:一六北水,二七南火,三八东木,四九西金,五十中土。",
     {"scope": "河图数系统"}, {"num_to_place": {"1": "北水", "6": "北水", "2": "南火", "7": "南火",
                                       "3": "东木", "8": "东木", "4": "西金", "9": "西金",
                                       "5": "中土", "10": "中土"}}),
    ("RL-HL-002", "P-HL-003", "河图生成数:天一生水地六成之,地二生火天七成之,天三生木地八成之,地四生金天九成之,天五生土地十成之。",
     {"scope": "河图生成数"}, {"pairs": {"1": "6水", "2": "7火", "3": "8木", "4": "9金", "5": "10土"}}),
    ("RL-HL-003", "P-HL-003", "地支五行归属(河图):亥子水,寅卯木,巳午火,申酉金,辰戌丑未土。",
     {"scope": "地支取数"}, {"branch_wuxing": {"亥子": "水", "寅卯": "木", "巳午": "火",
                                   "申酉": "金", "辰戌丑未": "土"}}),
    ("RL-HL-004", "P-HL-005", "洛书九宫数位:戴九履一,左三右七,二四为肩,六八为足,五十居中。",
     {"scope": "洛书九宫"}, {"lo_shu_grid": {"1": "北", "2": "西南", "3": "东", "4": "东南",
                                  "5": "中", "6": "西北", "7": "西", "8": "东北", "9": "南"}}),
    ("RL-HL-005", "P-HL-005", "依洛书配卦:一坎二坤三震四巽五中六乾七兑八艮九离。",
     {"scope": "依洛书取卦"}, {"num_to_gua": {"1": "坎", "2": "坤", "3": "震", "4": "巽",
                                   "6": "乾", "7": "兑", "8": "艮", "9": "离", "5": "中(寄)"}}),
]

# rule→evidence 溯源映射(rule.source_refs)
RULE_EVIDENCE = {
    "RL-HL-001": ["E-HL-003"], "RL-HL-002": ["E-HL-003"], "RL-HL-003": ["E-HL-003"],
    "RL-HL-004": ["E-HL-005"], "RL-HL-005": ["E-HL-005"],
}

# algorithms: (algorithm_id, name, domain, type, hl_module, status)
ALGORITHMS = [
    ("HL-ALG-001", "河图数系统", "数理", "LUT", "HL-01", "RESEARCHING", "V0.1",
     [{"name": "地支", "type": "branch"}, {"name": "五行方位数", "type": "int"}],
     [{"name": "河图数", "type": "LUT"}],
     [{"book_id": BOOK_ID, "chapter_id": "HELUO-LISHU-03", "page": None}],
     ["RL-HL-001", "RL-HL-002", "RL-HL-003"], ["HL-G-R-0001"]),
    ("HL-ALG-002", "洛书数系统", "数理", "LUT", "HL-02", "RESEARCHING", "V0.1",
     [{"name": "数字", "type": "int 1-9"}],
     [{"name": "九宫位", "type": "LUT"}, {"name": "八卦", "type": "gua"}],
     [{"book_id": BOOK_ID, "chapter_id": "HELUO-LISHU-05", "page": None}],
     ["RL-HL-004", "RL-HL-005"], []),
]

# golden: (case_id, input, expected_hetu, source, status, version)
GOLDEN = [
    ("HL-G-R-0001",
     {"主题": "河图地支五行归属(研究参考)", "输入": "地支亥子/寅卯/巳午/申酉/辰戌丑未"},
     {"五行": {"亥子": "水", "寅卯": "木", "巳午": "火", "申酉": "金", "辰戌丑未": "土"},
      "河图数": {"亥子": [1, 6], "寅卯": [3, 8], "巳午": [2, 7], "申酉": [4, 9], "辰戌丑未": [5, 10]}},
     "识典NA09030 说河图篇(OCR,未对印刷版复核)", "research_reference", "HL-CALC-V0.1"),
]

# links: (link_id, algorithm_id, link_type, passage_id, evidence_id, rule_id, golden_case_id)
LINKS = [
    ("HL-LINK-0001", "HL-ALG-001", "ALGORITHM_PASSAGE", "P-HL-003", None, None, None),
    ("HL-LINK-0002", "HL-ALG-001", "ALGORITHM_RULE", None, None, "RL-HL-001", None),
    ("HL-LINK-0003", "HL-ALG-001", "ALGORITHM_RULE", None, None, "RL-HL-003", None),
    ("HL-LINK-0004", "HL-ALG-001", "ALGORITHM_EVIDENCE", None, "E-HL-003", None, None),
    ("HL-LINK-0005", "HL-ALG-002", "ALGORITHM_PASSAGE", "P-HL-005", None, None, None),
    ("HL-LINK-0006", "HL-ALG-002", "ALGORITHM_RULE", None, None, "RL-HL-005", None),
    ("HL-LINK-0007", "HL-ALG-002", "ALGORITHM_EVIDENCE", None, "E-HL-005", None, None),
    ("HL-LINK-0008", "HL-ALG-001", "ALGORITHM_GOLDEN", None, None, None, "HL-G-R-0001"),
]


# ---------------------------------------------------------------------------
# JSON 注册表更新
# ---------------------------------------------------------------------------
def upsert_registry(rel: str, key: str, item: dict) -> bool:
    path = KB / rel
    d = json.loads(path.read_text(encoding="utf-8"))
    items = d.setdefault("items", [])
    for i, it in enumerate(items):
        if it.get(key) == item[key]:
            items[i] = item
            path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
            return False  # updated
    items.append(item)
    path.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")
    return True  # added


def upsert_registries() -> None:
    print("[registry] books += HELUO-LISHU:",
          upsert_registry("books.json", "book_id", BOOK))
    print("[registry] editions += EDITION-HELUO-LISHU-NA09030:",
          upsert_registry("editions.json", "edition_id", EDITION))
    for c in CHAPTERS:
        print(f"[registry] chapters += {c['chapter_id']}:",
              upsert_registry("chapters.json", "chapter_id", c))
    for pid, cid, cname, text, loc, para in PASSAGES:
        p = {
            "passage_id": pid, "book_id": BOOK_ID, "chapter_id": cid, "sequence": int(pid[-3:]),
            "source_layer": "paraphrase",  # V-5L:pending 期非 verified→paraphrase 层,classical_original.text 留空
            "classical_original": {"text": "", "verification": "pending_verification", "locator": loc},
            "commentary_layers": [], "paraphrase": {"text": para, "locator": loc},
            "source_reference": loc, "edition": "识典NA09030",
            "edition_id": "EDITION-HELUO-LISHU-NA09030",
            "edition_note": "OCR研究底稿。V-5L:pending 期 classical_original.text 留空(宁缺毋假,裁定② OCR 不得占最终原文槽);OCR 全文保留在 DB passages.original_text(pending)+ docs/v40/heluo_research/10_hetu_luoshu.md。印刷版(故宫珍本B)逐字复核后升 verified 再填本槽。",
            "verification_status": "pending_verification", "status": "review",
            "principle_ids": [], "concept_ids": [],
        }
        print(f"[registry] passages += {pid}:",
              upsert_registry("passages.json", "passage_id", p))


# ---------------------------------------------------------------------------
# DB 入库
# ---------------------------------------------------------------------------
def kb_conn():
    dsn = get_dsn().replace("/otcg", "/shuntian_kb")
    return psycopg2.connect(dsn)


def import_db() -> None:
    conn = kb_conn()
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT EXISTS (SELECT 1 FROM information_schema.tables "
                "WHERE table_schema='public' AND table_name='hl_algorithms')")
    if not cur.fetchone()[0]:
        print("[db] 河洛三补表缺失,先执行: python scripts/shuntian_hl_schema.py migrate")
        conn.close()
        sys.exit(1)

    # sources
    cur.execute("""
        INSERT INTO sources (source_id, title_zh, author_or_attribution, claimed_author,
            dynasty, edition_source, source_type, verification_status, notes)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        ON CONFLICT (source_id) DO UPDATE SET
            title_zh=EXCLUDED.title_zh, verification_status=EXCLUDED.verification_status,
            updated_at=now()
    """, (BOOK_ID, BOOK["title"], "陈抟(旧题)/邵雍(述)", "陈抟",
          "宋代(旧题)", "识典NA09030电子本(研究底稿)", "classical", "pending",
          "印刷版(故宫珍本B)到位前恒pending;卷之一算法链待逐章录入"))

    # passages
    for pid, cid, cname, text, loc, para in PASSAGES:
        cur.execute("""
            INSERT INTO passages (passage_id, source_id, book_id, chapter_id, chapter_name,
                original_text, source_location, verification_status, confidence,
                source_refs, cross_verified, version_notes, notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s,'pending','medium',%s,false,%s,%s)
            ON CONFLICT (passage_id) DO UPDATE SET
                original_text=EXCLUDED.original_text, source_location=EXCLUDED.source_location,
                verification_status=EXCLUDED.verification_status, updated_at=now()
        """, (pid, BOOK_ID, BOOK_ID, cid, cname, text, loc,
              json.dumps(["识典NA09030"], ensure_ascii=False),
              "OCR研究底稿,印刷版复核前恒PENDING",
              "H1-A 河图洛书;对应文档 docs/v40/heluo_research/10_hetu_luoshu.md"))

    # claims (evidence 链第二环)
    for cid, pid, ctext in CLAIMS:
        cur.execute("""
            INSERT INTO claims (claim_id, passage_id, claim_text, domain, claim_status, source_refs)
            VALUES (%s,%s,%s,'hetu_luoshu','DRAFT',%s)
            ON CONFLICT (claim_id) DO UPDATE SET
                claim_text=EXCLUDED.claim_text, domain=EXCLUDED.domain, updated_at=now()
        """, (cid, pid, ctext, json.dumps(["识典NA09030"], ensure_ascii=False)))

    # evidence (cascade: status 与 passage 一致=pending)
    for eid, cid, orig, interp in EVIDENCE:
        pid = eid.replace("E-HL-", "P-HL-")
        cur.execute("""
            INSERT INTO evidence (evidence_id, source_type, source_id, passage_id, claim_id,
                evidence_type, verification_method, source_location, original_text,
                interpretation, verification_status, confidence,
                cross_verified, source_refs, version_notes)
            VALUES (%s,'passage',%s,%s,%s,'直接引文','OCR研究底稿未核',%s,%s,%s,'pending','medium',
                false,%s,'印刷版复核前恒PENDING')
            ON CONFLICT (evidence_id) DO UPDATE SET
                interpretation=EXCLUDED.interpretation,
                verification_status=EXCLUDED.verification_status, updated_at=now()
        """, (eid, BOOK_ID, pid, cid,
              "识典NA09030 chapter/1m8od60nhc1me", orig, interp,
              json.dumps(["识典NA09030"], ensure_ascii=False)))

    # rules (DRAFT;provenance=classical,链接 passage/claim/evidence)
    for rid, pid, rtext, cond, result in RULES:
        claim = "CLAIM-" + pid[2:]  # P-HL-003 → CLAIM-HL-003
        cur.execute("""
            INSERT INTO rules (rule_id, claim_id, source_id, book_id, passage_id, system, domain,
                rule_text, rule_status, confidence, requires_human_review, provenance,
                condition, result, source_refs, notes)
            VALUES (%s,%s,%s,%s,%s,'hetu_luoshu','KNOWLEDGE',%s,'DRAFT','medium',true,'classical',
                %s,%s,%s,%s)
            ON CONFLICT (rule_id) DO UPDATE SET
                rule_text=EXCLUDED.rule_text, rule_status=EXCLUDED.rule_status,
                condition=EXCLUDED.condition, result=EXCLUDED.result, updated_at=now()
        """, (rid, claim, BOOK_ID, BOOK_ID, pid, rtext,
              json.dumps(cond, ensure_ascii=False), json.dumps(result, ensure_ascii=False),
              json.dumps(RULE_EVIDENCE[rid], ensure_ascii=False),
              "H1-A;主源 docs/v40/heluo_research/10_hetu_luoshu.md;DRAFT 不参与推理"))

    # hl_algorithms
    for (aid, name, domain, atype, mod, status, ver, inp, outp, src, rules_, gold) in ALGORITHMS:
        cur.execute("""
            INSERT INTO hl_algorithms (algorithm_id, algorithm_code, algorithm_name,
                algorithm_domain, algorithm_type, hl_module, input_spec, output_spec,
                source_scope, rule_scope, golden_scope, status, hl_calc_version, description)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (algorithm_id) DO UPDATE SET
                algorithm_name=EXCLUDED.algorithm_name, status=EXCLUDED.status,
                input_spec=EXCLUDED.input_spec, output_spec=EXCLUDED.output_spec,
                source_scope=EXCLUDED.source_scope, rule_scope=EXCLUDED.rule_scope,
                updated_at=now()
        """, (aid, aid, name, domain, atype, mod,
              json.dumps(inp, ensure_ascii=False), json.dumps(outp, ensure_ascii=False),
              json.dumps(src, ensure_ascii=False), json.dumps(rules_, ensure_ascii=False),
              json.dumps(gold, ensure_ascii=False), status, ver,
              f"H1-A 研究态;主源 docs/v40/heluo_research/10_hetu_luoshu.md"))

    # golden (research reference)
    for (gid, inp, exp, src, verstat, ver) in GOLDEN:
        cur.execute("""
            INSERT INTO golden_cases (case_id, input, expected_hetu, source,
                verification_status, version, notes)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (case_id) DO UPDATE SET
                expected_hetu=EXCLUDED.expected_hetu,
                verification_status=EXCLUDED.verification_status, updated_at=now()
        """, (gid, json.dumps(inp, ensure_ascii=False), json.dumps(exp, ensure_ascii=False),
              src, verstat, ver, "研究级案例(HL-G-R),禁标 GOLDEN_VERIFIED"))

    # links
    for (lid, aid, ltype, pid, eid, rid, gid) in LINKS:
        cur.execute("""
            INSERT INTO hl_algorithm_evidence (link_id, algorithm_id, link_type,
                passage_id, evidence_id, rule_id, golden_case_id, source_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (link_id) DO UPDATE SET link_type=EXCLUDED.link_type
        """, (lid, aid, ltype, pid, eid, rid, gid, BOOK_ID))

    conn.close()
    print("[db] H1-A 入库完成: sources 1 / passages 6 / evidence 6 / rules 5 / "
          "algorithms 2 / golden 1 / links 8")


def main() -> None:
    upsert_registries()
    import_db()


if __name__ == "__main__":
    main()
