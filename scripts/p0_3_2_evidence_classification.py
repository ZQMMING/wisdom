"""P0-3.2 五经 Corpus 全量 Evidence Classification。

对 FOR-BAZI 全部 376 条做交叉验证，输出五分类：
- EXACT_PRIMARY：原典逐字原文，权威原书命中（证据等级最高）
- PARTIAL：部分命中，存在版本/节选差异
- DERIVED_TEXT：FOR-BAZI 无"原文"字段，从其他字段构建（隔离，不进入证据池）
- NOT_FOUND：权威原书未找到
- CONFLICT：存在冲突

核心：DERIVED_TEXT 与 EXACT_PRIMARY 彻底隔离。

输出：docs/P0_3_2_EVIDENCE_CLASSIFICATION_REPORT.md + data/p0_3_2_evidence_classification_results.json
"""
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, r"D:\shuntian\backend\src")

from tongshu.corpus.adapter import FiveClassicsCorpusAdapter
from tongshu.corpus.validation import CrossValidator


def main():
    print("=== P0-3.2 全量 Evidence Classification ===")

    adapter = FiveClassicsCorpusAdapter()
    adapter.load()

    validator = CrossValidator(adapter)

    # 全部条目
    all_entries = adapter.get_all_entries()
    print(f"全部条目: {len(all_entries)} 条")

    # 全量验证
    results = validator.validate_entries(all_entries)

    # 汇总
    summary = validator.get_summary(results)
    print(f"\n=== 五分类汇总 ===")
    print(f"总数: {summary['total']}")
    print(f"按证据分类: {summary['by_class']}")
    print(f"按状态: {summary['by_status']}")

    print("\n按经典:")
    for cid, stats in summary["by_classic"].items():
        print(f"  {cid}: total={stats['total']}, by_class={stats['by_class']}")

    # DERIVED_TEXT 隔离检查
    derived = [r for r in results if r.evidence_class == "DERIVED_TEXT"]
    primary = [r for r in results if r.evidence_class == "EXACT_PRIMARY"]
    print(f"\n=== 隔离检查 ===")
    print(f"EXACT_PRIMARY（可用于辨证证据池）: {len(primary)}")
    print(f"DERIVED_TEXT（已隔离，不进入证据池）: {len(derived)}")
    print(f"隔离比例: {len(derived)}/{len(results)} = {len(derived)/len(results):.1%}")

    # 保存结果
    results_data = {
        "generated": "2026-08-30",
        "method": "P0-3.2 全量 Evidence Classification",
        "total": len(results),
        "summary": summary,
        "results": [r.to_dict() for r in results],
    }
    data_dir = Path(r"D:\shuntian\backend\data")
    data_dir.mkdir(exist_ok=True)
    results_path = data_dir / "p0_3_2_evidence_classification_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(results_data, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存: {results_path}")

    # 生成报告
    generate_report(results_data, results)

    return results, summary


