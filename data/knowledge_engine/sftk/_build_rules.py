# -*- coding: utf-8 -*-
"""Author RuleCandidate set for SFTK, bound to ORIGINAL sources."""
import json, io, os

OUTDIR = r"D:\shuntian\data\knowledge_engine\sftk"
ENG="SHENFENG_TONGKAO"
def sid(ch): return f"SFTK-{ch}-001"

R=[]
def add(ch, rtype, scope, subj, pred, pre, op, outs, ev, note):
    R.append({
        "rule_id": f"CAND-SFTK-{len(R)+1:03d}",
        "engine": ENG,
        "source_id": sid(ch),
        "rule_type": rtype,
        "scope": scope,
        "subject": subj,
        "predicate": pred,
        "preconditions": pre,
        "operation": op,
        "outputs": outs,
        "evidence_requirement": ev,
        "status": "CANDIDATE",
        "notes": note,
    })

C=lambda conds: {"type":"conjunction","conditions":conds}
def eq(f,v): return {"field":f,"operator":"equals","value":v}
def in_(f,arr): return {"field":f,"operator":"in","value":arr}
def has(f): return {"field":f,"operator":"has","value":f}
def abs_(f): return {"field":f,"operator":"absent","value":f}
def em(f,v): return {"field":f,"value":v}

# ===== 006 動靜說 =====
add("006","activation","natal","stem_interaction","can_act",
    C([eq("plane","天干")]),"emit",[em("cross_branch","天干之動只能攻天干之動，不能攻地支之靜")],"A",
    "神峰通考卷一·動靜說")
add("006","activation","natal","stem_interaction","can_act",
    C([eq("plane","地支")]),"emit",[em("cross_stem","地支之靜只能攻地支之靜，不能攻天干之動")],"A",
    "神峰通考卷一·動靜說")
add("006","activation","natal","storage_branch","need_unlock",
    C([in_("branch",["辰","戌","丑","未"])]),"require",[em("unlock_method","須沖開庫鎖方出所藏")],"A",
    "神峰通考卷一·動靜說")

# ===== 007 蓋頭說 =====
add("007","diagnosis","natal","food_hurt","exposed_harm",
    C([eq("ten_god","傷官"),eq("stem_position","透出天干")]),"emit",[em("status","傷官露出頭面即作害")],"A",
    "神峰通考卷一·蓋頭說")
add("007","medicine","decade","luck_stem","covers_branch_head",
    C([has("decade_stem")]),"emit",[em("effect","運天干蓋地支頭可抑其害")],"B",
    "神峰通考卷一·蓋頭說")

# ===== 008 六親說 =====
add("008","definition","natal","year_pillar","represents",
    C([has("year_stem")]),"emit",[em("rel","年上財官主祖宗榮顯")],"A",
    "神峰通考卷一·六親說")
add("008","definition","natal","month_pillar","represents",
    C([has("month_stem")]),"emit",[em("rel","月上官殺主兄弟凋零")],"A",
    "神峰通考卷一·六親說")
add("008","definition","natal","father","is",
    C([]),"emit",[em("father","偏財為父")],"A","神峰通考卷一·六親說")
add("008","definition","natal","mother","is",
    C([]),"emit",[em("mother","正印為母")],"A","神峰通考卷一·六親說")
add("008","definition","natal","children","is",
    C([]),"emit",[em("children","以官殺為子")],"A","神峰通考卷一·六親說")
add("008","resolution","natal","day_branch","bingsi",
    C([in_("day_branch",["巳"])]),"emit",[em("note","乙巳丁巳坐下有庚，不可謂無壻")],"B",
    "神峰通考卷一·六親說")
add("008","resolution","natal","day_branch","xinhai",
    C([eq("day_branch","亥")]),"emit",[em("note","辛亥日坐下正財，不可謂無郎")],"B",
    "神峰通考卷一·六親說")
add("008","resolution","natal","day_branch","wushen",
    C([eq("day_branch","申")]),"emit",[em("status","戊申日女命坐下庚金，極損夫")],"B",
    "神峰通考卷一·六親說")
add("008","resolution","natal","day_branch","jiayin",
    C([eq("day_branch","寅")]),"emit",[em("status","甲寅日夫星絕於寅，女命極剋夫")],"B",
    "神峰通考卷一·六親說")

# ===== 009 病藥說類 =====
add("009","resolution","natal","pattern","has_bing",
    C([has("bing")]),"emit",[em("status","有病方為貴，無傷不是奇")],"A",
    "神峰通考卷一·病藥說類")
