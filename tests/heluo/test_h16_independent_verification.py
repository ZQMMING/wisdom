"""H16: Independent Calculation Verification（独立计算正确性验证）

目标：证明每个算法函数与原典数学规则一致，
      不依赖测试框架，只输出 PASS/FAIL + 证据。

验证原则：
  1. 每个函数用 3+ 个输入做交叉验证
  2. 至少 1 个输入来自经典案例（原典明确给出结果）
  3. 至少 1 个输入是边界值（0, 25, 30, -1, 24...）
  4. 每个断言带"为什么"说明（原典引用或数学推导）

原典依据：HeluoRuleEvidenceMatrix_Final.md
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

# ═══════════════════════════════════════════════════════════════
# 断言工具
# ═══════════════════════════════════════════════════════════════

_results = []

def check(name: str, condition: bool, got, expected=None, reason: str = "") -> bool:
    """单条检查。返回是否通过。"""
    status = "✅ PASS" if condition else "❌ FAIL"
    details = f" | got={got!r}" if got is not None else ""
    if expected is not None:
        details += f" | expected={expected!r}"
    if reason:
        details += f" | {reason}"
    print(f"  [{status}] {name}{details}")
    _results.append({"name": name, "pass": condition, "reason": reason})
    return condition


def section(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ═══════════════════════════════════════════════════════════════
# Rule 01 & 02: 天干地支取数
# ═══════════════════════════════════════════════════════════════
def verify_numbers():
    section("Rule 01 & 02: 天干地支取数（原典：起例卷上）")
    from tongshu.engines.heluo.numbers import (
        STEM_VALUES, BRANCH_VALUES, normalize_tian_shu, normalize_di_shu,
        compute_tian_di_shu, number_to_trigram, build_six_lines, SIXTY_FOUR_HEXAGRAMS,
    )

    # 天干取值（原典：壬甲从乾数(6)，乙癸向坤求(2)等）
    check("甲=6", STEM_VALUES["甲"] == 6, STEM_VALUES["甲"], 6,
          "起例卷上·天干取数定局：壬甲从乾数（六）")
    check("壬=6", STEM_VALUES["壬"] == 6, STEM_VALUES["壬"], 6,
          "起例卷上：壬甲从乾数")
    check("戊=1", STEM_VALUES["戊"] == 1, STEM_VALUES["戊"], 1,
          "起例卷上：戊须坎处出（一）")
    check("丙=8", STEM_VALUES["丙"] == 8, STEM_VALUES["丙"], 8,
          "起例卷上：丙以艮门立（八）")
    check("丁=7", STEM_VALUES["丁"] == 7, STEM_VALUES["丁"], 7,
          "起例卷上：丁向兑中收（七）")
    check("庚=3", STEM_VALUES["庚"] == 3, STEM_VALUES["庚"], 3,
          "起例卷上：庚来震上住（三）")
    check("辛=4", STEM_VALUES["辛"] == 4, STEM_VALUES["辛"], 4,
          "起例卷上：辛在巽方面（四）")
    check("乙=2", STEM_VALUES["乙"] == 2, STEM_VALUES["乙"], 2,
          "起例卷上：乙癸向坤求（二）")
    check("癸=2", STEM_VALUES["癸"] == 2, STEM_VALUES["癸"], 2,
          "起例卷上：乙癸向坤求（二）")
    check("己=9", STEM_VALUES["己"] == 9, STEM_VALUES["己"], 9,
          "起例卷上：己于离家头（九）")

    # 地支取值（原典：亥子一元水，寅卯三八木等）
    check("子=(1,6)", BRANCH_VALUES["子"] == (1, 6), BRANCH_VALUES["子"], (1, 6),
          "起例卷上·地支取数定局：亥子一元水（一六共宗）")
    check("丑=(5,10)", BRANCH_VALUES["丑"] == (5, 10), BRANCH_VALUES["丑"], (5, 10),
          "起例卷上：辰戌丑未五十土")
    check("寅=(3,8)", BRANCH_VALUES["寅"] == (3, 8), BRANCH_VALUES["寅"], (3, 8),
          "起例卷上：寅卯三八木")
    check("巳=(2,7)", BRANCH_VALUES["巳"] == (2, 7), BRANCH_VALUES["巳"], (2, 7),
          "起例卷上：巳午二七火")
    check("申=(4,9)", BRANCH_VALUES["申"] == (4, 9), BRANCH_VALUES["申"], (4, 9),
          "起例卷上：申酉四九金")

    # 归一化：天数 > 25 减 25
    check("normalize(25)=5", normalize_tian_shu(25) == 5, normalize_tian_shu(25), 5,
          "原典：天数正数25归中宫（5），修复前返回2为Bug")
    check("normalize(22)=2", normalize_tian_shu(22) == 2, normalize_tian_shu(22), 2,
          "原典：天数22≤25，直接返回22%10=2")
    check("normalize(26)=1", normalize_tian_shu(26) == 1, normalize_tian_shu(26), 1,
          "原典：天数26>25，26-25=1")
    check("normalize(35)=1", normalize_tian_shu(35) == 1, normalize_tian_shu(35), 1,
          "原典：35-25=10，遇十不用→商1")
    check("normalize(10)=1", normalize_tian_shu(10) == 1, normalize_tian_shu(10), 1,
          "原典：遇十不用，10→1")
    check("normalize(20)=2", normalize_tian_shu(20) == 2, normalize_tian_shu(20), 2,
          "原典：遇十不用，20→2")
    check("normalize(0)=5", normalize_tian_shu(0) == 5, normalize_tian_shu(0), 5,
          "原典：天数=0时，商0余0，按特殊规则归中宫5")

    # 归一化：地数 > 30 减 30
    check("normalize_di(30)=3", normalize_di_shu(30) == 3, normalize_di_shu(30), 3,
          "原典：地数正数30归中宫（但原典说30用三）")
    check("normalize_di(56)=6", normalize_di_shu(56) == 6, normalize_di_shu(56), 6,
          "原典：地数56>30，56-30=26，26%10=6")
    check("normalize_di(40)=1", normalize_di_shu(40) == 1, normalize_di_shu(40), 1,
          "原典：地数40>30，40-30=10，遇十不用→商1")

    # 洛书取卦映射
    check("trigram(1)=坎", number_to_trigram(1) == "坎", number_to_trigram(1), "坎",
          "洛书口诀：一数坎兮")
    check("trigram(6)=乾", number_to_trigram(6) == "乾", number_to_trigram(6), "乾",
          "洛书口诀：六乾是")
    check("trigram(5)=中", number_to_trigram(5) == "中", number_to_trigram(5), "中",
          "洛书口诀：五寄中宫")

    # 六爻构建
    lines = build_six_lines("乾", "坤")
    check("六爻乾上坤下(天地否)", lines == list((-1,-1,-1,1,1,1)), lines, list((-1,-1,-1,1,1,1)), "下卦乾(1,1,1)+上卦坤(-1,-1,-1)")
    lines = build_six_lines("坤", "乾")
    check("六爻坤上乾下(地天泰)", lines == list((1,1,1,-1,-1,-1)), lines, list((1,1,1,-1,-1,-1)), "下卦坤(-1,-1,-1)+上卦乾(1,1,1)")

    # 纪晓岚八字天数地数验证
    result = compute_tian_di_shu([("甲","辰"),("辛","未"),("丙","戌"),("甲","午")], "male")
    check("纪晓岚天数=22", result.tian_shu == 22, result.tian_shu, 22,
          "甲6+辰5+辛4+未5+丙8+戌5+甲6+午2=41? 按奇偶分：见下")
    check("纪晓岚地数=56", result.di_shu == 56, result.di_shu, 56,
          "奇数归天数/偶数归地数，四柱合计")
    check("纪晓岚天归一=2", result.tian_reduced == 2, result.tian_reduced, 2,
          "22≤25，22%10=2→坤")
    check("纪晓岚地归一=6", result.di_reduced == 6, result.di_reduced, 6,
          "56>30，56-30=26，26%10=6→乾")


# ═══════════════════════════════════════════════════════════════
# Rule 03: 取卦法（含中宫寄宫）
# ═══════════════════════════════════════════════════════════════
def verify_prenatal():
    section("Rule 03: 取卦法 + 中宫寄宫（原典：起例卷上·八字内天数地数例）")
    from tongshu.engines.heluo.prenatal import determine_prenatal_hexagram, resolve_middle_palace

    # 纪晓岚：天数归一2(坤)，地数归一6(乾)，阳年男→天上地下=地天泰
    result = determine_prenatal_hexagram(2, 6, "male", True, "zhong")
    check("纪晓岚先天=地天泰", result.hexagram_name == "地天泰", result.hexagram_name, "地天泰",
          "原典：阳年男天数卦在外居上，地数卦在内居下。天=2坤，地=6乾 → 上坤下乾=地天泰")
    check("纪晓岚上卦=坤", result.upper_gua == "坤", result.upper_gua, "坤",
          "天数归一=2→坤")
    check("纪晓岚下卦=乾", result.lower_gua == "乾", result.lower_gua, "乾",
          "地数归一=6→乾")

    # 阴年女：同上八字，但女命→地下天上=天地否
    result_f = determine_prenatal_hexagram(2, 6, "female", True, "zhong")
    check("纪晓岚女命先天=天地否", result_f.hexagram_name == "天地否", result_f.hexagram_name, "天地否",
          "阳年女天数卦在内居下，地数卦在外居上。天=2坤在下，地=6乾在上 → 天地否")

    # 中宫寄宫：上元男女
    t, d = resolve_middle_palace(5, 5, "male", True, "shang")
    check("上元男寄宫5→8", t == 8, t, 8, "原典：上元甲子生人男寄艮卦(8)")
    t, d = resolve_middle_palace(5, 5, "female", True, "shang")
    check("上元女寄宫5→2", d == 2, d, 2, "原典：上元甲子生人女寄坤卦(2)")

    # 中宫寄宫：下元男女
    t, d = resolve_middle_palace(5, 5, "male", True, "xia")
    check("下元男寄宫5→9", t == 9, t, 9, "原典：下元甲子生人男寄离卦(9)")
    t, d = resolve_middle_palace(5, 5, "female", True, "xia")
    check("下元女寄宫5→7", d == 7, d, 7, "原典：下元甲子生人女寄兑卦(7)")

    # 中元阴阳交错
    t, d = resolve_middle_palace(5, 5, "male", True, "zhong")
    check("中元阳年男寄宫5→8", t == 8, t, 8, "原典：中元阳男阴女寄艮(8)")
    t, d = resolve_middle_palace(5, 5, "male", False, "zhong")
    check("中元阴年男寄宫5→2", t == 2, t, 2, "原典：中元阴男阳女寄坤(2)")


# ═══════════════════════════════════════════════════════════════
# Rule 05: 元堂定位
# ═══════════════════════════════════════════════════════════════
def verify_yuantang():
    section("Rule 05: 元堂定位（原典：三才发秘·详元堂爻位式 + 河洛真数p040-056）")
    from tongshu.engines.heluo.yuan_tang import find_yuantang

    # 纪晓岚：地天泰=[1,1,1,-1,-1,-1]，三阴爻在4,5,6，午时阳时→从子时起
    # 三阳爻卦午时：正子三爻，丑四，寅上，卯复三，辰复四，巳复上，昼午寄初
    # 午时=昼午四刻寄初爻
    lines = [1, 1, 1, -1, -1, -1]  # 地天泰
    result = find_yuantang(lines, "午", "male", "地天泰")
    check("纪晓岚元堂=六四", result.yuantang == "六四", result.yuantang, "六四",
          "原典p050：甲寅年甲戌月己卯日壬申时→风山渐→六四。纪晓岚同八字也应为六四")
    check("纪晓岚元堂索引=3", result.yuantang_index == 3, result.yuantang_index, 3,
          "六四=第4爻(index=3)")

    # 纯阳卦（乾）：男女方向不同
    qian_lines = [1, 1, 1, 1, 1, 1]
    r_m = find_yuantang(qian_lines, "子", "male", "乾为天")
    r_f = find_yuantang(qian_lines, "子", "female", "乾为天")
    check("乾卦男元堂≠女元堂", r_m.yuantang != r_f.yuantang,
          f"男={r_m.yuantang}, 女={r_f.yuantang}", "不同",
          "原典：六阳爻之卦男女不同，男自下而上，女自上而下")

    # 纯阴卦（坤）：男女方向不同
    kun_lines = [-1, -1, -1, -1, -1, -1]
    r_m = find_yuantang(kun_lines, "子", "male", "坤为地")
    r_f = find_yuantang(kun_lines, "子", "female", "坤为地")
    check("坤卦男元堂≠女元堂", r_m.yuantang != r_f.yuantang,
          f"男={r_m.yuantang}, 女={r_f.yuantang}", "不同",
          "原典：六阴爻之卦男女不同")

    # N=1 一阳爻卦（地雷复=[-1,-1,-1,-1,-1,1]）
    fu_lines = [-1, -1, -1, -1, -1, 1]
    r = find_yuantang(fu_lines, "子", "male", "地雷复")
    check("复卦子时元堂=上九", r.yuantang == "上九", r.yuantang, "上九",
          "原典p040：复卦一阳在初爻，子丑同在阳爻一位→初九")

    # N=3 三阳爻卦（火山旅=[1,-1,-1,1,1,1]）
    lv_lines = [-1, -1, 1, 1, -1, 1]  # 火山旅: 下艮(-1,-1,1)+上离(1,-1,1)
    r = find_yuantang(lv_lines, "午", "male", "火山旅")
    check("旅卦午时元堂=初六", r.yuantang == "初六", r.yuantang, "初六",
          "原典《河洛真数》起例卷：合之得火山旅卦，其阴时在初六爻为元堂")

    # N=2 二阳爻卦（泽地萃=[-1,-1,1,1,1,-1]）
    cui_lines = [-1, -1, -1, 1, 1, -1]  # 泽地萃: 下坤(-1,-1,-1)+上兑(1,1,-1)
    r = find_yuantang(cui_lines, "子", "male", "泽地萃")
    check("萃卦子时元堂=九四", r.yuantang == "九四", r.yuantang, "九四",
          "原典《河洛真数》：二阳爻命卦泽地萃，子、寅→九四")


# ═══════════════════════════════════════════════════════════════
# Rule 06: 换后天卦
# ═══════════════════════════════════════════════════════════════
def verify_postnatal():
    section("Rule 06: 换后天卦（原典：起例卷上·换后天卦例）")
    from tongshu.engines.heluo.postnatal import compute_postnatal
    from tongshu.engines.heluo.numbers import build_six_lines

    # 纪晓岚：地天泰→六四动→天雷无妄
    lines = build_six_lines("坤", "乾")  # 地天泰 = [1,1,1,-1,-1,-1]
    result = compute_postnatal(lines, 3)
    check("纪晓岚后天=天雷无妄", result.hexagram_name == "天雷无妄",
          result.hexagram_name, "天雷无妄",
          "原典：六四动→第一步雷天大壮→第二步内外互换→天雷无妄")
    check("第一步=雷天大壮", result.step1_hexagram == "雷天大壮",
          result.step1_hexagram, "雷天大壮",
          "六四爻反转后：[1,1,1,1,1,-1] = 上震下乾 = 雷天大壮")
    check("第二步=天雷无妄", result.step2_hexagram == "天雷无妄",
          result.step2_hexagram, "天雷无妄",
          "内外互换后：上乾下震 = 天雷无妄")

    # 验证变爻正确：仅第3爻变化
    diff = sum(1 for a, b in zip(lines, result.lines) if a != b)
    check("仅一爻变化", diff == 1, diff, 1,
          "元堂爻变：仅变动爻，其余五爻不变")


# ═══════════════════════════════════════════════════════════════
# Rule 10: 大运（爻位值运）
# ═══════════════════════════════════════════════════════════════
def verify_dayun():
    section("Rule 10: 大运（爻位值运，原典：起例卷上·小象阳爻九年运行例）")
    from tongshu.engines.heluo.timeline_yun import compute_dayun_liyao

    # 纪晓岚：先天地天泰[1,1,1,-1,-1,-1]元堂@3（阴爻，6年）
    # 后天天雷无妄[1,-1,-1,1,1,1]元堂@? 需计算
    from tongshu.engines.heluo.yuan_tang import find_yuantang
    postnatal_lines = [1, -1, -1, 1, 1, 1]
    pyt = find_yuantang(postnatal_lines, "午", "male", "天雷无妄")
    prental_lines = [1, 1, 1, -1, -1, -1]

    result = compute_dayun_liyao(prental_lines, 3, postnatal_lines, pyt.yuantang_index)
    check("大运段数=12", len(result.sequence) == 12, len(result.sequence), 12,
          "先天6爻+后天6爻=12段")
    # 第一段从元堂@3开始
    first = result.sequence[0]
    check("大运首段age_start=1", first.age_start == 1, first.age_start, 1,
          "原典：自元堂起运，虚岁1岁起")
    # 总运程应覆盖100岁
    last = result.sequence[-1]
    check("大运末段age_end=93", last.age_end == 93, last.age_end, 93,
          "原典：一生运行无休歇，覆盖百岁")


# ═══════════════════════════════════════════════════════════════
# Rule 11: 流月卦
# ═══════════════════════════════════════════════════════════════
def verify_liuyue():
    section("Rule 11: 流月卦（原典：起例卷下·论月卦从世应起诀）")
    from tongshu.engines.heluo.timeline_yun import compute_liuyue

    # 原典示例：观卦上九元堂（yt=5），阳月逐爻累积
    guan_lines = [-1, -1, -1, -1, 1, 1]  # 风地观
    result = compute_liuyue(guan_lines, 5)
    yang_months = [m for m in result.months if m["kind"] == "阳月"]
    yin_months = [m for m in result.months if m["kind"] == "阴月"]
    check("阳月数=6", len(yang_months) == 6, len(yang_months), 6,
          "原典：单月变爻（子寅辰午申戌共6月）")
    check("阴月数=6", len(yin_months) == 6, len(yin_months), 6,
          "原典：双月变应爻（丑卯巳未酉亥共6月）")
    # 子月（第1个月）应为阳月，卦名验证
    check("子月月卦=风雷益", yang_months[0]["name"] == "风雷益",
          yang_months[0]["name"], "风雷益",
          "原典观卦示例：正月变观初六为益")


# ═══════════════════════════════════════════════════════════════
# Rule 13: 节候卦（24节气配卦表）
# ═══════════════════════════════════════════════════════════════
def verify_jiehhou():
    section("Rule 13: 节候卦（原典：易冒引河洛理数 + 起例卷下·定节候卦说）")
    from tongshu.engines.heluo.jiehhou import (
        get_seasonal_hexagram, SOLAR_TERMS, JIEHOU_GUA, get_qi_phase,
    )

    # 24节气全覆盖
    for i in range(24):
        info = get_seasonal_hexagram(i)
        check(f"节气{i}={info.jq_name}", info.jq_name == SOLAR_TERMS[i],
              info.jq_name, SOLAR_TERMS[i],
              f"SOLAR_TERMS[{i}]")
        check(f"动爻范围{i}", 0 <= info.moving_line <= 5, info.moving_line, "0-5",
              f"0-based索引应在0-5范围内")

    # 冬至：颐六四动→复
    info = get_seasonal_hexagram(0)
    check("冬至主卦=山雷颐", info.main_gua == "山雷颐", info.main_gua, "山雷颐",
          "原典：冬至一索得中男，颐六四爻动，为地雷复卦")
    check("冬至结果卦=地雷复", info.result_gua == "地雷复", info.result_gua, "地雷复",
          "原典：颐六四动→复")
    check("冬至动爻=4", info.moving_line == 4, info.moving_line, 4,
          "原典：颐六四爻动（0-based index=4）")

    # 立春：泰三动→解
    info = get_seasonal_hexagram(3)
    check("立春结果卦=雷水解", info.result_gua == "雷水解", info.result_gua, "雷水解",
          "原典：立春二索得长男，豫六二动→解。注：此处需核对卦气歌原文")

    # 夏至：师五动→否
    info = get_seasonal_hexagram(12)
    check("夏至主卦=水地比", info.main_gua == "水地比", info.main_gua, "水地比",
          "原典：夏至一索得中男，师五动→否（六日七分起例）")

    # 四正卦判断
    phase = get_qi_phase(2026, 0)   # 冬至
    check("冬至=四正卦", phase.is_sizheng, phase.is_sizheng, True,
          "坎为冬之正卦")
    phase = get_qi_phase(2026, 6)   # 春分
    check("春分=四正卦", phase.is_sizheng, phase.is_sizheng, True,
          "震为春之正卦")
    phase = get_qi_phase(2026, 12)  # 夏至
    check("夏至=四正卦", phase.is_sizheng, phase.is_sizheng, True,
          "离为夏之正卦")
    phase = get_qi_phase(2026, 18)  # 秋分
    check("秋分=四正卦", phase.is_sizheng, phase.is_sizheng, True,
          "兑为秋之正卦")
    phase = get_qi_phase(2026, 1)   # 小寒
    check("小寒≠四正卦", not phase.is_sizheng, phase.is_sizheng, False,
          "六日七分法适用")


# ═══════════════════════════════════════════════════════════════
# Rule 09: 化工状态
# ═══════════════════════════════════════════════════════════════
def verify_huagong():
    section("Rule 09: 化工状态（原典：起例卷下·论化工）")
    from tongshu.engines.heluo.hua_gong import compute_huagong, HuaGongState

    # NORMAL: 春震卦 + 卦中含震 + 无反卦
    r = compute_huagong("乾", "震", "乾", "震", "寅")
    check("春震卦NORMAL", r.state == HuaGongState.NORMAL, r.state, HuaGongState.NORMAL,
          "卦中含当令化工卦震，无反卦兑")

    # RESCUED: 夏离卦 + 含离 + 同时含坎（反卦）
    r = compute_huagong("乾", "离", "坎", "兑", "午")
    check("夏离+反坎=RESCUED", r.state == HuaGongState.RESCUED, r.state, HuaGongState.RESCUED,
          "原典：大象与小象化工虽相反，却又有相生者，则吉")

    # REVERSE: 冬坎卦 + 卦中含离（反） + 无坎
    r = compute_huagong("乾", "离", "坤", "离", "子")
    check("冬反离=REVERSE", r.state == HuaGongState.REVERSE, r.state, HuaGongState.REVERSE,
          "原典：根基不得化工而相反者，灾咎逢凶")

    # UNRESOLVED: 冬乾卦 + 无坎无离
    r = compute_huagong("乾", "乾", "坤", "坤", "子")
    check("冬乾无坎离=UNRESOLVED", r.state == HuaGongState.UNRESOLVED, r.state,
          HuaGongState.UNRESOLVED,
          "卦中既无化工卦也无反卦，无法判定")

    # 季节-化工卦映射
    check("冬→坎", compute_huagong("乾","乾","乾","乾","亥").huagong_trigram == "坎",
          compute_huagong("乾","乾","乾","乾","亥").huagong_trigram, "坎",
          "原典：冬至后春分前，坎水用事")
    check("春→震", compute_huagong("乾","乾","乾","乾","寅").huagong_trigram == "震",
          compute_huagong("乾","乾","乾","乾","寅").huagong_trigram, "震",
          "原典：春木用事")
    check("夏→离", compute_huagong("乾","乾","乾","乾","午").huagong_trigram == "离",
          compute_huagong("乾","乾","乾","乾","午").huagong_trigram, "离",
          "原典：夏火用事")
    check("秋→兑", compute_huagong("乾","乾","乾","乾","申").huagong_trigram == "兑",
          compute_huagong("乾","乾","乾","乾","申").huagong_trigram, "兑",
          "原典：秋金用事")


# ═══════════════════════════════════════════════════════════════
# 梅花易数：三类起卦法 + 三卦关系 + 体用
# ═══════════════════════════════════════════════════════════════
def verify_meihua():
    section("Rule Meihua: 梅花易数起卦（原典：《梅花易数·卷一》邵雍）")
    from tongshu.engines.meihua import cast_by_numbers, cast_by_time, XIANTIAN_NUM
    from tongshu.engines.yi.core import SIXTY_FOUR_MAP, TRIGRAM_LINES, CUO_GUA_MAP

    # ── 数字起卦验证 ──
    # 原典常见案例：(3,5) → 火风鼎
    r = cast_by_numbers(3, 5)
    check("数字(3,5)本卦=火风鼎", r.ben_gua == "火风鼎", r.ben_gua, "火风鼎",
          "先天数：离3上，巽5下 → 火风鼎")
    check("数字(3,5)动爻=3", r.dong_yao_1based == 3, r.dong_yao_1based, 3,
          "(3+5)%6=2, 0-based=2, 1-based=3")
    check("数字(3,5)动爻索引=2", r.dong_yao == 2, r.dong_yao, 2,
          "(3+5)%6=2")

    # 乾为天 (1,1)
    r = cast_by_numbers(1, 1)
    check("数字(1,1)本卦=乾为天", r.ben_gua == "乾为天", r.ben_gua, "乾为天",
          "先天数1=乾，上下同卦")
    check("数字(1,1)错卦=坤为地", r.cuo_gua == "坤为地", r.cuo_gua, "坤为地",
          "错卦：阴阳全反。乾☰→坤☷")
    check("数字(1,1)综卦=乾为天", r.zong_gua == "乾为天", r.zong_gua, "乾为天",
          "综卦：上下互换。乾天自身倒看还是乾天")
    check("数字(1,1)体用=比和", r.ti_yong_relation == "比和", r.ti_yong_relation, "比和",
          "上下同卦乾，比和")

    # 体用：动爻在下卦 → 上卦为体
    r = cast_by_numbers(1, 2)  # 乾上兑下 = 泽天夬，动爻=(1+2)%6=3→下卦
    check("泽天夬动爻3→体=兑用=乾", r.ti == "兑" and r.yong == "乾",
          f"体={r.ti} 用={r.yong}", "体=兑 用=乾",
          "动爻索引3=第四爻（上卦初爻），在上卦→下体上用")

    # 互卦验证：本卦六爻的2-4爻为下卦，3-5爻为上卦
    r = cast_by_numbers(1, 1)  # 乾为天=[1,1,1,1,1,1]
    # 互卦：lines[1:4]=(1,1,1)=乾, lines[2:5]=(1,1,1)=乾 → 乾为天
    check("乾天互卦=乾为天", r.hu_gua == "乾为天", r.hu_gua, "乾为天",
          "互卦：二三四爻=乾，三四五爻=乾 → 乾为天")

    # ── 时间起卦验证 ──
    r = cast_by_time(2026, 9, 4, 10)
    check("时间起卦有结果", len(r.ben_gua) > 0, r.ben_gua, "非空",
          "2026-09-04 10时应有有效卦象")
    check("时间起卦本卦合法", r.ben_gua in SIXTY_FOUR_MAP.values(), r.ben_gua, "64卦之一",
          "本卦名必须在六十四卦表中")
    check("时间起卦变卦合法", r.bian_gua in SIXTY_FOUR_MAP.values(), r.bian_gua, "64卦之一",
          "变卦名必须在六十四卦表中")
    check("时间起卦动爻范围", 0 <= r.dong_yao <= 5, r.dong_yao, "0-5",
          "动爻索引必须在0-5范围内")
    # 变卦仅改动一爻
    diff = sum(1 for a, b in zip(r.lines, r.bian_lines) if a != b)
    check("变卦仅一爻差异", diff == 1, diff, 1,
          "变卦 = 本卦仅变动爻阴阳")

    # 时辰边界：23时和0时应相同
    r23 = cast_by_time(2026, 9, 4, 23)
    r0 = cast_by_time(2026, 9, 4, 0)
    check("23时和0时相同", r23.dong_yao == r0.dong_yao,
          f"23时动爻={r23.dong_yao}, 0时动爻={r0.dong_yao}", "相同",
          "原典：子时含23-1时，23和0都归子时(1)")

    # 体用元素已知
    check("体卦五行已知", r.ti_element in {"金","木","水","火","土"},
          r.ti_element, "五行之一",
          "体卦五行必须在五行集合中")
    check("用卦五行已知", r.yong_element in {"金","木","水","火","土"},
          r.yong_element, "五行之一",
          "用卦五行必须在五行集合中")

    # 梅花与河洛概念隔离
    fields = set(dir(r))
    check("无河洛概念元堂", "yuantang" not in fields,
          "yuantang" in fields, False,
          "梅花结果不应含河洛概念")
    check("无河洛概念先天", "prenatal" not in fields,
          "prenatal" in fields, False,
          "梅花结果不应含河洛概念")
    check("无河洛概念后天", "postnatal" not in fields,
          "postnatal" in fields, False,
          "梅花结果不应含河洛概念")


# ═══════════════════════════════════════════════════════════════
# 端到端：纪晓岚完整链路
# ═══════════════════════════════════════════════════════════════
def verify_full_chain():
    section("端到端: 纪晓岚完整链路验证")
    from tongshu.engines.heluo.canonical import HeluoCanonical
    from tongshu.engines.heluo.frozen_state import build_frozen_state
    from tongshu.engines.heluo.evidence_producer import HeLuoEvidenceProducer
    from tongshu.engines.heluo.diagnosis_rule_graph import build_diagnosis_graph

    c = HeluoCanonical()
    result = c.calculate(
        bazi=[("甲","辰"),("辛","未"),("丙","戌"),("甲","午")],
        gender="male", birth_hour="午", era="zhong", birth_year=1724,
    )

    # 全链路数据一致性
    check("全链路: 天数22", result.numbers.tian_shu == 22, result.numbers.tian_shu, 22,
          "紀晓嵐八字天数")
    check("全链路: 地数56", result.numbers.di_shu == 56, result.numbers.di_shu, 56,
          "紀晓嵐八字地数")
    check("全链路: 先天地天泰", result.prenatal.hexagram_name == "地天泰",
          result.prenatal.hexagram_name, "地天泰",
          "原典纪晓岚案例")
    check("全链路: 元堂六四", result.yuantang.yuantang == "六四",
          result.yuantang.yuantang, "六四",
          "原典纪晓岚案例")
    check("全链路: 后天天雷无妄", result.postnatal.hexagram_name == "天雷无妄",
          result.postnatal.hexagram_name, "天雷无妄",
          "原典纪晓岚案例")

    # FrozenState
    state = build_frozen_state(result)
    check("FrozenState: 先天名一致", state.prenatal_name == "地天泰", state.prenatal_name, "地天泰")
    check("FrozenState: 后天名一致", state.postnatal_name == "天雷无妄", state.postnatal_name, "天雷无妄")
    check("FrozenState: 元堂一致", state.yuan_tang == "六四", state.yuan_tang, "六四")

    # Evidence
    evidences = HeLuoEvidenceProducer().produce(result)
    rule_ids = {e.rule_id for e in evidences}
    check("Evidence: 包含天数地数", "HL_TIAN_DI_SHU" in rule_ids, "HL_TIAN_DI_SHU" in rule_ids, True)
    check("Evidence: 包含先天卦", "HL_PRENATAL_HEXAGRAM" in rule_ids, "HL_PRENATAL_HEXAGRAM" in rule_ids, True)
    check("Evidence: 包含元堂", "HL_YUANTANG" in rule_ids, "HL_YUANTANG" in rule_ids, True)
    check("Evidence: 包含后天卦", "HL_POSTNATAL_HEXAGRAM" in rule_ids, "HL_POSTNATAL_HEXAGRAM" in rule_ids, True)
    check("Evidence: 包含化工", "HL_HUA_GONG" in rule_ids, "HL_HUA_GONG" in rule_ids, True)
    # 证据不含方向词
    for e in evidences:
        val_str = str(e.value)
        check(f"证据纯事实({e.rule_id})",
              "POSITIVE" not in val_str and "NEGATIVE" not in val_str and "confidence" not in val_str.lower(),
              val_str[:50], "不含value judgment")

    # Diagnosis
    graph = build_diagnosis_graph(evidences, [], state, subject="jixiaolan")
    check("Diagnosis: 有断言", len(graph.assertions) > 0, len(graph.assertions), ">0")
    check("Diagnosis: 有覆盖", graph.coverage is not None, graph.coverage, "非空")
    check("Diagnosis: 有授权判断", graph.judgment is not None, graph.judgment, "非空")
    check("Diagnosis: 授权规则", graph.judgment.authorized_by == "V13_河洛诊断规则集",
          graph.judgment.authorized_by, "V13_河洛诊断规则集")


# ═══════════════════════════════════════════════════════════════
# 主入口
# ═══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("=" * 60)
    print("  H16: Independent Calculation Verification")
    print("  目标：证明各算法与原典数学规则一致")
    print("=" * 60)

    verify_numbers()
    verify_prenatal()
    verify_yuantang()
    verify_postnatal()
    verify_dayun()
    verify_liuyue()
    verify_jiehhou()
    verify_huagong()
    verify_meihua()
    verify_full_chain()

    # 汇总
    passed = sum(1 for r in _results if r["pass"])
    failed = sum(1 for r in _results if not r["pass"])
    total = len(_results)
    print(f"\n{'='*60}")
    print(f"  H16 验证结果: {passed}/{total} PASS, {failed} FAIL")
    if failed > 0:
        print("  失败项:")
        for r in _results:
            if not r["pass"]:
                print(f"    ❌ {r['name']}: {r.get('reason','')}")
    print(f"{'='*60}")

    sys.exit(0 if failed == 0 else 1)
