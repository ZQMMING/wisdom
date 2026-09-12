# -*- coding: utf-8 -*-
"""P0 锁定测试: 月令得令/失令 生克方向 (RED 探针 — 当前引擎 判据倒置 会 FAIL).

独立坐实的通行语义 (B1):
    得令 = 月支 生/同 日主 (SUPPORTIVE/SAME)
    失令 = 月支 泄/耗/克 日主 (DRAINING/CONSUMING/OPPOSING)
  即 以 日主 视角 看 月支 对 日主 的 生克。

现行 bug (engine.relation + judge_ling 参数序):
    JIA(木) 日主 + HAI(水) 月支: 水 生 木 → 通行 得令;  引擎 误判 失令
    JIA(木) 日主 + SI(火) 月支:  木 生 火 (泄) → 通行 失令;  引擎 误判 得令

本测试 锁定 正确 语义; 修正 engine/judgment 后 转绿, 原 27 测试 零回归.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import src.tongshu.reasoning.ziping_v3.constants as C
from src.tongshu.reasoning.ziping_v3.engine import EngineContext
from src.tongshu.reasoning.ziping_v3.judgment import judge_ling
from src.tongshu.reasoning.ziping_v3.types import FrozenBaziFact


def _fact(day_master: str, month_branch: str) -> FrozenBaziFact:
    """最小 排盘事实: 月支=month_branch, 日主=day_master, 其余中性 (不干扰 得令判定)."""
    def h(b):
        return dict(C.BRANCH_HIDDEN.get(b, {"main": "", "middle": "", "residual": "", "all": []}))
    return FrozenBaziFact(
        four_pillars=(("WU", "YIN"), ("REN", month_branch), (day_master, "CHEN"), ("GUI", "YU".lower().upper())),
        day_master=day_master,
        month_branch=month_branch,
        hidden_stems={"YEAR": h("YIN"), "MONTH": h(month_branch), "DAY": h("CHEN"), "HOUR": h("XU")},
        stem_ten_gods={"YEAR": "", "MONTH": "", "DAY": "DAY_MASTER", "HOUR": ""},
        branch_ten_gods={}, stem_he_pairs=[], branch_relations={}, twelve_growth={},
        luck_pillars=[], start_age=0.0, gender="male",
    )


def _judge(day_master: str, month_branch: str) -> str:
    fact = _fact(day_master, month_branch)
    avail = {"four_pillars", "day_master", "month_branch", "hidden_stems",
             "raw_relations", "stem_ten_gods"}
    ctx = EngineContext(fact, avail, {})
    return judge_ling(ctx, None).state


# 通行 语义 锁定表 (日主, 月支, 期望态):
#   水生木 → 得令;  木生火(泄) → 失令;  火同火 → 得令;  土克水(官) → 失令;  金克木 → 失令;  水同水 → 得令
_CASES = [
    ("JIA", "HAI", "DE_LING"),    # 水生木, 得令  ← 现行引擎 误判 SHI_LING (P0 倒置)
    ("JIA", "SI", "SHI_LING"),    # 木生火, 泄, 失令  ← 现行引擎 误判 DE_LING (P0 倒置)
    ("BING", "WU", "DE_LING"),    # 火同火, SAME, 得令 (旗舰案例, 对称 不暴露 bug)
    ("GENG", "YIN", "SHI_LING"),  # 木克金, 失令
    ("REN", "ZI", "DE_LING"),     # 水同水, SAME, 得令
    ("GENG", "CHOU", "SHI_LING"), # 土? 丑=土, 金... 土生金 → 得令; 但 丑 本气己土, 己土生庚金 → 得令
]
# 更正 CHOU 行: 丑本气己土, 土生金 → GENG 日主 丑月 应 得令
_CASES[-1] = ("GENG", "CHOU", "DE_LING")


def test_shengke_direction_de_ling():
    """水生木/同气 → 得令; 泄/克 → 失令 (B1 方向 锁定)."""
    for dm, mb, want in _CASES:
        got = _judge(dm, mb)
        assert got == want, (
            f"B1 得令方向 错误: 日主{dm} 月支{mb} 期望 {want} 实 {got} "
            f"(生克: {C.BRANCH_ELEMENT.get(mb)} 对 日主 {C.STEM_ELEMENT.get(dm)})"
        )
    print("B1 生克方向 得令/失令 6 案例 全 ✓")


def test_same_symmetric_not_masked():
    """对称 SAME 案例 (旗舰 BING/WU) 必须 得令 — 但 不得 因此 掩盖 非对称 生克 案例."""
    assert _judge("BING", "WU") == "DE_LING", "火同火 SAME 应得令"
    print("SAME 对称 得令 ✓ (旗舰 不回归)")


if __name__ == "__main__":
    test_shengke_direction_de_ling()
    test_same_symmetric_not_masked()
    print("\nB1 得令方向 RED 探针 全绿 ✓ (修正后)")
