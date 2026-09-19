# -*- coding: utf-8 -*-
import re

path=r'D:\shuntian-ziping-p0\engines\common\daymaster_power_queries.py'
content=open(path,encoding='utf-8').read()

old="    wang_ling = bool(sea.get('in_season', False) or sea.get('month_supports', False) or shishang_ling)"
new="    # 月令是日主墓库/余气+重根+印比透干也算旺令(如腊月壬水旺)\n    MU_KU = {'甲':'未','乙':'未','丙':'戌','丁':'戌','戊':'辰','己':'辰','庚':'丑','辛':'丑','壬':'辰','癸':'辰'}\n    YU_QI = {'甲':'辰','乙':'辰','丙':'未','丁':'未','戊':'戌','己':'戌','庚':'未','辛':'未','壬':'丑','癸':'丑'}\n    month_is_muku = bool(day_stem and month_branch and MU_KU.get(day_stem) == month_branch)\n    month_is_yuqi = bool(day_stem and month_branch and YU_QI.get(day_stem) == month_branch)\n    muku_wang = bool((month_is_muku or month_is_yuqi) and heavy and (bijie_stem or yin_stem))\n    wang_ling = bool(sea.get('in_season', False) or sea.get('month_supports', False) or shishang_ling or muku_wang)"

content=content.replace(old,new)

open(path,'w',encoding='utf-8',newline='').write(content)
print('done')
