# -*- coding: utf-8 -*-
"""H10 扩展断法测试（原著优先·K3-447《河洛理数》卷一/卷十）

覆盖：
  ① 金锁银匙歌起数（卷十·原典三例复算：2542/3347/2942）
  ② 四体八体/伏体（卷一·渐卦例）
  ③ 福力层次（卷一·论应其时合其用）
  ④ 五命得卦（卷一·五命得卦）
  ⑤ 论所得卦数吉凶·余数断（卷一 p129-130）
  ⑥ 月令非时论·四时五行盛衰（卷一 p117-119）
  ⑦ 数极京城山林（卷一·详说伏体要旨，标注级）
"""
import pytest

from src.tongshu.engines.heluo import canping as cp
from src.tongshu.engines.heluo import guajie as g


# ── ① 金锁银匙歌起数（卷十·原典三例复算） ──────────────────────

class TestQishu:
    def test_yinshu_yimao_2542(self):
        """戌日寅时，乙卯（纳音水）：2000+500+14(十1零4)+27+1=2542 ✓ 原典例"""
        r = cp.qishu("戌", "寅", "水")
        assert r["total"] == 2542
        assert (r["qian"], r["bai"], r["shi"], r["ling"]) == (2, 5, 4, 2)
        assert r["part"] == "水部"

    def test_shenshi_wuwu_3347(self):
        """申日申时，戊午（纳音火）：2000+1300+18(十1零8)+27+2=3347 ✓ 原典例"""
        r = cp.qishu("申", "申", "火")
        assert r["total"] == 3347
        assert (r["qian"], r["bai"], r["shi"], r["ling"]) == (3, 3, 4, 7)

    def test_yinshu_ni_2942(self):
        """戌日寅时逆数（乙卯水）：2000+900+14+27+1=2942 ✓ 原典例（时日顺冲还共语）"""
        r = cp.qishu("戌", "寅", "水", direction="逆")
        assert r["total"] == 2942

    def test_nayin_add_pei(self):
        """纳音加数/配数：木金虚度(0)、土+50；配数水1火2木3金4土5"""
        assert cp.NAYIN_ADD["木"] == 0 and cp.NAYIN_ADD["金"] == 0
        assert cp.NAYIN_ADD["土"] == 50 and cp.NAYIN_ADD["水"] == 27
        assert cp.NAYIN_PEI == {"水": 1, "火": 2, "木": 3, "金": 4, "土": 5}

    def test_dayun_liunian(self):
        """起大运例/起流年例：只将大运/太岁替时支，其余照前例"""
        rd = cp.qishu_dayun("戌", "卯", "水")
        rl = cp.qishu_liunian("戌", "午", "水")
        assert rd["total"] > 2000 and rl["total"] > 2000
        assert rd["total"] == cp.qishu("戌", "卯", "水")["total"]
        assert rl["total"] == cp.qishu("戌", "午", "水")["total"]


# ── ② 四体八体/伏体（卷一·渐卦例） ─────────────────────────────

class TestSitiBati:
    def test_jian_bati(self):
        """渐卦（巽上艮下）→正体巽艮/伏体震兑/互体离坎/变体（后天鼎=离上巽下）"""
        r = g.compute_siti_bati("渐", "鼎")
        assert r["zheng_ti"] == {"upper": "巽", "lower": "艮"}
        # 原典："艮有伏震，巽有伏兑"
        assert r["fu_ti"] == {"upper": "震", "lower": "兑"}
        # 原典："九五六四九三互离，六四九三六二互坎"
        assert r["hu_ti"] == {"upper": "离", "lower": "坎"}
        assert r["bian_ti"] == {"upper": "离", "lower": "巽"}

    def test_fu_li(self):
        """福力层次：本体为最；渐之反体/对体皆归妹（渐归妹互为综错）"""
        out = g.judge_fu_li("渐")
        joined = "；".join(out)
        assert "皆不若本体有之为妙耳" in joined
        assert "受兄弟子孙之福" in joined
        assert "遭变故而得安宁" in joined
        assert "虽死而有余福" in joined
        assert "反体（归妹）" in joined and "对体（归妹）" in joined


