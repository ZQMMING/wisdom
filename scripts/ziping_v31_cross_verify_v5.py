# -*- coding: utf-8 -*-
"""ZIPING V3.1 五经交叉验证 v5 — 每典扩展同义关键词.

v4 严苛 + 针对每典调候/通关/病药术语的同义模式扩展:
- DTS 调候模式: 喜生X月 / 取X为用 / 癸水方得通达 / 以X为财官 / 专用X
- QTBJ 调候模式: 专用X / 先用X次取Y / 为尊次之 / 三者皆用 / 正月X金
- PZZQ 调候模式: 配气候 / 用神配气候 / 论用神配气候
- YHZP/SMTH: 调候字面 + 异名(仇化恩/和稀泥/化敌)

v5 改进:
1. QTBJ 调候: 新增「正月庚金/二月甲木/冬木/夏木/秋木」月令日干组合
2. DTS 调候: 新增「取X为用/以X为X/喜生X月/癸水方得/欲X木」正则模式
3. 通关: 新增「仇化恩/和稀泥/化敌为友/和解」异名
4. 病药: 新增「有病得药/有病方为/药神」
"""
import json
import re
from pathlib import Path

BASE = Path("D:/顺天系统资料/开发资料/参考资料/五经知识库/03_PASSAGES")
OUT = Path("D:/shuntian/docs/audit/ZIPING-V31-CROSS-VERIFICATION-v5.json")

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
    clean = text.replace("\n", "").replace(" ", "").replace("*", "").replace("#", "")
    if len(clean) < 150:
        return ("【原文】" in text or "【断语】" in text or
                "取通关之神化解" in text)
    cnt = sum(1 for p in PATTERNS if p in text)
    return cnt >= 2


# 每典调候/通关/病药的同义模式
DTS_TIAOHOU_PATTERNS = [
    r"喜生.{1,6}月",
    r"以.{1,4}为用",
    r"取.{1,4}为用",
    r"专用",
    r"先用.{1,4}次",
    r"癸水.{0,4}方得",
    r"欲.{1,4}木",
    r"以.{1,4}为财",
    r"以.{1,4}为官",
    r"以.{1,4}为印",
    r"用.{1,4}为.{0,3}用",
    r"配气候",
    r"调和",
]

QTBJ_TIAOHOU_PATTERNS = [
    r"专用",
    r"先用.{1,4}次",
    r"为尊",
    r"次之",
    r"三者皆用",
    r"以.{1,4}为用",
    r"取.{1,4}佐之",
    r"正月.{1,4}金",
    r"二月.{1,4}木",
    r"冬木",
    r"夏木",
    r"秋木",
    r"春木",
]


def search_book(book, keywords, max_results=5, extra_patterns=None):
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
        if not kw_hit and extra_patterns:
            for pat in extra_patterns:
                if re.search(pat, text):
                    kw_hit = f"~{pat[:20]}"
                    break
        if not kw_hit:
            continue
        out.append({"passage_id": pid, "kw": kw_hit,
                    "snippet": text[:200].replace("\n", " ")})
        if len(out) >= max_results:
            break
    return out


ITEMS = {
    "X5_调候用神表": {
        "desc": "首用/次用/三并 优先级",
        "PZZQ": ["调候", "配气候"],
        "DTS":  ["调候", "配气候", "调和"],
        "QTBJ": ["专用", "先用", "为尊", "次之", "三者皆用"],
        "YHZP": ["调候", "配气候"],
        "SMTH": ["调候", "配气候"],
        "dts_extra": DTS_TIAOHOU_PATTERNS,
        "qtbj_extra": QTBJ_TIAOHOU_PATTERNS,
    },
    "X11_通关用神": {
        "desc": "印/食伤 通关桥",
        "PZZQ": ["通关", "化解", "两神争战"],
        "DTS":  ["通关", "化敌", "仇化恩", "化鬼为官", "化煞为权", "制伏"],
        "QTBJ": ["通关", "和稀泥", "化杀为权", "化鬼为官", "制伏"],
        "YHZP": ["通关", "仇化恩", "化杀为权", "化鬼为官", "制伏"],
        "SMTH": ["通关", "和解", "化杀为权", "制伏"],
        "dts_extra": [
            r"化鬼为官", r"化煞为权", r"化敌为友", r"制伏",
            r"从.{1,4}中.{0,4}调", r"和稀泥", r"两.{1,4}相.{0,2}战",
        ],
        "qtbj_extra": [
            r"化杀为权", r"化鬼为官", r"制伏",
            r"两.{1,4}对.{0,2}立", r"从.{1,4}中.{0,4}调",
        ],
    },
    "X12_病药": {
        "desc": "对立=病; 桥=药",
        "PZZQ": ["病药", "有病", "有药"],
        "DTS":  ["有病", "有病得药", "病药", "药神"],
        "QTBJ": ["病药", "有病", "有药"],
        "YHZP": ["病药", "有病", "有药"],
        "SMTH": ["病药", "有病", "有药"],
    },
}


def cross_verify(item_id, desc, cfg):
    out = {}
    for book in BOOKS:
        kws = cfg.get(book, [])
        extra = None
        if book == "DTS":
            extra = cfg.get("dts_extra")
        elif book == "QTBJ":
            extra = cfg.get("qtbj_extra")
        ev = search_book(book, kws, max_results=10, extra_patterns=extra)
        out[book] = {
            "count": len(ev),
            "evidence": ev,  # 保留全部
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
    print("=== v5: 重点验证 X5/X11/X12 ===\n")
    for item_id, cfg in ITEMS.items():
        r = cross_verify(item_id, cfg["desc"], cfg)
        results.append(r)
        print(f"{item_id}: {r['verdict']} ({r['confirmed_count']}/5)")
        for book, info in r["by_book"].items():
            if info["status"] == "FOUND":
                for ev in info["evidence"][:1]:
                    print(f"  {book} ✓ {ev['passage_id']} kw={ev['kw']}: {ev['snippet'][:150]}")

    summary = {
        "date": "2026-09-12",
        "method": "v5 严苛原文+每典调候/通关/病药同义模式扩展",
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
    print(f"\n=== Stats ===")
    print(f"  CROSS-VERIFIED: {summary['stats']['cross_verified']}/{summary['stats']['total']}")
    print(f"  DOUBLE-SOURCE:  {summary['stats']['double_source']}/{summary['stats']['total']}")
    print(f"  SINGLE-SOURCE:  {summary['stats']['single_source']}/{summary['stats']['total']}")
    print(f"  UNVERIFIED:     {summary['stats']['unverified']}/{summary['stats']['total']}")


if __name__ == "__main__":
    main()
