# -*- coding: utf-8 -*-
"""ZIPING V3.1 五经交叉验证 v3 — 严苛真实原文判据句级.

严苛规则:
- 必须是 original_text (原文), 非 normalized_text (知识梳理)
- 排除 _0001 总论页 (各典籍 P0[0] 是目录/序言, 不是判据)
- 排除"知识梳理"/"AI知识库"/"核心注疏"标题的段落 (知识库加工, 非原文)
- 段落必须 ≥150 字 (排除目录/标题页)
- 必须含 ≥2 个判据结构词 (用/取/为/即/者/必/则/得)
- 必须含关键词 (X 项)
- 找不到则诚实 MISSING
"""
import json
from pathlib import Path
import re

BASE = Path("D:/顺天系统资料/开发资料/参考资料/五经知识库/03_PASSAGES")
OUT = Path("D:/shuntian/docs/audit/ZIPING-V31-CROSS-VERIFICATION-v3.json")

BOOKS = {"PZZQ": "子平真诠", "DTS": "滴天髓", "QTBJ": "穷通宝鉴",
         "YHZP": "渊海子平", "SMTH": "三命通会"}

PATTERNS = ["用", "取", "为", "即", "者", "必", "则", "得",
            "比劫", "印星", "食伤", "财星", "官杀",
            "墓", "库", "长生", "帝旺", "临官",
            "月令", "日主", "寒", "暖", "燥", "湿",
            "开", "闭", "冲", "刑", "合",
            "扶抑", "通关", "体用", "党多"]

# 排除段落标识 (知识库加工/目录页)
EXCLUDE_TITLE_PATTERNS = [
    "知识梳理", "AI知识库", "核心注疏", "摘录与白话",
    "_0001_P0",  # 目录页
    "章节", "目录", "序", "卷一", "卷二",  # 卷首
]


def is_excluded(passage_id, text):
    """判断是否总论/目录/知识库加工页."""
    for pat in EXCLUDE_TITLE_PATTERNS:
        if pat in passage_id or pat in text[:300]:
            return True
    # 目录页特征: 大量"*"开头 (markdown list)
    if text.count("* ") > 10:
        return True
    return False


def is_real_content(text):
    """实际内容: 原文 (original_text), 长度 > 150 字, 含判据结构."""
    clean = text.replace("\n", "").replace(" ", "").replace("*", "").replace("#", "")
    if len(clean) < 150:
        return False
    cnt = sum(1 for p in PATTERNS if p in text)
    return cnt >= 2


def search_book(book, keywords, max_results=5):
    """单典判据句级搜索."""
    passages_path = BASE / book / f"{book}_P0_passages.json"
    if not passages_path.exists():
        return []
    passages = json.loads(passages_path.read_text(encoding="utf-8")).get("passages", [])
    out = []
    for p in passages:
        # 只用 original_text, 不用 normalized_text (知识梳理)
        text = p.get("original_text", "")
        pid = p.get("passage_id", "?")
        if not text:
            continue
        if is_excluded(pid, text):
            continue
        if not is_real_content(text):
            continue
        # 关键词至少命中 1
        kw_hit = next((k for k in keywords if k in text), None)
        if not kw_hit:
            continue
        out.append({
            "passage_id": pid,
            "kw": kw_hit,
            "snippet": text[:200].replace("\n", " ")
        })
        if len(out) >= max_results:
            break
    return out


