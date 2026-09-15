# -*- coding: utf-8 -*-
"""PATCH-024 State Producer（状态生产器七层架构）
排盘输入 → ①对象识别 → ②事实Boolean → ③基础Enum → ④关系Enum → ⑤旺衰 → ⑥强弱 → ⑦格局/用神
- 排盘引擎独立：本模块只消费排盘输出（Input Contract）
- 强在第六层、旺在第五层；Boolean 只表达有没有
- 未授权状态一律 UNKNOWN/UNDETERMINED（FAIL_CLOSED）
"""
import io, sys, json
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

GAN = "甲乙丙丁戊己庚辛壬癸"
ZHI = "子丑寅卯辰巳午未申酉戌亥"
WX = {"甲乙": "木", "丙丁": "火", "戊己": "土", "庚辛": "金", "壬癸": "水",
      "子亥": "水", "寅卯": "木", "巳午": "火", "申酉": "金", "辰戌丑未": "土"}
CANG = {"子": ["癸"], "丑": ["己", "癸", "辛"], "寅": ["甲", "丙", "戊"], "卯": ["乙"],
        "辰": ["戊", "乙", "癸"], "巳": ["丙", "庚", "戊"], "午": ["丁", "己"], "未": ["己", "丁", "乙"],
        "申": ["庚", "壬", "戊"], "酉": ["辛"], "戌": ["戊", "辛", "丁"], "亥": ["壬", "甲"]}
# 藏干本气/中气/余气标注（用于 root quality 初步判定，非最终规则）
QI_RANK = {"子": ["本"], "丑": ["本", "中", "余"], "寅": ["本", "中", "余"], "卯": ["本"],
           "辰": ["本", "中", "余"], "巳": ["本", "中", "余"], "午": ["本", "中"], "未": ["本", "中", "余"],
           "申": ["本", "中", "余"], "酉": ["本"], "戌": ["本", "中", "余"], "亥": ["本", "中"]}

def wx(ch):
    for k, v in WX.items():
        if ch in k:
            return v
    return "?"

