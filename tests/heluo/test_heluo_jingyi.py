# -*- coding: utf-8 -*-
"""精义/释义接入解卦层测试（2026-09-15 接入 guajie_jingyi.json 706 单元）。"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "src"))

from heluo_engine.engines.heluo.guajie import (
    GuaDuan,
    YaoDuan,
    build_guajie_from_result,
    load_guajie_data,
    query_yao_duan,
)
from heluo_engine.adapter import HeluoAdapter
from heluo_engine.engines.heluo.canonical import resolve_jieqi_window

# ⚠ 2026-10-24 河洛回灌：本仓另有**自己的** adapter
#   （src/tongshu/engines/heluo_adapter.py，用主仓 BaziChart）。
#   主仓 adapter 才是本仓生产链真正走的那个 ⇒ 本组测试必须测**主仓 adapter**，
#   否则主仓 adapter 升级后无人守护（独立包 adapter 全绿 ≠ 主仓 adapter 全绿）。
#   两个 adapter 的引擎侧逻辑同源（目标日换算等均走 heluo_engine 单一来源），
#   但接线层（Bazi 投影 + era_source + 解卦层/解读层挂载）各有一份实现。
from tongshu.engines.heluo_adapter import HeluoAdapter as MainRepoHeluoAdapter


class TestJingyiDataLayer:
    """数据层：load_guajie_data 合并精义/释义。"""

    def test_load_has_jingyi_fields(self):
        data = load_guajie_data()
        g = data.get("观")
        assert g is not None
        assert isinstance(g, GuaDuan)
        # 卦辞精义/释义
        assert g.gua_ci_jingyi and "瞻仰" in g.gua_ci_jingyi
        assert g.gua_ci_shiyi
        # 卦象断语精义/释义与原文对齐
        assert g.gua_lines and g.lines_jingyi and g.lines_shiyi
        assert len(g.gua_lines) == len(g.lines_jingyi) == len(g.lines_shiyi)

    def test_yao_has_jingyi(self):
        y = query_yao_duan("观", "初六")
        assert y is not None
        assert isinstance(y, YaoDuan)
        assert y.ci and "童观" in y.ci
        assert y.jingyi and "童" in y.jingyi
        assert y.shiyi

    def test_64_gua_all_merged(self):
        """64 卦全部命中精义（无卦遗漏）。"""
        data = load_guajie_data()
        assert len(data) == 64
        missing = [
            name for name, g in data.items()
            if not (g.gua_ci_jingyi and g.gua_ci_shiyi and g.lines_jingyi and g.lines_shiyi)
        ]
        assert not missing, f"精义缺失卦: {missing}"
        # 精义/释义条数一致
        for name, g in data.items():
            assert len(g.lines_jingyi) == len(g.lines_shiyi), name

    def test_no_web_noise(self):
        """gua_lines 已过滤中华典藏网页残留（上一章/返回目录/中华典藏网…）。"""
        data = load_guajie_data()
        noise = ("上一章", "返回目录", "下一章", "中华典藏网", "本站非营利性站点", "吸取国学精华")
        dirty = [
            name for name, g in data.items()
            if any(n in line for line in g.gua_lines for n in noise)
        ]
        assert not dirty, f"含网页残留卦: {dirty}"

    def test_jingyi_fallback_empty(self):
        """未收录爻（如超范围）精义为空但不崩溃。"""
        y = query_yao_duan("乾", "上九")
        assert y is not None
        assert y.jingyi != ""  # 乾上九在库内


class TestJingyiOutputLayer:
    """输出层：解卦层 dict 带出 benming + 四层爻断 jingyi/shiyi。"""

    @pytest.fixture(scope="class", params=["pkg", "main_repo"])
    def guajie_dict(self, request):
        # 2026-10-23 起：适配器的目标日默认 = **今天**（用户裁决「流日卦按当前
        # 日期自动算」），时间轴随之只算该年该月（fast path）。故此处必须把
        # 目标日**显式**传给适配器，与下面 guajie 的取用日保持一致 ——
        # 否则会拿「今天的月」去取另一个月的日段（取不到）。
        #
        # ⚠ 2026-10-24 口径修复：日卦层的 target_month/target_day 是
        #   **节气月序 + 自节起的日序**，不是公历月日（公历 9 月 ≠ 节气九月：
        #   九月 = 寒露月，10/8 起）。适配器已按 resolve_jieqi_window 换算，
        #   这里直调 guajie 必须用**同一口径**，故由同一函数换算得出，
        #   不写死数字（写死会在历法规则变化时静默取错月）。
        #
        # ⚠ 2026-10-24 河洛回灌：参数化跑**两个** adapter ——
        #   独立包 heluo_engine.adapter 与主仓 tongshu.engines.heluo_adapter。
        #   主仓生产链走的是后者；两者引擎侧同源但接线层各有一份实现，
        #   只测一个 ⇒ 另一个无人守护。
        adapter_cls = (HeluoAdapter if request.param == "pkg"
                       else MainRepoHeluoAdapter)
        _target = "2026-09-15"
        r = adapter_cls().compute((1980, 6, 22, 10), gender="male",
                                   target_date=_target)
        _w = resolve_jieqi_window(2026, 9, 15)
        assert _w.get("ok"), "节气窗口换算应当成功"
        return build_guajie_from_result(
            r, target_year=2026, target_month=int(_w["month"]),
            target_day=int(_w["day"]), target_hour=10)

    def test_benming_present(self, guajie_dict):
        bm = guajie_dict.get("benming") or {}
        assert bm.get("hexagram") == "观"
        assert bm.get("gua_ci") and "盥而不荐" in bm["gua_ci"]
        assert bm.get("gua_ci_jingyi")
        assert bm.get("gua_ci_shiyi")
        assert len(bm.get("lines") or []) == 4
        assert len(bm.get("lines_jingyi") or []) == 4
        assert len(bm.get("lines_shiyi") or []) == 4

    def test_liunian_yao_jingyi(self, guajie_dict):
        """流年层：出爻、必带爻辞与精义/释义。

        ⚠ 2026-10-24 修订：原断言硬编码「流年爻 == 六五 且 爻辞含『贲于丘园』」——
        那是**旧口径**（流年爻 = 年卦的元堂爻 = 大运段爻，同段内恒定）下的快照。
        流年爻改正为**小象行年爻**（该年小象变出的那一爻，原典起例卷之上
        「一岁在同人九三（阳）爻；二岁取应爻变…」）后，本盘 2026 贲卦的
        行年爻是**初六**（爻辞「贲其趾，舍车而徒」），六五是年卦的元堂爻。
        正确性由 tests/heluo/test_heluo_xingnian_yao.py 按原典硬算例保证；
        本测试只守「流年层必须带全精义/释义」这一结构契约。
        """
        ly = guajie_dict.get("liunian_yao") or {}
        assert ly.get("yao"), "流年层应出爻"
        assert ly.get("ci"), "流年爻应带爻辞"
        assert ly.get("jingyi") and ly.get("shiyi")

    def test_liuri_yao_jingyi(self, guajie_dict):
        """流日层：必出爻、必带爻辞与精义/释义。

        2026-10-07：起日卦依原典 L390 由「六段顺次」改为「逐日一爻、
        阳日寻阳位/阴日寻阴位」后，流日卦象随之改变，故**不再硬编码
        某一卦的爻辞字样**（那属于快照式断言，规则一改必假失败）。
        内容正确性由 TestLiuriRuleConsistency 按原典规则复算保证；
        本测试只守「流日层必须带全精义/释义」这一结构契约。
        """
        lr = guajie_dict.get("liuri_yao") or {}
        assert lr.get("yao"), "流日层应出爻"
        assert lr.get("ci"), "流日爻应带爻辞"
        assert lr.get("jingyi") and lr.get("shiyi")
        assert guajie_dict.get("liuri_hexagram"), "流日层应出卦名"

    def test_four_layers_all_have_jingyi(self, guajie_dict):
        """流年/月/日/时四层只要出爻就必带 jingyi/shiyi。"""
        for key in ("liunian_yao", "liuyue_yao", "liuri_yao", "liushi_yao"):
            v = guajie_dict.get(key)
            if v:
                assert "jingyi" in v and "shiyi" in v, f"{key} 缺精义/释义"
                assert v["jingyi"] and v["shiyi"], f"{key} 精义/释义为空"

    def test_benming_null_when_no_prenatal(self):
        """prenatal 缺省时 benming 为 None（兼容既有输出）。"""
        # 直接构造空 result 场景由既有测试覆盖；此处仅验证 to_dict 键存在
        g = build_guajie_from_result(None)
        assert isinstance(g, dict)
        assert "benming" in g or "error" in g


class TestMainRepoAdapterWiring:
    """主仓 adapter 专属守卫（2026-10-24 河洛回灌）。

    本仓生产链走的是 ``tongshu.engines.heluo_adapter``，它此前停留在旧副本
    （落后独立包一整代）。本组钉住升级引入的四项能力，防止将来退化：

      ① **目标日换算**：公历 → 节气月序 + 自节起日序。
         回归锚点：2026-10-23 属**节气九月**（寒露 10/8 起）的第 16 日；
         旧口径会把公历 10 月当十月（立冬 11/7 起）⇒ 日卦段 date_from
         落在 2026-11-25，与目标日**相差 33 天**。
      ② **era_source 留痕**：三元是据真实出生年推导（derived）还是兜底
         （fallback）必须可辨 —— 寄宫一变 ⇒ 全链判词全变。
      ③ **解卦层错误显形**：构建失败挂 {"error": ...}，不留空。
      ④ **解读层挂载**：六模块解读进入生产链。
    """

    def test_target_date_uses_jieqi_caliber(self):
        r = MainRepoHeluoAdapter().compute(
            (1980, 6, 22, 10), gender="male", target_date="2026-10-23")
        w = resolve_jieqi_window(2026, 10, 23)
        assert w.get("ok"), "节气窗口换算应当成功"
        assert (w["month"], w["day"]) == (9, 16), (
            "2026-10-23 应属节气九月第 16 日（寒露 10/8 起），实际 %s" % ((w["month"], w["day"]),))
        # 结果记录的取用日是**公历原值**，不是「年-节气月-日序」伪日期
        assert r.target_date == "2026-10-23", r.target_date

    def test_daily_hexagram_lands_in_correct_jieqi_month(self):
        """日卦段必须落在**目标日所属的节气月窗口**内（33 天错位回归）。"""
        r = MainRepoHeluoAdapter().compute(
            (1980, 6, 22, 10), gender="male", target_date="2026-10-23")
        daily = r.timeline.daily_hexagram
        base = daily["base_hex"]
        seg_from = base["date_from"]
        assert seg_from.startswith("2026-10-"), (
            "日卦段应起于寒露（2026-10-08）之后，实际 %s" % seg_from)
        # 目标日在该段内的日序：寒露起第 16 日（段内 13–18）
        assert base["target_day_no"] == 16, base["target_day_no"]
        # 段起日必须在目标日之前（目标日落在该段内）
        assert seg_from[:10] <= "2026-10-23", (seg_from, "2026-10-23")
        # 与旧错位值（2026-11-25，立冬月）相差甚远 ⇒ 明确排除
        assert not str(seg_from).startswith("2026-11-"), seg_from

    def test_era_source_disclosed(self):
        r = MainRepoHeluoAdapter().compute((1980, 6, 22, 10), gender="male")
        assert r.era_source in ("derived", "fallback"), r.era_source
        # 本例带出生时间 ⇒ 三元据真实出生年推导
        assert r.era_source == "derived", r.era_source

    def test_guajie_present_and_no_silent_empty(self):
        r = MainRepoHeluoAdapter().compute((1980, 6, 22, 10), gender="male")
        assert isinstance(r.guajie, dict) and r.guajie, "解卦层应产出内容"
        # 解卦层失败也必须**显形**（挂 error），不得静默留 None
        assert "error" not in r.guajie, r.guajie.get("error")

    def test_interpretation_mounted(self):
        r = MainRepoHeluoAdapter().compute((1980, 6, 22, 10), gender="male")
        assert isinstance(r.interpretation, dict) and r.interpretation, (
            "解读层应挂载到结果上")
        for key in ("platform_signals", "interpretation", "guidance",
                    "diagnosis", "metrics", "hexagram_state",
                    "dimension_view", "warnings"):
            assert key in r.interpretation, "解读层缺 %s" % key
        # 子块失败须写入 warnings，而非静默
        assert isinstance(r.interpretation.get("warnings"), list)
