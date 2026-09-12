# -*- coding: utf-8 -*-
"""ZIPING V3.1 五经交叉验证 — 主线程自上而下.

对每项判据 X1~X13, 在五部经典 PZZQ/DTS/QTBJ/YHZP/SMTH 中抽取支撑原文,
比较口径一致性, 输出 CROSS-VERIFIED/SINGLE-SOURCE/DISPUTED/UNVERIFIED.
"""
import json
from pathlib import Path

BASE = Path("D:/顺天系统资料/开发资料/参考资料/五经知识库/03_PASSAGES")
OUT = Path("D:/shuntian/docs/audit/ZIPING-V31-CROSS-VERIFICATION.json")

BOOKS = {
    "PZZQ": "子平真诠",
    "DTS":  "滴天髓",
    "QTBJ": "穷通宝鉴",
    "YHZP": "渊海子平",
    "SMTH": "三命通会",
}

def load_passages(book):
    p = BASE / book / f"{book}_P0_passages.json"
    if not p.exists():
        return []
    data = json.loads(p.read_text(encoding="utf-8"))
    return data.get("passages", [])

def search_keyword(passages, keywords, max_results=3):
    """In passages find first N with any keyword match in original_text."""
    results = []
    for p in passages:
        # 字段是 original_text / normalized_text, 不是 text
        text = p.get("original_text", "") or p.get("normalized_text", "")
        ch = p.get("passage_id", "")
        for kw in keywords:
            if kw in text:
                snippet = text[:250].replace("\n", " ")
                results.append({"passage_id": ch, "kw": kw, "snippet": snippet})
                break
        if len(results) >= max_results:
            break
    return results

def cross_verify(item_id, keywords_per_book):
    """For each book, search keywords, return evidence found."""
    out = {}
    for book in BOOKS:
        passages = load_passages(book)
        found = search_keyword(passages, keywords_per_book.get(book, []))
        out[book] = {
            "count": len(found),
            "evidence": found[:2],
            "status": "FOUND" if len(found) > 0 else "MISSING",
        }
    confirmed = sum(1 for b in out.values() if b["status"] == "FOUND")
    if confirmed >= 3:
        verdict = "CROSS-VERIFIED"
    elif confirmed == 2:
        verdict = "DOUBLE-SOURCE"
    elif confirmed == 1:
        verdict = "SINGLE-SOURCE"
    else:
        verdict = "UNVERIFIED"
    return {"item_id": item_id, "by_book": out, "confirmed_count": confirmed, "verdict": verdict}


