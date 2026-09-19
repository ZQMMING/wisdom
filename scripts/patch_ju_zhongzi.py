# -*- coding: utf-8 -*-
# 运支即复合完整三合/三会局成员(原局已成局、岁运再临局中字=合化加力/伏吟化神),
# 化神复合成势tier>=2则运支按化神判喜忌(长生/墓库支本气与化神异者从化神), 不按本气。
# 与 new_huashen(运支加入才新凑成局)互补。L623从财: 原局巳酉丑金局成、再逢巳运, 巳火本气比劫应从金财(fav),
# "干透水支拱金大得际遇"吉。化神休囚不成势(tier<2)不从, 防误化。
import io
fp=r'D:\shuntian-ziping-p0\scripts\dayun_align.py'
s=io.open(fp,encoding='utf-8').read()
old="""                and _KEME.get(w)==_zwx and _zwx in fav)]
"""
assert s.count(old)==1, s.count(old)
new="""                and _KEME.get(w)==_zwx and _zwx in fav)]
        # 运支临完整三合/三会局成员、化神成势 -> 从化神判喜忌(合化加力)
        _jjcf=tp.get('combination_facts',{}) if isinstance(tp,dict) else {}
        for _pr in (list(_jjcf.get('sanhe',[]))+list(_jjcf.get('sanhui',[]))):
            _m=re.match(r'^([子丑寅卯辰巳午未申酉戌亥])([子丑寅卯辰巳午未申酉戌亥])([子丑寅卯辰巳午未申酉戌亥]).*?([金木水火土])',str(_pr))
            if _m and z in (_m.group(1),_m.group(2),_m.group(3)) and element_power_tier(tp['wuxing_power'],_m.group(4))['tier']>=2:
                zc=cls_w(_m.group(4),fav,av); break
"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched yunzhi lin ju-zhongzi conghuashen')
