# -*- coding: utf-8 -*-
# 化气格结构识别补全(保守, 只动CANDIDATE识别, CONFIRMED门槛不变):
# (1) chengshi 增"化神透干+本气根(透干通根)且日主无根无印": 任注"丙火透而通根,化火斯真"(丙禄巳/坐戌库),
#     不当令不成局但化神透干通根、日主无根无印亦论化(落CANDIDATE, CONFIRMED仍须line183得令无根);
#     日主有本气根(如甲坐寅禄)不在此门, 归从势/原假化, 不抢化气。
# (2) 合神本身即使是官杀(戊癸合之戊=癸官)不作"克身牵挂"排除; 仅合神外官杀有根透干方阻化。
# L1640 丙戌戊戌癸巳壬戌: 戊癸合火、丙透通根巳禄+三戌火库、癸无根无金本气印=化火(原误从官)。
import io
fp=r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'
s=io.open(fp,encoding='utf-8').read()
old1="            chengshi = on_qi or hju >= 1 or hb >= 2     # 化神得令/成局/本气成势方论化"
assert s.count(old1)==1, ('old1',s.count(old1))
new1="""            chengshi = (on_qi or hju >= 1 or hb >= 2
                        or (hs_t >= 1 and hb >= 1 and dm_ben_eff == 0 and yin_ben_eff == 0))   # 化神得令/成局/本气成势, 或透干通根而日主无根无印(任注"透而通根斯真"); 后者落CANDIDATE"""
s=s.replace(old1,new1)
old2="""            if gs_stem >= 1 and gs_ben >= 1:
                continue   # 官杀有根透干克身=牵挂, 合而不真化(戊申甲寅戊土坐未实从财); 虚浮无根官杀被化神克伤不阻化"""
assert s.count(old2)==1, ('old2',s.count(old2))
new2="""            _GWX_H={'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}
            _gs_he = 1 if (other and _GWX_H.get(other[0]) == gs_wx) else 0
            if (gs_stem - _gs_he) >= 1 and gs_ben >= 1:
                continue   # 合神(与日干五合之干)本身虽为官杀不作克身牵挂; 合神外官杀有根透干方为牵挂不真化(戊申甲寅戊土坐未实从财)"""
s=s.replace(old2,new2)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched huaqi tougan tonggen v3 (rootless gate)')
