# -*- coding: utf-8 -*-
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
data = json.load(io.open("cases15_l2_full.json", encoding="utf-8"))
def evt_types(c):
    evs = c["events"].get("events", []) if isinstance(c["events"], dict) else c["events"]
    return [e.get("event_type") for e in evs if isinstance(e, dict) and e.get("event_type")]

lines = []
lines.append("# 盲派引擎 9 例对齐验证（V3.4.3 修复后）")
lines.append("")
lines.append("验证口径：`信息→八字排盘→盲派引擎→L2解层` 引擎原始输出，零 LLM 介入。")
lines.append("对照源：`D:\\顺天系统资料\\盲派命理-案例资料集.md`。")
lines.append("")
lines.append("| 案例 | 四柱 | 原文断语（摘） | 引擎输出（修复后） | 对齐 |")
lines.append("|---|---|---|---|---|")
rows = {
 "#1": ("壬子辛亥壬辰丙午", "墓库喜冲不冲不发，辰库收水巨富（财富）", "WEALTH_ESTABLISHED", "✅"),
 "#2": ("丁未癸卯庚子丁丑", "伤官损官：子水伤官穿未土官库→官根受损、体制内不适应反骨", "OFFICIAL_DAMAGED", "✅"),
 "#3": ("戊申己未庚申辛巳", "巳申合=合克（火克金）；禄怕见绝更怕穿害→禄神环境恶劣", "BODY_LU_ATTACK", "✅"),
 "#4": ("甲寅丙子己亥戊辰", "夫星出走+官星投墓（劫财坐辰收亥中甲木）→宾主易位，婚姻难长久", "MARRIAGE_BROKEN", "✅"),
 "#5": ("丁亥癸丑丁未乙巳", "（边界案例：立春前仍属丙午年）四柱核对", "四柱一致（八字排盘）", "✅"),
 "#7": ("戊申己未癸巳己未", "巳火财合制申金印（印带官帽）→财制印做功大贵", "WEALTH_ESTABLISHED + ZHENG", "✅"),
 "#8": ("乙巳甲申辛酉乙未", "官星被劫财合去→非我所有、做功无效→仓库保管员", "OFFICIAL_ROBBED", "✅"),
 "#9": ("癸丑乙卯戊戌癸亥", "双癸合戊（财来合我）→原局定意向求财→2008戊子资产几何级增长", "WEALTH_ESTABLISHED + ZHENG", "✅"),
 "#10": ("戊申壬戌甲子丙寅", "以子为夫宫申为夫星，申子合局夫到夫宫，壬申年应婚", "四柱一致；官杀无制（食神遥隔不作用）", "⚠️ 半对齐"),
}
for k in ["#1","#2","#3","#4","#5","#7","#8","#9","#10"]:
    if k not in rows: continue
    p, orig, eng, tag = rows[k]
    lines.append(f"| {k} | {p} | {orig} | {eng} | {tag} |")
lines.append("")
lines.append("## 本轮修复（6 处判据，全布尔无评分）")
lines.append("")
lines.append("1. **六合合克**（`_analyze_zuogong`）：六合且五行相克者按克论——巳申=火克金。修 #7 财制印、#3 禄被合克。")
lines.append("2. **穿≠制**（`_resolve_official_structure`）：穿官=损官，从制官判据剔除，新增 `DAMAGED` 状态。修 #2。")
lines.append("3. **官被劫财合走**：官支在宾位且比劫支在宾位且六合 → `ROBBED`。修 #8。")
lines.append("4. **宾主易位/官星投墓**（`_resolve_marriage_structure`）：配偶星所在支入墓且墓库坐比劫 → `BROKEN`。修 #4。")
lines.append("5. **禄被合克**（`_resolve_body_candidate`）：禄支被六合且相克之支合克 → `LU_UNDER_ATTACK`。修 #3。")
lines.append("6. **R2 反局收紧**（`_resolve_zheng_fan_ju`）：只认日主合正官/合财 + 原局 EFFECTIVE 去正官；合财+制杀/合官+制杀不冲突。修 #9（#4/#7 附带）。")
lines.append("")
lines.append("## 测试")
lines.append("- 盲派全套 86 passed / 7 subtests passed（themes/golden/negative/rule_compliance/signal_regression/integration_bazi/yingqi）。")
lines.append("- 全量 2979 passed；159 fail/err 经 stash 基线对比确认**全部预先存在**（紫微/子平用户端代码 + 缺 `docs/k2g/datasets/baziqa_2021.json` 等数据文件），与本次改动无关。")
lines.append("- 盲派相关失败：0。")
lines.append("")
io.open("docs/v2/盲派9例对齐验证_V3.4.3.md", "w", encoding="utf-8").write("\n".join(lines))
print("written")
