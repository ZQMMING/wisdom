# -*- coding: utf-8 -*-
"""
PATCH-124: SMTH(三命通会) 34 条候选 Evidence -> SPO Assertion
只处理组织者预筛后的 registries/evidence/smth_patch124_candidates.json 中 34 条候选。
宁漏勿误：仅转结构关系/定义型；案例/歌诀/命例/神煞表/人事断语一律 skip。
输出: registries/assertions/smth_assertions.jsonl (新建, 唯一)
"""
import json, os, sys, collections

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "registries", "assertions", "smth_assertions.jsonl")
CAND = os.path.join(ROOT, "registries", "evidence", "smth_patch124_candidates.json")

ALLOWED_NS = {"SMTH.luck", "SMTH.luck_response", "SMTH.time_modifier", "SMTH.special_reference"}
ALLOWED_TYPE = {"DEFINITION", "CONDITION", "RELATION", "EXCEPTION", "NEGATION"}
ALLOWED_GRADE = {"A", "B"}
ALLOWED_RUNTIME = {"SUPPORT_STATE", "CHANGE_RELATION", "BLOCK_RULE", "CONTEXT_MARKER"}

# 禁线扫描词：岁运改写命局 / 应期断语 / 人事吉凶断语
FORBIDDEN_PRED = ["rewrite", "alters", "alters_natal", "rewrites_natal", "changes_natal",
                  "overwrites", "replaces_natal"]
FORBIDDEN_TEXT = ["发财", "升官", "结婚", "娶妻", "生子", "夭", "富貴", "富贵", "貧賤", "贫贱",
                  "娼", "淫", "克妻", "無子", "无子", "主貴", "主贵", "主賤", "主贱",
                  "耗散", "破家", "破祖", "作丐", "餓死", "橫死", "横死", "伶仃", "別祖宗",
                  "夭折", "顛倒", "佞媚", "狡勇", "飄蓬"]

def A(aid, ev, ns, subj, pred, obj, pos, neg, exc, pol, atype, grade, runtime, htext):
    return {
        "assertion_id": aid,
        "source_evidence": ev,
        "classic": "三命通会",
        "namespace": ns,
        "subject": subj,
        "predicate": pred,
        "object": obj,
        "condition": {"positive": pos, "negative": neg, "exception": exc},
        "polarity": pol,
        "assertion_type": atype,
        "grade": grade,
        "consumer": ["SMTH"],
        "runtime_action": runtime,
        "human_text": htext,
        "audit_status": "CANDIDATE",
    }

