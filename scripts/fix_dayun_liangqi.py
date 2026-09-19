# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在化气格判断后面增加两气格的喜忌判断
old = """    is_huaqi = bool(huaqi_wx)
    # 化气格喜忌: 喜化神五行+生化神的五行, 忌克化神的五行+化神克的五行
    # 专旺格喜忌: 喜专旺五行+生专旺的五行, 忌克专旺的五行+专旺克的五行
    # 从格喜忌: 喜从神的旺地, 忌生扶日主的运(比劫+印)"""

new = """    is_huaqi = bool(huaqi_wx)
    # V4.5: 两气格喜忌判断 (基于滴天髓两气成象: 两气格喜两行旺地, 忌克泄两行)
    # 两气格类型: 两气成象(木火)/两气成象(火土)/两气成象(土金)/两气成象(金水)/两气成象(水木)
    liangqi_match = re.search(r'两气成象\(([金木水火土])([金木水火土])\)', special_name)
    liangqi_wuxing = [liangqi_match.group(1), liangqi_match.group(2)] if liangqi_match else []
    is_liangqi = len(liangqi_wuxing) == 2
    # 两气格喜忌: 喜两行的五行, 忌克两行的五行
    # 化气格喜忌: 喜化神五行+生化神的五行, 忌克化神的五行+化神克的五行
    # 专旺格喜忌: 喜专旺五行+生专旺的五行, 忌克专旺的五行+专旺克的五行
    # 从格喜忌: 喜从神的旺地, 忌生扶日主的运(比劫+印)"""
c = c.replace(old, new)

# 在大运循环中增加两气格的喜忌判断
old2 = """        # V4.4: 化气格喜忌判断
        if is_huaqi:"""

new2 = """        # V4.5: 两气格喜忌判断
        if is_liangqi:
            # 两气格喜: 两行的五行
            for lw in liangqi_wuxing:
                if gan_wx == lw or zhi_wx == lw:
                    pattern_xi = True
            # 两气格忌: 克两行的五行
            for lw in liangqi_wuxing:
                ke_lw = KE_ME.get(lw, '')
                if ke_lw and (gan_wx == ke_lw or zhi_wx == ke_lw):
                    pattern_ji = True
        
        # V4.4: 化气格喜忌判断
        if is_huaqi:"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.4'", "'module': 'DAYUN_XIJI_V4.5'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.5完成(增加两气格喜忌判断: 两气成象, 喜两行旺地, 忌克两行)')
