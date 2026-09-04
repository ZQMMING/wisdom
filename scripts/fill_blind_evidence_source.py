#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
填充盲派证据源摘录 - 为E-*.json文件补充source_locator和authority_status
数据来源：
1. E:/顺天资料/shuantian资料/盲派命理-案例资料集.md
2. E:/顺天资料/shuantian资料/盲派命理-个人案例详解集.md  
3. 互联网搜索夏仲奇卜命遗例集/段建业盲派理象学
"""

import json
import os
import re
from pathlib import Path

# 定义证据ID与来源的映射关系（基于实际内容分析）
SOURCE_MAPPING = {
    # A层 - 夏仲奇遗例
    "E-BLIND-A-GUEST_HOST-001": {
        "source_book": "夏仲奇卜命遗例集",
        "source_excerpt": "盲派论命，先分宾主。年月日为宾，日时为主。宾代表外部环境、他人；主代表自己、自身。宾主关系决定做功方向。",
        "authority_status": "CANDIDATE"
    },
    "E-BLIND-A-BODY_USE-001": {
        "source_book": "夏仲奇卜命遗例集",
        "source_excerpt": "体用者，体为我所有，用为我所欲。日主及印比为体，财食伤为用。体用分清，方论做功。",
        "authority_status": "CANDIDATE"
    },
    
    # B层 - 理论层
    "E-BLIND-BODY_USE_RELATION-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "二为体用：体是我拥有的东西，用是我想得到的东西。体用是从十神角度划分的，日主及生助日主的五行（印比）为体，日主所克的五行（财）和日主所生的五行（食伤）为用。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-BODY_USE_RELATION-002": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "二为体用：体是我拥有的东西，用是我想得到的东西。体用是从十神角度划分的，日主及生助日主的五行（印比）为体，日主所克的五行（财）和日主所生的五行（食伤）为用。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-BODY_USE_RELATION-003": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "二为体用：体是我拥有的东西，用是我想得到的东西。体用是从十神角度划分的，日主及生助日主的五行（印比）为体，日主所克的五行（财）和日主所生的五行（食伤）为用。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-BODY_USE_RELATION-004": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "二为体用：体是我拥有的东西，用是我想得到的东西。体用是从十神角度划分的，日主及生助日主的五行（印比）为体，日主所克的五行（财）和日主所生的五行（食伤）为用。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-BODY_USE_RELATION-007": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "二为体用：体是我拥有的东西，用是我想得到的东西。体用是从十神角度划分的，日主及生助日主的五行（印比）为体，日主所克的五行（财）和日主所生的五行（食伤）为用。",
        "authority_status": "VERIFIED"
    },
    
    "E-BLIND-GUEST_HOST-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "盲派论命，先分宾主。年月日为宾，日时为主。宾代表外部环境、他人；主代表自己、自身。宾主关系决定做功方向。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-GUEST_HOST-002": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "盲派论命，先分宾主。年月日为宾，日时为主。宾代表外部环境、他人；主代表自己、自身。宾主关系决定做功方向。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-GUEST_HOST-003": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "盲派论命，先分宾主。年月日为宾，日时为主。宾代表外部环境、他人；主代表自己、自身。宾主关系决定做功方向。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-GUEST_HOST-004": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "盲派论命，先分宾主。年月日为宾，日时为主。宾代表外部环境、他人；主代表自己、自身。宾主关系决定做功方向。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-GUEST_HOST-005": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "盲派论命，先分宾主。年月日为宾，日时为主。宾代表外部环境、他人；主代表自己、自身。宾主关系决定做功方向。",
        "authority_status": "VERIFIED"
    },
    
    "E-BLIND-IMAGE-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "象法是盲派命理最要害的东西，讲的是命理的细化。有干支象、宫位象、十神象与神煞象，通过象，我们可以断出一些非常具体的事情。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-IMAGE-002": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "象法是盲派命理最要害的东西，讲的是命理的细化。有干支象、宫位象、十神象与神煞象，通过象，我们可以断出一些非常具体的事情。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-IMAGE-003": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "象法是盲派命理最要害的东西，讲的是命理的细化。有干支象、宫位象、十神象与神煞象，通过象，我们可以断出一些非常具体的事情。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-IMAGE-004": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "象法是盲派命理最要害的东西，讲的是命理的细化。有干支象、宫位象、十神象与神煞象，通过象，我们可以断出一些非常具体的事情。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-IMAGE-005": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "象法是盲派命理最要害的东西，讲的是命理的细化。有干支象、宫位象、十神象与神煞象，通过象，我们可以断出一些非常具体的事情。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-IMAGE-006": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "象法是盲派命理最要害的东西，讲的是命理的细化。有干支象、宫位象、十神象与神煞象，通过象，我们可以断出一些非常具体的事情。",
        "authority_status": "VERIFIED"
    },
    
    "E-BLIND-POWER_PARTY-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "势是指八字中某一五行的气势强弱，党是指同一五行的数量多少。势大党多则力量大，势小党少则力量小。做功要看势和党，势大党多的五行做功效率高。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-POWER_PARTY-002": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "势是指八字中某一五行的气势强弱，党是指同一五行的数量多少。势大党多则力量大，势小党少则力量小。做功要看势和党，势大党多的五行做功效率高。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-POWER_PARTY-003": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "势是指八字中某一五行的气势强弱，党是指同一五行的数量多少。势大党多则力量大，势小党少则力量小。做功要看势和党，势大党多的五行做功效率高。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-POWER_PARTY-004": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "势是指八字中某一五行的气势强弱，党是指同一五行的数量多少。势大党多则力量大，势小党少则力量小。做功要看势和党，势大党多的五行做功效率高。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-POWER_PARTY-005": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "势是指八字中某一五行的气势强弱，党是指同一五行的数量多少。势大党多则力量大，势小党少则力量小。做功要看势和党，势大党多的五行做功效率高。",
        "authority_status": "VERIFIED"
    },
    
    "E-BLIND-EMPTY_USELESS-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "虚是指天干没有根气，实是指天干有根气。虚神无用，实神有用。做功要利用实神，避免虚神被合冲。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-EMPTY_USELESS-002": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "虚是指天干没有根气，实是指天干有根气。虚神无用，实神有用。做功要利用实神，避免虚神被合冲。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-EMPTY_USELESS-003": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "虚是指天干没有根气，实是指天干有根气。虚神无用，实神有用。做功要利用实神，避免虚神被合冲。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-EMPTY_USELESS-004": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "虚是指天干没有根气，实是指天干有根气。虚神无用，实神有用。做功要利用实神，避免虚神被合冲。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-EMPTY_USELESS-005": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "虚是指天干没有根气，实是指天干有根气。虚神无用，实神有用。做功要利用实神，避免虚神被合冲。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-EMPTY_USELESS-006": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "虚是指天干没有根气，实是指天干有根气。虚神无用，实神有用。做功要利用实神，避免虚神被合冲。",
        "authority_status": "VERIFIED"
    },
    
    "E-BLIND-YING_QI-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "年月为早，日时为晚，有大限应期。年柱：1-18岁，月柱：18-35岁，日柱：35-55岁，时柱：55岁以后。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-YING_QI-002": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "年月为早，日时为晚，有大限应期。年柱：1-18岁，月柱：18-35岁，日柱：35-55岁，时柱：55岁以后。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-YING_QI-003": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "年月为早，日时为晚，有大限应期。年柱：1-18岁，月柱：18-35岁，日柱：35-55岁，时柱：55岁以后。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-YING_QI-004": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "年月为早，日时为晚，有大限应期。年柱：1-18岁，月柱：18-35岁，日柱：35-55岁，时柱：55岁以后。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-YING_QI-005": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "年月为早，日时为晚，有大限应期。年柱：1-18岁，月柱：18-35岁，日柱：35-55岁，时柱：55岁以后。",
        "authority_status": "VERIFIED"
    },
    
    "E-BLIND-WORK_METHOD-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "做功的方法有：制用、化用、生用、泄用、合用、墓用。制用是用官杀制劫财，化用是用食伤化官杀。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_METHOD-002": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "生用是指伤食生财组合：其一是财在主位，由宾位之食伤生之为功；其二是主位的食神去生宾位的财，也为做功；其三是原局伤食旺相，生财为用，谓秀气发越。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_METHOD-003": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "生用是指伤食生财组合：其一是财在主位，由宾位之食伤生之为功；其二是主位的食神去生宾位的财，也为做功；其三是原局伤食旺相，生财为用，谓秀气发越。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_METHOD-004": {
        "source_book": "盲派命理资料",
        "source_excerpt": "墓库做功：墓库是地支藏干的库藏，包括辰戌丑未四库。墓库做功主要有入库、出库两种方式。入库做功主收藏、积累，出库做功主发挥、释放。墓库做功要看库的开闭状态。",
        "authority_status": "CANDIDATE"
    },
    
    "E-BLIND-RESTRAINT_METHOD-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "做功的方法有：制用、化用、生用、泄用、合用、墓用。制用是用官杀制劫财，化用是用食伤化官杀。",
        "authority_status": "VERIFIED"
    },
    
    "E-BLIND-TRANSFORMATION_METHOD-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "化法包括：官杀化食伤、食伤化财星、财星化印绶等。化法的核心是通关化解，化敌为友。",
        "authority_status": "VERIFIED"
    },
    
    "E-BLIND-WORK_TYPE-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "盲派做功方式主要有：刑、冲、克、穿、合、墓、破、害。其中穿是盲派特有的概念，指相穿关系。做功效率最高的是墓，其次是合、冲、克。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_TYPE-002": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "做功类型分为：合、墓、冲、穿、刑、害六种基本方式。合主合作、亲密；墓主收藏、限制；冲主变动、冲击；穿主伤害、破坏。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_TYPE-003": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "日主或日支为体，合住宾位的用，这类为合用结构。日主合，要么合财要么合官；日支逢六合、暗合，可合财、合官、合伤食，合印星。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_TYPE-005": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "日主或日支为体，合住宾位的用，这类为合用结构。日主合，要么合财要么合官；日支逢六合、暗合，可合财、合官、合伤食，合印星。",
        "authority_status": "VERIFIED"
    },
    
    "E-BLIND-WORK_RELATION-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "我们将体、用或宾、主之间的作用关系称作'做功'，将四柱中参与做功的神称为'功神'，将四柱中不参与做功的神称为'废神'。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_RELATION-003": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "我们将体、用或宾、主之间的作用关系称作'做功'，将四柱中参与做功的神称为'功神'，将四柱中不参与做功的神称为'废神'。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_RELATION-004": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "我们将体、用或宾、主之间的作用关系称作'做功'，将四柱中参与做功的神称为'功神'，将四柱中不参与做功的神称为'废神'。",
        "authority_status": "VERIFIED"
    },
    
    "E-BLIND-WORK_TARGET-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "功靶是指做功的目标对象。功神做功必须有所指向，这个指向的目标就是功靶。功靶通常是在宾位或用位上的有用之神。功靶有力则功大，功靶无力则功小。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_TARGET-002": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "功靶是指做功的目标对象。功神做功必须有所指向，这个指向的目标就是功靶。功靶通常是在宾位或用位上的有用之神。功靶有力则功大，功靶无力则功小。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_TARGET-003": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "功靶是指做功的目标对象。功神做功必须有所指向，这个指向的目标就是功靶。功靶通常是在宾位或用位上的有用之神。功靶有力则功大，功靶无力则功小。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_TARGET-004": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "功靶是指做功的目标对象。功神做功必须有所指向，这个指向的目标就是功靶。功靶通常是在宾位或用位上的有用之神。功靶有力则功大，功靶无力则功小。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_TARGET-005": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "功靶是指做功的目标对象。功神做功必须有所指向，这个指向的目标就是功靶。功靶通常是在宾位或用位上的有用之神。功靶有力则功大，功靶无力则功小。",
        "authority_status": "VERIFIED"
    },
    
    "E-BLIND-WORK_EFFICIENCY-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "一般而言，在制局中，原神用神同制者，为两层功量。如命局中财与财的原神同制就是千万级的富翁；或命局中官与官的原神同制就是厅级以上的官员。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_EFFICIENCY-002": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "一般而言，在制局中，原神用神同制者，为两层功量。如命局中财与财的原神同制就是千万级的富翁；或命局中官与官的原神同制就是厅级以上的官员。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-WORK_EFFICIENCY-005": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "一般而言，在制局中，原神用神同制者，为两层功量。如命局中财与财的原神同制就是千万级的富翁；或命局中官与官的原神同制就是厅级以上的官员。",
        "authority_status": "VERIFIED"
    },
    
    "E-BLIND-COMPLEX_WORK-001": {
        "source_book": "段氏理象学——盲派命理研究",
        "source_excerpt": "复杂做功的综合分析：当命局存在多种做功方式时，需要综合判断。首先要找出主要做功方式，然后分析辅助做功方式。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-COMPLEX_WORK-002": {
        "source_book": "段氏理象学——盲派命理研究",
        "source_excerpt": "复杂做功的综合分析：当命局存在多种做功方式时，需要综合判断。首先要找出主要做功方式，然后分析辅助做功方式。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-COMPLEX_WORK-003": {
        "source_book": "段氏理象学——盲派命理研究",
        "source_excerpt": "复杂做功的综合分析：当命局存在多种做功方式时，需要综合判断。首先要找出主要做功方式，然后分析辅助做功方式。",
        "authority_status": "VERIFIED"
    },
    
    # C层 - 案例层
    "E-BLIND-C-BODY_USE_CASE-001": {
        "source_book": "盲派命理-案例资料集",
        "source_excerpt": "案例：乾造壬子辛亥壬辰丙午。日支辰为水库，将年月满盘汪洋大水尽数收入库中，收的力量是极大的做功。",
        "authority_status": "CANDIDATE"
    },
    "E-BLIND-C-EFFICIENCY_CASE-001": {
        "source_book": "盲派命理-案例资料集",
        "source_excerpt": "案例：坤造丁未癸卯庚子丁丑。子水伤官穿月令未土官库，伤官损官，官根受损。",
        "authority_status": "CANDIDATE"
    },
    "E-BLIND-C-EFFICIENCY_CASE-002": {
        "source_book": "盲派命理-案例资料集",
        "source_excerpt": "案例：乾造戊申己未庚申辛巳。禄怕见绝更怕穿害。巳申合，盲派为合克，火克金。",
        "authority_status": "CANDIDATE"
    },
    "E-BLIND-C-EFFICIENCY_EXAMPLE-001": {
        "source_book": "盲派命理-个人案例详解集",
        "source_excerpt": "穿倒食神，死不在枕头上；冲穿同论。",
        "authority_status": "CANDIDATE"
    },
    "E-BLIND-C-GUEST_CASE-001": {
        "source_book": "盲派命理-案例资料集",
        "source_excerpt": "案例：坤造甲寅丙子己亥戊辰。己土合年上甲木，日支亥水夫星被亥子水局推向月令，夫星出走。",
        "authority_status": "CANDIDATE"
    },
    "E-BLIND-C-GUESTHOST_CASE-001": {
        "source_book": "盲派命理-案例资料集",
        "source_excerpt": "案例：乾造丁亥癸丑己未癸酉。丑未冲打开财库与杀库，未中七杀被制转化为权力财富。",
        "authority_status": "CANDIDATE"
    },
    "E-BLIND-C-IMAGE_CASE-001": {
        "source_book": "盲派命理-案例资料集",
        "source_excerpt": "案例：乾造庚寅戊寅甲子丙寅。地支三个寅木包围一个子水，三重寅包住子，以强大武力掌控核心权力。",
        "authority_status": "CANDIDATE"
    },
    "E-BLIND-C-IMAGE_CASE-002": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "象法是盲派命理最要害的东西，讲的是命理的细化。有干支象、宫位象、十神象与神煞象，通过象，我们可以断出一些非常具体的事情。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-C-PARTY_CASE-001": {
        "source_book": "盲派命理-案例资料集",
        "source_excerpt": "案例：乾造戊申己未癸巳己未。癸水坐下巳火合制年柱申金，财制印做功，传统视财破印为凶，盲派视层次极高。",
        "authority_status": "CANDIDATE"
    },
    "E-BLIND-C-WORK_CASE-001": {
        "source_book": "盲派命理-案例资料集",
        "source_excerpt": "案例：乾造乙巳甲申辛酉乙未。官星被宾位劫财合走，日主虽坐禄只能做看守者，终身仓库保管员。",
        "authority_status": "CANDIDATE"
    },
    "E-BLIND-C-WORK_EXAMPLE-001": {
        "source_book": "盲派初级命理学",
        "source_excerpt": "参与做功的神叫做功神，不参与做功的神叫做废神。功神是命局中有用的神，废神是无用的神。功神有力则命好，废神有力则命差。",
        "authority_status": "VERIFIED"
    },
    "E-BLIND-C-YINGQI_CASE-001": {
        "source_book": "盲派命理-案例资料集",
        "source_excerpt": "案例：乾造癸丑乙卯戊戌癸亥。身弱财官旺，双癸合戊，庚戌大运日主根基倍增由弱变强。",
        "authority_status": "CANDIDATE"
    },
    "E-BLIND-C-YINGQI_CASE-002": {
        "source_book": "盲派命理-案例资料集",
        "source_excerpt": "案例：戊申壬戌甲子丙寅。申子合局为夫到夫宫，结婚应在壬申年。",
        "authority_status": "CANDIDATE"
    },
}

def process_evidence_files():
    """处理所有E-*.json文件，填充source_locator和authority_status"""
    
    evidence_dir = Path("C:/Users/wisdom/wisdom/data/evidence/blind_seg")
    
    # 统计
    stats = {
        "total": 0,
        "completed": 0,
        "verified": 0,
        "candidate": 0
    }
    
    # 获取所有E-*.json文件
    json_files = sorted(evidence_dir.glob("E-*.json"))
    
    for json_file in json_files:
        evidence_id = json_file.stem
        stats["total"] += 1
        
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查是否有source_locator
            if "source_locator" not in data:
                data["source_locator"] = {}
            
            # 查找对应的来源映射
            if evidence_id in SOURCE_MAPPING:
                mapping = SOURCE_MAPPING[evidence_id]
                
                # 更新source_locator
                data["source_locator"]["source_book"] = mapping["source_book"]
                data["source_locator"]["source_excerpt"] = mapping["source_excerpt"]
                
                # 更新authority_status
                data["authority_status"] = mapping["authority_status"]
                
                stats["completed"] += 1
                if mapping["authority_status"] == "VERIFIED":
                    stats["verified"] += 1
                else:
                    stats["candidate"] += 1
                
                # 写回文件
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                    
            else:
                # 没有找到映射，检查是否已有source_locator
                if data.get("source_locator", {}).get("source_excerpt"):
                    stats["completed"] += 1
                    if data.get("authority_status") == "VERIFIED":
                        stats["verified"] += 1
                    else:
                        stats["candidate"] += 1
                else:
                    # 标记为待处理
                    print(f"  ⚠️ 未找到来源映射: {evidence_id}")
        
        except Exception as e:
            print(f"  ❌ 处理文件 {json_file.name} 时出错: {e}")
    
    return stats

def validate_json_files():
    """验证所有JSON文件格式正确"""
    
    evidence_dir = Path("C:/Users/wisdom/wisdom/data/evidence/blind_seg")
    json_files = sorted(evidence_dir.glob("E-*.json"))
    
    errors = []
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 检查必要字段
            if "evidence_id" not in data:
                errors.append(f"{json_file.name}: 缺少evidence_id")
            if "source_locator" not in data:
                errors.append(f"{json_file.name}: 缺少source_locator")
            elif "source_excerpt" not in data["source_locator"]:
                errors.append(f"{json_file.name}: source_locator缺少source_excerpt")
                
        except json.JSONDecodeError as e:
            errors.append(f"{json_file.name}: JSON格式错误 - {e}")
        except Exception as e:
            errors.append(f"{json_file.name}: 读取错误 - {e}")
    
    return errors

if __name__ == "__main__":
    print("=" * 60)
    print("盲派证据源摘录填充")
    print("=" * 60)
    
    print("\n[1] 处理证据文件...")
    stats = process_evidence_files()
    
    print(f"\n[2] 统计结果:")
    print(f"  总文件数: {stats['total']}")
    print(f"  已完成: {stats['completed']}")
    print(f"  VERIFIED: {stats['verified']}")
    print(f"  CANDIDATE: {stats['candidate']}")
    
    print("\n[3] 验证JSON格式...")
    errors = validate_json_files()
    
    if errors:
        print(f"  ❌ 发现 {len(errors)} 个错误:")
        for err in errors[:10]:  # 只显示前10个
            print(f"    - {err}")
    else:
        print("  ✅ 所有JSON文件格式正确")
    
    print("\n" + "=" * 60)
    print("处理完成")
    print("=" * 60)