# ── ④ 五命得卦（卷一·五命得卦） ─────────────────────────────────

class TestWumingDeGua:
    def test_shui_ming_jian(self):
        """癸亥（水命）得渐（巽上艮下）：巽风起波浪秋冬可畏 / 艮山下有险为巨壑流蹇"""
        out = g.judge_wuming_de_gua("癸亥", "渐")
        joined = "；".join(out)
        assert "水命" in joined
        assert "巽风起波浪" in joined
        assert "艮山下有险" in joined

    def test_jin_ming_guan(self):
        """庚申（金命）得观（巽上坤下）：巽冷风潇潇秋冬喜遇 / 坤抱母得源多获福庆"""
        out = g.judge_wuming_de_gua("庚申", "观")
        joined = "；".join(out)
        assert "金命" in joined
        assert "巽冷风潇潇" in joined
        assert "坤抱母得源" in joined

    def test_empty_input(self):
        assert g.judge_wuming_de_gua("", "渐") == []
        assert g.judge_wuming_de_gua("甲", "渐") == []


# ── ⑤ 论所得卦数吉凶·余数断（卷一 p129-130） ────────────────────

class TestSuoshuJiXiong:
    def test_winter_odd_junzi(self):
        """冬半年（阳令）：天数>25，余奇数=君子之合象（吉）"""
        out = g.judge_suoshu_ji_xiong(29, 30, 3, 0, "winter")
        assert len(out) == 1 and "君子之合象" in out[0]

    def test_winter_even_si_light(self):
        """冬半年：余4=巽（轻）：四为巽，巽者顺也，有隐忍之心，未为甚害"""
        out = g.judge_suoshu_ji_xiong(29, 30, 4, 0, "winter")
        assert len(out) == 1 and "巽" in out[0] and "轻" in out[0]

    def test_winter_even_liu_heavy(self):
        """冬半年：余6=乾（重）：六为乾，乾者健也…遇阳年阳命犯之者必主刑伤之祸"""
        out = g.judge_suoshu_ji_xiong(31, 30, 6, 0, "winter")
        assert len(out) == 1 and "乾" in out[0] and "重" in out[0]

    def test_summer_di_yu_kun(self):
        """夏半年（阴令）：地数>30，余2=坤（原文未载轻重）：二为坤，纵有杀尚存慈母惜子之心"""
        out = g.judge_suoshu_ji_xiong(25, 32, 0, 2, "summer")
        assert len(out) == 1 and "坤" in out[0]

    def test_summer_yi_kan_heavy(self):
        """夏半年：余1=坎（重）：一为坎，坎者陷也，主陷害于人"""
        out = g.judge_suoshu_ji_xiong(25, 31, 0, 1, "summer")
        assert len(out) == 1 and "坎" in out[0] and "重" in out[0]

    def test_no_remainder(self):
        """天数25/地数30 无余 → 不断"""
        assert g.judge_suoshu_ji_xiong(25, 30, 0, 0, "winter") == []
        assert g.judge_suoshu_ji_xiong(25, 30, 0, 0, "summer") == []


# ── ⑥ 月令非时论·四时五行盛衰（卷一 p117-119） ──────────────────

