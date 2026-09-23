# -*- coding: utf-8 -*-
"""从格族F0总闸"""
import sys
sys.path.insert(0, '.')
from spec.root_qi import calc_root_qi, STEM_WUXING

# 十神：比劫、印星
BI_JIE = {
    "甲": ["甲", "乙"], "乙": ["甲", "乙"],
    "丙": ["丙", "丁"], "丁": ["丙", "丁"],
    "戊": ["戊", "己"], "己": ["戊", "己"],
    "庚": ["庚", "辛"], "辛": ["庚", "辛"],
    "壬": ["壬", "癸"], "癸": ["壬", "癸"],
}

YIN_XING = {
    "甲": ["壬", "癸"], "乙": ["壬", "癸"],
    "丙": ["甲", "乙"], "丁": ["甲", "乙"],
    "戊": ["丙", "丁"], "己": ["丙", "丁"],
    "庚": ["戊", "己"], "辛": ["戊", "己"],
    "壬": ["庚", "辛"], "癸": ["庚", "辛"],
}

# 克我者（官杀，用来克比劫）
GUAN_SHA = {
    "甲": ["庚", "辛"], "乙": ["庚", "辛"],
    "丙": ["壬", "癸"], "丁": ["壬", "癸"],
    "戊": ["甲", "乙"], "己": ["甲", "乙"],
    "庚": ["丙", "丁"], "辛": ["丙", "丁"],
    "壬": ["戊", "己"], "癸": ["戊", "己"],
}

# 我克者（财星，用来克印星）
CAI_XING = {
    "甲": ["戊", "己"], "乙": ["戊", "己"],
    "丙": ["庚", "辛"], "丁": ["庚", "辛"],
    "戊": ["壬", "癸"], "己": ["壬", "癸"],
    "庚": ["甲", "乙"], "辛": ["甲", "乙"],
    "壬": ["丙", "丁"], "癸": ["丙", "丁"],
}


def _is_bi_jie(day_stem: str, stem: str) -> bool:
    return stem in BI_JIE[day_stem]


def _is_yin_xing(day_stem: str, stem: str) -> bool:
    return stem in YIN_XING[day_stem]


def 无气(stems: list, day_stem: str) -> bool:
    """
    天干无比印，或比印被尽除
    stems: [年干, 月干, 日干, 时干]
    """
    # 找所有比劫和印星（除日干外）
    bi_yin_stems = []
    for i, stem in enumerate(stems):
        if i == 2:  # 日干不算
            continue
        if _is_bi_jie(day_stem, stem) or _is_yin_xing(day_stem, stem):
            bi_yin_stems.append((i, stem))

    if not bi_yin_stems:
        return True  # 无比印，无气成立

    # 检查每个比印是否被尽除
    for i, stem in bi_yin_stems:
        # 找邻干（前一个、后一个）
        neighbors = []
        if i > 0:
            neighbors.append(stems[i-1])
        if i < 3:
            neighbors.append(stems[i+1])

        # 比劫：被官杀紧贴克破 → 算尽除
        if _is_bi_jie(day_stem, stem):
            broken = False
            for n in neighbors:
                if n in GUAN_SHA[day_stem]:
                    broken = True
                    break
            if not broken:
                return False  # 有比劫未被克破，有气

        # 印星：被财星紧贴克破 → 算尽除
        if _is_yin_xing(day_stem, stem):
            broken = False
            for n in neighbors:
                if n in CAI_XING[day_stem]:
                    broken = True
                    break
            if not broken:
                return False  # 有印未被财克，有气

    return True  # 所有比印都被尽除


def F0_pass(day_stem: str, branches: list, stems: list) -> bool:
    """
    F0总闸：日主无根无气（F1/F2/F3用）
    返回 True=通过（可入从格族），False=不通过（退回正格）
    注意：F4从强不调用本函数，只要求root_qi==0
    """
    root_qi = calc_root_qi(day_stem, branches, stems)
    wu_qi = 无气(stems, day_stem)
    return (root_qi == 0) and wu_qi


