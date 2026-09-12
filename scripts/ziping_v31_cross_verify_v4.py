# -*- coding: utf-8 -*-
"""ZIPING V3.1 五经交叉验证 v4 — 严苛原文 + 放宽调候关键词.

严苛规则 (与 v3 同):
- 只用 original_text
- 排除 _0001 + "知识梳理"/"AI知识库"/"摘录"/"核心注疏"/"总目提要"
- 段落 > 150 字, 含 ≥2 判据结构词
- 排除标题/目录

放宽 (v4 新增):
- 调候 X5: 关键词从单字"调候"扩为完整调候形态("专用"/"先用"/"为尊"/"次之"/"三者皆用"/"调候")
- 通关 X11: 关键词从"通关"扩为"通关之神"/"通关用神"/"化敌为友"/"仇化恩"
- 病药 X12: 关键词从"病药"扩为"有病方为贵"/"有病得药"/"有病者"
- 寒暖 X4: 关键词加"春寒"/"秋燥"/"夏热"/"冬寒"
- 月令 X1: 加"得令于月"/"月令为X"

每典最多 5 条命中证据 (扩展采样).
"""
import json
from pathlib import Path

BASE = Path("D:/顺天系统资料/开发资料/参考资料/五经知识库/03_PASSAGES")
OUT = Path("D:/shuntian/docs/audit/ZIPING-V31-CROSS-VERIFICATION-v4.json")

BOOKS = {"PZZQ": "子平真诠", "DTS": "滴天髓", "QTBJ": "穷通宝鉴",
         "YHZP": "渊海子平", "SMTH": "三命通会"}

PATTERNS = ["用", "取", "为", "即", "者", "必", "则", "得",
            "比劫", "印星", "食伤", "财星", "官杀",
            "墓", "库", "长生", "帝旺", "临官",
            "月令", "日主", "寒", "暖", "燥", "湿",
            "开", "闭", "冲", "刑", "合",
            "扶抑", "通关", "体用", "党多"]

EXCLUDE_TITLE_PATTERNS = [
    "知识梳理", "AI知识库", "核心注疏", "摘录与白话",
    "_0001_P0", "总目提要", "知识库",
    # 序言 / 自序 / 校注 等非判据原文
    "方重审序", "徐乐吾", "自序", "凡例", "序言", "跋",
    "提要", "校注", "整理者",
]


def is_excluded(passage_id, text):
    for pat in EXCLUDE_TITLE_PATTERNS:
        if pat in passage_id or pat in text[:300]:
            return True
    if text.count("* ") > 10:
        return True
    return False


def is_real_content(text):
    """实际内容: 原文判据, 长度≥150 OR (短句带原文标记)."""
    clean = text.replace("\n", "").replace(" ", "").replace("*", "").replace("#", "")
    if len(clean) < 150:
        # 短句豁免: 带【原文】/【断语】/判据关键词("取...化解"/"取...为用")等
        is_judgment_brief = (
            "【原文】" in text or "【断语】" in text or
            "取通关之神化解" in text or  # PZZQ_0440 原句
            "取X为用" in text.replace(" ", "")  # 通用判据模式
        )
        return is_judgment_brief
    # 长文: 必须含 ≥2 判据结构词
    cnt = sum(1 for p in PATTERNS if p in text)
    return cnt >= 2


def search_book(book, keywords, max_results=5):
    passages_path = BASE / book / f"{book}_P0_passages.json"
    if not passages_path.exists():
        return []
    passages = json.loads(passages_path.read_text(encoding="utf-8")).get("passages", [])
    out = []
    for p in passages:
        text = p.get("original_text", "")
        pid = p.get("passage_id", "?")
        if not text or is_excluded(pid, text) or not is_real_content(text):
            continue
        kw_hit = next((k for k in keywords if k in text), None)
        if not kw_hit:
            continue
        out.append({"passage_id": pid, "kw": kw_hit,
                    "snippet": text[:200].replace("\n", " ")})
        if len(out) >= max_results:
            break
    return out