class TestYueLingFeiShi:
    def test_winter_shui_sheng(self):
        """冬三月水盛：水为当时，而丰亨豫泰"""
        bazi = [("甲", "子"), ("丙", "子"), ("戊", "辰"), ("庚", "午")]
        out = g.judge_yue_ling_fei_shi(bazi, 25, 40)
        joined = "；".join(out)
        assert "冬三月" in joined
        assert "丰亨豫泰" in joined

    def test_winter_tu_sheng(self):
        """冬三月土盛：水被土制，而贫愁困苦"""
        bazi = [("甲", "子"), ("丙", "子"), ("戊", "辰"), ("庚", "辰")]
        out = g.judge_yue_ling_fei_shi(bazi, 25, 40)
        assert any("土盛" in x and "贫愁困苦" in x for x in out)

    def test_spring_huo_sheng(self):
        """春三月火盛：木去生火，为子孙昌荣"""
        bazi = [("甲", "寅"), ("丙", "寅"), ("丙", "午"), ("庚", "午")]
        out = g.judge_yue_ling_fei_shi(bazi, 30, 32)
        assert any("火盛" in x and "子孙昌荣" in x for x in out)

    def test_empty_bazi(self):
        assert g.judge_yue_ling_fei_shi([], 25, 30) == []
        assert g.judge_yue_ling_fei_shi([("甲", "子")], 25, 30) == []


# ── ⑦ 数极京城山林（标注级） ────────────────────────────────────

class TestShuJi:
    def test_not_triggered(self):
        assert g.judge_shu_ji(["正常断语"]) == []

    def test_triggered_on_jun_yao(self):
        out = g.judge_shu_ji(["后天之气数行至君爻之位，此为数足，到此必死"])
        assert len(out) == 1
        assert "京城" in out[0] and "山林" in out[0]

    def test_triggered_on_shang_ji(self):
        out = g.judge_shu_ji(["纵到君爻，亦不许行至上极一爻，寿必不久"])
        assert len(out) == 1 and "京城" in out[0]


# ── ⑧ 深度检验回归（2026-09-12：无效卦名 / 节气精确半年） ─────────

class TestDeepAudit:
    def test_invalid_gua_no_kun_false_positive(self):
        """无效卦名不得误算成坤（修复：_gua_to_lines 无效返回 None）"""
        r = g.compute_siti_bati("?", "?")
        assert r["zheng_ti"] == {"upper": "", "lower": ""}
        assert r["hu_ti"] == {"upper": "", "lower": ""}
        fl = g.judge_fu_li("?")
        assert len(fl) == 1 and "本体" in fl[0]  # 只有本体，无互/反/对体

    def test_pure_gua_siti_bati(self):
        """纯卦八体：乾→正乾乾/伏坤坤/互乾乾"""
        r = g.compute_siti_bati("乾", "坤")
        assert r["zheng_ti"] == {"upper": "乾", "lower": "乾"}
        assert r["fu_ti"] == {"upper": "坤", "lower": "坤"}
        assert r["hu_ti"] == {"upper": "乾", "lower": "乾"}
        fl = "；".join(g.judge_fu_li("乾"))
        assert "对体（坤）" in fl

    def test_solar_phase_wuzi_boundary(self):
        """节气精确半年：午月初（夏至前）仍为 winter；子月初（冬至前）仍为 summer
        （修复月支近似在 6/15、12/15 的误差）"""
        assert g._solar_phase("1980-06-15") == "winter"   # 6/15 夏至前
        assert g._solar_phase("1980-06-25") == "summer"   # 6/25 夏至后
        assert g._solar_phase("1980-12-15") == "summer"   # 12/15 冬至前
        assert g._solar_phase("1980-12-25") == "winter"   # 12/25 冬至后
        assert g._solar_phase("") == ""

    def test_solar_phase_1980_1983(self):
        """历史案例：1980-06-22 夏至后=summer；1983-11-03 立冬前=summer"""
        assert g._solar_phase("1980-06-22") == "summer"
        assert g._solar_phase("1983-11-03") == "summer"

# ── ⑨ 卷十诗断 OCR 语料检索（2026-09-12 建档） ───────────────────

