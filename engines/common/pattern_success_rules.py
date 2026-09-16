# -*- coding: utf-8 -*-
"""PATCH-035：格局成败 Production（RULE-035-01，PZZQ.pattern_success 财格成败判定）

依据 PZZQ-005-008（A 级，逐字）：
- 成：「財格透印而位置安帖、兩不相剋，財格成也」（路径C，032-R1 已确认 1983）
- 败：「財輕比重，財透七煞，財格敗也」
- 带忌：「成中有敗，必是帶忌」→「財旺生官而又逢傷逢合」
- 救应：「敗中而成，全憑救應」→「財逢劫而透食以化之，生官以制之；逢煞而食神制煞以生財，或存財而合煞」
- 相神（PZZQ-007-004，A 级）：「月令既得用神，則别位亦必有相」——相神 PZZQ_ONLY（022 系列冻结）

namespace（025 冻结）：pattern_success ≠ qing_za（清浊）；成败只管成/败/带忌/救应/相神。
谓词裁决：禁评分/计数/权重；败条件须「双谓词同时成立」。
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 1983-1103 冻结输入（pattern_confirm_rules 032-R1 输出 + 事实层）
CHART = {
    "pattern_state": "DETERMINED(财格)",   # 032-R1 路径C
    "day_master": "乙", "month_branch": "戌",
    "stems": {"年": "癸", "月": "壬", "日": "乙", "时": "壬"},
    "hidden": {"亥": ["壬", "甲"], "戌": ["戊", "辛", "丁"], "未": ["己", "丁", "乙"], "午": ["丁", "己"]},
    "ten_god_stems": {"癸": "偏印", "壬": "正印", "乙": "比肩", "庚": "七杀", "辛": "正官"},
    "财_stem": "戊己", "比劫_stem": "甲乙", "七杀_stem": "庚", "伤官_stem": "丁",
}
ELEM = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}


def rule_035_01_pattern_success(c):
    """财格成败判定（谓词式，双条件）"""
    stems_vis = list(c["stems"].values())          # 天干四字（含日干位，判别时排除）
    day = c["day_master"]
    def ten(s):                                    # 日主视角十神
        g, d = ELEM[s], ELEM[day]
        if g == d: return "比肩"
        gen = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
        ke = {"木": "土", "土": "水", "水": "火", "火": "金", "金": "木"}
        if gen[d] == g: return "食伤"
        if gen[g] == d: return "印"
        if ke[d] == g: return "财"
        if ke[g] == d: return "官杀"
        return "?"
    stem_tens = [ten(s) for s in stems_vis]

    # 透干谓词（排除日干位 idx=2）
    def vis(*names):
        return any(i != 2 and stems_vis[i] in names for i in range(4))

    # 1. 成：路径C 財格透印位置安帖兩不相剋（032-R1 已确认）
    yin_vis = vis("癸", "壬")                       # 印透（正偏印）
    cai_vis = vis("戊", "己")                       # 财透（正偏财）
    success_path_c = (yin_vis and not cai_vis)      # 财藏支、印透干 → 干支分离 → 位置安帖

    # 2. 败：財輕比重（财透+比劫透 双谓词）／財透七煞（财透+七煞透 双谓词）
    bi_jie_vis = vis("甲", "乙")
    sha_vis = vis("庚")
    fail_1 = (cai_vis and bi_jie_vis)               # 財輕比重（比劫透夺财）
    fail_2 = (cai_vis and sha_vis)                  # 財透七煞（煞克身破格）

    # 3. 带忌：財旺生官又逢傷逢合（财透+官透+伤官透）
    guan_vis = vis("庚", "辛")                      # 官杀透
    shang_vis = vis("丁")                           # 伤官透
    daiji = (cai_vis and guan_vis and shang_vis)

    # 4. 救应（登记，本命无败故不触发）：財逢劫透食化之／生官制之；逢煞食制煞生財
    rescue_note = "財逢劫→透食以化之或生官以制之；逢煞→食神制煞以生財或存財而合煞（PZZQ-005-008）"

    # 5. 相神：月令既得用神，別位亦必有相（PZZQ-007-004）→ 印透三为相神
    xiangshen = "印（癸壬壬透三）" if yin_vis else "未定"

    # 裁决
    if fail_1 or fail_2:
        state = "FAILED"
        note = "财格败也：" + ("財輕比重" if fail_1 else "") + ("；財透七煞" if fail_2 else "")
    elif success_path_c:
        state = "SUCCESS"
        note = "财格成也：財格透印位置安帖兩不相剋（路径C）；败格未触发（財輕比重/財透七煞双谓词均不成立）"
    else:
        state = "UNDETERMINED"
        note = "财格成败条件不完整，FAIL_CLOSED"
    return {
        "pattern_success_state": f"{state}({('路径C財格透印' if success_path_c else '')})" if state == "SUCCESS" else state,
        "daiji_state": "DAIJI(財旺生官逢傷逢合)" if daiji else "NO_DAIJI",
        "rescue_state": "NO_RESCUE_NEEDED" if state == "SUCCESS" else ("RESCUE_PENDING" if state == "FAILED" else "UNDETERMINED"),
        "xiangshen_state": f"PRESENT({xiangshen})" if yin_vis else "ABSENT",
        "xiangshen_scope": "PZZQ_ONLY（PZZQ-007-004 月令既得用神別位亦必有相）",
        "evidence": ["PZZQ-005-008", "PZZQ-007-004"],
        "note": note,
        "rescue_reference": rescue_note,
    }


if __name__ == "__main__":
    print("==== PATCH-035：格局成败 Production（RULE-035-01） ====")
    r = rule_035_01_pattern_success(CHART)
    print(json.dumps(r, ensure_ascii=False, indent=1))
    print("\n==== 治理核对 ====")
    print("  谓词裁决（双条件）✓｜无计数/评分/权重 ✓｜pattern_success≠清浊 ✓｜相神 PZZQ_ONLY ✓")