AS = [
 A("ASSERT-SMTH-0001", ["SMTH-003-001"], "SMTH.special_reference",
   "正印", "defines",
   "五行之正库(金命见乙丑/木见癸未/火见甲戌/水土见壬辰丙辰)",
   "", "", "", "neutral", "DEFINITION", "A", "SUPPORT_STATE",
   "正印为五行之正库，按命五行对应固定支库：金见乙丑、木见癸未、火见甲戌、水土见壬辰丙辰。"),

 A("ASSERT-SMTH-0002", ["SMTH-003-002"], "SMTH.special_reference",
   "華蓋印", "defines",
   "正印之亚型(如亥卯未局得癸未之类)",
   "", "", "", "neutral", "DEFINITION", "B", "SUPPORT_STATE",
   "華蓋印为正印之一亚型，以亥卯未等局得癸未之类为例。"),

 A("ASSERT-SMTH-0003", ["SMTH-003-003"], "SMTH.special_reference",
   "文章印", "defines",
   "正印之亚型(纳音克身、干神相制或干神制支神合)",
   "", "", "", "neutral", "DEFINITION", "B", "SUPPORT_STATE",
   "文章印为正印之一亚型，由纳音克身、干神相制或干神制支神合而成。"),

 A("ASSERT-SMTH-0004", ["SMTH-003-004"], "SMTH.special_reference",
   "正印", "avoids",
   "刑冲破害",
   "正印逢库基生旺扶助互换禄马贵人并相合", "", "",
   "negative", "RELATION", "A", "CHANGE_RELATION",
   "正印要逢库基扶助互换禄马贵人并相合，最忌刑冲破害。"),

 A("ASSERT-SMTH-0005", ["SMTH-003-009"], "SMTH.special_reference",
   "臨空印", "defines",
   "印落空亡且支无六合",
   "", "", "", "neutral", "DEFINITION", "B", "SUPPORT_STATE",
   "臨空印为正印之一亚型，指印落空亡且支无六合。"),

 A("ASSERT-SMTH-0006", ["SMTH-004-001"], "SMTH.special_reference",
   "德秀", "defines",
   "逐月干支对应(寅午戌月丙丁为德戊癸为秀/申子辰月壬癸戊己为德丙辛甲己为秀/巳酉丑月庚辛为德乙庚为秀/亥卯未月甲乙为德丁壬为秀)",
   "", "", "", "neutral", "DEFINITION", "A", "SUPPORT_STATE",
   "德秀按月令取干：寅午戌月丙丁为德戊癸为秀，申子辰月壬癸戊己为德丙辛甲己为秀，巳酉丑月庚辛为德乙庚为秀，亥卯未月甲乙为德丁壬为秀。"),

 A("ASSERT-SMTH-0007", ["SMTH-008-007"], "SMTH.time_modifier",
   "行运", "modifies",
   "遇羊刃为不利修饰",
   "大运或流年行至羊刃", "", "",
   "negative", "RELATION", "B", "CHANGE_RELATION",
   "行运遇羊刃为不利之运年修饰，仅作引动标记，不改原局结构。"),

 A("ASSERT-SMTH-0008", ["SMTH-009-001"], "SMTH.special_reference",
   "空亡", "defines",
   "旬尽十干不到(有位无禄曰空，有支无干曰亡，如甲子旬无戌亥)",
   "", "", "", "neutral", "DEFINITION", "A", "SUPPORT_STATE",
   "空亡起于旬尽：十干不到为空，有位无禄曰空、有支无干曰亡，如甲子旬遁至十干足而无戌亥。"),

 A("ASSERT-SMTH-0009", ["SMTH-009-003"], "SMTH.special_reference",
   "太岁与日柱", "interacts_with",
   "互换空亡(以实为空则实可映空，以空为空无所映)",
   "", "", "", "neutral", "RELATION", "B", "CHANGE_RELATION",
   "太岁与日柱互在对方旬中空亡为互换空亡，其实空相生之理与普通空亡不同。"),

 A("ASSERT-SMTH-0010", ["SMTH-009-003", "SMTH-009-008"], "SMTH.special_reference",
   "空亡", "is_neutralized_by",
   "六合(合则不能空)",
   "", "", "", "positive", "RELATION", "B", "CHANGE_RELATION",
   "空亡逢合则空亡之力被解，合与空不能并存。"),

 A("ASSERT-SMTH-0011", ["SMTH-009-003"], "SMTH.special_reference",
   "真空亡", "defines",
   "无冲无合",
   "", "", "", "neutral", "DEFINITION", "B", "SUPPORT_STATE",
   "真空亡指柱中既无冲亦无合之空亡。"),

 A("ASSERT-SMTH-0012", ["SMTH-009-004"], "SMTH.special_reference",
   "真空亡", "defines",
   "按旬五行(甲子旬水土/甲戌旬金/甲申旬火土/甲午旬火土/甲辰旬木/甲寅旬水土)",
   "", "", "", "neutral", "DEFINITION", "A", "SUPPORT_STATE",
   "真空亡又按旬分五行：甲子旬水土、甲戌旬金、甲申旬火土、甲午旬火土、甲辰旬木、甲寅旬水土。"),

 A("ASSERT-SMTH-0013", ["SMTH-009-006"], "SMTH.special_reference",
   "空亡之支", "interacts_with",
   "本命(克命之空亡为忌)",
   "空亡之支克本命干", "", "",
   "negative", "RELATION", "B", "CHANGE_RELATION",
   "空亡之支若克本命干则为忌，与一般空亡相区别。"),

 A("ASSERT-SMTH-0014", ["SMTH-009-008"], "SMTH.special_reference",
   "五行逢空", "corresponds_to",
   "各五行之空象(金空则响/火空则明/水空则清/木空则折/土空则崩)",
   "", "", "", "neutral", "RELATION", "A", "CHANGE_RELATION",
   "五行逢空各有其象：金空则响、火空则明、水空则清、木空则折、土空则崩。"),

 A("ASSERT-SMTH-0015", ["SMTH-009-009"], "SMTH.time_modifier",
   "空亡", "activates_on",
   "运年冲刑(反引动为虚煞)",
   "原局空亡遇大运流年冲刑", "", "同干之支冲之(如壬申冲壬寅)则不引动",
   "neutral", "RELATION", "B", "CHANGE_RELATION",
   "原局空亡遇大运流年冲刑则反被引动为虚煞；唯同干之支冲之则不引动。"),

 A("ASSERT-SMTH-0016", ["SMTH-009-010"], "SMTH.special_reference",
   "截路空亡", "defines",
   "按日干取时表(甲己日见申酉/乙庚见午未/丙辛见辰巳/丁壬见寅卯/戊癸见戌亥)",
   "", "", "", "neutral", "DEFINITION", "A", "SUPPORT_STATE",
   "截路空亡只以日干取时：甲己日见申酉、乙庚见午未、丙辛见辰巳、丁壬见寅卯、戊癸见戌亥，于所遇壬癸水之时为截路。"),

 A("ASSERT-SMTH-0017", ["SMTH-009-011"], "SMTH.special_reference",
   "四大空亡", "defines",
   "按旬所缺五行(甲子甲午旬缺水/甲寅甲申旬缺金)",
   "", "", "", "neutral", "DEFINITION", "A", "SUPPORT_STATE",
   "四大空亡按旬所缺五行：甲子甲午旬独缺水、甲寅甲申旬独缺金，此四旬五行不全。"),

 A("ASSERT-SMTH-0018", ["SMTH-009-011"], "SMTH.time_modifier",
   "行运", "activates",
   "至四大空亡所缺五行处亦为犯",
   "原局不犯四大空亡，行运至所缺水金处", "", "",
   "neutral", "RELATION", "B", "CHANGE_RELATION",
   "原局不犯四大空亡者，行运至所缺之水金处亦引动为犯，仅作运年引动标记，不改本命格局。"),

 A("ASSERT-SMTH-0019", ["SMTH-026-001"], "SMTH.special_reference",
   "天干", "corresponds_to",
   "五脏六腑(甲胆乙肝丙小肠丁心戊胃己脾庚大肠辛肺壬膀胱癸肾，三焦寄壬包络寄癸)",
   "", "", "", "neutral", "DEFINITION", "A", "SUPPORT_STATE",
   "干支配脏腑：甲胆乙肝、丙小肠丁心、戊胃己脾、庚大肠辛肺、壬膀胱癸肾，三焦寄壬、包络寄癸。"),
]

