"""P0-3.1 交叉验证抽样脚本 — 每部经典10条，覆盖不同类型。

抽样策略（GPT裁决要求）：
- 每部经典 10 条，共 50 条
- 覆盖类型：原文/诗诀/格局/旺衰/调候/十神/体象/用神
- 不能全部随机，要覆盖最危险的数据类型

输出：docs/P0_3_1_CROSS_VALIDATION_REPORT.md + data/p0_3_1_cross_validation_results.json
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, r"D:\shuntian\backend\src")

from tongshu.corpus.adapter import FiveClassicsCorpusAdapter
from tongshu.corpus.validation import CrossValidator

# ============================================================
# 抽样配置：每部经典 10 条，覆盖不同类型
# ============================================================

# 关键：每部经典选择不同类型/不同类别的条目
# 策略：优先选"最危险的数据类型"（诗诀/体象/格局/旺衰/调候），再补充其他

SAMPLE_ENTRY_IDS = {
    # 滴天髓（19条：十干体性10 + 理法9）— 选10条，覆盖十干体性+理法
    "di_tian_sui": [
        "十干体性_甲", "十干体性_乙", "十干体性_壬", "十干体性_癸",
        "通神论_天干", "通神论_地支", "日主衰旺论", "月令提纲论", "用神论", "生克制化_总论",
    ],
    # 子平真诠（23条：格局13 + 用神5 + 月令4）— 选10条，覆盖格局+用神+月令
    "ziping_zhenquan": [
        "正官格", "七杀格", "食神格", "正财格", "正印格",
        "用神_扶抑", "用神_调候", "用神_病药",
        "月令_说明", "月令_透干成格",
    ],
    # 穷通宝鉴（120条：全为调候用神，十天干×十二月）— 选10条，覆盖不同日干不同月
    "qiongtong_baojian": [
        "甲日_寅月", "乙日_卯月", "丙日_午月", "丁日_巳月", "戊日_辰月",
        "己日_未月", "庚日_申月", "辛日_酉月", "壬日_子月", "癸日_亥月",
    ],
    # 三命通会（27条：强弱8 + 六亲6 + 宫位4 + 运年8 + ...）— 选10条，覆盖强弱+六亲+宫位+运年
    "sanming_tonghui": [
        "强弱_得令", "强弱_得地", "强弱_得势", "强弱_身强条件", "强弱_身弱条件",
        "六亲_父母", "年柱", "月柱",
        "运年_起大运", "运年_太岁并冲",
    ],
    # 渊海子平（187条：十神/体象/论法/诗诀/总论）— 选10条，覆盖十神+体象+论法+诗诀+总论
    "yuanhai_ziping": [
        "十神_心印口诀_162", "论法_论 五 行 生 剋 制 化_2", "论法_论 月 令_4",
        "天干体象_甲_11", "地支体象_子_22",
        "诗诀_诗诀_44", "诗诀_诗诀_35",
        "总论_玄 机 赋_168", "总论_喜 忌 篇_148", "总论_四 言 独 步_179",
    ],
}


def main():
    print("=== P0-3.1 交叉验证抽样 ===")

    # 加载 Corpus
    adapter = FiveClassicsCorpusAdapter()
    adapter.load()

    # 创建验证器
    validator = CrossValidator(adapter)

    # 收集抽样条目
    all_entries = {e.entry_id: e for e in adapter.get_all_entries()}
    sample_entries = []
    missing = []

    for classic_id, entry_ids in SAMPLE_ENTRY_IDS.items():
        for eid in entry_ids:
            if eid in all_entries:
                sample_entries.append(all_entries[eid])
            else:
                missing.append((classic_id, eid))

    print(f"抽样条目: {len(sample_entries)} 条")
    if missing:
        print(f"缺失条目: {len(missing)}")
        for cid, eid in missing:
            print(f"  [{cid}] {eid} 未找到")

    # 执行验证
    results = validator.validate_entries(sample_entries)

    # 汇总
    summary = validator.get_summary(results)
    print(f"\n=== 验证汇总 ===")
    print(f"总数: {summary['total']}")
    print(f"按状态: {summary['by_status']}")
    print("\n按经典:")
    for cid, stats in summary["by_classic"].items():
        print(f"  {cid}: total={stats['total']}, {stats['by_status']}")

    # 输出详细结果
    print("\n=== 详细结果 ===")
    for r in results:
        status_mark = {"EXACT_MATCH": "✅", "PARTIAL_MATCH": "🟡", "NOT_FOUND": "❌", "CONFLICT": "⚠️"}.get(
            r.verification_status, "❓")
        frag = r.original_text[:30] + "..." if len(r.original_text) > 30 else r.original_text
        print(f"  {status_mark} [{r.classic_name}] {r.entry_id}")
        print(f"     状态: {r.verification_status} | 命中: {r.matched_passage_id or '-'}")
        print(f"     原文: {frag}")

    # 保存结果
    results_data = {
        "generated": "2026-08-30",
        "summary": summary,
        "results": [r.to_dict() for r in results],
    }
    data_dir = Path(r"D:\shuntian\backend\data")
    data_dir.mkdir(exist_ok=True)
    results_path = data_dir / "p0_3_1_cross_validation_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存: {results_path}")

    # 生成报告
    generate_report(results_data, results, adapter)

    return results, summary


def generate_report(results_data, results, adapter):
    """生成 Markdown 报告。"""
    summary = results_data["summary"]
    lines = []
    lines.append("# P0-3.1 交叉验证报告（工程事实，非裁决）")
    lines.append("")
    lines.append("> **本报告只陈述验证事实，不包含裁决结论。** 裁决由 AI 审计者（GPT）基于 GitHub commit 审阅后作出。")
    lines.append("> **验证对象**: FOR-BAZI Corpus 候选证据 vs 顺天权威原书（段落数据 JSON）")
    lines.append("> **验证日期**: 2026-08-30")
    lines.append("")
    lines.append("## 一、验证方法")
    lines.append("")
    lines.append("- **候选源**: FOR-BAZI 五经 JSON（`D:/today/Canonical-Mining/FOR-BAZI五书JSON/`）")
    lines.append("- **权威源**: 顺天段落数据 JSON（`D:/today/Canonical-Mining/五部经典完整数据/*_段落数据.json`），每部经典整合多来源")
    lines.append("- **规范化**: 去空白/去标点/繁简归一后比对")
    lines.append("- **验证状态**: EXACT_MATCH（覆盖率≥95%）/ PARTIAL_MATCH（≥30%）/ NOT_FOUND（<30%）/ DERIVED_TEXT（FOR-BAZI无原文，从其他字段构建）/ CONFLICT")
    lines.append("- **抽样规模**: 每部经典 10 条，共 50 条，覆盖不同类型")
    lines.append("")
    lines.append("## 二、验证结果汇总")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|---|---|")
    lines.append(f"| 总数 | {summary['total']} |")
    for status, count in summary["by_status"].items():
        lines.append(f"| {status} | {count} |")
    lines.append("")
    lines.append("### 按经典")
    lines.append("")
    lines.append("| 经典 | 总数 | EXACT | PARTIAL | NOT_FOUND | DERIVED | CONFLICT |")
    lines.append("|---|---|---|---|---|---|---|")
    for cid, stats in summary["by_classic"].items():
        bs = stats["by_status"]
        lines.append(f"| {cid} | {stats['total']} | {bs.get('EXACT_MATCH', 0)} | {bs.get('PARTIAL_MATCH', 0)} | {bs.get('NOT_FOUND', 0)} | {bs.get('DERIVED_TEXT', 0)} | {bs.get('CONFLICT', 0)} |")
    lines.append("")
    lines.append("### 按分类")
    lines.append("")
    lines.append("| 分类 | 总数 | EXACT | PARTIAL | NOT_FOUND | DERIVED | CONFLICT |")
    lines.append("|---|---|---|---|---|---|---|")
    for cat, stats in summary["by_category"].items():
        bs = stats["by_status"]
        lines.append(f"| {cat} | {stats['total']} | {bs.get('EXACT_MATCH', 0)} | {bs.get('PARTIAL_MATCH', 0)} | {bs.get('NOT_FOUND', 0)} | {bs.get('DERIVED_TEXT', 0)} | {bs.get('CONFLICT', 0)} |")
    lines.append("")
    lines.append("## 三、关键发现")
    lines.append("")
    # 统计各状态条目
    exact_entries = [r for r in results if r.verification_status == "EXACT_MATCH"]
    notfound_entries = [r for r in results if r.verification_status == "NOT_FOUND"]
    derived_entries = [r for r in results if r.verification_status == "DERIVED_TEXT"]
    lines.append(f"### 3.1 EXACT_MATCH（{len(exact_entries)}条）— 原典逐字验证通过")
    lines.append("")
    lines.append(f"分布在：{', '.join(sorted(set(r.classic_name for r in exact_entries)))}")
    lines.append("说明这些条目的原文在权威原书中逐字命中，可作为候选证据。")
    lines.append("")
    lines.append(f"### 3.2 NOT_FOUND（{len(notfound_entries)}条）— 需重点审查")
    lines.append("")
    lines.append("以下条目在权威原书中未找到逐字命中：")
    lines.append("")
    lines.append("| 条目 | 经典 | 原文 | 可能原因 |")
    lines.append("|---|---|---|---|")
    for r in notfound_entries:
        reason = "FOR-BAZI 原文为现代整理语句，非原典逐字" if r.classic_id == "sanming_tonghui" else "待人工复核"
        lines.append(f"| {r.entry_id} | {r.classic_name} | {r.original_text[:40]}... | {reason} |")
    lines.append("")
    lines.append(f"### 3.3 DERIVED_TEXT（{len(derived_entries)}条）— FOR-BAZI 无原文字段")
    lines.append("")
    lines.append("以下条目在 FOR-BAZI 中无'原文'字段，从其他字段（取格/喜/忌/口诀/断法）构建候选文本，不能作为原典逐字证据：")
    lines.append("")
    for r in derived_entries:
        lines.append(f"- **{r.entry_id}**（{r.classic_name}）：{r.verification_notes}")
    lines.append("")
    lines.append("## 四、逐条验证结果")
    lines.append("")
    for r in results:
        lines.append(f"### {r.entry_id}")
        lines.append("")
        lines.append(f"- **经典**: {r.classic_name} | **分类**: {r.category} | **key**: {r.key}")
        lines.append(f"- **状态**: {r.verification_status}")
        lines.append(f"- **原文**: {r.original_text}")
        lines.append(f"- **出处(FOR-BAZI)**: {r.source}")
        lines.append(f"- **命中段落**: {r.matched_passage_id or '-'} ({r.matched_passage_source or '-'})")
        if r.matched_fragment:
            lines.append(f"- **命中片段**: {r.matched_fragment[:200]}")
        lines.append(f"- **source_hash**: {r.source_hash}")
        lines.append(f"- **备注**: {r.verification_notes}")
        lines.append("")
    lines.append("## 四、待 AI 审计者裁决的问题")
    lines.append("")
    lines.append("1. EXACT_MATCH 的阈值（95%）是否合理？是否需要更严格？")
    lines.append("2. PARTIAL_MATCH 是否需要细分（例如节选差异 vs 版本差异）？")
    lines.append("3. NOT_FOUND 条目是否说明 FOR-BAZI Corpus 存在原文失真？是否需要补正？")
    lines.append("4. source_hash 机制是否足以防止证据漂移？")
    lines.append("5. 下一轮是否需要扩大到全部 376 条验证？")
    lines.append("")

    report_path = Path(r"D:\shuntian\backend\docs\P0_3_1_CROSS_VALIDATION_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"报告已保存: {report_path}")


if __name__ == "__main__":
    results, summary = main()
