# -*- coding: utf-8 -*-
# 法则A 冲拔喜用凶(布尔+有序枚举+角色, 非tier单因子):
# clash已用复合tier有序比较出衰者拔/旺神发; 叠加喜用角色:
#  - 命局旺支冲拔运喜用支(to>tz, 运支五行∈fav) -> 运来喜用根被拔, 凶
#  - 运旺支冲拔命局喜用支(tz>to, 命局被冲支五行∈fav) -> 命局喜用根被拔, 凶
# 同阶两停不判; 化神会局主导(new_hs)时不覆盖(保by_ju 34步对齐)。
# 覆盖: L620申财被寅拔/L852巳财被亥拔/L1013午官被子拔/L1016巳财被亥拔/L695亥财被巳拔。
import io
fp=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(fp,encoding='utf-8').read()
old="""        clash=[c['verdict'] for c in transit_clash_verdicts(tp) if z in c['pair']]
        if lc in ('mix','xian'): st['neutral']+=1; continue"""
assert s.count(old)==1, s.count(old)
new="""        clash=[]; _clash_av=False
        for _c in transit_clash_verdicts(tp):
            _pair=_c['pair']; clash.append(_c['verdict'])
            if z not in _pair: continue
            _o=_pair[0] if _pair[1]==z else _pair[1]
            _tz=_c['a_tier']['tier'] if _pair[0]==z else _c['b_tier']['tier']
            _to=_c['a_tier']['tier'] if _pair[0]==_o else _c['b_tier']['tier']
            _ow=BRANCH_WX[_o]; _zw=BRANCH_WX[z]
            if _to>_tz and _zw in fav and _zw not in av: _clash_av=True   # 运喜用支被命局旺神冲拔
            elif _tz>_to and _ow in fav and _ow not in av: _clash_av=True # 命局喜用根被运旺支冲拔
        if not new_hs and _clash_av: lc='av'
        if lc in ('mix','xian'): st['neutral']+=1; continue"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched clash chongba xiyong role')