add("009","resolution","natal","pattern","bing_zhong_de_yao",
    C([eq("bing_yao_ratio","病重藥得")]),"emit",[em("wealth_rank","大富大貴")],"B",
    "神峰通考卷一·病藥說類")
add("009","resolution","natal","pattern","bing_qing_de_yao",
    C([eq("bing_yao_ratio","病輕藥得")]),"emit",[em("wealth_rank","略富略貴")],"B",
    "神峰通考卷一·病藥說類")
add("009","resolution","natal","pattern","no_bing_no_yao",
    C([abs_("bing"),abs_("yao")]),"emit",[em("wealth_rank","不富不貴，平常人")],"B",
    "神峰通考卷一·病藥說類")
add("009","medicine","natal","wealth_use","bing_medicine",
    C([eq("use","財"),eq("bing","比肩")]),"emit",[em("medicine","喜官殺為藥")],"A",
    "神峰通考卷一·病藥說類")
add("009","medicine","natal","food_hurt_use","bing_medicine",
    C([eq("use","食神傷官"),eq("bing","印")]),"emit",[em("medicine","喜財為藥")],"A",
    "神峰通考卷一·病藥說類")
add("009","resolution","natal","diagnosis_method","cong_zhong_zhe",
    C([has("month_branch_qi")]),"emit",[em("method","從重者論：先看日干次看月令同氣聚處")],"B",
    "神峰通考卷一·病藥說類")

# ===== 010 雕枯旺弱四病說類 =====
add("010","medicine","decade","officer_too_strong","remove",
    C([eq("ten_god","官星"),eq("strength","太旺")]),"emit",[em("luck_direction","宜行傷官運以去其官星")],"A",
    "神峰通考卷一·四病說")
add("010","medicine","decade","wealth_too_strong","remove",
    C([eq("ten_god","財星"),eq("strength","太旺")]),"emit",[em("luck_direction","宜行比劫運以去其財星")],"A",
    "神峰通考卷一·四病說")
add("010","medicine","decade","seal_too_strong","break",
    C([eq("ten_god","印星"),eq("strength","太旺")]),"emit",[em("luck_direction","宜行財星運以破其印星")],"A",
    "神峰通考卷一·四病說")
add("010","medicine","decade","daymaster_too_strong","control",
    C([eq("target","日干"),eq("strength","太旺")]),"emit",[em("luck_direction","宜行官殺運以制其日主")],"A",
    "神峰通考卷一·四病說")
add("010","resolution","natal","officer_root","absent",
    C([eq("ten_god","官星"),abs_("root")]),"emit",[em("note","官星無根則官從何出")],"A",
    "神峰通考卷一·四病說")
add("010","effectiveness","natal","weak_with_root","can_strengthen",
    C([eq("strength","弱"),has("root")]),"emit",[em("note","弱而有根則可致其旺，根在苗先")],"A",
    "神峰通考卷一·四病說")

# ===== 011 損益生長四藥說類 =====
add("011","medicine","natal","officer_surplus","reduce",
    C([eq("ten_god","官星"),eq("qi","有餘")]),"emit",[em("medicine","損其官星")],"A",
    "神峰通考卷一·四藥說")
add("011","medicine","natal","wealth_surplus","reduce",
    C([eq("ten_god","財星"),eq("qi","有餘")]),"emit",[em("medicine","損其財星")],"A",
    "神峰通考卷一·四藥說")
add("011","medicine","decade","officer_deficit","supplement",
    C([eq("ten_god","官星"),eq("qi","不足")]),"emit",[em("luck_direction","謂官旺之鄉")],"A",
    "神峰通考卷一·四藥說")
add("011","medicine","decade","wealth_deficit","supplement",
    C([eq("ten_god","財星"),eq("qi","不足")]),"emit",[em("luck_direction","行財旺之地")],"A",
    "神峰通考卷一·四藥說")
add("011","resolution","natal","sheng_position","not_yet_strong",
    C([has("sheng_position")]),"emit",[em("note","財官印臨生地，未可便為旺")],"A",
    "神峰通考卷一·四藥說")

# ===== 012 正官格 / 偏官格 =====
add("012","definition","natal","zheng_guan","is",
    C([eq("yin_yang","陰陽相見")]),"emit",[em("ten_god","正官")],"A",
    "神峰通考卷一·正官格")
add("012","resolution","natal","officer_heavy_shallow_root","becomes_sha",
    C([eq("ten_god","官星"),eq("condition","犯重日主根弱")]),"emit",[em("becomes","七殺")],"B",
    "神峰通考卷一·正官格")
add("012","medicine","natal","seven_killings","need_control",
    C([eq("ten_god","七殺"),eq("condition","尅身")]),"emit",[em("medicine","喜傷官食神以制其官殺")],"A",
    "神峰通考卷一·正官格")