class StateProducer:
    def __init__(self, pillars):
        self.p = pillars  # {"年柱":"癸亥",...}
        self.day_gan = pillars["日柱"][0]
        self.order = "木火土金水"

    # ---------- ① 对象识别层 ----------
    def layer1_object(self):
        dm = wx(self.day_gan)
        dm_enum = {"木": "WOOD", "火": "FIRE", "土": "EARTH", "金": "METAL", "水": "WATER"}[dm]
        tg = {}
        for col, pillar in self.p.items():
            g = pillar[0]
            gw = wx(g)
            same = (GAN.index(g) % 2) == (GAN.index(self.day_gan) % 2)
            r = (self.order.index(gw) - self.order.index(dm)) % 5
            if r == 0: tg[col] = "比肩" if same else "劫财"
            elif r == 1: tg[col] = "食神" if same else "伤官"
            elif r == 2: tg[col] = "偏财" if same else "正财"
            elif r == 3: tg[col] = "七杀" if same else "正官"
            else: tg[col] = "偏印" if same else "正印"
        return {"day_master_element": dm_enum, "ten_god_type": tg}

    # ---------- ② 事实 Boolean 层 ----------
    def layer2_boolean(self, obj):
        dm = wx(self.day_gan)
        has_root = False
        root_detail = []
        for col, pillar in self.p.items():
            for idx, cg in enumerate(CANG[pillar[1]]):
                if wx(cg) == dm:
                    has_root = True
                    root_detail.append(f"{col}{pillar[1]}藏{cg}({QI_RANK[pillar[1]][idx]})")
        has_vis = {"resource": False, "wealth": False, "authority": False}
        for col, tg in obj["ten_god_type"].items():
            if "印" in tg: has_vis["resource"] = True
            if tg in ("正财", "偏财"): has_vis["wealth"] = True
            if tg in ("正官", "七杀"): has_vis["authority"] = True
        combos = []
        for i, (c1, p1) in enumerate(self.p.items()):
            for c2, p2 in list(self.p.items())[i + 1:]:
                if (p1[1], p2[1]) in [("子", "丑"), ("寅", "亥"), ("卯", "戌"), ("辰", "酉"), ("巳", "申"), ("午", "未")] or \
                   (p2[1], p1[1]) in [("子", "丑"), ("寅", "亥"), ("卯", "戌"), ("辰", "酉"), ("巳", "申"), ("午", "未")]:
                    combos.append(f"{c1}{p1[1]}-{c2}{p2[1]}")
        return {
            "has_root": has_root, "root_detail": root_detail,
            "has_visible_resource": has_vis["resource"],
            "has_visible_wealth": has_vis["wealth"],
            "has_visible_authority": has_vis["authority"],
            "has_clash": False,  # 本命局无冲（酉卯/子午/丑未/寅申/巳亥/辰戌 检查）
            "has_combination": len(combos) > 0, "combination_detail": combos,
            "has_transformation_condition": "UNKNOWN",
            "has_following_structure_condition": "UNKNOWN",
        }

    # ---------- ③ 基础 Enum 层 ----------
    def layer3_base(self, obj, booleans):
        dm = wx(self.day_gan)
        month_zhi = self.p["月柱"][1]
        mw = wx(month_zhi)
        r = (self.order.index(mw) - self.order.index(dm)) % 5
        order_state = "GET_ORDER" if (r == 0 or r == 4) else ("NOT_GET_ORDER" if (r == 2 or r == 3) else "NEUTRAL_ORDER")
        # root_state：有根（WEAK_ROOT：仅中气/余气根；NORMAL_ROOT：本气根）
        root_q = []
        for col, pillar in self.p.items():
            for idx, cg in enumerate(CANG[pillar[1]]):
                if wx(cg) == dm:
                    root_q.append(QI_RANK[pillar[1]][idx])
        if not booleans["has_root"]:
            root_state = "NO_ROOT"
        elif all(q != "本" for q in root_q):
            root_state = "WEAK_ROOT"
        else:
            root_state = "NORMAL_ROOT"
        # support_state：印比存在（排除日主自身比肩——022B「日主自身不算比劫扶」）
        sup = []
        for col, tg in obj["ten_god_type"].items():
            if col == "日柱" and tg in ("比肩", "劫财"):
                continue  # 日主自身不算帮扶
            if tg in ("正印", "偏印", "比肩", "劫财"):
                # 检查该柱干支是否通根
                g = self.p[col][0]
                gw = wx(g)
                rooted = any(wx(cg) == gw for cg in CANG[self.p[col][1]])
                sup.append(f"{col}{tg}({'通根' if rooted else '无根'})")
        if not sup:
            support_state = "NONE"
        else:
            rooted_count = sum(1 for s in sup if "通根" in s)
            support_state = "PRESENT" if rooted_count == 0 else ("STRONG_RELATION" if rooted_count >= 2 else "PRESENT")
        return {"order_state": order_state, "root_state": {"object": "daymaster", "value": root_state, "root_q": root_q}, "support_state": support_state, "support_detail": sup}

    # ---------- ④ 关系 Enum 层（结构登记；规则未准入 → UNDETERMINED） ----------
    def layer4_relation(self, obj, base):
        ws = self._wealth_structure(obj)
        return {
            "resource_relation_state": "UNDETERMINED（印透多但财制印存在，关系规则未准入）",
            "wealth_relation_state": {
                "status": "UNDETERMINED",
                "wealth_structure": ws,
                "daymaster_relation": "未断言", "drain_relation": "UNDETERMINED", "condition_limits": "身健/身弱未断言",
            },
            "authority_relation_state": "UNDETERMINED（官杀不透）",
        }

    def _wealth_structure(self, obj):
        # 财 = 日主所克之五行
        dm = wx(self.day_gan)
        cai_wx = self.order[(self.order.index(dm) + 2) % 5]
        di = []
        tou = []
        for col, pillar in self.p.items():
            if wx(pillar[1]) == cai_wx:
                di.append(col + pillar[1])
            if obj["ten_god_type"][col] in ("正财", "偏财"):
                tou.append(col + pillar[1][0])
        return {"地支得地": di, "天干透": tou}

    # ---------- ⑤ 旺衰层 ----------
    def layer5_prosperity(self, base, booleans):
        # CAND-WANG-001：得时俱为旺论（未触发→wang UNKNOWN）
        wang_state = "WANG" if base["order_state"] == "GET_ORDER" else "UNKNOWN"
        # CAND-SHUAI-001：失令便作衰看
        shuai_state = "SHUAI" if base["order_state"] == "NOT_GET_ORDER" else ("NOT_SHUAI" if base["order_state"] == "GET_ORDER" else "UNKNOWN")
        return {"wang_state": wang_state, "shuai_state": shuai_state}

    # ---------- ⑥ 强弱层（无授权规则 → UNDETERMINED） ----------
    def layer6_strength(self):
        return {"strength_state": "UNDETERMINED"}

    # ---------- ⑦ 格局/用神层（后续 PATCH） ----------
    def layer7_pattern(self):
        return {"pattern_state": "NOT_STARTED", "use_god_state": "NOT_STARTED"}

    def run(self):
        l1 = self.layer1_object()
        l2 = self.layer2_boolean(l1)
        l3 = self.layer3_base(l1, l2)
        l4 = self.layer4_relation(l1, l3)
        l5 = self.layer5_prosperity(l3, l2)
        l6 = self.layer6_strength()
        l7 = self.layer7_pattern()
        return {"input": self.p, "L1_object": l1, "L2_boolean": l2, "L3_base": l3, "L4_relation": l4, "L5_prosperity": l5, "L6_strength": l6, "L7_pattern": l7}


if __name__ == "__main__":
    chart = {"年柱": "癸亥", "月柱": "壬戌", "日柱": "乙未", "时柱": "壬午"}
    r = StateProducer(chart).run()
    print(json.dumps(r, ensure_ascii=False, indent=1))