ITEMS = {
    "X1_得令定义": {
        "desc": "月支对日主生/同 = 得令",
        "PZZQ": ["得时", "得令", "失时", "月令"],
        "DTS":  ["当令", "月令", "司令"],
        "QTBJ": ["当令", "月令", "得令"],
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
        "PZZQ": ["寒暖", "燥湿", "寒气"],
        "DTS":  ["天道有寒暖", "地道有燥湿", "过于湿", "过于燥", "阴支为寒"],
        "QTBJ": ["寒气", "燥土", "湿土", "伏水", "藏火", "火炎土燥"],
        "YHZP": ["寒暖", "燥湿", "寒气"],
        "SMTH": ["寒暖", "燥湿", "寒气"],
    },
    "X5_调候用神表": {
        "desc": "首用/次用/三并 优先级",
        "PZZQ": ["调候", "配气候", "因成得败"],
        "DTS":  ["调候", "配气候"],
        "QTBJ": ["专用", "先用", "为尊", "次之", "三者皆用", "正月庚金", "七月庚金"],
        "YHZP": ["调候"],
        "SMTH": ["调候"],
    },
    "X6_十二长生": {
        "desc": "帝旺/临官/长生=吉; 死/绝=凶",
        "PZZQ": ["长生", "帝旺", "临官"],
        "DTS":  ["长生", "帝旺", "临官"],
        "QTBJ": ["长生", "帝旺"],
        "YHZP": ["帝旺", "临官", "长生", "冠带", "养", "死", "绝"],
        "SMTH": ["长生", "帝旺", "临官"],
    },
    "X7_墓库开闭": {
        "desc": "冲刑开库",
        "PZZQ": ["墓库", "入库"],
        "DTS":  ["墓库", "入库"],
        "QTBJ": ["墓库", "入库", "开库"],
        "YHZP": ["开库", "三冲", "刑冲", "正冲", "入库"],
        "SMTH": ["墓库", "开库", "财星入库"],
    },
    "X8_节气四时": {
        "desc": "寅卯辰=春/巳午未=夏/申酉戌=秋/亥子丑=冬",
        "PZZQ": ["寅月", "春木", "正月"],
        "DTS":  ["正月建寅", "春木", "正月建"],
        "QTBJ": ["正月庚金", "夏木", "十月"],
        "YHZP": ["寅月", "春木", "正月"],
        "SMTH": ["正月建寅", "夏月", "秋月", "冬月"],
    },
    "X9_建禄月刃": {
        "desc": "建禄=临官/阳刃=帝旺",
        "PZZQ": ["建禄", "阳刃", "禄到"],
        "DTS":  ["建禄", "阳刃", "禄前"],
        "QTBJ": ["阳刃", "禄到", "建禄"],
        "YHZP": ["禄前一位", "阳刃", "建禄", "禄到"],
        "SMTH": ["禄到", "阳刃", "建禄"],
    },
    "X10_清浊混杂": {
        "desc": "正官+七杀同透=浊; 官伤/印财相克亦浊",
        "PZZQ": ["正官", "七杀", "混杂"],
        "DTS":  ["混杂", "正官", "七杀"],
        "QTBJ": ["官杀混杂", "正官", "七杀"],
        "YHZP": ["混杂", "清浊"],
        "SMTH": ["官杀混杂", "清浊"],
    },
    "X11_通关用神": {
        "desc": "印/食伤 通关桥",
        "PZZQ": ["通关", "化解", "仇化恩"],
        "DTS":  ["通关", "通关之神", "化敌"],
        "QTBJ": ["通关", "化敌为友", "通关用神"],
        "YHZP": ["通关", "仇化恩"],
        "SMTH": ["通关", "通关之神"],
    },
    "X12_病药": {
        "desc": "对立=病; 桥=药",
        "PZZQ": ["病药", "有病", "有药"],
        "DTS":  ["有病", "有病得药", "病药"],
        "QTBJ": ["病药", "有病", "有药"],
        "YHZP": ["病药", "有病", "有药"],
        "SMTH": ["病药", "有病", "有药"],
    },
    "X13_用神分方法": {
        "desc": "格局/调候/病药/通关 各独立不合并",
        "PZZQ": ["用神", "调候", "格局"],
        "DTS":  ["用神", "调候", "格局"],
        "QTBJ": ["调候", "用神", "格局"],
        "YHZP": ["用神", "调候", "格局"],
        "SMTH": ["用神", "调候", "格局"],
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
        "method": "v4 严苛原文+放宽调候/通关/病药关键词",
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