add("012","medicine","natal","officer_too_many","control",
    C([eq("ten_god","官星"),eq("condition","官旺官多")]),"emit",[em("medicine","喜食神以制去之")],"A",
    "神峰通考卷一·正官格")
add("012","medicine","natal","officer_weak","generate",
    C([eq("ten_god","官星"),eq("condition","氣弱")]),"emit",[em("medicine","喜財神以生之")],"A",
    "神峰通考卷一·正官格")
add("012","resolution","natal","official_seal","cheng",
    C([eq("pattern","官印兩全"),abs_("chong_xing_po_hai")]),"emit",[em("status","官生印印生身，廊廟大材")],"B",
    "神峰通考卷一·正官格")
add("012","resolution","natal","month_zheng_guan","cheng",
    C([eq("pattern","月正官"),abs_("chong_xing_po_hai")]),"emit",[em("status","功名顯達為奇特")],"B",
    "神峰通考卷一·正官格")
add("012","definition","natal","pian_guan","is",
    C([eq("yin_yang","同陰同陽")]),"emit",[em("ten_god","偏官(七殺)")],"A",
    "神峰通考卷一·偏官格")
add("012","resolution","natal","sha_first","priority",
    C([has("seven_killings")]),"emit",[em("method","有殺須論殺，無殺方論用")],"A",
    "神峰通考卷一·偏官格")
add("012","resolution","natal","follow_sha","pattern",
    C([eq("daymaster_qi","全無生氣"),eq("chart","純官殺")]),"emit",[em("pattern","棄命從殺")],"B",
    "神峰通考卷一·偏官格")
add("012","medicine","decade","follow_sha","support",
    C([eq("pattern","棄命從殺")]),"emit",[em("luck_direction","喜財生殺，行財殺運生助其殺")],"B",
    "神峰通考卷一·偏官格")
add("012","suppress","decade","follow_sha","forbid",
    C([eq("pattern","棄命從殺")]),"emit",[em("forbid","畏見日主根及制殺運")],"B",
    "神峰通考卷一·偏官格")
add("012","resolution","natal","xu_guan","value",
    C([eq("position","歲日時虛官")]),"emit",[em("status","虛官用之十有九貴")],"B",
    "神峰通考卷一·正官格")

# ===== 060-067 神趣八法 =====
add("061","definition","natal","shu_xiang","pattern",
    C([in_("day_stem",["甲","乙"]),eq("branch_combo","亥卯未全")]),"emit",[em("pattern","屬象")],"A",
    "神峰通考卷三·神趣八法")
add("062","definition","natal","cong_xiang","pattern",
    C([in_("day_stem",["甲","乙"]),abs_("root"),eq("branch","純金")]),"emit",[em("pattern","從象(從金)")],"B",
    "神峰通考卷三·神趣八法")
add("063","definition","natal","hua_xiang","pattern",
    C([in_("day_stem",["甲","乙"]),in_("month_branch",["辰","戌","丑","未"]),eq("tian_gan","一己合甲")]),"emit",[em("pattern","甲己化土")],"B",
    "神峰通考卷三·神趣八法")
add("063","medicine","decade","hua_xiang","luck",
    C([eq("pattern","甲己化土")]),"emit",[em("luck_direction","喜行火旺運")],"B",
    "神峰通考卷三·神趣八法")
add("064","definition","natal","zhao_xiang","pattern",
    C([eq("day_stem","丙"),in_("branch",["巳","午","未"]),eq("hour_branch","卯")]),"emit",[em("pattern","木火相照")],"B",
    "神峰通考卷三·神趣八法")
add("065","resolution","natal","fan_xiang","pattern",
    C([eq("condition","月令用神引至時上絕鄉")]),"emit",[em("pattern","返象，用而不用")],"B",
    "神峰通考卷三·神趣八法")
add("066","definition","natal","gui_xiang","pattern",
    C([in_("day_stem",["甲","乙"]),eq("season","秋"),eq("branch","純金")]),"emit",[em("pattern","鬼象")],"B",
    "神峰通考卷三·神趣八法")
add("067","definition","natal","fu_xiang","pattern",
    C([eq("branch","寅午戌全"),eq("month_branch","午"),eq("day_stem","壬"),abs_("丁"),abs_("壬根")]),"emit",[em("pattern","伏象")],"C",
    "神峰通考卷三·神趣八法")

# ===== 068 論大運 / 069 論太歲 =====
add("068","activation","year","year_luck_clash","judgement",
    C([has("clash")]),"emit",[em("note","歲沖運不吉，運沖歲甚不利")],"A",
    "神峰通考卷三·論大運")
