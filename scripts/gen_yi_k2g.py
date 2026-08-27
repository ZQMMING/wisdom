#!/usr/bin/env python3
"""Generate K2G YIJING concept registry from yi engine data."""
import yaml
from tongshu.engines.yi.hexagram_symbol import TRIGRAM_DATA, SIXTY_FOUR_MAP
from tongshu.engines.yi.yao_ci_data import YAO_CI

today = "2026-08-27"
concepts = []
cid = 0

# 1. 八卦 TRIGRAMS
trigram_defs = {
    "乾": "八卦之一，三爻皆阳，象征天、健、刚，五行属金，先天数1。",
    "兑": "八卦之一，上缺下二阳，象征泽、悦，五行属金，先天数2。",
    "离": "八卦之一，中虚上下阳，象征火、明、丽，五行属火，先天数3。",
    "震": "八卦之一，上二阴下一阳，象征雷、动，五行属木，先天数4。",
    "巽": "八卦之一，下断上二阳，象征风、入，五行属木，先天数5。",
    "坎": "八卦之一，中实上下阴，象征水、险、陷，五行属水，先天数6。",
    "艮": "八卦之一，上阳下二阴，象征山、止，五行属土，先天数7。",
    "坤": "八卦之一，三爻皆阴，象征地、顺、柔，五行属土，先天数8。",
}
for name, defn in trigram_defs.items():
    cid += 1
    concepts.append({
        "concept_id": f"YI_TR_{cid:03d}",
        "traditional_term": name,
        "canonical_definition": defn,
        "category": "TRIGRAMS",
        "product_semantic": "trigram",
        "source_refs": ["周易·说卦传"],
        "verification_status": "DRAFT",
        "created_at": today,
    })

# 2. 六十四卦 HEXAGRAMS
hex_list = sorted(SIXTY_FOUR_MAP.items(), key=lambda x: (x[0][0], x[0][1]))
for (upper, lower), name in hex_list:
    cid += 1
    elem_upper = TRIGRAM_DATA.get(upper, {}).get("element", "")
    elem_lower = TRIGRAM_DATA.get(lower, {}).get("element", "")
    defn = f"六十四卦之一，{upper}上{lower}下（{elem_upper}{elem_lower}），卦名{name}。"
    concepts.append({
        "concept_id": f"YI_HX_{cid:03d}",
        "traditional_term": name,
        "canonical_definition": defn,
        "category": "HEXAGRAMS",
        "product_semantic": "hexagram",
        "source_refs": ["周易·六十四卦"],
        "verification_status": "DRAFT",
        "created_at": today,
    })

# 3. 核心术语 KEY_TERMS
key_terms = [
    ("卦辞", "周易六十四卦每卦卦下所系之辞，总括一卦之义，如乾卦元亨利贞。"),
    ("爻辞", "周易六十四卦每爻所系之辞，说明各爻之义，共384条。"),
    ("彖辞", "十翼之一，解释卦辞，论断一卦之义，如大哉乾元。"),
    ("象辞", "十翼之一，分大象（解释卦象）和小象（解释爻象），如天行健君子以自强不息。"),
    ("文言", "十翼之一，专论乾坤两卦之义，阐发乾坤之德。"),
    ("系辞", "十翼之一，通论周易大义，含一阴一阳之谓道等核心命题。"),
    ("说卦", "十翼之一，论述八卦取象与方位，如帝出乎震齐乎巽。"),
    ("序卦", "十翼之一，论述六十四卦排列次序之理。"),
    ("杂卦", "十翼之一，以极简语言综论各卦卦义，如乾刚坤柔。"),
    ("元亨利贞", "周易四德，元为始、亨为通、利为宜、贞为正，乾卦卦辞。"),
    ("吉凶悔吝", "周易占断四态，吉为善、凶为恶、悔为小疵、吝为难。"),
    ("无咎", "周易占断用语，意为无大过咎，非吉非凶之中态。"),
    ("动爻", "起卦时发生阴阳变化之爻，为断卦核心依据。"),
    ("变卦", "动爻阴阳变化后所得之卦，又称之卦。"),
    ("互卦", "取本卦二三四爻为下卦、三四五爻为上卦所成之卦，用于深层分析。"),
    ("错卦", "本卦六爻阴阳全变所得之卦，又称正对卦。"),
    ("综卦", "本卦倒置所得之卦，又称覆卦。"),
    ("先天八卦", "伏羲八卦，乾南坤北离东坎西，序数乾1兑2离3震4巽5坎6艮7坤8。"),
    ("后天八卦", "文王八卦，离南坎北震东兑西，用于方位与月令。"),
    ("纳甲", "京房易体系，将十天干分配于八卦六爻，用于六爻断事。"),
    ("世应", "京房易体系，每卦定世爻（我）与应爻（彼），为六爻断事核心。"),
    ("飞伏", "京房易体系，飞神为现显之爻，伏神为隐藏之爻，用于深挖隐情。"),
]
for term, defn in key_terms:
    cid += 1
    concepts.append({
        "concept_id": f"YI_KT_{cid:03d}",
        "traditional_term": term,
        "canonical_definition": defn,
        "category": "KEY_TERMS",
        "product_semantic": "yi_term",
        "source_refs": ["周易·十翼"],
        "verification_status": "DRAFT",
        "created_at": today,
    })

data = {
    "registry": {
        "domain": "YIJING",
        "version": "1.0.0",
        "generated_at": today,
        "status": "DRAFT",
        "total_count": len(concepts),
    },
    "concepts": concepts,
}

out = "src/tongshu/k2g/concepts/yi_concepts.yaml"
with open(out, "w", encoding="utf-8") as f:
    yaml.dump(data, f, allow_unicode=True, default_flow_style=False, sort_keys=False)

print(f"生成完成: {len(concepts)} 个概念 -> {out}")
print(f"  八卦 TRIGRAMS: 8")
print(f"  六十四卦 HEXAGRAMS: 64")
print(f"  核心术语 KEY_TERMS: {len(key_terms)}")
