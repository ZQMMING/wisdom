import sys
sys.path.insert(0, '.')
from engines.common.l0_fact_builder import build as l0build
from engines.common.wuxing_power import build_wuxing_power, build_spectrum_from_power
from engines.common.daymaster_tian_he import build_tian_he
from engines.common.special_pattern import build_special_patterns
from engines.common.yongshen_engine import build_yongshen_engine
from engines.common.dayun_xiji import build_dayun_xiji

def check(bazi, dayun):
    p={'year':list(bazi[0]),'month':list(bazi[1]),'day':list(bazi[2]),'hour':list(bazi[3])}
    f=l0build(p); th=build_tian_he(p,f); wp=build_wuxing_power(p,f,th)
    sp=build_special_patterns(p,f,wp,th,None); sp2=build_spectrum_from_power(wp)
    ys=build_yongshen_engine(p,f,wp,sp2,sp,{})
    dx=build_dayun_xiji(p,ys,[dayun],wp)
    for s in dx['per_step']:
        if s['ganzhi']==dayun:
            print(dayun, 'overall=', s['overall']['result'],
                  'first5=', s['first_5']['result'], '('+s['first_5']['gan']+')',
                  'last5=', s['last_5']['result'], '('+s['last_5']['zhi']+')')

print('L270 庚午(原典xiong,午运凶):')
check([('戊','寅'),('乙','丑'),('丙','寅'),('庚','寅')], '庚午')
print('L811 乙酉(原典ji,酉运吉):')
check([('壬','辰'),('丙','午'),('丙','午'),('壬','辰')], '乙酉')