def F0_root_only(day_stem: str, branches: list, stems: list) -> bool:
    """
    F4从强专用总闸：只要求日主无根，不要求无气
    （印比是所从之神，透干正常）
    """
    root_qi = calc_root_qi(day_stem, branches, stems)
    return root_qi == 0


def test():
    """测试用例"""
    # C1: 癸巳 乙卯 己亥 癸酉 → F0=True
    f0 = F0_pass("己", ["巳", "卯", "亥", "酉"], ["癸", "乙", "己", "癸"])
    print(f"C1 F0: {f0} (预期True)")

    # C2: 癸巳 乙卯 己子 癸酉 → F0=False（巳中戊根未被冲）
    f0 = F0_pass("己", ["巳", "卯", "子", "酉"], ["癸", "乙", "己", "癸"])
    print(f"C2 F0: {f0} (预期False)")

    # C3': 庚申 辛酉 甲子 辛未 → F0=False（未中乙余气根）
    f0 = F0_pass("甲", ["申", "酉", "子", "未"], ["庚", "辛", "甲", "辛"])
    print(f"C3' F0: {f0} (预期False)")

    # C4: 庚申 辛酉 甲子 辛丑 → F0=True（丑中无木）
    f0 = F0_pass("甲", ["申", "酉", "子", "丑"], ["庚", "辛", "甲", "辛"])
    print(f"C4 F0: {f0} (预期True)")

    # C5: 庚申 甲申 甲子 乙丑 → F0=False（月干甲比肩帮身）
    f0 = F0_pass("甲", ["申", "申", "子", "丑"], ["庚", "甲", "甲", "乙"])
    print(f"C5 F0: {f0} (预期False，月干甲比肩帮身)")

    # C6: 庚申 甲申 甲子 庚午 → F0=True
    # 月干甲比肩，被年干庚七杀紧贴克破→视为尽除；地支无木根
    f0 = F0_pass("甲", ["申", "申", "子", "午"], ["庚", "甲", "甲", "庚"])
    print(f"C6 F0: {f0} (预期True，月干甲比肩被年干庚紧贴克破)")


if __name__ == "__main__":
    test()


# ========== F1-F4：旺势判定 ==========

# 十神分类（按日主五行）
SHISHEN_CLASSES = {
    "木": {"印": {"水"}, "比": {"木"}, "食伤": {"火"}, "财": {"土"}, "官杀": {"金"}},
    "火": {"印": {"木"}, "比": {"火"}, "食伤": {"土"}, "财": {"金"}, "官杀": {"水"}},
    "土": {"印": {"火"}, "比": {"土"}, "食伤": {"金"}, "财": {"水"}, "官杀": {"木"}},
    "金": {"印": {"土"}, "比": {"金"}, "食伤": {"水"}, "财": {"木"}, "官杀": {"火"}},
    "水": {"印": {"金"}, "比": {"水"}, "食伤": {"木"}, "财": {"火"}, "官杀": {"土"}},
}

# 五行→十神对应
WUXING_OF = {
    "木": {"官杀": "金", "财": "土", "食伤": "火", "印": "水"},
    "火": {"官杀": "水", "财": "金", "食伤": "土", "印": "木"},
    "土": {"官杀": "木", "财": "水", "食伤": "金", "印": "火"},
    "金": {"官杀": "火", "财": "木", "食伤": "水", "印": "土"},
    "水": {"官杀": "土", "财": "火", "食伤": "木", "印": "金"},
}


def _tou_gan(stems: list, day_wx: str, shen_class: str, exclude_day=True) -> bool:
    """判某类十神是否在天干透出（默认排除日干自身）
    stems顺序：年干、月干、日干、时干
    """
    from spec.root_qi import STEM_WUXING
    cls = SHISHEN_CLASSES[day_wx][shen_class]
    if exclude_day:
        # 排除日干（stems[2]）
        check_stems = [s for i, s in enumerate(stems) if i != 2]
    else:
        check_stems = stems
    return any(STEM_WUXING[s] in cls for s in check_stems)


