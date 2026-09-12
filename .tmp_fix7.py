# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()

old = """        # V3.4.3 【官被劫财合走】ROBBED：官杀支被比劫支六合（如巳申=官被劫财合去）
        # （案例8原文"官星被劫财合去→非我所有、做功无效、终身仓库保管员"）
        bi_branches = [
            b for b in branches
            if any(ten_god(day_master, h) in GROUP_BI for h, _p in BRANCH_HIDDEN_STEMS.get(b, []))
        ]
        officer_robbed = any(
            BRANCH_LIUHE.get(b_bi) in officer_branches for b_bi in bi_branches
        )
"""
new = """        # V3.4.3 【官被劫财合走】ROBBED：官杀支被比劫支六合（如巳申=官被劫财合去）
        # （案例8原文"官星被劫财合去→非我所有、做功无效、终身仓库保管员"）
        # 宾主约束：官支在宾位（年月）且比劫支也在宾位（年月）→ 宾位劫财合走宾位官
        # = 非我所有。主位比肩合宾位官（如1980庚申壬午丙寅癸巳 时支巳合年支申）
        # = 制杀得权，不算被夺。
        bi_branches = [
            b for b in branches
            if any(ten_god(day_master, h) in GROUP_BI for h, _p in BRANCH_HIDDEN_STEMS.get(b, []))
        ]
        officer_robbed = any(
            branches.index(b_bi) < 2 and branches.index(o_b) < 2
            and BRANCH_LIUHE.get(b_bi) == o_b
            for b_bi in bi_branches for o_b in officer_branches
        )
"""
assert old in src, "ROBBED OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK ROBBED宾位约束 已加")
