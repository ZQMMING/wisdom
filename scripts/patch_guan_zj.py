# -*- coding: utf-8 -*-
# 官星真假两分支(《滴天髓·真假》《子平真诠》官格救应), 优先于调候:
# (护官 L232 庚申壬午辛酉癸巳) 午官当令有根为真神、孤无财生, 壬癸食伤众透坐申长生克官破格
#   -> 护官: P官、S印(制食伤护官)、A食伤; 丁亥水克尽午火凶。与常规身旺食伤制杀相反(此官当令成格、食伤破格)。
# (舍官 L1046 丙辰辛丑庚辰丙子) 两丙官杀虚透完全无根、丙辛合化水, 辰丑辰三重湿土晦光, 寒湿
#   -> 官不真: 舍官从湿, P食伤水(制土卫水)、S财木(破湿土)、A虚官火(丙午丁未虚激反凶)、A湿土印。
# 分界=官有根当令为真(护) vs 官虚透无根被合化+湿土晦为不真(舍)。
import io
fp=r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
s=io.open(fp,encoding='utf-8').read()
old="""        cai_usable=bool(cai_root) and stem(t['cai'])>=1 and not (cai_gan_he and ling(t['cai']) in ('囚','死'))
        # B1 仲冬调候(火透: 杀重则制杀调候合一, 否则身有气寒木向阳; 印重破印让位)"""
assert s.count(old)==1, s.count(old)
new="""        cai_usable=bool(cai_root) and stem(t['cai'])>=1 and not (cai_gan_he and ling(t['cai']) in ('囚','死'))
        # 官星当令为真神、孤而无辅(无财生), 食伤众透有气克官破格 -> 印制食伤护官(L232)
        if primary is None and BRANCH_WX.get(mz)==t['guan'] and ben(t['guan'])>=1 \\
                and stem(t['shi'])>=2 and (ben(t['shi'])>=1 or cs(t['shi']) or d(t['shi']).get('zhong_n',0)>=1) \\
                and ben(t['cai'])==0 and stem(t['cai'])==0:
            P(t['guan'],'BINGYAO','官星当令为真神、孤而无辅，食伤众透有气克官破格，护官为急')
            S(t['yin'],'印制食伤护官'); A(t['shi'],'食伤克官为病')
        # 官星虚透无根被合化、三重以上湿土晦光(寒湿): 官不真, 舍官从湿(L1046)
        if primary is None and stem(t['guan'])>=1 and ben(t['guan'])==0 \\
                and d(t['guan']).get('zhong_n',0)==0 and d(t['guan']).get('yu_n',0)==0 \\
                and sum(1 for b in brs if b in ('辰','丑'))>=3 and cold:
            _he_ou={'丙':'辛','丁':'壬','甲':'己','乙':'庚','戊':'癸','己':'甲','庚':'乙','辛':'丙','壬':'丁','癸':'戊'}
            _gg=[gg for k in _pks for gg in [pillars[k][0]] if WX.get(gg)==t['guan']]
            if any(_he_ou.get(gg) in [pillars[k][0] for k in _pks] for gg in _gg):
                P(t['shi'],'BINGYAO','官星虚透无根、被合化，重重湿土晦光，官不真，舍官从湿，食伤制土卫水')
                S(t['cai'],'财破湿土印'); A(t['guan'],'虚官无根被合化、火运虚激反凶'); A(t['yin'],'湿土晦光为病')
        # B1 仲冬调候(火透: 杀重则制杀调候合一, 否则身有气寒木向阳; 印重破印让位)"""
s=s.replace(old,new)
io.open(fp,'w',encoding='utf-8',newline='').write(s)
print('patched guan zhen/jia (L232 huguan, L1046 sheguan)')