add("068","resolution","year","year_luck_sheng","good",
    C([has("year_luck_sheng")]),"emit",[em("status","歲運相生者吉")],"A",
    "神峰通考卷三·論大運")
add("069","activation","year","day_clashes_year","severity",
    C([eq("relation","日犯歲君")]),"emit",[em("status","災殃必重，有救其年反為財")],"B",
    "神峰通考卷三·論太歲")

# ===== 103 天德 / 104 月德 / 107 華蓋 =====
add("104","definition","natal","yue_de","is",
    C([eq("month_group","寅午戌")]),"emit",[em("shen_sha","月德在丙")],"A",
    "神峰通考卷四·月德")
add("104","definition","natal","yue_de","is",
    C([eq("month_group","申子辰")]),"emit",[em("shen_sha","月德在壬")],"A",
    "神峰通考卷四·月德")
add("104","definition","natal","yue_de","is",
    C([eq("month_group","亥卯未")]),"emit",[em("shen_sha","月德在甲")],"A",
    "神峰通考卷四·月德")
add("104","definition","natal","yue_de","is",
    C([eq("month_group","巳酉丑")]),"emit",[em("shen_sha","月德在庚")],"A",
    "神峰通考卷四·月德")
add("107","definition","natal","hua_gai","is",
    C([eq("year_group","寅午戌"),eq("branch","戌")]),"emit",[em("shen_sha","華蓋")],"A",
    "神峰通考卷四·華蓋")
add("107","definition","natal","hua_gai","is",
    C([eq("year_group","亥卯未"),eq("branch","未")]),"emit",[em("shen_sha","華蓋")],"A",
    "神峰通考卷四·華蓋")
add("107","definition","natal","hua_gai","is",
    C([eq("year_group","申子辰"),eq("branch","辰")]),"emit",[em("shen_sha","華蓋")],"A",
    "神峰通考卷四·華蓋")
add("107","definition","natal","hua_gai","is",
    C([eq("year_group","巳酉丑"),eq("branch","丑")]),"emit",[em("shen_sha","華蓋")],"A",
    "神峰通考卷四·華蓋")
add("107","definition","natal","jiang_xing","is",
    C([eq("year_group","寅午戌"),eq("branch","午")]),"emit",[em("shen_sha","將星")],"A",
    "神峰通考卷四·將星")
add("107","definition","natal","yi_ma","is",
    C([eq("year_group","寅午戌"),eq("branch","申")]),"emit",[em("shen_sha","驛馬")],"A",
    "神峰通考卷四·驛馬")

# ===== 113 孤神 / 114 劫殺 / 115 破軍 / 117 紅艷殺 / 122 天羅地網 / 125 太白星 =====
add("113","definition","natal","gu_shen","is",
    C([eq("year_branch","子"),eq("branch","未")]),"emit",[em("shen_sha","孤神")],"A",
    "神峰通考卷四·孤神")
add("114","definition","natal","jie_sha","is",
    C([eq("year_group","申子辰"),eq("branch","巳")]),"emit",[em("shen_sha","劫殺")],"A",
    "神峰通考卷四·劫殺")
add("114","definition","natal","jie_sha","is",
    C([eq("year_group","寅午戌"),eq("branch","亥")]),"emit",[em("shen_sha","劫殺")],"A",
    "神峰通考卷四·劫殺")
add("114","definition","natal","jie_sha","is",
    C([eq("year_group","亥卯未"),eq("branch","申")]),"emit",[em("shen_sha","劫殺")],"A",
    "神峰通考卷四·劫殺")
add("114","definition","natal","jie_sha","is",
    C([eq("year_group","巳酉丑"),eq("branch","寅")]),"emit",[em("shen_sha","劫殺")],"A",
    "神峰通考卷四·劫殺")
add("115","definition","natal","po_jun","is",
    C([eq("year_group","申子辰"),eq("branch","亥")]),"emit",[em("shen_sha","破軍")],"A",
    "神峰通考卷四·破軍")
add("117","definition","natal","hong_yan","is",
    C([eq("ming_wu","木"),in_("branch",["丑","子"])]),"emit",[em("shen_sha","紅艷殺")],"B",
    "神峰通考卷四·紅艷殺")
add("122","definition","natal","tian_luo","is",
    C([eq("branch","辰")]),"emit",[em("shen_sha","天羅")],"A",
    "神峰通考卷四·天羅地網")
add("122","definition","natal","di_wang","is",
    C([eq("branch","戌")]),"emit",[em("shen_sha","地網")],"A",
    "神峰通考卷四·天羅地網")

