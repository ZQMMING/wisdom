# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = c = f.read()

# 在从格判断后面增加专旺格的喜忌判断
old = """    is_cong_ge = any(cong_type in special_name for cong_type in ['从财格', '从杀格', '从官格', '从儿格', '从势格'])
    # 从格喜忌: 喜从神的旺地, 忌生扶日主的运(比劫+印)"""

new = """    is_cong_ge = any(cong_type in special_name for cong_type in ['从财格', '从杀格', '从官格', '从儿格', '从势格'])
    # V4.3: 专旺格喜忌判断 (基于滴天髓一行得气: 专旺格喜顺势, 忌克泄)
    # 专旺格类型: 曲直格(木)/炎上格(火)/稼穡格(土)/从革格(金)/润下格(水)
    zhuanwang_names = {'曲直格': '木', '炎上格': '火', '稼穡格': '土', '从革格': '金', '润下格': '水'}
    zhuanwang_wx = ''
    for zn_name, zn_wx in zhuanwang_names.items():
        if zn_name in special_name:
            zhuanwang_wx = zn_wx
            break
    is_zhuanwang = bool(zhuanwang_wx)
    # 专旺格喜忌: 喜专旺五行+生专旺的五行, 忌克专旺的五行+专旺克的五行
    # 从格喜忌: 喜从神的旺地, 忌生扶日主的运(比劫+印)"""
c = c.replace(old, new)

# 在大运循环中增加专旺格的喜忌判断
old2 = """        # V4.2: 从格喜忌判断
        if is_cong_ge:"""

new2 = """        # V4.3: 专旺格喜忌判断
        if is_zhuanwang:
            # 专旺格喜: 专旺五行+生专旺的五行
            if gan_wx == zhuanwang_wx or zhi_wx == zhuanwang_wx:
                pattern_xi = True
            # 生专旺的五行
            sheng_zhuanwang = ''
            for k, v in SHENG.items():
                if v == zhuanwang_wx:
                    sheng_zhuanwang = k
                    break
            if sheng_zhuanwang and (gan_wx == sheng_zhuanwang or zhi_wx == sheng_zhuanwang):
                pattern_xi = True
            # 专旺格忌: 克专旺的五行+专旺克的五行
            ke_zhuanwang = KE_ME.get(zhuanwang_wx, '')
            if ke_zhuanwang and (gan_wx == ke_zhuanwang or zhi_wx == ke_zhuanwang):
                pattern_ji = True
            zhuanwang_ke = KE.get(zhuanwang_wx, '')
            if zhuanwang_ke and (gan_wx == zhuanwang_ke or zhi_wx == zhuanwang_ke):
                pattern_ji = True
        
        # V4.2: 从格喜忌判断
        if is_cong_ge:"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.2'", "'module': 'DAYUN_XIJI_V4.3'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.3完成(增加专旺格喜忌判断: 曲直/炎上/稼穡/从革/润下, 喜专旺+生专旺, 忌克专旺+专旺克)')
