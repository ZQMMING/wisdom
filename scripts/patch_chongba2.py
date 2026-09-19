# -*- coding: utf-8 -*-
# 喜用逢冲根拔(极窄, 有序枚举比较非数值): 运支本气为喜用(zc fav), 复合冲局verdict明确点名运支
# 为"X衰者拔"(旺者冲衰衰者拔) -> 喜用根拔, 降av_l; 运支为"旺神发"/同阶两停不拔/被拔者非运支, 不触发。
# 转: L620庚申(申财被寅旺冲拔)/L852丁巳/L1016丁巳(巳火被亥冲拔)/L1013戊午(午被子冲拔)/L695丁亥(亥财被巳冲拔)。
# 不触发: L752甲申(申旺神发、被拔是寅)/L965甲申/L1656癸酉(运支非喜用)/两停。
import io
fp=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(fp,encoding='utf-8').read()
old="""        if lc is None:
            ss={gc,zc}"""
assert s.count(old)==1, ('old',s.count(old))
new="""        # 喜用逢冲根拔: 运支本气喜用、被对宫旺支冲而"衰者拔" -> 喜用根拔降av_l(旺神发/两停/拔非运支不触发)
        if lc is None and zc=='fav' and BRANCH_WX[z] in fav:
            for _cv in transit_clash_verdicts(tp):
                if z in _cv.get('pair',''):
                    _ba=re.search(r'([子丑寅卯辰巳午未申酉戌亥])衰者拔',_cv.get('verdict',''))
                    if _ba and _ba.group(1)==z:
                        lc='av_l'; break
        if lc is None:
            ss={gc,zc}"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched xiyong chong-gen-ba (narrow, transit verdict named)')
