# -*- coding: utf-8 -*-
"""盲派端到端管道 V1
Feature Calculator → Rule Matcher → Assertion → Judgment Engine → Modern Engine
"""
from typing import Set, List
from .blind_feature_calculator import (
    calc_features, BlindFeatureSet,
    STEM_ELEMENT, BRANCH_ELEMENT, TEN_GODS,
    BRANCH_HIDDEN,
)
from .blind_assertion_registry import ASSERTION_REGISTRY


def feature_to_assertions(f: BlindFeatureSet) -> tuple[Set[str], Set[str]]:
    """从BlindFeatureSet转成 (assertions_present, features_present)"""
    assertions: Set[str] = set()
    features: Set[str] = set()

    # ── 宾主体用 ──
    assertions.add("A-BZ-MAINGUEST")
    features.add("FEAT_MAIN_BRANCHES_PRESENT")
    features.add("FEAT_GUEST_BRANCHES_PRESENT")

    assertions.add("A-TY-TIYONG")
    features.add("FEAT_TI_BRANCHES_PRESENT")
    features.add("FEAT_YONG_BRANCHES_PRESENT")

    assertions.add("A-GF-GONGSHEN")
    features.add("FEAT_WORKING_BRANCHES_PRESENT")
    features.add("FEAT_WORK_TARGETS_PRESENT")

    # ── 正局反局 ──
    if f.zheng_fan_ju == "ZHENG":
        assertions.add("A-PJ-ZHENG")
        features.add("FEAT_ZHENG_JU_TRUE")
    elif f.zheng_fan_ju == "FAN":
        assertions.add("A-PJ-FAN")
        features.add("FEAT_NATAL_FANJU")

    # ── 贼捕 ──
    if f.zei_bu == "ZEI_BU":
        assertions.add("A-ZB-ROBBER_CATCHER")
        features.add("FEAT_ZEI_BU_TRUE")
        features.add("FEAT_MAIN_KILLS_GUEST")

    # ── 墓库 ──
    if f.muku_branches:
        assertions.add("A-MUKU-IDENTIFIED")
        features.add("FEAT_MUKU_PRESENT")
        for m in f.muku_branches:
            features.add(f"FEAT_MUKU_{m}")

    if f.muku_opened:
        assertions.add("A-MUKU-OPENED")
        features.add("FEAT_MUKU_OPENED")
        if "冲" in f.work_methods:
            features.add("FEAT_MUKU_OPEN_BY_CHONG")
        if "刑" in f.work_methods:
            features.add("FEAT_MUKU_OPEN_BY_XING")

    # ── 类象 ──
    # 天干类象
    for s in f.all_stems:
        features.add(f"FEAT_STEM_{s}")
    assertions.add("A-BODY-GAN")

    # 地支类象
    for b in f.all_branches:
        features.add(f"FEAT_BRANCH_{b}")
    assertions.add("A-BODY-ZHI")

    # 宫位类象
    assertions.add("A-BODY-GONGWEI")

    # ── 关系 ──
    if f.chong_pairs:
        features.add("FEAT_CHONG_PRESENT")
        for p in f.chong_pairs:
            b1, b2 = sorted(p)
            features.add(f"FEAT_CHONG_{b1}_{b2}")

    if f.he_pairs:
        features.add("FEAT_HE_PRESENT")
        for p in f.he_pairs:
            b1, b2 = sorted(p)
            features.add(f"FEAT_HE_{b1}_{b2}")

    if f.xing_pairs:
        features.add("FEAT_XING_PRESENT")
        for p in f.xing_pairs:
            b1, b2 = sorted(p)
            features.add(f"FEAT_XING_{b1}_{b2}")

    if f.chuan_pairs:
        features.add("FEAT_CHUAN_PRESENT")
        for p in f.chuan_pairs:
            b1, b2 = sorted(p)
            features.add(f"FEAT_CHUAN_{b1}_{b2}")

    # ── 刑灾牢狱 ──
    disaster_branches = {"亥", "丑", "辰"}
    if set(f.all_branches) & disaster_branches:
        features.add("FEAT_HARMFUL_BRANCH_PRESENT")
        assertions.add("A-DISASTER-PRISON")

    # ── 神煞先算（后面高阶特征要用）──
    # 禄神
    lu_map = {"甲": "寅", "乙": "卯", "丙": "巳", "丁": "午",
              "戊": "巳", "己": "午", "庚": "申", "辛": "酉",
              "壬": "亥", "癸": "子"}
    dm = f.day_master
    lu_zhi = lu_map.get(dm, "")
    if lu_zhi and lu_zhi in f.all_branches:
        features.add("FEAT_LU_PRESENT")
        assertions.add("A-SHEN-LU")

    # 羊刃
    ren_map = {"甲": "卯", "乙": "辰", "丙": "午", "丁": "未",
               "戊": "午", "己": "未", "庚": "酉", "辛": "戌",
               "壬": "子", "癸": "丑"}
    ren_zhi = ren_map.get(dm, "")
    if ren_zhi and ren_zhi in f.all_branches:
        features.add("FEAT_YANGREN_PRESENT")
        assertions.add("A-SHEN-YANGREN")

    # ── 高阶：十神定位（财/官/印在哪个宫位）──
    year_gan, month_gan, day_gan, hour_gan = f.all_stems
    year_zhi, month_zhi, day_zhi, hour_zhi = f.all_branches
    
    # 配偶宫
    spouse_palace = day_zhi
    
    # 地支集合
    branch_set = set(f.all_branches)
    
    # 财星（男命以财为妻/财）
    # 简化：从十神判断财在哪个柱
    wealth_gods = {'正财', '偏财'}
    wealth_pillars = []
    if f.year_tg in wealth_gods:
        wealth_pillars.append('年')
        features.add("FEAT_WEALTH_AT_YEAR")
        features.add("FEAT_ROOT_IN_GUEST")
    if f.month_tg in wealth_gods:
        wealth_pillars.append('月')
        features.add("FEAT_ROOT_IN_GUEST")
    if f.hour_tg in wealth_gods:
        wealth_pillars.append('时')
        features.add("FEAT_ROOT_IN_MAIN")
    
    # 日支藏干为财 = 财在主位
    dm_elem = STEM_ELEMENT[day_gan]
    day_zhi_hidden = BRANCH_HIDDEN.get(day_zhi, [])
    for hs in day_zhi_hidden:
        tg = TEN_GODS.get((dm_elem, STEM_ELEMENT.get(hs, '')), '')
        if tg in wealth_gods:
            features.add("FEAT_ROOT_IN_MAIN")
            break

    # 官杀星
    official_gods = {'正官', '七杀'}
    if f.year_tg in official_gods:
        features.add("FEAT_OFFICIAL_AT_YEAR")
    if day_zhi in [h for h in day_zhi_hidden]:
        for hs in day_zhi_hidden:
            tg = TEN_GODS.get((dm_elem, STEM_ELEMENT.get(hs, '')), '')
            if tg in official_gods:
                features.add("FEAT_OFFICIAL_AT_DAY_HOUR")
                break
    if f.hour_tg in official_gods:
        features.add("FEAT_OFFICIAL_AT_DAY_HOUR")

    # 官透干克身（简化：官杀克日主五行）
    if f.year_tg in official_gods or f.month_tg in official_gods or f.hour_tg in official_gods:
        official_stems = [s for s in [year_gan, month_gan, hour_gan] if TEN_GODS.get((dm_elem, STEM_ELEMENT.get(s, '')), '') in official_gods]
        if official_stems:
            features.add("FEAT_OFFICIAL_TRANSPARENT_ATTACK")

    # ── 高阶：木火=文，金水=理 ──
    elem_set = set()
    for s in f.all_stems:
        elem_set.add(STEM_ELEMENT[s])
    for b in branch_set:
        elem_set.add(BRANCH_ELEMENT[b])
    
    if '木' in elem_set and '火' in elem_set:
        features.add("FEAT_WOOD_FIRE_WEN")
    if '金' in elem_set and '水' in elem_set:
        features.add("FEAT_METAL_WATER_LI")

    # ── 高阶：丑未冲=资本运营 ──
    if frozenset({'丑', '未'}) in f.chong_pairs:
        features.add("FEAT_CHOU_WEI_CHONG_CAPITAL")

    # ── 高阶：穿（比冲更狠）──
    if f.chuan_pairs:
        features.add("FEAT_CHUAN_PRESENT")
        # 时柱被穿
        hour_zhi = f.all_branches[3]
        for p in f.chuan_pairs:
            if hour_zhi in p:
                features.add("FEAT_HOUR_PILLAR_CHUAN")
                break

    # ── 高阶：财官透干无根=富贵不实 ──
    # 简化：财星/官星透干但地支无根
    def stem_rooted(stem, branches):
        """判断天干在地支有没有根"""
        stem_elem = STEM_ELEMENT[stem]
        for b in branches:
            for hs in BRANCH_HIDDEN.get(b, []):
                if STEM_ELEMENT.get(hs, '') == stem_elem:
                    return True
        return False
    
    # 财星透干无根
    for s in [year_gan, month_gan, hour_gan]:
        tg = TEN_GODS.get((dm_elem, STEM_ELEMENT.get(s, '')), '')
        if tg in wealth_gods and not stem_rooted(s, f.all_branches):
            features.add("FEAT_WEALTH_TRANSPARENT_TALENT")  # 财虚透=才华
            break
    
    # 时上财虚透=时尚
    hour_tg = f.hour_tg
    if hour_tg in wealth_gods and not stem_rooted(hour_gan, f.all_branches):
        features.add("FEAT_WEALTH_TRANSPARENT_AT_HOUR_FASHION")

    # ── 高阶：藏支有气=暗中得利 ──
    # 简化：财星/官星藏在地支不透
    for b in f.all_branches:
        for hs in BRANCH_HIDDEN.get(b, []):
            tg = TEN_GODS.get((dm_elem, STEM_ELEMENT.get(hs, '')), '')
            if tg in wealth_gods:
                features.add("FEAT_WEALTH_HIDDEN_ROOT")  # 财藏支有气
                break

    # ── 高阶：羊刃逢冲=血光之灾 ──
    if ren_zhi and ren_zhi in f.all_branches:
        for p in f.chong_pairs:
            if ren_zhi in p:
                features.add("FEAT_YANGREN_CHONG_BLOOD")
                break

    # ── 高阶：财星有根=富贵有源 ──
    for b in f.all_branches:
        for hs in BRANCH_HIDDEN.get(b, []):
            tg = TEN_GODS.get((dm_elem, STEM_ELEMENT.get(hs, '')), '')
            if tg in wealth_gods:
                features.add("FEAT_WEALTH_HAS_ROOT")
                break

    # ── 高阶：食伤做功=技术赚 ──
    food_injury_gods = {'食神', '伤官'}
    has_food_injury = (f.year_tg in food_injury_gods or 
                       f.month_tg in food_injury_gods or 
                       f.hour_tg in food_injury_gods)
    if has_food_injury and len(f.work_methods) > 0:
        features.add("FEAT_FOOD_INJURY_WORK_TECH")

    # ── 高阶：过河拆桥（主位财生宾位官）──
    # 简化：日主坐财（主位财）+ 官杀在宾位
    day_zhi_has_wealth = False
    for hs in BRANCH_HIDDEN.get(day_zhi, []):
        tg = TEN_GODS.get((dm_elem, STEM_ELEMENT.get(hs, '')), '')
        if tg in wealth_gods:
            day_zhi_has_wealth = True
            break
    
    guest_has_official = (f.year_tg in official_gods or f.month_tg in official_gods)
    
    if day_zhi_has_wealth and guest_has_official:
        features.add("FEAT_CROSS_RIVER_BRIDGE")  # 过河拆桥

    # ── 高阶：官统财/财统官 ──
    # 简化：官杀和财都在做功
    has_wealth_work = any(
        TEN_GODS.get((dm_elem, STEM_ELEMENT.get(hs, '')), '') in wealth_gods
        for b in f.working_branches
        for hs in BRANCH_HIDDEN.get(b, [])
    )
    has_official_work = any(
        TEN_GODS.get((dm_elem, STEM_ELEMENT.get(hs, '')), '') in official_gods
        for b in f.working_branches
        for hs in BRANCH_HIDDEN.get(b, [])
    )
    if has_wealth_work and has_official_work:
        features.add("FEAT_GUAN_WEALTH_UNIFIED")

    # ── 高阶：无财伤食当财 ──
    has_wealth_star = (f.year_tg in wealth_gods or 
                       f.month_tg in wealth_gods or 
                       f.hour_tg in wealth_gods)
    for b in f.all_branches:
        for hs in BRANCH_HIDDEN.get(b, []):
            tg = TEN_GODS.get((dm_elem, STEM_ELEMENT.get(hs, '')), '')
            if tg in wealth_gods:
                has_wealth_star = True
                break
    
    if not has_wealth_star and has_food_injury:
        features.add("FEAT_NO_WEALTH_SHANGSHI_AS_WEALTH")
        features.add("FEAT_SHANGSHI_WEALTH_NATURE")

    # ── 高阶：繁花素果（头胎性别）──
    # 日干旺头胎生女，日干弱头胎生儿；财多生女
    # 简化：财多=生女
    wealth_count = sum(1 for s in [year_gan, month_gan, hour_gan] 
                       if TEN_GODS.get((dm_elem, STEM_ELEMENT.get(s, '')), '') in wealth_gods)
    if wealth_count >= 2:
        features.add("FEAT_WEALTH_STRONG_YEAR_MONTH_FEMALE")  # 财旺女命/头胎生女

    # ── 高阶：金水伤官喜见官 ──
    # 金水伤官=金日主+水伤官
    if dm_elem == '金' and '水' in elem_set:
        features.add("FEAT_METAL_WATER_HURT_OFFICIAL")
        if any(s in official_gods for s in [f.year_tg, f.month_tg, f.hour_tg]):
            features.add("FEAT_METAL_WATER_LIKE_OFFICIAL")

    # ── 高阶：土金伤官怕见官 ──
    # 土金伤官=土日主+金伤官
    if dm_elem == '土' and '金' in elem_set:
        features.add("FEAT_EARTH_METAL_HURT_OFFICIAL")

    # ── 高阶：食神带官帽=经理人 ──
    food_gods = {'食神'}
    has_shishen = (f.year_tg in food_gods or f.month_tg in food_gods or f.hour_tg in food_gods)
    if has_shishen and any(s in official_gods for s in [f.year_tg, f.month_tg, f.hour_tg]):
        features.add("FEAT_SHISHEN_WITH_OFFICIAL_MANAGER")

    # ── 高阶：财带官帽=公家 ──
    if any(s in wealth_gods for s in [f.year_tg, f.month_tg, f.hour_tg]) and \
       any(s in official_gods for s in [f.year_tg, f.month_tg, f.hour_tg]):
        features.add("FEAT_WEALTH_WITH_OFFICIAL_CAP_PUBLIC")

    # ── 高阶：官带财帽=管理 ──
    if any(s in official_gods for s in [f.year_tg, f.month_tg, f.hour_tg]) and \
       any(s in wealth_gods for s in [f.year_tg, f.month_tg, f.hour_tg]):
        features.add("FEAT_OFFICIAL_WITH_WEALTH_CAP_MANAGER")

    # ── 高阶：印带官帽=权力 ──
    yin_gods = {'正印', '偏印'}
    has_yin = (f.year_tg in yin_gods or f.month_tg in yin_gods or f.hour_tg in yin_gods)
    if has_yin and any(s in official_gods for s in [f.year_tg, f.month_tg, f.hour_tg]):
        features.add("FEAT_YIN_WITH_OFFICIAL_CAP_POWER")

    # ── 高阶：印带财帽=薪水 ──
    if has_yin and any(s in wealth_gods for s in [f.year_tg, f.month_tg, f.hour_tg]):
        features.add("FEAT_YIN_WITH_WEALTH_CAP_SALARY")

    # ── 高阶：内食神=企业 ──
    if day_zhi and any(
        TEN_GODS.get((dm_elem, STEM_ELEMENT.get(hs, '')), '') in food_gods
        for hs in BRANCH_HIDDEN.get(day_zhi, [])
    ):
        features.add("FEAT_INNER_SHISHEN_BUSINESS")

    # ── 高阶：辰拱水=化工制药 ──
    if '辰' in branch_set and '子' in branch_set:
        features.add("FEAT_CHEN_ZI_CHEMICAL_PHARMA")

    # ── 高阶：丑=玄学 ──
    if '丑' in branch_set:
        features.add("FEAT_CHOU_XUANXUE")

    # ── 高阶：申=金融，酉=法律 ──
    if '申' in branch_set:
        features.add("FEAT_SHEN_FINANCE")
    if '酉' in branch_set:
        features.add("FEAT_YOU_LAW")

    # ── 高阶：阳木遇火=家具，阴木遇火=纺织 ──
    if '甲' in f.all_stems and '火' in elem_set:
        features.add("FEAT_YANG_WOOD_FIRE_FURNITURE")
    if '乙' in f.all_stems and '火' in elem_set:
        features.add("FEAT_YIN_WOOD_FIRE_TEXTILE")

    # ── 高阶：辛金取财=五金，火克金=冶炼 ──
    if '辛' in f.all_stems and has_wealth_star:
        features.add("FEAT_XIN_METAL_WEALTH_HARDWARE")
    if '火' in elem_set and '金' in elem_set:
        features.add("FEAT_FIRE_ATTACK_METAL_SMELTING")

    # ── 高阶：甲丁=头发稀，甲头丁面癸克=面损 ──
    if '甲' in f.all_stems and '丁' in f.all_stems:
        features.add("FEAT_JIA_DING_HAIR_THIN")
    if '甲' in f.all_stems and '丁' in f.all_stems and '癸' in f.all_stems:
        features.add("FEAT_JIA_HEAD_DING_FACE_GUI_ATTACK")

    # ── 高阶：禄配印/禄不配印 ──
    if lu_zhi and lu_zhi in f.all_branches:
        # 有印吗？
        yin_gods = {'正印', '偏印'}
        has_yin = (f.year_tg in yin_gods or f.month_tg in yin_gods or f.hour_tg in yin_gods)
        if has_yin:
            features.add("FEAT_LU_WITH_YIN_EASE")
        else:
            features.add("FEAT_LU_NO_YIN_HARD")
        features.add("FEAT_LU_AS_WEALTH_CONDITION")

    # ── 高阶：羊刃有制/无制 ──
    if ren_zhi and ren_zhi in f.all_branches:
        # 羊刃被合或被冲 = 有制
        ren_controlled = False
        for p in f.he_pairs | f.chong_pairs:
            if ren_zhi in p:
                ren_controlled = True
                break
        if ren_controlled:
            features.add("FEAT_YANGREN_CONTROLLED_ORTHODOX")
        else:
            features.add("FEAT_YANGREN_UNCONTROLLED_UNORTHODOX")

    # ── 高阶：财库/官杀库 ──
    if f.muku_branches:
        # 简化：丑为金库（金=印/官杀 depending on day master）
        # 这里先简化：辰=水库（财库 for fire day master），戌=火库（财库 for metal）
        # 先统一标记
        features.add("FEAT_WEALTH_MUKU_BANK")
        features.add("FEAT_GUANSHA_MUKU_ORG")

    # ── 高阶：驿马被合 ──
    if "FEAT_YIMA_PRESENT" in features:
        # 驿马支被合 = 不动
        for group, yima_zhi in yima_map.items():
            if branch_set & group and yima_zhi in branch_set:
                for p in f.he_pairs:
                    if yima_zhi in p:
                        features.add("FEAT_YIMA_HE_STATIONARY")
                break

    # ── 高阶：夫妻宫状态 ──
    # 日支被冲/穿 = 夫妻宫被破坏
    spouse_palace_damaged = False
    for p in f.chong_pairs | f.chuan_pairs | f.xing_pairs:
        if spouse_palace in p:
            spouse_palace_damaged = True
            break
    if spouse_palace_damaged:
        features.add("FEAT_SPOUSE_PALACE_DAMAGED")
    else:
        features.add("FEAT_SPOUSE_PALACE_QUIET_CONTROL")

    # ── 高阶：牢狱五条结构 ──
    # 1. 亥丑辰坏阳用之物
    if set(f.all_branches) & {'亥', '丑', '辰'}:
        features.add("FEAT_CHOU_CHEN_HAI_DAMAGE_YANG_USEFUL")
    
    # 2. 水多金沉（简化：水>=3且金存在）
    water_count = sum(1 for b in f.all_branches if BRANCH_ELEMENT[b] == '水')
    has_metal = any(BRANCH_ELEMENT[b] == '金' for b in f.all_branches)
    if water_count >= 3 and has_metal:
        features.add("FEAT_WATER_METAL_SINK_PRISON")
    
    # 3. 枭神夺食（简化：偏印克食神）
    # 这里先简化，后面再精确

    # 4. 劫财+伤官+抗官杀（简化）
    # 5. 反局+丑辰
    if f.zheng_fan_ju == "FAN" and (frozenset({'丑'}) & set(f.all_branches) or frozenset({'辰'}) & set(f.all_branches)):
        features.add("FEAT_FANJU_WITH_CHOU_CHEN_MOST_PRISON")

    # ── 神煞（续）──
    # 驿马（简化：申子辰马在寅，寅午戌马在申，巳酉丑马在亥，亥卯未马在巳）
    yima_map = {
        frozenset({'申', '子', '辰'}): '寅',
        frozenset({'寅', '午', '戌'}): '申',
        frozenset({'巳', '酉', '丑'}): '亥',
        frozenset({'亥', '卯', '未'}): '巳',
    }
    branch_set = set(f.all_branches)
    for group, yima_zhi in yima_map.items():
        if branch_set & group:
            if yima_zhi in branch_set:
                features.add("FEAT_YIMA_PRESENT")
                assertions.add("A-SHEN-YIMA")
            break

    # ── 高阶：空亡分宫 ──
    # 六甲旬空亡表
    XUNKONG_MAP = {
        '甲子': ('戌', '亥'), '甲戌': ('申', '酉'), '甲申': ('午', '未'),
        '甲午': ('辰', '巳'), '甲辰': ('寅', '卯'), '甲寅': ('子', '丑'),
    }
    
    # 日柱旬空
    day_gz_str = f.day_gz
    xunkong_branches = set()
    for jia_xun, (kong1, kong2) in XUNKONG_MAP.items():
        # 简化：日柱地支在哪个旬
        jia_xun_start = jia_xun[1]
        # 这里用简化方法：直接查日柱
        pass
    
    # 更简单的方法：用日柱算旬空
    # 甲子旬中戌亥空，甲戌旬中申酉空...
    # 这里用一个简化映射
    day_zhi_xunkong = {
        '子': ('戌', '亥'), '丑': ('戌', '亥'),
        '寅': ('申', '酉'), '卯': ('申', '酉'),
        '辰': ('午', '未'), '巳': ('午', '未'),
        '午': ('辰', '巳'), '未': ('辰', '巳'),
        '申': ('寅', '卯'), '酉': ('寅', '卯'),
        '戌': ('子', '丑'), '亥': ('子', '丑'),
    }
    
    # 这里用日柱干支来算旬空（简化版）
    # 先标记有没有空亡
    xunkong_found = set()
    for b in f.all_branches:
        # 简化：如果是日支，不算空亡
        pass
    
    # 简化：直接标记空亡特征（后面精确计算）
    # 年柱空亡=祖业空，月柱空亡=兄弟无靠，日柱空亡=夫妻缘薄，时柱空亡=子女迟育
    # 这里先简化：如果有戌亥、申酉等组合，标记空亡
    branch_set = set(f.all_branches)
    
    # 简化版空亡检测（后面精确）
    # 先标记：年柱地支
    year_zhi = f.all_branches[0]
    month_zhi = f.all_branches[1]
    day_zhi = f.all_branches[2]
    hour_zhi = f.all_branches[3]
    
    # 简化：日支为日主坐支，不算空亡
    # 这里先留个占位，后面精确计算旬空
    # features.add("FEAT_YEAR_KONGWANG_ZUYE")
    # features.add("FEAT_MONTH_KONGWANG_BROTHER")
    # features.add("FEAT_DAY_KONGWANG_SPOUSE")
    # features.add("FEAT_HOUR_KONGWANG_CHILDREN")

    # ── 高阶：桃花 ──
    # 桃花：申子辰在酉，寅午戌在卯，巳酉丑在午，亥卯未在子
    taohua_map = {
        frozenset({'申', '子', '辰'}): '酉',
        frozenset({'寅', '午', '戌'}): '卯',
        frozenset({'巳', '酉', '丑'}): '午',
        frozenset({'亥', '卯', '未'}): '子',
    }
    
    for group, taohua_zhi in taohua_map.items():
        if branch_set & group:
            if taohua_zhi in branch_set:
                features.add("FEAT_TAOHUA_PRESENT")
            break

    # ── 高阶：华盖 ──
    # 华盖：申子辰在辰，寅午戌在戌，巳酉丑在丑，亥卯未在未
    huagai_map = {
        frozenset({'申', '子', '辰'}): '辰',
        frozenset({'寅', '午', '戌'}): '戌',
        frozenset({'巳', '酉', '丑'}): '丑',
        frozenset({'亥', '卯', '未'}): '未',
    }
    
    for group, huagai_zhi in huagai_map.items():
        if branch_set & group:
            if huagai_zhi in branch_set:
                features.add("FEAT_HUAGAI_PRESENT")
            break

    # ── 高阶：将星 ──
    # 将星：申子辰在子，寅午戌在午，巳酉丑在酉，亥卯未在卯
    jiangxing_map = {
        frozenset({'申', '子', '辰'}): '子',
        frozenset({'寅', '午', '戌'}): '午',
        frozenset({'巳', '酉', '丑'}): '酉',
        frozenset({'亥', '卯', '未'}): '卯',
    }
    
    for group, jiangxing_zhi in jiangxing_map.items():
        if branch_set & group:
            if jiangxing_zhi in branch_set:
                features.add("FEAT_JIANGXING_PRESENT")
            break

    # ── 婚姻 ──
    features.add(f"FEAT_SPOUSE_PALACE_{spouse_palace}")
    features.add("FEAT_SPOUSE_PALACE_PRESENT")

    # 配偶星（男财女官，这里先简化）
    features.add("FEAT_SPOUSE_STAR_PRESENT")
    assertions.add("A-MARRIAGE-TIMING")

    return assertions, features


