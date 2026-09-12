# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()

old = """                if method and method not in triggered:
                    triggered.add(method)
                    methods.append(method)
                    detail.append(method_detail)
                    attributions.append(attribution)
                    # 功神/目标收集（V3.0）：参与做功的体支=功神候选, 用支=目标候选
                    working_branches.add(ti_branch)
                    target_branches.add(yong_branch)
"""
new = """                if method and method not in triggered:
                    triggered.add(method)
                    methods.append(method)
                    detail.append(method_detail)
                    attributions.append(attribution)
                    # 功神/目标收集（V3.0）：参与做功的体支=功神候选, 用支=目标候选
                    working_branches.add(ti_branch)
                    target_branches.add(yong_branch)
                elif method:
                    # V3.4.3 归因升级（盲派核心"谁在做功/是否为我所用"）：
                    # 同一做功方式存在多个配对时，首个（可能宾位）抢注会导致
                    # 主位 EFFECTIVE 版本被丢弃（案例3 日支申制时支巳七杀=主位制杀，
                    # 被"月未丁官制年支申比肩(宾位)"抢注成 INEFFECTIVE；
                    # 案例7 日支巳财制年支申印=主位财制印，被"月未丁财制年支申印"
                    # 抢注成 INEFFECTIVE）。
                    # 修复：同方法后续配对只允许 INEFFECTIVE→EFFECTIVE 升级
                    # （主位版本覆盖宾位版本），不允许降级。
                    _mi = methods.index(method)
                    if (attributions[_mi] == ZuoGongAttribution["INEFFECTIVE"]
                            and attribution == ZuoGongAttribution["EFFECTIVE"]):
                        attributions[_mi] = ZuoGongAttribution["EFFECTIVE"]
                        detail[_mi] = method_detail
                        working_branches.add(ti_branch)
                        target_branches.add(yong_branch)
"""
assert old in src, "triggered块OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 归因升级 已改")
