# -*- coding: utf-8 -*-
import io
p = "src/tongshu/engines/blind_bazi_engine.py"
src = io.open(p, encoding="utf-8").read()

old = """        zhi_guan_eff = [
            m for m, a in zip(result.zuo_gong_methods, result.zuo_gong_attributions)
            if a == ZuoGongAttribution["EFFECTIVE"]
            and ('伤官制官' in m or '制正官' in m or '刑制正官' in m or '穿制正官' in m)
        ]
        # 原书R2："日主合时柱官做功，要看官坐下的支去干啥了；官的坐支与日支
        # 做的功相反时，就反局了" —— 日主合正官(追求权位) 或 日主合财(求财)
        # 与原局去正官（丢官）并存 = 意向冲突。
        if day_he_methods and zhi_guan_eff:
            he_has_guan = any('正官' in m for m in day_he_methods)
            he_has_cai = any('财' in m for m in day_he_methods)
            if he_has_guan or he_has_cai:
                reasons.append(
                    f"R2日主做功与日支做功相反: {'+'.join(day_he_methods)}(追求)"
                    f" vs 原局{'+'.join(zhi_guan_eff)}(去除正官)"
                )
"""
new = """        zhi_guan_eff = [
            m for m, a in zip(result.zuo_gong_methods, result.zuo_gong_attributions)
            if a == ZuoGongAttribution["EFFECTIVE"]
            and ('伤官制官' in m or '制正官' in m or '刑制正官' in m or '穿制正官' in m)
        ]
        # V3.4.3 【天干伤官明克正官】（反证 D28 己巳乙亥壬申丁未 原文"左边伤官
        # 制官（乙木克己土）"=年柱天干紧贴明克，是反局依据；引擎做功层按藏干/
        # 宾位判 INEFFECTIVE 丢失）：
        # 判据：相邻(含同柱)的天干伤官 克 天干正官（明干相克=原局实际发生的去官功）。
        zhi_tiangan = False
        _stems4 = [
            chart.year_pillar.heavenly_stem, chart.month_pillar.heavenly_stem,
            chart.day_pillar.heavenly_stem, chart.hour_pillar.heavenly_stem,
        ]
        for _i in range(4):
            for _j in range(4):
                if abs(_i - _j) > 1:
                    continue
                if (ten_god(day_master, _stems4[_i]) == "伤官"
                        and ten_god(day_master, _stems4[_j]) == "正官"
                        and CONTROLS.get(STEM_ELEMENT[_stems4[_i]]) == STEM_ELEMENT[_stems4[_j]]):
                    zhi_tiangan = True
                    break
            if zhi_tiangan:
                break
        # 原书R2："日主合时柱官做功，要看官坐下的支去干啥了；官的坐支与日支
        # 做的功相反时，就反局了" —— 日主合正官(追求权位) 或 日主合财(求财)
        # 与原局去正官（丢官）并存 = 意向冲突。
        if day_he_methods and (zhi_guan_eff or zhi_tiangan):
            he_has_guan = any('正官' in m for m in day_he_methods)
            he_has_cai = any('财' in m for m in day_he_methods)
            if he_has_guan or he_has_cai:
                reasons.append(
                    f"R2日主做功与日支做功相反: {'+'.join(day_he_methods)}(追求)"
                    f" vs 原局{'+'.join(zhi_guan_eff or ['伤官制官(天干明克)'])}"
                    "(去除正官)"
                )
"""
assert old in src, "R2块OLD NOT FOUND"
src = src.replace(old, new, 1)
io.open(p, "w", encoding="utf-8").write(src)
print("OK 天干明克制官 已补")