def generate_report(results_data, results):
    """生成 Markdown 报告（纯事实，不裁决）。"""
    summary = results_data["summary"]
    lines = []
    lines.append("# P0-3.2 五经 Corpus 全量 Evidence Classification 报告（工程事实，非裁决）")
    lines.append("")
    lines.append("> **本报告只陈述分类事实，不包含裁决结论。** 裁决由 AI 审计者（GPT）基于 GitHub commit 审阅后作出。")
    lines.append("> **分类对象**: FOR-BAZI Corpus 全部 376 条")
    lines.append("> **分类方法**: 与顺天权威原书（段落数据 JSON）交叉验证")
    lines.append("> **分类日期**: 2026-08-30")
    lines.append("")
    lines.append("## 一、五分类定义")
    lines.append("")
    lines.append("| 分类 | 定义 | 证据等级 |")
    lines.append("|---|---|---|")
    lines.append("| EXACT_PRIMARY | 原典逐字原文，权威原书命中 | 最高（可进入证据池） |")
    lines.append("| PARTIAL | 部分命中，存在版本/节选差异 | 中（需交叉验证） |")
    lines.append("| DERIVED_TEXT | FOR-BAZI 无'原文'字段，从其他字段构建 | 隔离（不进入证据池） |")
    lines.append("| NOT_FOUND | 权威原书未找到 | 低（不能作为原典证据） |")
    lines.append("| CONFLICT | 存在冲突 | 需人工复核 |")
    lines.append("")
    lines.append("## 二、全量分类汇总")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|---|---|")
    lines.append(f"| 总数 | {summary['total']} |")
    for cls, count in summary["by_class"].items():
        lines.append(f"| {cls} | {count} |")
    lines.append("")
    lines.append("### 按经典")
    lines.append("")
    lines.append("| 经典 | 总数 | EXACT_PRIMARY | PARTIAL | DERIVED_TEXT | NOT_FOUND | CONFLICT |")
    lines.append("|---|---|---|---|---|---|---|")
    for cid, stats in summary["by_classic"].items():
        bc = stats["by_class"]
        lines.append(f"| {cid} | {stats['total']} | {bc.get('EXACT_PRIMARY', 0)} | {bc.get('PARTIAL', 0)} | {bc.get('DERIVED_TEXT', 0)} | {bc.get('NOT_FOUND', 0)} | {bc.get('CONFLICT', 0)} |")
    lines.append("")
    lines.append("### 按分类")
    lines.append("")
    lines.append("| 分类 | 总数 | EXACT_PRIMARY | PARTIAL | DERIVED_TEXT | NOT_FOUND | CONFLICT |")
    lines.append("|---|---|---|---|---|---|---|")
    for cat, stats in summary["by_category"].items():
        bc = stats["by_class"]
        lines.append(f"| {cat} | {stats['total']} | {bc.get('EXACT_PRIMARY', 0)} | {bc.get('PARTIAL', 0)} | {bc.get('DERIVED_TEXT', 0)} | {bc.get('NOT_FOUND', 0)} | {bc.get('CONFLICT', 0)} |")
    lines.append("")
    lines.append("## 三、DERIVED_TEXT 隔离清单")
    lines.append("")
    lines.append("以下条目被隔离，不进入辨证证据池（FOR-BAZI 无'原文'字段，从其他字段构建，非原典逐字）：")
    lines.append("")
    lines.append("| 条目 | 经典 | 字段来源 |")
    lines.append("|---|---|---|")
    for r in [x for x in results if x.evidence_class == "DERIVED_TEXT"]:
        lines.append(f"| {r.entry_id} | {r.classic_name} | {r.verification_notes[:60]} |")
    lines.append("")
    lines.append("## 四、NOT_FOUND 清单")
    lines.append("")
    lines.append("以下条目在权威原书中未找到逐字命中：")
    lines.append("")
    lines.append("| 条目 | 经典 | 原文 |")
    lines.append("|---|---|---|")
    for r in [x for x in results if x.evidence_class == "NOT_FOUND"]:
        lines.append(f"| {r.entry_id} | {r.classic_name} | {r.original_text[:40]}... |")
    lines.append("")
    lines.append("## 五、关键发现（事实）")
    lines.append("")
    lines.append(f"- **EXACT_PRIMARY {len([r for r in results if r.evidence_class=='EXACT_PRIMARY'])} 条**：原典逐字原文，可用于辨证证据池")
    lines.append(f"- **DERIVED_TEXT {len([r for r in results if r.evidence_class=='DERIVED_TEXT'])} 条已隔离**：不进入证据池")
    lines.append(f"- **NOT_FOUND {len([r for r in results if r.evidence_class=='NOT_FOUND'])} 条**：需排查（多为现代整理语句）")
    lines.append(f"- **隔离比例 {len([r for r in results if r.evidence_class=='DERIVED_TEXT'])/len(results):.1%}**")
    lines.append("")
    lines.append("## 六、逐条分类结果")
    lines.append("")
    for r in results:
        cls = r.evidence_class
        mark = {"EXACT_PRIMARY": "🟢", "PARTIAL": "🟡", "DERIVED_TEXT": "🔒", "NOT_FOUND": "❌", "CONFLICT": "⚠️"}.get(cls, "❓")
        lines.append(f"### {r.entry_id}")
        lines.append("")
        lines.append(f"- **经典**: {r.classic_name} | **分类**: {r.category} | **证据分类**: {cls} {mark}")
        lines.append(f"- **原文**: {r.original_text[:80]}")
        lines.append(f"- **命中段落**: {r.matched_passage_id or '-'}")
        lines.append(f"- **source_hash**: {r.source_hash}")
        lines.append(f"- **备注**: {r.verification_notes}")
        lines.append("")
    lines.append("## 七、待 AI 审计者裁决的问题")
    lines.append("")
    lines.append("1. EXACT_PRIMARY 是否可以作为辨证证据池的准入标准？")
    lines.append("2. DERIVED_TEXT 是否应永久隔离，还是需从权威原书补正'原文'后重新分类？")
    lines.append("3. NOT_FOUND 条目（多为三命通会现代整理语句）应如何处理：弃用 / 从权威原书补正 / 标注为现代解释？")
    lines.append("4. PARTIAL 条目（若有）是否需要细分版本差异？")
    lines.append("5. CONFLICT 条目（若有）是否需要人工裁决？")
    lines.append("6. 证据池准入后，下一步是否进入 P0-3.3 辨证规则工程化？")
    lines.append("")

    report_path = Path(r"D:\shuntian\backend\docs\P0_3_2_EVIDENCE_CLASSIFICATION_REPORT.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"报告已保存: {report_path}")


if __name__ == "__main__":
    results, summary = main()