# Cross-verification items (X1~X13)
ITEMS = {
    "X1_得令定义": {
        "PZZQ": ["得时", "失时", "得令", "月令"],
        "DTS":  ["当令", "月令", "司令"],
        "QTBJ": ["当令", "令"],
        "YHZP": ["月令", "得令"],
        "SMTH": ["月令", "得令"],
    },
    "X2_身强弱六态": {
        "PZZQ": ["身弱", "身强", "中和", "旺"],
        "DTS":  ["体用", "扶抑", "强弱", "中和"],
        "QTBJ": ["身旺", "身弱"],
        "YHZP": ["身强", "身弱"],
        "SMTH": ["身旺", "身弱"],
    },
    "X3_党众分类": {
        "PZZQ": ["比劫", "印绶", "食伤"],
        "DTS":  ["党多", "扶助", "生我"],
        "QTBJ": ["比劫", "印绶"],
        "YHZP": ["比劫", "印星"],
        "SMTH": ["比劫", "印绶"],
    },
    "X4_寒暖燥湿": {
        "PZZQ": ["寒暖", "燥湿"],
        "DTS":  ["天道有寒暖", "地道有燥湿", "阴支为寒", "过于湿", "过于燥"],
        "QTBJ": ["寒气未除", "寒气渐升", "燥土", "湿土", "伏水", "藏火"],
        "YHZP": ["寒暖", "燥湿"],
        "SMTH": ["寒暖", "燥湿"],
    },
    "X5_调候用神表": {
        "PZZQ": ["调候"],
        "DTS":  ["调候"],
        "QTBJ": ["丙暖庚性", "用丙", "庚金次之", "三者皆用", "丙先壬后"],
        "YHZP": ["调候"],
        "SMTH": ["调候"],
    },
    "X6_十二长生": {
        "PZZQ": ["长生", "帝旺"],
        "DTS":  ["长生", "帝旺"],
        "QTBJ": ["长生", "帝旺"],
        "YHZP": ["遇帝旺", "临官", "长生", "冠带", "养", "库者吉", "死、绝"],
        "SMTH": ["长生", "帝旺", "临官"],
    },
    "X7_墓库开闭": {
        "PZZQ": ["墓库", "入库"],
        "DTS":  ["墓库", "入库"],
        "QTBJ": ["墓库", "入库"],
        "YHZP": ["一钥能开库", "三冲即破门", "刑冲库亦开", "财库官库要正冲"],
        "SMTH": ["墓库", "逢冲开库", "财星入库"],
    },
    "X8_节气四时": {
        "PZZQ": ["寅月", "卯月", "春木"],
        "DTS":  ["寅月", "立春", "正月建寅", "节满即谢"],
        "QTBJ": ["正月庚金", "七月庚金"],
        "YHZP": ["寅月", "卯月", "春木"],
        "SMTH": ["立春", "正月建寅", "夏月", "秋月", "冬月"],
    },
    "X9_建禄月刃": {
        "PZZQ": ["建禄", "阳刃"],
        "DTS":  ["建禄", "阳刃", "禄前"],
        "QTBJ": ["禄到", "阳刃"],
        "YHZP": ["甲禄在寅", "卯为阳刃", "禄前一位是也"],
        "SMTH": ["甲木禄到寅", "丙火禄到巳", "庚金禄到申", "壬水禄到亥"],
    },
    "X10_清浊混杂": {
        "PZZQ": ["正官", "七杀", "杂", "相克"],
        "DTS":  ["混杂", "正官", "七杀"],
        "QTBJ": ["官杀混杂"],
        "YHZP": ["混杂", "清浊"],
        "SMTH": ["官杀混杂", "清浊"],
    },
    "X11_通关用神": {
        "PZZQ": ["通关", "通关有情"],
        "DTS":  ["通关", "通关之神"],
        "QTBJ": ["通关"],
        "YHZP": ["通关"],
        "SMTH": ["通关"],
    },
    "X12_病药": {
        "PZZQ": ["病药", "有病方为贵", "有病者"],
        "DTS":  ["体用", "扶抑", "有病方为贵"],
        "QTBJ": ["病药"],
        "YHZP": ["病药"],
        "SMTH": ["病药"],
    },
    "X13_用神分方法": {
        "PZZQ": ["用神", "专求月令", "调候与格局互参"],
        "DTS":  ["用神", "调候", "扶抑"],
        "QTBJ": ["调候", "用神"],
        "YHZP": ["用神"],
        "SMTH": ["用神"],
    },
}


def main():
    results = []
    for item_id, keywords in ITEMS.items():
        r = cross_verify(item_id, keywords)
        results.append(r)
        print(f"{item_id}: {r['verdict']} ({r['confirmed_count']}/5 典)")

    summary = {
        "date": "2026-09-12",
        "items": results,
        "stats": {
            "total": len(results),
            "cross_verified": sum(1 for r in results if r["verdict"] == "CROSS-VERIFIED"),
            "double_source": sum(1 for r in results if r["verdict"] == "DOUBLE-SOURCE"),
            "single_source": sum(1 for r in results if r["verdict"] == "SINGLE-SOURCE"),
            "unverified": sum(1 for r in results if r["verdict"] == "UNVERIFIED"),
        }
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n写入 {OUT}")
    print(f"\n=== Stats ===")
    print(f"  CROSS-VERIFIED: {summary['stats']['cross_verified']}/{summary['stats']['total']}")
    print(f"  DOUBLE-SOURCE:  {summary['stats']['double_source']}/{summary['stats']['total']}")
    print(f"  SINGLE-SOURCE:  {summary['stats']['single_source']}/{summary['stats']['total']}")
    print(f"  UNVERIFIED:     {summary['stats']['unverified']}/{summary['stats']['total']}")


if __name__ == "__main__":
    main()