# ===== 130/131 起大運 =====
add("130","definition","decade","da_yun_direction","is",
    C([eq("yin_yang_nan_nv","陽男陰女")]),"emit",[em("direction","順行")],"A",
    "神峰通考卷四·起大運法")
add("131","definition","decade","da_yun_direction","is",
    C([eq("yin_yang_nan_nv","陰男陽女")]),"emit",[em("direction","逆行")],"A",
    "神峰通考卷四·起大運法")

# ===== 129 看命入式 =====
add("129","resolution","natal","wealth_health","condition",
    C([eq("condition","身衰財旺")]),"emit",[em("status","多反破財傷身")],"B",
    "神峰通考卷四·看命入式")
add("129","definition","natal","gong_position","represents",
    C([eq("position","年")]),"emit",[em("rel","年為根為上祖")],"A",
    "神峰通考卷四·看命入式")
add("129","definition","natal","gong_position","represents",
    C([eq("position","月")]),"emit",[em("rel","月為苗為父母")],"A",
    "神峰通考卷四·看命入式")
add("129","definition","natal","gong_position","represents",
    C([eq("position","時")]),"emit",[em("rel","時為花實為子息")],"A",
    "神峰通考卷四·看命入式")

# ===== 133 江湖摘錦 =====
add("133","medicine","natal","use_official","protect",
    C([eq("use","官")]),"emit",[em("forbid","不可傷")],"A",
    "神峰通考卷四·江湖摘錦")
add("133","medicine","natal","use_wealth","protect",
    C([eq("use","財")]),"emit",[em("forbid","不可劫")],"A",
    "神峰通考卷四·江湖摘錦")
add("133","medicine","natal","use_seal","protect",
    C([eq("use","印綬")]),"emit",[em("forbid","不可破")],"A",
    "神峰通考卷四·江湖摘錦")
add("133","medicine","natal","use_food","protect",
    C([eq("use","食神")]),"emit",[em("forbid","不可奪")],"A",
    "神峰通考卷四·江湖摘錦")
add("133","medicine","natal","seven_killings","control_limit",
    C([has("七殺")]),"emit",[em("note","須要制，制伏太過反為凶")],"A",
    "神峰通考卷四·江湖摘錦")
add("133","medicine","decade","hurt_official","luck",
    C([eq("ten_god","傷官")]),"emit",[em("forbid","最怕行官運")],"A",
    "神峰通考卷四·江湖摘錦")

# ===== 141 十干從化定訣 =====
add("141","resolution","natal","cong_hua","priority",
    C([]),"emit",[em("method","先明從化為本，從化不成方論財官")],"A",
    "神峰通考卷四·十干從化定訣")
add("141","definition","natal","tian_gan_hua","is",
    C([eq("pair","甲己")]),"emit",[em("hua","化土")],"A",
    "神峰通考卷四·十干從化定訣")
add("141","definition","natal","tian_gan_hua","is",
    C([eq("pair","乙庚")]),"emit",[em("hua","化金")],"A",
    "神峰通考卷四·十干從化定訣")
add("141","definition","natal","tian_gan_hua","is",
    C([eq("pair","丙辛")]),"emit",[em("hua","化水")],"A",
    "神峰通考卷四·十干從化定訣")
add("141","definition","natal","tian_gan_hua","is",
    C([eq("pair","丁壬")]),"emit",[em("hua","化木")],"A",
    "神峰通考卷四·十干從化定訣")
add("141","definition","natal","tian_gan_hua","is",
    C([eq("pair","戊癸")]),"emit",[em("hua","化火")],"A",
    "神峰通考卷四·十干從化定訣")

# ===== 153-155 格歌 =====
add("153","medicine","natal","use_official","likes_dislikes",
    C([eq("use","官")]),"emit",[em("likes","喜身旺喜印及財星"),em("dislikes","嫌刃與沖刑傷食")],"C",
    "神峰通考卷四·正官格歌")
add("154","medicine","natal","use_sha","likes_dislikes",
    C([eq("use","七殺")]),"emit",[em("likes","喜印刃傷官與食神"),em("dislikes","身旺者忌見官星")],"C",
    "神峰通考卷四·七殺格歌")
add("155","medicine","natal","use_wealth","likes_dislikes",
    C([eq("use","財")]),"emit",[em("dislikes","身弱忌羊刃"),em("likes","身旺印宜")],"C",
    "神峰通考卷四·用財歌")

with io.open(os.path.join(OUTDIR,"rules_candidate.jsonl"),"w",encoding="utf-8",newline="") as f:
    for r in R:
        f.write(json.dumps(r,ensure_ascii=False)+"\n")
print("rules:", len(R))
