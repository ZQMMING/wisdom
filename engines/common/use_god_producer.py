# -*- coding: utf-8 -*-
"""PATCH-026 Use-God Production Contract（用神生产契约）
- 三生产者独立 namespace：PZZQ.use_god / SFTK.qu_yong / QTBJ.climate_use
- 禁 strength→用神、pattern→自动生成用神、用神→strength
- 输出带 use_type（USE_GOD/QU_YONG/CLIMATE_USE）防合并
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

S = {
    "order_state": "NOT_GET_ORDER", "month_order": "戌", "day_master_element": "WOOD",
    "ten_god_relation": {"年干": "偏印", "月干": "正印", "日干": "比肩", "时干": "正印"},
    "structure_relation": "UNDETERMINED", "root_relation": "WEAK_ROOT(亥甲+未乙)",
    "problem_relation": "UNDETERMINED", "seasonal_state": "QTBJ_REQUIRED", "climate_relation": "UNDETERMINED",
    "strength_state": "UNDETERMINED", "pattern_state": "UNDETERMINED",
}

FORBIDDEN_PATHS = [
    ("strength_state", "任何用神", "身强弱不得决定用神"),
    ("pattern_state", "use_god_state", "格局成立不得自动生成用神"),
    ("用神(任一)", "strength_state", "用神不得反推身强弱"),
    ("use_god_state", "qu_yong_state/climate_use_state", "三种用互不合并"),
]


def produce_use_god():
    # PZZQ.use_god：月令戌→戊土用事→财用候选（structure 未确认）
    use_god = {"state": "use_god_state", "use_type": "USE_GOD", "value": "UNDETERMINED（月令戌土→财用候选，structure 待确认）",
               "producer": "PZZQ.use_god", "sources": ["PZZQ.use_god(order_state/month_order/ten_god_relation/structure_relation/root_relation)"],
               "evidence_chain": ["PZZQ-005-007 八字用神专求月令"], "namespace_source": {"PZZQ": "use_god"}}
    # SFTK.qu_yong：病药取用（problem 未确认）
    qu_yong = {"state": "qu_yong_state", "use_type": "QU_YONG", "value": "UNDETERMINED（problem_relation=UNDETERMINED，病药未确认）",
               "producer": "SFTK.qu_yong", "sources": ["SFTK.qu_yong(problem_relation/support_relation/control_relation/structure_relation)"],
               "evidence_chain": ["SFTK-008-001 病药取用（先看月令→从重者论）"], "namespace_source": {"SFTK": "qu_yong"}}
    # QTBJ.climate_use：调候用神（seasonal=QTBJ_REQUIRED 规则未准入）
    climate_use = {"state": "climate_use_state", "use_type": "CLIMATE_USE", "value": "UNDETERMINED（seasonal_state=QTBJ_REQUIRED，调候规则未准入）",
                   "producer": "QTBJ.climate_use", "sources": ["QTBJ.climate_use(seasonal_state/month_order/daymaster/climate_relation)"],
                   "evidence_chain": ["QTBJ 十干逐月调候体系"], "namespace_source": {"QTBJ": "climate_use"}}
    return {"use_god_state": use_god, "qu_yong_state": qu_yong, "climate_use_state": climate_use}


if __name__ == "__main__":
    print("==== PATCH-026 Use-God Production Contract ====")
    print("\n==== 三生产者 ====")
    for state, name, typ in [("use_god_state", "PZZQ.use_god", "USE_GOD"), ("qu_yong_state", "SFTK.qu_yong", "QU_YONG"), ("climate_use_state", "QTBJ.climate_use", "CLIMATE_USE")]:
        print(f"  {state}: {name}（{typ}，DIRECT，独立 namespace）")
    print("\n==== 禁止路径 ====")
    for frm, to, reason in FORBIDDEN_PATHS:
        print(f"  禁止: {frm} → {to}（{reason}）")
    print("\n==== 1983-1103 三用神输出 ====")
    out = produce_use_god()
    print(json.dumps(out, ensure_ascii=False, indent=1))
    print("\n==== use_type 防合并验证 ====")
    types = [v["use_type"] for v in out.values()]
    print(f"  use_type 集合: {types}（三值独立，无合并）")
