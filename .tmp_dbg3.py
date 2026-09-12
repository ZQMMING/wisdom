# -*- coding: utf-8 -*-
import io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from src.tongshu.engines.bazi_engine import BaziEngine, _branch_element, STEM_ELEMENT
from src.tongshu.engines.blind_bazi_engine import BlindBaziEngine, BRANCH_LIUHE
from src.tongshu.reasoning.bazi_ten_gods import ten_god, BRANCH_HIDDEN_STEMS, GENERATES, CONTROLS

be = BaziEngine()
bb = BlindBaziEngine(be)
ch = be.compute((2028,8,3,10), gender="male")
dm = ch.day_pillar.heavenly_stem
print("日主:", dm)
pillars = [
    (0, ch.year_pillar.heavenly_stem, ch.year_pillar.earthly_branch),
    (1, ch.month_pillar.heavenly_stem, ch.month_pillar.earthly_branch),
    (2, dm, ch.day_pillar.earthly_branch),
    (3, ch.hour_pillar.heavenly_stem, ch.hour_pillar.earthly_branch),
]
TI = {'比肩','劫财','偏印','正印','食神','伤官'}
YO = {'正财','偏财','正官','七杀'}
ti_pos, yo_pos = [], []
for idx, stem, branch in pillars:
    if idx == 2:
        ti_pos.append((stem, '比肩', idx, branch, False))
    else:
        tg = ten_god(dm, stem)
        if tg in TI: ti_pos.append((stem, tg, idx, branch, False))
        elif tg in YO: yo_pos.append((stem, tg, idx, branch, False))
    for hs, _p in BRANCH_HIDDEN_STEMS.get(branch, []):
        tg = ten_god(dm, hs)
        if tg in TI: ti_pos.append((hs, tg, idx, branch, True))
        elif tg in YO: yo_pos.append((hs, tg, idx, branch, True))
print("TI:", [(t[0],t[1],t[2],t[3]) for t in ti_pos])
print("YO:", [(y[0],y[1],y[2],y[3]) for y in yo_pos])
print("CONTROLS:", CONTROLS)
print("branch_element(SHEN)=", _branch_element("SHEN"), " branch_element(SI)=", _branch_element("SI"))
for ti in ti_pos:
    ts, tt, tix, tib, tih = ti
    for yo in yo_pos:
        ys, yt, yix, yib, yih = yo
        dist = abs(tix - yix)
        if dist > 2: continue
        rel = None
        if not tih and not yih:
            if (ts, ys) in __import__("src.tongshu.engines.blind_bazi_engine", fromlist=["STEM_HE"]).STEM_HE or (ys, ts) in __import__("src.tongshu.engines.blind_bazi_engine", fromlist=["STEM_HE"]).STEM_HE:
                rel = "he"
        if rel is None and tib != yib:
            if BRANCH_LIUHE.get(tib) == yib:
                te = _branch_element(tib); ye = _branch_element(yib)
                if CONTROLS.get(te) == ye: rel = "ke_ti_yong"
                elif CONTROLS.get(ye) == te: rel = "ke_yong_ti"
                else: rel = "liuhe"
        if rel:
            print(f"  {tib}({tt})x{yib}({yt}) dist={dist} rel={rel} ti_main={tix>=2} yo_main={yix>=2}")