def _dangling(cong_wx: str, month_branch: str) -> bool:
    """判所从五行是否当令（月支本气）"""
    from spec.root_qi import BENQI
    return BENQI[month_branch] == cong_wx


def _demote_count(shi_dict: dict, family: str, month_branch: str, day_wx: str, stems: list = None) -> int:
    """统计减项数量（每项-1）"""
    n = 0

    # 印比族的所从五行是印（比劫同五行，合并计算）
    if family == "印比":
        cong_wx = WUXING_OF[day_wx]["印"]
    else:
        cong_wx = WUXING_OF[day_wx][family]

    # 不当令
    if not _dangling(cong_wx, month_branch):
        n += 1

    # 旺神不纯：他神泄气（余气级别不算，阈值0.5）
    PURITY_THRESHOLD = 0.5  # 余气=0.5不算杂气
    if family == "官杀" and shi_dict.get("食伤", 0) > PURITY_THRESHOLD:
        n += 1
    if family == "财" and shi_dict.get("官杀", 0) > PURITY_THRESHOLD:
        n += 1
    # 从儿族：财星是喜神（吾儿又见儿），不算泄气减项
    # 从财族：食伤生财是喜神链，不算泄气减项
    if family == "印比" and (shi_dict.get("财", 0) > PURITY_THRESHOLD or shi_dict.get("官杀", 0) > PURITY_THRESHOLD):
        n += 1

    # 天干透一粒虚浮逆神（中等减项）
    if stems is not None:
        from spec.root_qi import STEM_WUXING
        from engines.cong_ge_gates import SHISHEN_CLASSES
        # 检查是否有逆神透干（不是印比，不是所从之神）
        reverse_shen = {
            "官杀": ["食伤", "印"],  # 从杀忌食伤、印
            "财": ["比", "印", "官杀"],  # 从财忌比劫、印、官杀
            "食伤": ["印", "官杀"],  # 从儿忌印、官杀
            "印比": ["官杀", "财"],  # 从强忌官杀、财
        }
        for shen in reverse_shen.get(family, []):
            # 印透干：虚透被制不算减项
            if shen == "印":
                # 检查是否虚透被制
                yin_xu = _yin_xu_tou_bei_zhi(stems, [], day_wx)
                if yin_xu:
                    continue  # 虚透被制，不算减项
            cls = SHISHEN_CLASSES[day_wx][shen]
            for i, s in enumerate(stems):
                if i == 2:  # 跳过日干
                    continue
                if STEM_WUXING.get(s) in cls:
                    n += 1
                    break  # 每类逆神只算一次

    return n



def _yin_xu_tou_bei_zhi(stems, branches, day_wx):
    """判印星是否虚透被制（无根+被克）"""
    from spec.root_qi import STEM_WUXING, BENQI
    yin_wuxing = WUXING_OF[day_wx]["印"]
    
    # 找透干的印星
    yin_stems = []
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) == yin_wuxing:
            yin_stems.append((i, s))
    
    if not yin_stems:
        return False
    
    # 检查印星是否有本气根（地支本气=印星）
    has_root = False
    for b in branches:
        if BENQI.get(b) == yin_wuxing:
            has_root = True
            break
    
    if has_root:
        return False  # 有本气根，破格
    
    # 检查是否被克：财星克印（紧贴）
    cai_wuxing = WUXING_OF[day_wx]["财"]
    for i, s in enumerate(stems):
        if i == 2: continue
        if STEM_WUXING.get(s) == cai_wuxing:
            for yin_i, yin_s in yin_stems:
                if abs(i - yin_i) == 1:  # 紧贴
                    return True
    
    return False