# X 项 + 每典关键词
ITEMS = {
    "X1_得令定义": {
        "desc": "月支对日主生/同 = 得令",
        "PZZQ": ["得时", "得令", "失时", "月令"],
        "DTS":  ["当令", "月令", "司令"],
        "QTBJ": ["当令", "月令"],
        "YHZP": ["月令", "得令"],
        "SMTH": ["月令", "得令"],
    },
    "X2_身强弱六态": {
        "desc": "得令不旺/失令不弱/中和/身弱",
        "PZZQ": ["身旺", "身弱", "中和", "扶抑"],
        "DTS":  ["体用", "扶抑", "身旺", "身弱"],
        "QTBJ": ["身旺", "身弱"],
        "YHZP": ["身强", "身弱"],
        "SMTH": ["身旺", "身弱"],
    },
    "X3_党众分类": {
        "desc": "比劫+印=帮身 / 食伤+财+官杀=对立",
        "PZZQ": ["比劫", "印绶", "食伤"],
        "DTS":  ["党多", "扶助", "生我"],
        "QTBJ": ["比劫", "印绶"],
        "YHZP": ["比劫", "印星"],
        "SMTH": ["比劫", "印绶"],
    },
    "X4_寒暖燥湿": {
        "desc": "天道寒暖×地道燥湿 二维",
        "PZZQ": ["寒暖", "燥湿"],
        "DTS":  ["天道有寒暖", "地道有燥湿", "过于湿", "过于燥", "阴支为寒"],
        "QTBJ": ["寒气", "燥土", "湿土", "伏水", "藏火"],
        "YHZP": ["寒暖", "燥湿"],
        "SMTH": ["寒暖", "燥湿"],
    },
    "X5_调候用神表": {
        "desc": "首用/次用/三并 优先级",
        "PZZQ": ["调候"],
        "DTS":  ["调候"],
        "QTBJ": ["用丙", "庚金次之", "三者皆用", "丙先壬后"],
        "YHZP": ["调候"],
        "SMTH": ["调候"],
    },
    "X6_十二长生": {
        "desc": "帝旺/临官/长生=吉; 死/绝=凶",
        "PZZQ": ["长生", "帝旺"],
        "DTS":  ["长生", "帝旺"],
        "QTBJ": ["长生", "帝旺"],
        "YHZP": ["帝旺", "临官", "长生", "冠带", "养", "死", "绝"],
        "SMTH": ["长生", "帝旺", "临官"],
    },
    "X7_墓库开闭": {
        "desc": "冲刑开库",
        "PZZQ": ["墓库", "入库"],
        "DTS":  ["墓库", "入库"],
        "QTBJ": ["墓库", "入库"],
        "YHZP": ["开库", "三冲", "刑冲", "正冲"],
        "SMTH": ["墓库", "开库", "财星入库"],
    },
    "X8_节气四时": {
        "desc": "寅卯辰=春/巳午未=夏/申酉戌=秋/亥子丑=冬",
        "PZZQ": ["寅月", "春木"],
        "DTS":  ["正月建寅", "春木"],
        "QTBJ": ["正月庚金", "夏木"],
        "YHZP": ["寅月", "春木"],
        "SMTH": ["正月建寅", "夏月", "秋月", "冬月"],
    },
    "X9_建禄月刃": {
        "desc": "建禄=临官/阳刃=帝旺",
        "PZZQ": ["建禄", "阳刃"],
        "DTS":  ["建禄", "阳刃"],
        "QTBJ": ["阳刃", "禄到"],
        "YHZP": ["禄前一位", "阳刃", "建禄"],
        "SMTH": ["禄到", "阳刃"],
    },
    "X10_清浊混杂": {
        "desc": "正官+七杀同透=浊; 官伤/印财相克亦浊",
        "PZZQ": ["正官", "七杀", "混杂"],
        "DTS":  ["混杂", "正官", "七杀"],
        "QTBJ": ["官杀混杂"],
        "YHZP": ["混杂", "清浊"],
        "SMTH": ["官杀混杂", "清浊"],
    },
    "X11_通关用神": {
        "desc": "印/食伤 通关桥",
        "PZZQ": ["通关", "化解"],
        "DTS":  ["通关"],
        "QTBJ": ["通关"],
        "YHZP": ["通关"],
        "SMTH": ["通关"],
    },
    "X12_病药": {
        "desc": "对立=病; 桥=药",
        "PZZQ": ["病药", "有病"],
        "DTS":  ["体用", "扶抑", "有病"],
        "QTBJ": ["病药"],
        "YHZP": ["病药"],
        "SMTH": ["病药"],
    },
    "X13_用神分方法": {
        "desc": "格局/调候/病药/通关 各独立不合并",
        "PZZQ": ["用神", "调候"],
        "DTS":  ["用神", "调候"],
        "QTBJ": ["调候", "用神"],
        "YHZP": ["用神"],
        "SMTH": ["用神"],
    },
}


def cross_verify(item_id, desc, kw_per_book):
    out = {}
    for book in BOOKS:
        ev = search_book(book, kw_per_book.get(book, []))
        out[book] = {
            "count": len(ev),
            "evidence": ev[:2],
            "status": "FOUND" if ev else "MISSING"
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
    return {"item_id": item_id, "desc": desc, "by_book": out,
            "confirmed_count": confirmed, "verdict": verdict}


def main():
    results = []
    for item_id, cfg in ITEMS.items():
        r = cross_verify(item_id, cfg["desc"], cfg)
        results.append(r)
        print(f"{item_id}: {r['verdict']} ({r['confirmed_count']}/5)")

    summary = {
        "date": "2026-09-12",
        "method": "严苛判据句级 (排除_0001+知识梳理+目录)",
        "items": results,
        "stats": {
            "total": len(results),
            "cross_verified": sum(1 for r in results if r["verdict"] == "CROSS-VERIFIED"),
            "double_source": sum(1 for r in results if r["verdict"] == "DOUBLE-SOURCE"),
            "single_source": sum(1 for r in results if r["verdict"] == "SINGLE-SOURCE"),
            "unverified": sum(1 for r in results if r["verdict"] == "UNVERIFIED"),
        }
    }
    OUT.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n写入 {OUT}")
    print(f"\n=== Stats ===")
    print(f"  CROSS-VERIFIED: {summary['stats']['cross_verified']}/{summary['stats']['total']}")
    print(f"  DOUBLE-SOURCE:  {summary['stats']['double_source']}/{summary['stats']['total']}")
    print(f"  SINGLE-SOURCE:  {summary['stats']['single_source']}/{summary['stats']['total']}")
    print(f"  UNVERIFIED:     {summary['stats']['unverified']}/{summary['stats']['total']}")


if __name__ == "__main__":
    main()