def main():
    # 载入候选 evidence id 集合用于回查
    with open(CAND, "r", encoding="utf-8") as f:
        cands = {c["evidence_id"] for c in json.load(f)}

    errors = []
    used_ev = set()

    for i, a in enumerate(AS, 1):
        # 断言 id 顺编
        exp_id = "ASSERT-SMTH-%04d" % i
        if a["assertion_id"] != exp_id:
            errors.append("id 不顺: %s != %s" % (a["assertion_id"], exp_id))
        # 必填字段
        for k in ["assertion_id","source_evidence","classic","namespace","subject","predicate",
                   "object","condition","polarity","assertion_type","grade","consumer",
                   "runtime_action","human_text","audit_status"]:
            if k not in a:
                errors.append("%s 缺字段 %s" % (exp_id, k))
        # source 回查
        for eid in a["source_evidence"]:
            if eid not in cands:
                errors.append("%s source_evidence 不在候选集: %s" % (exp_id, eid))
            used_ev.add(eid)
        if a["namespace"] not in ALLOWED_NS:
            errors.append("%s namespace 越界: %s" % (exp_id, a["namespace"]))
        if a["assertion_type"] not in ALLOWED_TYPE:
            errors.append("%s type 越界: %s" % (exp_id, a["assertion_type"]))
        if a["grade"] not in ALLOWED_GRADE:
            errors.append("%s grade 越界: %s" % (exp_id, a["grade"]))
        if a["runtime_action"] not in ALLOWED_RUNTIME:
            errors.append("%s runtime 越界: %s" % (exp_id, a["runtime_action"]))
        if a["consumer"] != ["SMTH"]:
            errors.append("%s consumer 越界: %s" % (exp_id, a["consumer"]))
        if a["classic"] != "三命通会":
            errors.append("%s classic 错误" % exp_id)
        if a["audit_status"] != "CANDIDATE":
            errors.append("%s audit_status 错误" % exp_id)
        # 禁线：predicate 不得 rewrite/alter 本命
        if a["predicate"].lower() in [p.lower() for p in FORBIDDEN_PRED]:
            errors.append("%s predicate 踩岁运改写命局线: %s" % (exp_id, a["predicate"]))
        # 禁线：文本禁词
        blob = " ".join([str(a["subject"]), str(a["predicate"]), str(a["object"]),
                         a["condition"]["positive"], a["condition"]["negative"],
                         a["condition"]["exception"], a["human_text"]])
        for w in FORBIDDEN_TEXT:
            if w in blob:
                errors.append("%s 文本含禁词 %r" % (exp_id, w))

    # 写文件
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        for a in AS:
            f.write(json.dumps(a, ensure_ascii=False) + "\n")

    # 统计
    type_c = collections.Counter(a["assertion_type"] for a in AS)
    grade_c = collections.Counter(a["grade"] for a in AS)
    ns_c = collections.Counter(a["namespace"] for a in AS)
    skipped = sorted(cands - used_ev)

    print("=== PATCH-124 SMTH Assertion 生成报告 ===")
    print("总条数:", len(AS))
    print("assertion_type 分布:", dict(type_c))
    print("grade 分布:", dict(grade_c))
    print("namespace 分布:", dict(ns_c))
    print("引用候选 evidence 数:", len(used_ev))
    print("跳过候选数:", len(skipped))
    print("跳过清单:", skipped)
    print("错误:", len(errors))
    for e in errors:
        print("  ERR:", e)
    if errors:
        sys.exit(1)

if __name__ == "__main__":
    main()
