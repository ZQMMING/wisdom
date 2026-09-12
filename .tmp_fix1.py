# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()
old = """                # 地支六合
                if relation is None and ti_branch != yong_branch:
                    if BRANCH_LIUHE.get(ti_branch) == yong_branch:
                        relation = "liuhe"
"""
new = """                # 地支六合（盲派「合克」：六合且五行相克者按克论——案例3原文
                # "巳申合：盲派为合克（火克金）"；案例7"巳火合制年柱申金=财制印"。
                # 子丑=土克水、卯戌=木克土亦属合克；辰酉/午未/寅亥合而不克仍按合论）
                if relation is None and ti_branch != yong_branch:
                    if BRANCH_LIUHE.get(ti_branch) == yong_branch:
                        _ti_el_h = _branch_element(ti_branch)
                        _yo_el_h = _branch_element(yong_branch)
                        if CONTROLS.get(_ti_el_h) == _yo_el_h:
                            relation = "ke_ti_yong"   # 合克：体克用
                        elif CONTROLS.get(_yo_el_h) == _ti_el_h:
                            relation = "ke_yong_ti"   # 合克：用克体
                        else:
                            relation = "liuhe"
"""
assert old in src, "OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 六合合克已改")
