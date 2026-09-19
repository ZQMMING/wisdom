# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 1. 添加import re
old1 = """from typing import Dict, List, Any

WX ="""
new1 = """from typing import Dict, List, Any
import re

WX ="""
c = c.replace(old1, new1)

# 2. 在专旺格判断后面增加化气格的喜忌判断
old2 = """    is_zhuanwang = bool(zhuanwang_wx)
    # 专旺格喜忌: 喜专旺五行+生专旺的五行, 忌克专旺的五行+专旺克的五行
    # 从格喜忌: 喜从神的旺地, 忌生扶日主的运(比劫+印)"""
new2 = """    is_zhuanwang = bool(zhuanwang_wx)
    # V4.4: 化气格喜忌判断 (基于滴天髓化象: 化气格喜化神旺地, 忌克化神)
    # 化气格类型: 化土气格/化金气格/化水气格/化木气格/化火气格
    huaqi_match = re.search(r'化([金木水火土])气格', special_name)
    huaqi_wx = huaqi_match.group(1) if huaqi_match else ''
    is_huaqi = bool(huaqi_wx)
    # 化气格喜忌: 喜化神五行+生化神的五行, 忌克化神的五行+化神克的五行
    # 专旺格喜忌: 喜专旺五行+生专旺的五行, 忌克专旺的五行+专旺克的五行
    # 从格喜忌: 喜从神的旺地, 忌生扶日主的运(比劫+印)"""
c = c.replace(old2, new2)

# 3. 在大运循环中增加化气格的喜忌判断
old3 = """        # V4.3: 专旺格喜忌判断
        if is_zhuanwang:"""
new3 = """        # V4.4: 化气格喜忌判断
        if is_huaqi:
            # 化气格喜: 化神五行+生化神的五行
            if gan_wx == huaqi_wx or zhi_wx == huaqi_wx:
                pattern_xi = True
            # 生化神的五行
            sheng_huaqi = ''
            for k, v in SHENG.items():
                if v == huaqi_wx:
                    sheng_huaqi = k
                    break
            if sheng_huaqi and (gan_wx == sheng_huaqi or zhi_wx == sheng_huaqi):
                pattern_xi = True
            # 化气格忌: 克化神的五行+化神克的五行
            ke_huaqi = KE_ME.get(huaqi_wx, '')
            if ke_huaqi and (gan_wx == ke_huaqi or zhi_wx == ke_huaqi):
                pattern_ji = True
            huaqi_ke = KE.get(huaqi_wx, '')
            if huaqi_ke and (gan_wx == huaqi_ke or zhi_wx == huaqi_ke):
                pattern_ji = True
        
        # V4.3: 专旺格喜忌判断
        if is_zhuanwang:"""
c = c.replace(old3, new3)

# 4. 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.3'", "'module': 'DAYUN_XIJI_V4.4'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.4完成(添加import re+增加化气格喜忌判断)')