def cong_ge_pan(shi_dict: dict, stems: list, day_stem: str, month_branch: str, root_qi_val: float, branches: list = None):
    """
    从格族判定总入口
    返回 (family, confidence, reason_tag)
    """
    day_wx = STEM_WUXING[day_stem]

    # 硬闸：日主有根则不从（交给正格或专旺型）
    if root_qi_val > 0:
        return None

    # 合并印+比为"印比"键，删除独立键避免干扰
    if "印" in shi_dict or "比" in shi_dict:
        shi_dict["印比"] = shi_dict.get("印", 0) + shi_dict.get("比", 0)
        shi_dict.pop("印", None)
        shi_dict.pop("比", None)

    # 找主势
    main_family = max(shi_dict.items(), key=lambda kv: kv[1])[0]

    # F1 从杀
    if main_family == "官杀":
        # 硬闸① 印透化煞（只看透干，藏印不拦）
        if _tou_gan(stems, day_wx, "印"):
            return ("从杀", "REJECT", "F1①·印透化煞")
        # 减项计数
        demote = _demote_count(shi_dict, "官杀", month_branch, day_wx, stems)
        if shi_dict.get("食伤", 0) > 0:
            demote = max(demote, 1)  # 食伤有势→至少MID_1
        # 分级
        if demote == 0:
            conf = "CONFIRMED"
        elif demote == 1:
            conf = "MID_1"
        elif demote == 2:
            conf = "MID_2"
        else:
            conf = "REJECT"
        return ("从杀", conf, f"从杀·减项{demote}")

    # F2 从财
    if main_family == "财":
        if _tou_gan(stems, day_wx, "比"):
            return ("从财", "REJECT", "F2①·比劫争财")
        # 印透硬闸：印虚透被制不算破格（印无根+被克）
        if _tou_gan(stems, day_wx, "印") and not _yin_xu_tou_bei_zhi(stems, branches or [month_branch], day_wx):
            return ("从财", "REJECT", "F2②·印透生身")
        demote = _demote_count(shi_dict, "财", month_branch, day_wx, stems)
        if demote == 0:
            conf = "CONFIRMED"
        elif demote == 1:
            conf = "MID_1"
        elif demote == 2:
            conf = "MID_2"
        else:
            conf = "REJECT"
        return ("从财", conf, f"从财·减项{demote}")

    # F3 从儿
    if main_family == "食伤":
        if _tou_gan(stems, day_wx, "印"):
            return ("从儿", "REJECT", "F3①·枭夺食")
        demote = _demote_count(shi_dict, "食伤", month_branch, day_wx, stems)
        if demote == 0:
            conf = "CONFIRMED"
        elif demote == 1:
            conf = "MID_1"
        elif demote == 2:
            conf = "MID_2"
        else:
            conf = "REJECT"
        return ("从儿", conf, f"从儿·减项{demote}")

    # F4 从强：印比势最大 ∧ root_qi==0 ∧ 印比占比≥75%
    if main_family == "印比":
        if root_qi_val > 0:
            return None  # 交给专旺型
        
        # 新增：印比占比≥75%（8字里至少6个是印比）
        yin_wx = WUXING_OF[day_wx]["印"]
        bi_wx = day_wx  # 比劫=日主同五行
        yin_bi_count = 0
        for s in stems:
            if STEM_WUXING.get(s) in {yin_wx, bi_wx}:
                yin_bi_count += 1
        for b in branches:
            from spec.root_qi import BENQI
            if BENQI.get(b) in {yin_wx, bi_wx}:
                yin_bi_count += 1
        if yin_bi_count < 6:  # <75%（6/8=75%）
            return None  # 印比未到满盘，退回正格
        
        # F4从强：只要求root_qi==0，不要求无气（印比是所从之神）
        demote = _demote_count(shi_dict, "印比", month_branch, day_wx, stems)
        if demote == 0:
            conf = "CONFIRMED"
        elif demote == 1:
            conf = "MID_1"
        elif demote == 2:
            conf = "MID_2"
        else:
            conf = "REJECT"
        return ("从强", conf, f"从强·减项{demote}")

    return ("正格", "REJECT", "势不专一")
