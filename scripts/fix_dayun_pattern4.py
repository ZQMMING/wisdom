# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\dayun_xiji.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 在格局判断部分增加七杀格和建禄月劫格的判断
old = """    # 阳刃格: 月令是阳刃(阳干的帝旺位)
    YANG_REN = {'甲':'卯', '丙':'午', '戊':'午', '庚':'酉', '壬':'子'}
    is_yangren_month = (dm in YANG_REN and month_branch_main == YANG_REN[dm])
    
    per_step = []"""

new = """    # 阳刃格: 月令是阳刃(阳干的帝旺位)
    YANG_REN = {'甲':'卯', '丙':'午', '戊':'午', '庚':'酉', '壬':'子'}
    is_yangren_month = (dm in YANG_REN and month_branch_main == YANG_REN[dm])
    
    # V4.1: 七杀格(偏官格)判断
    # 七杀格: 月令本气是七杀(克日主的同性五行)
    is_qisha_month = False
    if month_benqi_wx == guan_wx:
        dm_yang = dm in '甲丙戊庚壬'
        mb_yang = month_benqi in '甲丙戊庚壬'
        if dm_yang == mb_yang:  # 同性=七杀
            is_qisha_month = True
    # 七杀格用食制: 食神透干有根
    shi_wx = SHENG.get(dm_wx_local, '')  # 日主生的五行=食伤
    shi_stems = []
    for pos in ['year', 'month', 'day', 'hour']:
        stem = pillars[pos][0]
        if WX.get(stem, '') == shi_wx:
            shi_stems.append(stem)
    shi_has_root = False
    for pos in ['year', 'month', 'day', 'hour']:
        branch = pillars[pos][1]
        hidden = HIDDEN_STEMS.get(branch, [])
        for h in hidden:
            if WX.get(h, '') == shi_wx:
                shi_has_root = True
                break
        if shi_has_root:
            break
    is_qisha_yongshi = is_qisha_month and len(shi_stems) > 0 and shi_has_root
    
    # 七杀格用印化: 印星透干有根
    is_qisha_yongyin = is_qisha_month and len(yin_stems) > 0 and yin_has_root
    
    # V4.1: 建禄月劫格判断
    # 建禄: 月令是日主的临官位
    LU_POS = {'甲':'寅', '乙':'卯', '丙':'巳', '丁':'午', '戊':'巳', '己':'午', '庚':'申', '辛':'酉', '壬':'亥', '癸':'子'}
    is_jianlu_month = (month_branch_main == LU_POS.get(dm, ''))
    # 月劫: 月令是日主的劫财位(阴干的帝旺位或阳干的禄位)
    JIE_POS = {'甲':'卯', '乙':'寅', '丙':'午', '丁':'巳', '戊':'午', '己':'巳', '庚':'酉', '辛':'申', '壬':'子', '癸':'亥'}
    is_yuejie_month = (month_branch_main == JIE_POS.get(dm, '')) and not is_jianlu_month
    is_jianlu_yuejie = is_jianlu_month or is_yuejie_month
    # 建禄月劫格用官: 官星透干有根
    is_jianlu_yongguan = is_jianlu_yuejie and len(guan_stems) > 0 and guan_has_root
    # 建禄月劫格用财: 财星透干有根 + 食伤透干
    is_jianlu_yongcai = is_jianlu_yuejie and len(cai_stems) > 0 and cai_has_root and len(shi_stems) > 0
    
    per_step = []"""
c = c.replace(old, new)

# 在has_xi/has_ji条件中增加七杀格和建禄月劫格的喜忌判断
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
        
        # V4.1: 七杀格用食制: 印运为喜(印制食伤扶身), 财运为忌(财生杀)
        if is_qisha_yongshi:
            if gan_wx == yin_wx or zhi_wx == yin_wx:
                pattern_xi = True
            if gan_wx == cai_wx or zhi_wx == cai_wx:
                pattern_ji = True
        
        # 七杀格用印化: 印运为喜, 财运为忌(财破印)
        if is_qisha_yongyin:
            if gan_wx == yin_wx or zhi_wx == yin_wx:
                pattern_xi = True
            if gan_wx == cai_wx or zhi_wx == cai_wx:
                pattern_ji = True
        
        # 建禄月劫格用官: 财运为喜(财生官), 食伤为忌(食伤克官)
        if is_jianlu_yongguan:
            if gan_wx == cai_wx or zhi_wx == cai_wx:
                pattern_xi = True
            if gan_wx == shi_wx or zhi_wx == shi_wx:
                pattern_ji = True
        
        # 建禄月劫格用财: 食伤运为喜(食伤生财), 比劫为忌(比劫夺财)
        if is_jianlu_yongcai:
            if gan_wx == shi_wx or zhi_wx == shi_wx:
                pattern_xi = True
            bijie_wx = dmw  # 比劫五行=日主五行
            if gan_wx == bijie_wx or zhi_wx == bijie_wx:
                pattern_ji = True"""
c = c.replace(old2, new2)

# 修改module版本号
c = c.replace("'module': 'DAYUN_XIJI_V4.0'", "'module': 'DAYUN_XIJI_V4.1'")

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('dayun_xiji.py V4.1完成(增加七杀格用食制/用印化、建禄月劫格用官/用财的格局层面喜忌判断)')