class TestCanpingRawShici:
    def test_search_2542_example_poem(self):
        """金锁银匙歌 2542 例（戌日寅时乙卯水）：掌中秋月扇/举动好风生，水部 p29 丑酉列（v1 重读修正页）"""
        hits = cp.search_raw_poem("掌中秋月扇")
        assert hits and hits[0][0] == 29 and hits[0][1] == "丑酉"
        assert cp.search_raw_poem("举动好风生")

    def test_search_2942_example_poem(self):
        """金锁银匙歌 2942 例（逆数）：玉壺無別物/赤蟻似蜂屯，水部 p34 辰宾列（v1 重读修正页）"""
        hits = cp.search_raw_poem("玉壺無別物")
        assert hits and hits[0][0] == 34 and hits[0][1] == "辰宾"
        assert cp.search_raw_poem("赤蟻似蜂屯")

    def test_search_empty_and_missing(self):
        assert cp.search_raw_poem("") == []
        assert cp.search_raw_poem("zzz不存在的词") == []

    def test_search_no_false_positive(self):
        """检索不得误命中无关字（语料扩容后改用罕见字抽查；含 坤 句现已入语料）"""
        assert cp.search_raw_poem("齉") == []
        assert cp.search_raw_poem("龘") == []

    def test_search_full_corpus_hits(self):
        """全 35 页语料扩容后检索命中新部句（返回 (页, 列头, 句) 三元组；v1 重读修正列头）"""
        hits = cp.search_raw_poem("乾坤自我持")
        assert hits and hits[0][0] == 44 and hits[0][1] == "子辰" and hits[0][2] == "乾坤自我持"
        hits2 = cp.search_raw_poem("鴻毛草上風")
        assert hits2 and hits2[0][0] == 53 and hits2[0][1] == "未未" and hits2[0][2] == "鴻毛草上風"

    def test_canping_dir_default(self):
        """默认语料目录可解析（data/heluo/canping/ 存在）"""
        import os
        d = os.path.join(r"D:\shuntian", "data", "heluo", "canping")
        assert os.path.exists(os.path.join(d, "raw_shici_p24-58.json"))


class TestCanpingJintu:
    """金/土部诗断语料（448_008 五部全本，v1 转录）"""

    def test_corpus_counts(self):
        """五行齐全：金部 74 + 土部 82 = 156 编号"""
        items = cp.load_raw_shici_jintu()
        assert len(items) == 156
        jin = [i for i in items if i["part"] == "jin"]
        tu = [i for i in items if i["part"] == "tu"]
        assert len(jin) == 74 and len(tu) == 82

    def test_search_jin_no(self):
        """金部编号检索：3306 → p59 鹤在白雲棲（表头页）"""
        hits = cp.search_raw_poem_448(no="3306")
        assert hits and hits[0][0] == "jin" and hits[0][1] == 59
        assert "鶴在白雲棲" in hits[0][4]

    def test_search_tu_no(self):
        """土部编号检索：3357 → p75 蜘蛛結網羅（表头页）"""
        hits = cp.search_raw_poem_448(no="3357")
        assert hits and hits[0][0] == "tu" and hits[0][1] == 75
        assert "蜘蛛結網羅" in hits[0][4]

    def test_search_dup_no_returns_all(self):
        """448 编号非唯一键：金部三一七 跨页异文应全部返回（p61/p63）；三一六 另见 p69"""
        hits = cp.search_raw_poem_448(no="317", part="jin")
        assert {h[1] for h in hits} == {61, 63}
        hits2 = cp.search_raw_poem_448(no="316", part="jin")
        assert {h[1] for h in hits2} == {61, 69}

    def test_search_keyword_in_lines(self):
        """关键字检索句文：土部 内覈 条 三三七九 含 八尺長燈檠"""
        hits = cp.search_raw_poem_448(keyword="八尺長燈檠")
        assert hits and hits[0][2] == "3379" and hits[0][1] == 91

    def test_search_part_filter(self):
        """part 过滤：jin 不含土部句"""
        hits = cp.search_raw_poem_448(keyword="河洛出圖書", part="jin")
        assert hits == []
        hits = cp.search_raw_poem_448(keyword="河洛出圖書", part="tu")
        assert hits and hits[0][0] == "tu" and hits[0][1] == 77

    def test_search_missing(self):
        """语料缺失/无命中容错"""
        assert cp.search_raw_poem_448(keyword="", no="zzz") == []
        assert cp.search_raw_poem_448(keyword="", part="xx") == []
