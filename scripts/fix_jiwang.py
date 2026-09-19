# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

old="    wang_ling = bool(sea.get('in_season', False) or sea.get('month_supports', False))"
new="    # 伤官当令: 月令五行是日主所生的五行(如丁火戌月)\n    STEM_WX={'甲':'木','乙':'木','丙':'火','丁':'火','戊':'土','己':'土','庚':'金','辛':'金','壬':'水','癸':'水'}\n    BRANCH_WX={'寅':'木','卯':'木','巳':'火','午':'火','申':'金','酉':'金','亥':'水','子':'水','辰':'土','戌':'土','丑':'土','未':'土'}\n    SHENG={'木':'火','火':'土','土':'金','金':'水','水':'木'}\n    f = network.get('facts', {}) or {}\n    day_stem = f.get('day_stem', '')\n    month_branch = f.get('month_branch', '')\n    shishang_ling = bool(day_stem and month_branch and BRANCH_WX.get(month_branch) == SHENG.get(STEM_WX.get(day_stem,'')))\n    wang_ling = bool(sea.get('in_season', False) or sea.get('month_supports', False) or shishang_ling)"

content=content.replace(old,new)

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
