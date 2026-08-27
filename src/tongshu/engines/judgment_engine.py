"""P2 判定层: 调候+病药+常法喜忌+用神合成 (SHUNTIAN_V1.4 Gate P2).

架构定位:
- 以 D1StrengthResult 为基础输入
- 四层判定序(冻结): ①调候→②病药→③常法喜忌→④用神合成
- 每条规则可追溯古籍证据, 禁止黑箱

经典依据:
- 调候: 《穷通宝鉴》调候为急, 盲派"调候第一等药"
- 病药: 《滴天髓·病药》"有病方为贵, 无伤不是奇"
- 喜忌: 《滴天髓·衰旺》"强者宜泄, 弱者宜补"
- 用神: 《子平真诠》相神辅用, 取用顺序调候>病药>常法

输出契约(P2JudgmentResult):
    climate              寒暖燥湿 (复用D1)
    tiao_hou_element     调候所需五行 (cold→FIRE等)
    tiao_hou_present     调候字是否在局
    tiao_hou_is_yong     调候字是否为用神 (TIAO-01)
    evidence_tiaohou     《穷通宝鉴》调候为急

    bing                 病: 过旺五行/忌神透干
    yao                  药: 制病之五行
    you_bing_you_yao     有病有药方为贵

    verdict_from_d1      身强/身弱/从强/从弱
    favorable            喜(五行)
    unfavorable          忌(五行)
    evidence_xiji        《滴天髓·衰旺》

    yong_shen            最终用神(五行)
    yong_shen_source     tiao_hou/bingyao/normal
    xhen                 相神(辅用神者)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from tongshu.engines.bazi_engine import BaziChart, STEM_ELEMENT
from tongshu.engines.strength_engine import D1StrengthResult
from tongshu.reasoning.bazi_ten_gods import SEASON_BY_BRANCH


# 调候字映射: 气候象 → 所需五行 (粗粒度兜底, 优先用下方日主×季节表)
_TIAO_HOU_MAP = {
    "cold": "FIRE",   # 冬寒需火暖局
    "hot": "WATER",    # 夏热需水调候
    "dry": "WATER",    # 秋燥需水润局
    "wet": "FIRE",     # 春湿需火燥局
    "neutral": None,   # 中气调和, 无需调候
}

# 调候用神表(按天干×月令=120种) — 基于《穷通宝鉴》十天干卷+各天干日主专题
# V2.2: 最精细调候表, 键=(天干, 月支), 值=调候所需五行
# 依据: 《穷通宝鉴》原文(空空道人哲学整理版)+甲/乙/丙/丁/戊/己/庚/辛/壬9个天干日主专题
# 癸水日主专题缺失, 基于《穷通宝鉴》总览"癸水为雨露细流"推断
_TIAO_HOU_BY_STEM_MONTH = {
    # === 甲木(阳木,参天大树) ===
    # 寅月: 春寒未退, 丙火暖阳为第一要物 + 癸水滋润
    ("JIA", "YIN"): "FIRE",
    # 卯月: 甲木阳刃当令气场最旺, 庚金修剪旺木(不需要过多火生发)
    ("JIA", "MAO"): "METAL",
    # 辰月: 木春湿气偏重土中藏水, 金修剪旺气 + 水来润局防土埋木
    ("JIA", "CHEN"): "METAL",
    # 巳午未月: 夏甲先取癸水, 木燥根枯需水滋润
    ("JIA", "SI"): "WATER", ("JIA", "WU"): "WATER", ("JIA", "WEI"): "WATER",
    # 申酉月: 秋甲金旺克木, 官杀当令为忌, 专用丁火制杀炼金暖局(非金!)
    # V2.5 fix: 原表给METAL(庚金/辛金), 但甲木秋生金旺克木, 官杀是忌神非调候
    # 依据: 《穷通宝鉴》甲木申月"庚金七杀当令,专用丁火制杀,次用壬水滋杀"; 酉月"辛金正官当令,专用丁火炼金"
    ("JIA", "SHEN"): "FIRE", ("JIA", "YOU"): "FIRE",
    # 戌月: 燥土当令土厚埋根, 庚金疏土 + 水来润局养木
    ("JIA", "XU"): "METAL",
    # 亥子丑月: 冬甲第一核心丙火解冻, 丑月冻土需庚金开土+丁火暖局
    ("JIA", "HAI"): "FIRE", ("JIA", "ZI"): "FIRE", ("JIA", "CHOU"): "FIRE",

    # === 乙木(阴木,花草藤蔓) ===
    # 寅卯辰月: 春乙第一喜金修剪枝叶, 第二喜火透光输出才华
    ("YI", "YIN"): "METAL", ("YI", "MAO"): "METAL", ("YI", "CHEN"): "METAL",
    # 巳午未月: 夏乙最急需癸水雨露润局 + 湿土蓄水
    ("YI", "SI"): "WATER", ("YI", "WU"): "WATER", ("YI", "WEI"): "WATER",
    # 申酉戌月: 秋乙第一药物丙丁火暖局制金, 其次甲木护身挡杀
    ("YI", "SHEN"): "FIRE", ("YI", "YOU"): "FIRE", ("YI", "XU"): "FIRE",
    # 亥子丑月: 冬乙最需要丙火太阳解冻 + 燥土治水
    ("YI", "HAI"): "FIRE", ("YI", "ZI"): "FIRE", ("YI", "CHOU"): "FIRE",

    # === 丙火(阳火,太阳) ===
    # 寅卯辰月: 春丙阳气微弱, 最需要木来生火助力(木为火之源头)
    ("BING", "YIN"): "WOOD", ("BING", "MAO"): "WOOD", ("BING", "CHEN"): "WOOD",
    # 巳午未月: 夏丙太阳当空燥热至极, 最需要壬水大雨降温制衡
    ("BING", "SI"): "WATER", ("BING", "WU"): "WATER", ("BING", "WEI"): "WATER",
    # 申酉戌月: 秋丙木气凋零火势衰退, 需要木气续火生源 + 少量金平衡
    ("BING", "SHEN"): "WOOD", ("BING", "YOU"): "WOOD", ("BING", "XU"): "WOOD",
    # 亥子丑月: 冬丙最为珍贵, 一点暖阳便能解冻全局, 丙火透出即有生机
    ("BING", "HAI"): "FIRE", ("BING", "ZI"): "FIRE", ("BING", "CHOU"): "FIRE",

    # === 丁火(阴火,灯烛) ===
    # 寅卯辰月: 春丁木气充足燃料丰厚, 灯火得以长明(木望则丁火有缘)
    ("DING", "YIN"): "WOOD", ("DING", "MAO"): "WOOD", ("DING", "CHEN"): "WOOD",
    # 巳午未月: 夏丁烈日强光盖灯, 专用壬水既济降温存光(非土!)
    # V2.5 fix: 原表给EARTH(土晦火存光), 但《穷通宝鉴》丁火夏月"专用壬水", 土晦火是次要非调候第一
    # 依据: 《穷通宝鉴》丁火巳月"火旺木焚,专用壬水,次用庚金"; 午月/未月同论
    ("DING", "SI"): "WATER", ("DING", "WU"): "WATER", ("DING", "WEI"): "WATER",
    # 申酉戌月: 秋丁木叶凋零燃料枯竭, 急需甲乙木蓄火生源
    ("DING", "SHEN"): "WOOD", ("DING", "YOU"): "WOOD", ("DING", "XU"): "WOOD",
    # 亥子丑月: 冬丁寒夜灯火弥足珍贵, 是全局唯一温暖气场, 最怕大水浇灭
    ("DING", "HAI"): "FIRE", ("DING", "ZI"): "FIRE", ("DING", "CHOU"): "FIRE",

    # === 戊土(阳土,高山城墙) ===
    # 寅卯辰月: 春戊土虚浮松散底气不足, 需要火来夯实根基 + 木疏土透气
    ("WU", "YIN"): "FIRE", ("WU", "MAO"): "FIRE", ("WU", "CHEN"): "FIRE",
    # 巳午未月: 夏戊烈日炙烤燥土干裂坚硬, 急需大水灌溉水润燥土
    ("WU", "SI"): "WATER", ("WU", "WU"): "WATER", ("WU", "WEI"): "WATER",
    # 申酉戌月: 秋戊土气寒凉肃杀过重, 需要火来温养回暖 + 金泻土秀气
    ("WU", "SHEN"): "FIRE", ("WU", "YOU"): "FIRE", ("WU", "XU"): "FIRE",
    # 亥子丑月: 冬戊湿冻淤塞寒气缠身, 木疏土火解冻破除凝滞
    ("WU", "HAI"): "FIRE", ("WU", "ZI"): "FIRE", ("WU", "CHOU"): "FIRE",

    # === 己土(阴土,田园湿泥) ===
    # 寅卯辰月: 春己田园松软生机萌发, 微火升温细水滋养最适合孕育生长
    ("JI", "YIN"): "FIRE", ("JI", "MAO"): "FIRE", ("JI", "CHEN"): "FIRE",
    # 巳午未月: 夏己烈日干裂田园湿润, 优先补水润燥保住格局生机
    ("JI", "SI"): "WATER", ("JI", "WU"): "WATER", ("JI", "WEI"): "WATER",
    # 申酉戌月: 秋己寒凉肃杀草木凋零, 需要火来暖局回暖气场守住温润本心
    ("JI", "SHEN"): "FIRE", ("JI", "YOU"): "FIRE", ("JI", "XU"): "FIRE",
    # 亥子丑月: 冬己冻土泥泞寒湿缠身, 木疏土火解冻规避大水泛滥
    ("JI", "HAI"): "FIRE", ("JI", "ZI"): "FIRE", ("JI", "CHOU"): "FIRE",

    # === 庚金(阳金,矿石刀剑) ===
    # 寅卯辰月: 春耕金金气寒凉稚嫩生硬, 丙火锻造为先淬炼顽铁去除寒气 + 水淬炼
    ("GENG", "YIN"): "FIRE", ("GENG", "MAO"): "FIRE", ("GENG", "CHEN"): "FIRE",
    # 巳午未月: 夏耕金烈日溶金燥热过旺, 烈火熔炼之后必须壬水冷却定型
    ("GENG", "SI"): "WATER", ("GENG", "WU"): "WATER", ("GENG", "WEI"): "WATER",
    # 申酉戌月: 秋耕金金气最旺刚硬过盛肃杀太重, 必须烈火锤炼打磨利器
    ("GENG", "SHEN"): "FIRE", ("GENG", "YOU"): "FIRE", ("GENG", "XU"): "FIRE",
    # 亥子丑月: 冬耕金寒冰裹金通体寒凉毫无生机, 丙火解冻炼金是第一药物
    ("GENG", "HAI"): "FIRE", ("GENG", "ZI"): "FIRE", ("GENG", "CHOU"): "FIRE",

    # === 辛金(阴金,珠宝玉石) ===
    # 寅卯辰月: 春辛珠宝蒙尘暗藏光泽, 需要湿土(己土)藏养 + 清水擦拭去污提亮
    # 关键: 辛金为珠宝最怕烈火, 春金稚嫩需湿土护身, 不需要火锻炼
    ("XIN", "YIN"): "EARTH", ("XIN", "MAO"): "EARTH", ("XIN", "CHEN"): "EARTH",
    # 巳午未月: 夏辛烈日烘烤珠宝燥热, 壬水清泉润局涤荡燥热 + 己土湿土晦火护金
    # 误区: 夏辛忌戊土(燥土不生金反脆金), 最好壬水透干甲木疏土一清彻底
    ("XIN", "SI"): "WATER", ("XIN", "WU"): "WATER", ("XIN", "WEI"): "WATER",
    # 申酉戌月: 秋辛金旺埋株锋芒过盛, 壬水淘洗旺金得水秀气流通 + 甲木疏土
    # 关键: 秋辛得令身强第一需求是水泄秀, 丁火仅为辅助清炼(望金喜清火雕琢)
    ("XIN", "SHEN"): "WATER", ("XIN", "YOU"): "WATER", ("XIN", "XU"): "WATER",
    # 亥子丑月: 冬辛寒珠暗淡灵气不足, 丁火温暖全局解冻寒金(烛光温润慢慢滋养)
    # 误区: 冬辛优先丁火不取丙火(丙火焦阳燥热容易丙辛相合牵绊太重)
    ("XIN", "HAI"): "FIRE", ("XIN", "ZI"): "FIRE", ("XIN", "CHOU"): "FIRE",

    # === 壬水(阳水,江河大水) ===
    # 寅卯辰月: 春壬春水泛滥漫无边际, 先戊土筑坝止水稳住格局守住根基 + 火暖局
    ("REN", "YIN"): "EARTH", ("REN", "MAO"): "EARTH", ("REN", "CHEN"): "EARTH",
    # 巳午未月: 夏壬燥热干涸江河枯竭, 急需金气源源不断生水补源延续气场
    ("REN", "SI"): "METAL", ("REN", "WU"): "METAL", ("REN", "WEI"): "METAL",
    # 申酉戌月: 秋壬秋水寒凉肃杀过重, 火来暖局温润调和寒气
    ("REN", "SHEN"): "FIRE", ("REN", "YOU"): "FIRE", ("REN", "XU"): "FIRE",
    # 亥子丑月: 冬壬江河冰封停滞不动, 火解冻土固堤盘活全局稳住本心
    ("REN", "HAI"): "FIRE", ("REN", "ZI"): "FIRE", ("REN", "CHOU"): "FIRE",

    # === 癸水(阴水,雨露细流) ===
    # 注: 癸水日主专题资料缺失, 以下基于《穷通宝鉴》总览"癸水为雨露细流,细腻滋养润物无声"推断
    # 寅卯辰月: 春癸细雨滋养草木温润万物, 金气生源护灵气 + 微火温润(忌大水泛滥淹没生机)
    ("GUI", "YIN"): "METAL", ("GUI", "MAO"): "METAL", ("GUI", "CHEN"): "METAL",
    # 巳午未月: 夏癸烈日蒸发雨露易干, 金气生水续源护住灵气
    ("GUI", "SI"): "METAL", ("GUI", "WU"): "METAL", ("GUI", "WEI"): "METAL",
    # 申酉戌月: 秋癸寒露寒凉气场清冷, 微火升温温润调厚
    ("GUI", "SHEN"): "FIRE", ("GUI", "YOU"): "FIRE", ("GUI", "XU"): "FIRE",
    # 亥子丑月: 冬癸冻露成冰灵气封存, 火解冻木成雨露重焕生机
    ("GUI", "HAI"): "FIRE", ("GUI", "ZI"): "FIRE", ("GUI", "CHOU"): "FIRE",
}

# 调候用神表(按天干×季节=40种) — 基于《穷通宝鉴》十天干卷原文(兜底表, 优先用上方天干×月令表)
_TIAO_HOU_BY_STEM_SEASON = {
    # 甲木(阳木,参天大树): 春丙火暖阳, 夏癸水雨露, 秋丁火锻炼, 冬丙火解冻
    ("JIA", "SPRING"): "FIRE", ("JIA", "SUMMER"): "WATER",
    ("JIA", "AUTUMN"): "FIRE", ("JIA", "WINTER"): "FIRE",
    # 乙木(阴木,花草藤蔓): 春微火暖局, 夏癸水持续水润, 秋火制金护木, 冬微火解冻
    ("YI", "SPRING"): "FIRE", ("YI", "SUMMER"): "WATER",
    ("YI", "AUTUMN"): "FIRE", ("YI", "WINTER"): "FIRE",
    # 丙火(阳火,太阳): 春木生火助力, 夏壬水降温制衡, 秋木续火生源, 冬丙火暖阳解冻(一点暖阳解冻全局)
    ("BING", "SPRING"): "WOOD", ("BING", "SUMMER"): "WATER",
    ("BING", "AUTUMN"): "WOOD", ("BING", "WINTER"): "FIRE",
    # 丁火(阴火,灯烛): 春木燃料丰厚, 夏壬水既济降温存光, 秋木蓄火生源, 冬丁火温暖全局
    # V2.5 fix: 原表夏季给EARTH(土晦火), 修正为WATER(壬水既济), 与天干×月令表一致
    ("DING", "SPRING"): "WOOD", ("DING", "SUMMER"): "WATER",
    ("DING", "AUTUMN"): "WOOD", ("DING", "WINTER"): "FIRE",
    # 戊土(阳土,高山城墙): 春火夯实根基, 夏大水润燥, 秋火温养回暖, 冬火解冻
    ("WU", "SPRING"): "FIRE", ("WU", "SUMMER"): "WATER",
    ("WU", "AUTUMN"): "FIRE", ("WU", "WINTER"): "FIRE",
    # 己土(阴土,田园湿泥): 春微火升温, 夏水润燥保格局, 秋火暖局回暖, 冬火解冻
    ("JI", "SPRING"): "FIRE", ("JI", "SUMMER"): "WATER",
    ("JI", "AUTUMN"): "FIRE", ("JI", "WINTER"): "FIRE",
    # 庚金(阳金,矿石刀剑): 春丙火锻造+水淬炼, 夏壬水冷却定型, 秋烈火锤炼, 冬丙火解冻炼金
    ("GENG", "SPRING"): "FIRE", ("GENG", "SUMMER"): "WATER",
    ("GENG", "AUTUMN"): "FIRE", ("GENG", "WINTER"): "FIRE",
    # 辛金(阴金,珠宝玉石): 春己土湿土藏养(非火!), 夏壬水清泉润局, 秋壬水淘洗泄秀(非火!), 冬丁火温暖解冻
    # 关键修正: 原表春/秋均给FIRE(火锻炼), 但辛金为珠宝最怕烈火, 春需湿土护身, 秋得令需水泄秀
    ("XIN", "SPRING"): "EARTH", ("XIN", "SUMMER"): "WATER",
    ("XIN", "AUTUMN"): "WATER", ("XIN", "WINTER"): "FIRE",
    # 壬水(阳水,江河大水): 春戊土筑坝止水, 夏金持续生水补源, 秋火暖局温润, 冬火解冻
    ("REN", "SPRING"): "EARTH", ("REN", "SUMMER"): "METAL",
    ("REN", "AUTUMN"): "FIRE", ("REN", "WINTER"): "FIRE",
    # 癸水(阴水,雨露细流): 春金生源, 夏金生水续源, 秋微火升温温润, 冬火解冻
    ("GUI", "SPRING"): "METAL", ("GUI", "SUMMER"): "METAL",
    ("GUI", "AUTUMN"): "FIRE", ("GUI", "WINTER"): "FIRE",
}

# 调候用神表(按日主五行×季节) — 基于《穷通宝鉴》核心原则(兜底表, 优先用上方天干×季节表)
# 调候必须按具体日主+月令定, 不可按季节笼统套:
#   己土秋生(dry) → 需水润(秋燥土旺), 庚金秋生(dry) → 需火锻炼(秋金锐锐)
# 本表为日主五行×4季=20种粗粒度组合, 作为天干×季节表的兜底
_TIAO_HOU_BY_DM_SEASON = {
    # 春季(寅卯辰, 木旺)
    ("WOOD", "SPRING"): "FIRE",      # 甲乙木春生: 丙火泄秀/寒木向阳
    ("FIRE", "SPRING"): "WATER",      # 丙丁火春生: 壬水既济
    ("EARTH", "SPRING"): "WOOD",      # 戊己土春生: 甲木疏土(+丙火暖局, 取主)
    ("METAL", "SPRING"): "FIRE",      # 庚辛金春生: 丁火锻炼
    ("WATER", "SPRING"): "METAL",     # 壬癸水春生: 庚金生身
    # 夏季(巳午未, 火旺)
    ("WOOD", "SUMMER"): "WATER",      # 甲乙木夏生: 癸水润局
    ("FIRE", "SUMMER"): "WATER",      # 丙丁火夏生: 壬水既济为急
    ("EARTH", "SUMMER"): "WATER",     # 戊己土夏生: 壬癸水润燥
    ("METAL", "SUMMER"): "WATER",     # 庚辛金夏生: 壬水洗淘
    ("WATER", "SUMMER"): "METAL",     # 壬癸水夏生: 庚辛金生身
    # 秋季(申酉戌, 金旺)
    ("WOOD", "AUTUMN"): "FIRE",       # 甲乙木秋生: 丁火暖局
    ("FIRE", "AUTUMN"): "WOOD",       # 丙丁火秋生: 甲木生身
    ("EARTH", "AUTUMN"): "WATER",     # 戊己土秋生: 癸水润燥(己土戌月: 火炎土燥急需癸水)
    ("METAL", "AUTUMN"): "FIRE",      # 庚辛金秋生: 丁火锻炼(秋金锐锐非火不能成器)
    ("WATER", "AUTUMN"): "FIRE",      # 壬癸水秋生: 丁火财星暖局
    # 冬季(亥子丑, 水旺)
    ("WOOD", "WINTER"): "FIRE",       # 甲乙木冬生: 丙丁火暖局
    ("FIRE", "WINTER"): "FIRE",       # 丙丁火冬生: 冬月寒冷需火暖局(调候为急; 木为生身用神, 非调候)
    ("EARTH", "WINTER"): "FIRE",      # 戊己土冬生: 丙火暖局
    ("METAL", "WINTER"): "FIRE",      # 庚辛金冬生: 丁火暖局锻炼
    ("WATER", "WINTER"): "FIRE",      # 壬癸水冬生: 丙火暖局(+戊土制水, 取主)
}


# 喜忌映射: 旺衰结论 → 喜用五行
_XIJI_MAP = {
    "身强": {"favorable": ("OFFICIAL", "EATING", "WEALTH"), "unfavorable": ("SEAL", "COMPANION")},
    "身弱": {"favorable": ("SEAL", "COMPANION"), "unfavorable": ("OFFICIAL", "EATING", "WEALTH")},
    "从强": {"favorable": ("SEAL", "COMPANION", "EATING"), "unfavorable": ("OFFICIAL",)},
    "从弱": {"favorable": ("WEALTH", "OFFICIAL", "EATING"), "unfavorable": ("SEAL", "COMPANION")},
}

_EVIDENCE = {
    "tiao_hou": "《穷通宝鉴》: 调候为急, 寒暖燥湿皆需补救",
    "bing_yao": "《滴天髓·病药》: 有病方为贵, 无伤不是奇",
    "xiji": "《滴天髓·衰旺》: 强者宜泄, 弱者宜补",
    "yong_shen": "《子平真诠》: 相神辅用, 取用有序",
}


# 五行相生: key 生 value (木生火, 火生土, 土生金, 金生水, 水生木)
_GENERATES = {"WOOD": "FIRE", "FIRE": "EARTH", "EARTH": "METAL", "METAL": "WATER", "WATER": "WOOD"}
# 五行相克: key 克 value (木克土, 火克金, 土克水, 金克木, 水克火)
_CONTROLS = {"WOOD": "EARTH", "FIRE": "METAL", "EARTH": "WATER", "METAL": "WOOD", "WATER": "FIRE"}


def _get_ten_god_by_element(dm_element: str, element: str) -> str:
    """根据日主五行和某五行返回对应的十神类型。
    用于判断调候字是否为忌神。
    """
    if element == dm_element:
        return "COMPANION"  # 同我者=比劫
    if _GENERATES[element] == dm_element:
        return "SEAL"  # 生我者=印星
    if _GENERATES[dm_element] == element:
        return "EATING"  # 我生者=食伤
    if _CONTROLS[dm_element] == element:
        return "WEALTH"  # 我克者=财星
    if _CONTROLS[element] == dm_element:
        return "OFFICIAL"  # 克我者=官杀
    return "UNKNOWN"


def _get_element_by_ten_god(dm_element: str, ten_god: str) -> str:
    """根据日主五行和十神名返回对应五行。"""
    # 比劫 = 同五行
    if ten_god == "COMPANION":
        return dm_element
    # 印星 = 生我者
    if ten_god == "SEAL":
        # 印星是生我的五行: 反向查找 _GENERATES(找到 value==dm_element 的 key)
        for el, generates in _GENERATES.items():
            if generates == dm_element:
                return el
    # 食伤 = 我生者
    if ten_god == "EATING":
        return _GENERATES[dm_element]
    # 财 = 我克者
    if ten_god == "WEALTH":
        return _CONTROLS[dm_element]
    # 官杀 = 克我者
    if ten_god == "OFFICIAL":
        for el, controls in _CONTROLS.items():
            if controls == dm_element:
                return el
    return "UNKNOWN"


@dataclass
class P2JudgmentResult:
    """P2 判定结果 — 四层架构, 全部中间项可审计。"""
    # ---- 必须参数(无默认值) ----
    climate: str
    tiao_hou_element: Optional[str]
    tiao_hou_present: bool
    tiao_hou_is_yong: bool
    bing: str
    yao: Optional[str]
    you_bing_you_yao: bool
    verdict_from_d1: str
    favorable: tuple[str, ...]
    unfavorable: tuple[str, ...]
    yong_shen: Optional[str]
    yong_shen_source: str  # tiao_hou / bingyao / normal
    xhen: Optional[str]

    # ---- 证据引用(可选, 有默认) ----
    evidence_tiaohou: str = "《穷通宝鉴》: 调候为急"
    evidence_bingyao: str = "《滴天髓·病药》: 有病方为贵, 无伤不是奇"
    evidence_xiji: str = "《滴天髓·衰旺》: 强者宜泄, 弱者宜补"

    def to_dict(self) -> dict:
        return {
            "climate": self.climate,
            "tiao_hou_element": self.tiao_hou_element,
            "tiao_hou_present": self.tiao_hou_present,
            "tiao_hou_is_yong": self.tiao_hou_is_yong,
            "evidence_tiaohou": self.evidence_tiaohou,
            "bing": self.bing,
            "yao": self.yao,
            "you_bing_you_yao": self.you_bing_you_yao,
            "evidence_bingyao": self.evidence_bingyao,
            "verdict_from_d1": self.verdict_from_d1,
            "favorable": self.favorable,
            "unfavorable": self.unfavorable,
            "evidence_xiji": self.evidence_xiji,
            "yong_shen": self.yong_shen,
            "yong_shen_source": self.yong_shen_source,
            "xhen": self.xhen,
        }


def _has_element_in_chart(chart: BaziChart, element: str) -> bool:
    """检查日主五行是否在四柱中出现(天干或地支藏干)。"""
    stems = chart.four_stems()
    branches = chart.four_branches()

    # 检查天干
    for s in stems:
        if STEM_ELEMENT[s] == element:
            return True

    # 检查地支藏干
    from tongshu.reasoning.bazi_ten_gods import BRANCH_HIDDEN_STEMS
    for b in branches:
        for h, _pos in BRANCH_HIDDEN_STEMS[b]:
            if STEM_ELEMENT[h] == element:
                return True

    return False


def judgment(chart: BaziChart, d1_result: D1StrengthResult) -> P2JudgmentResult:
    """执行 P2 四层判定, 返回 P2JudgmentResult。"""
    dm_element = d1_result.day_master_element

    # ---- ① 调候层 ----
    climate = d1_result.climate
    # V2.2: 优先按天干×月令定调候(120种最精细表), 回退到天干×季节(40种), 再回退到五行×季节(20种), 最后回退到气候映射
    season = SEASON_BY_BRANCH.get(chart.month_pillar.earthly_branch)
    dm_stem = chart.day_pillar.heavenly_stem
    month_branch = chart.month_pillar.earthly_branch
    tiao_hou_element = (
        _TIAO_HOU_BY_STEM_MONTH.get((dm_stem, month_branch))
        or _TIAO_HOU_BY_STEM_SEASON.get((dm_stem, season))
        or _TIAO_HOU_BY_DM_SEASON.get((dm_element, season))
        or _TIAO_HOU_MAP.get(climate)
    )
    tiao_hou_present = False
    tiao_hou_is_yong = False

    if tiao_hou_element:
        tiao_hou_present = _has_element_in_chart(chart, tiao_hou_element)
        # TIAO-01: 调候缺失时调候字=第一用神
        tiao_hou_is_yong = not tiao_hou_present

    # ---- ② 病药层 ----
    # V2.1: 按旺衰类型分别设阈值和药, 修正原逻辑(身强泄耗过旺用比劫帮身的错误)
    # BING-01: 身强/从强 — 生扶过旺(占比>阈值)为病, 药=官杀制旺/食伤泄秀
    # BING-02: 身弱/从弱 — 泄耗过旺(占比>阈值)为病, 药=印星生身/比劫帮身
    # 阈值校准: 原阈值(生扶>40%/泄耗>60%)导致96%命例都"有病", 常法层失效
    #   新阈值: 身强生扶>55%, 身弱泄耗>70%, 从强生扶>60%, 从弱泄耗>75%
    total = d1_result.support_count + d1_result.drain_count
    support_ratio = d1_result.support_count / total if total > 0 else 0
    drain_ratio = d1_result.drain_count / total if total > 0 else 0

    bing = ""
    yao = None
    you_bing_you_yao = False
    verdict_raw = d1_result.verdict
    # V2.5 fix: 假从格按普通身强/身弱处理病药(与常法喜忌层一致), 原逻辑漏掉假从格导致病药层不触发
    if "(假)" in verdict_raw:
        verdict_for_bingyao = "身强" if "从强" in verdict_raw else "身弱"
    else:
        verdict_for_bingyao = verdict_raw

    if verdict_for_bingyao == "身强":
        # 身强: 生扶过旺(>55%)为病, 药=官杀制旺(身强喜官杀, 忌比劫印星)
        if support_ratio > 0.55:
            bing = f"生扶过旺({support_ratio:.0%})"
            yao = "OFFICIAL"
            you_bing_you_yao = True
    elif verdict_for_bingyao == "身弱":
        # 身弱: 泄耗过旺(>70%)为病, 药=印星生身(身弱喜印星, 忌官杀食伤财)
        if drain_ratio > 0.70:
            bing = f"泄耗克过旺({drain_ratio:.0%})"
            yao = "SEAL"
            you_bing_you_yao = True
    elif verdict_for_bingyao == "从强":
        # 从强: 生扶过旺(>60%)为病, 药=食伤泄秀(从强喜食伤泄秀, 忌官杀克身破局)
        if support_ratio > 0.60:
            bing = f"生扶过旺({support_ratio:.0%},从强)"
            yao = "EATING"
            you_bing_you_yao = True
    elif verdict_for_bingyao == "从弱":
        # 从弱: 泄耗过旺(>75%)为病, 药=比劫帮身(从弱喜比劫, 忌印星生身破局)
        if drain_ratio > 0.75:
            bing = f"泄耗克过旺({drain_ratio:.0%},从弱)"
            yao = "COMPANION"
            you_bing_you_yao = True

    # ---- ③ 常法喜忌层 ----
    # 假从格按普通身强/身弱处理喜忌, 不参与喜忌反转(P2-D1R1: 假从标注不参与喜忌反转)
    verdict_raw = d1_result.verdict
    if "(假)" in verdict_raw:
        verdict = "身强" if "从强" in verdict_raw else "身弱"
    else:
        verdict = verdict_raw
    xi_ji = _XIJI_MAP.get(verdict, {"favorable": (), "unfavorable": ()})

    favorable = xi_ji["favorable"]
    unfavorable = xi_ji["unfavorable"]

    # ---- ④ 用神合成 ----
    # YONG-01: yong_shen = tiao_hou(TIAO-01) > yao(BING) > favorable[0]
    # V2.3: 增加调候字与忌神冲突检测 — 调候字为忌神时取相神(生调候字者)代用
    yong_shen = None
    yong_shen_source = ""
    xhen = None
    evidence_tiaohou = "《穷通宝鉴》: 调候为急"

    if tiao_hou_is_yong and tiao_hou_element:
        # 冲突检测: 调候字对应的十神是否为忌神(基于旺衰常法喜忌)
        tiao_hou_ten_god = _get_ten_god_by_element(dm_element, tiao_hou_element)
        if tiao_hou_ten_god in unfavorable:
            # 调候字为忌神, 不能直接用, 取相神(生调候字者)代用
            # 相神 = 生调候五行的五行(反向查找 _GENERATES)
            xiang_shen = None
            for el, generates in _GENERATES.items():
                if generates == tiao_hou_element:
                    xiang_shen = el
                    break
            if xiang_shen:
                yong_shen = xiang_shen
                yong_shen_source = "tiao_hou"
                # 相神 = 调候字本身(辅助用神达到调候目的)
                xhen = tiao_hou_element
                evidence_tiaohou = (
                    f"《穷通宝鉴》: 调候为急, 但调候字{tiao_hou_element}"
                    f"({tiao_hou_ten_god})为忌神, 取相神{xiang_shen}代用"
                )
            # 若相神不存在(理论上不会), 则 fall through 到病药/常法
        else:
            yong_shen = tiao_hou_element
            yong_shen_source = "tiao_hou"

    if yong_shen is None and yao and you_bing_you_yao:
        yong_shen = _get_element_by_ten_god(dm_element, yao)
        yong_shen_source = "bingyao"
    elif yong_shen is None and favorable:
        first_fav = favorable[0]
        yong_shen = _get_element_by_ten_god(dm_element, first_fav)
        yong_shen_source = "normal"

    # 相神: 辅用神者
    # V2.4: 完善相神逻辑 — 调候来源相神=日主本气(原逻辑), 病药/常法来源相神=生用神者(用神的印星)
    if xhen is None and yong_shen:
        if yong_shen_source == "tiao_hou":
            # 调候用神时, 日主本气为相神(辅助维持调候效果)
            xhen = dm_element
        else:
            # 病药/常法用神时, 相神=生用神者(用神的印星, 辅助用神发挥作用)
            # 反向查找 _GENERATES: 找到 value==yong_shen 的 key
            for el, generates in _GENERATES.items():
                if generates == yong_shen:
                    xhen = el
                    break

    return P2JudgmentResult(
        climate=climate,
        tiao_hou_element=tiao_hou_element,
        tiao_hou_present=tiao_hou_present,
        tiao_hou_is_yong=tiao_hou_is_yong,
        evidence_tiaohou=evidence_tiaohou,
        bing=bing,
        yao=yao,
        you_bing_you_yao=you_bing_you_yao,
        verdict_from_d1=d1_result.verdict,
        favorable=favorable,
        unfavorable=unfavorable,
        yong_shen=yong_shen,
        yong_shen_source=yong_shen_source,
        xhen=xhen,
    )