def run_pipeline(year_gz: str, month_gz: str, day_gz: str, hour_gz: str) -> dict:
    """端到端跑一个案例"""
    # L1-L3: Feature Calculator
    f = calc_features(year_gz, month_gz, day_gz, hour_gz)

    # Feature → Assertion + Features
    assertions, features = feature_to_assertions(f)

    # Judgment Engine
    from .blind_judgment_engine import BlindJudgmentEngine
    jengine = BlindJudgmentEngine()
    jresult = jengine.judge(assertions, features)

    # Modern Engine
    from .blind_modern_engine import ModernSemanticEngine
    mengine = ModernSemanticEngine()
    mod_result = mengine.express(list(jresult.triggered_judgments))

    return {
        "features": f,
        "assertions": assertions,
        "features_present": features,
        "judgment_result": jresult,
        "modern_result": mod_result,
    }


if __name__ == "__main__":
    # 测试案例5：丁亥 癸丑 己未 癸酉
    print("=== 案例5：丁亥 癸丑 己未 癸酉 ===")
    r = run_pipeline("丁亥", "癸丑", "己未", "癸酉")
    print()
    print("--- Feature ---")
    f = r["features"]
    print(f"  冲对: {f.chong_pairs}")
    print(f"  墓库: {f.muku_branches}")
    print(f"  开库: {f.muku_opened}")
    print(f"  做功: {f.work_methods}")
    print()
    print("--- Assertions ---")
    print(f"  数量: {len(r['assertions'])}")
    for a in sorted(r["assertions"]):
        print(f"    - {a}")
    print()
    print("--- Features ---")
    print(f"  数量: {len(r['features_present'])}")
    for feat in sorted(r["features_present"])[:20]:
        print(f"    - {feat}")
    if len(r["features_present"]) > 20:
        print(f"    ... 还有 {len(r['features_present'])-20} 条")
    print()
    print("--- Judgment ---")
    jr = r["judgment_result"]
    print(f"  触发: {jr.total_triggered}")
    print(f"  跳过: {jr.total_skipped}")
    for j in jr.triggered_judgments:
        print(f"    ✓ {j.judgment_id}: {j.judgment_result}")
    print()
    print("--- Modern ---")
    mr = r["modern_result"]
    print(f"  映射: {mr.total_mapped}")
    for e in mr.expressions:
        print(f"    [{e.modern_domain}] {e.modern_expression}")
