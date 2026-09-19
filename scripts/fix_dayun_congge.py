# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在格局判断部分增加从格的喜忌判断
old = """    is_shangguan_peiyin = is_shangguan_month and len(yin_stems) > 0 and yin_has_root
    
    # V3.9: 其他格局判断 (基于子平真诠取运规则)"""

new = """    is_shangguan_peiyin = is_shangguan_month and len(yin_stems) > 0 and yin_has_root
    
    # V4.2: 从格喜忌判断 (基于滴天髓从象: 从格喜顺势, 忌生扶日主)
    # 从格类型: 从财格/从杀格/从官格/从儿格/从势格
    special_name = yongshen_result.get('special', '') or ''
    is_cong_ge = any(cong_type in special_name for cong_type in ['从财格', '从杀格', '从官格', '从儿格', '从势格'])
    # 从格喜忌: 喜从神的旺地, 忌生扶日主的运(比劫+印)
    # 从财格: 喜财+食伤, 忌比劫+印
    # 从杀格/从官格: 喜官杀+财, 忌比劫+印
    # 从儿格: 喜食伤+财, 忌印+比劫
    # 从势格: 喜顺势(最旺的五行), 忌比劫+印
    
    # V3.9: 其他格局判断 (基于子平真诠取运规则)"""
c = c.replace(old, new)

# 在大运循环中增加从格的喜忌判断
old2 = """        # 阳刃格: 财乡为喜(财生官煞制刃), 包括大运藏干中的财
        if is_yangren_month:
            if gan_wx == cai_wx or zhi_wx == cai_wx:
                pattern_xi = True
            else:
                # 检查大运藏干中是否有财
                for h in zhi_hidden:
                    if WX.get(h, '') == cai_wx:
                        pattern_xi = True
                        break"""

new2 = """        # 阳刃格: 财乡为喜(财生官煞制刃), 包括大运藏干中的财
        if is_yangren_month:
            if gan_wx == cai_wx or zhi_wx == cai_wx:
                pattern_xi = True
            else:
                # 检查大运藏干中是否有财
                for h in zhi_hidden:
                    if WX.get(h, '') == cai_wx:
                        pattern_xi = True
                        break
        
        # V4.2: 从格喜忌判断
        if is_cong_ge:
            # 从格忌生扶日主的运(比劫+印)
            if gan_wx == dmw or zhi_wx == dmw:  # 比劫运
                pattern_ji = True
            if gan_wx == yin_wx or zhi_wx == yin_wx:  # 印运
                pattern_ji = True
            # 从格喜从神的旺地
            if '从财格' in special_name:
                if gan_wx == cai_wx or zhi_wx == cai_wx:  # 财运
                    pattern_xi = True
                if gan_wx == shi_wx or zhi_wx == shi_wx:  # 食伤运
                    pattern_xi = True
            elif '从杀格' in special_name or '从官格' in special_name:
                if gan_wx == guan_wx or zhi_wx == guan_wx:  # 官杀运
                    pattern_xi = True
                if gan_wx == cai_wx or zhi_wx == cai_wx:  # 财运
                    pattern_xi = True
            elif '从儿格' in special_name:
                if gan_wx == shi_wx or zhi_wx == shi_wx:  # 食伤运
                    pattern_xi = True
                if gan_wx == cai_wx or zhi_wx == cai_wx:  # 财运
                    pattern_xi = True"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.1'", "'module': 'DAYUN_XIJI_V4.2'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.2完成(增加从格喜忌判断: 从财/从杀/从官/从儿/从势, 喜从神旺地, 忌生扶日主)')
