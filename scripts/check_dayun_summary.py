# -*- coding: utf-8 -*-
"""查看dayun_summary输出结构."""
import sys
sys.path.insert(0, r'D:\shuntian-ziping-p0')
from engines.common.l0_fact_builder import build
from engines.common.wuxing_power import build_wuxing_power
from engines.common.dayun_summary import build_dayun_summary

pillars = {
    'year': ('辛', '卯'),
    'month': ('丁', '酉'),
    'day': ('庚', '午'),
    'hour': ('丙', '子'),
}
facts = build(pillars)
wpo = build_wuxing_power(pillars, facts)

# 大运
dayun = [('丙','申'),('乙','未'),('癸','巳'),('壬','辰'),('庚','寅'),('己','丑'),('戊','子'),('丁','亥')]

for gz in dayun[:3]:
    dy = build_dayun_summary(pillars, facts, wpo, gz[0], gz[1])
    print('=== 大运 %s%s ===' % (gz[0], gz[1]))
    for k, v in dy.items():
        if isinstance(v, (list, dict)):
            print('  %s: %s' % (k, str(v)[:200]))
        else:
            print('  %s: %s' % (k, v))
    print()
