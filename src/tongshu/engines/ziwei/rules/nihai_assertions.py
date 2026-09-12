# -*- coding: utf-8 -*-
"""倪海厦紫微斗数断言库（天纪精选集）.

架构定位:
    本模块是独立断言库，不消费 MultiMethodSignal，不重算任何事实。
    直接从 FrozenZiweiChart 读取「每宫主星」→ 输出断言条目。
    解层可选项地合并到 ZiweiInterpretationOutput。

断言风格:
    倪师断言 = 星 × 宫 → 具体断语（一句话判断）
    特点：直接、具体、可验证，不说"可能"只说"主"
    例：紫微在命「代表官印，官的命」/ 禄存在命「标准小气」

断言来源:
    D:\顺天系统资料\倪海厦天纪-断言资料精选集.md
    语料库：4886 条判语（v2.0, Renhuai123/nihai-tianji-corpus）

约束:
    1. 断言只读 chart.palaces[*].major（主星列表），不重算四化/飞星
    2. 断言不带 LLM / score / weight
    3. 未命中的星不产生断言（fail-closed）
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ===========================================================================
# 数据模型
# ===========================================================================

@dataclass(frozen=True)
class NihaiAssertion:
    """单条倪师断言."""
    star: str              # 主星（如 "紫微"）
    palace: str            # 宫位（如 "命宫"）
    source: str            # 出处（章节+页码或讲次）
    category: str          # 断言类别（personality/career/wealth/marriage/health/fortune）
    direction: str         # "吉"/"凶"/"中性"
    strength: str          # "强"/"中"/"弱"（对应庙/旺/利/陷）
    text: str              # 断语原文（倪师原话，逐字抄录）

    def to_dict(self) -> dict[str, Any]:
        return {
            "star": self.star,
            "palace": self.palace,
            "source": self.source,
            "category": self.category,
            "direction": self.direction,
            "strength": self.strength,
            "text": self.text,
        }


# ===========================================================================
# 断言库（主星 × 宫位 → 断语）
#
# 断言覆盖原则:
#   - 每条断言必须有倪师原话依据（精选集可追溯）
#   - 无依据的不编造（宁可少不可编）
#   - 断言按宫位覆盖主星核心特征（命宫优先）
# ===========================================================================

# 断言条目注册表: (star, palace) → NihaiAssertion
_NIHAI_ASSERTIONS: Dict[Tuple[str, str], NihaiAssertion] = {}


def _register(star: str, palace: str, source: str,
              category: str, direction: str, strength: str,
              text: str) -> None:
    """注册一条断言."""
    _NIHAI_ASSERTIONS[(star, palace)] = NihaiAssertion(
        star=star, palace=palace, source=source,
        category=category, direction=direction, strength=strength,
        text=text,
    )


# ============================================================================
# 十四主星 × 命宫断言
# ============================================================================

# 紫微：北斗帝星，主官带
_register(
    "紫微", "命宫", "主星册·紫微",
    category="career", direction="吉", strength="强",
    text="紫微星是帝星，主的是官，官带。有紫微星出现的时候，代表的是官印，官的命。",
)
_register(
    "紫微", "命宫", "主星册·紫微",
    category="fortune", direction="吉", strength="强",
    text="紫微星出现的时候，代表的是官印，有紫微星在命宫的人，先天有贵气。",
)

# 天机：北斗文官带
_register(
    "天机", "命宫", "主星册·天机",
    category="career", direction="吉", strength="强",
    text="天机星也是个官带星，但是天机星是文官带，干公务人员、老师、银行做事都是。",
)

# 太阳：中天武官带，也主财禄
_register(
    "太阳", "命宫", "主星册·太阳",
    category="career", direction="吉", strength="强",
    text="太阳星是武官带，军人、警察、法官、外交官都是属于武官带。太阳也代表财禄。",
)
_register(
    "太阳", "命宫", "主星册·太阳",
    category="fortune", direction="吉", strength="强",
    text="太阳星主贵，也代表财禄，官禄宫就主官，财帛宫就主财。",
)

# 武曲：北斗财星王，也主武官
_register(
    "武曲", "命宫", "主星册·武曲",
    category="wealth", direction="吉", strength="强",
    text="武曲星第一个它代表的是武官，第二个它也代表财星，而且它是财星的王。",
)
_register(
    "武曲", "命宫", "主星册·武曲",
    category="personality", direction="吉", strength="强",
    text="武曲星的人个性跟太阳一样很火爆。但是这种一发就过去了，随发随走。",
)

# 天同：南斗福星，人和之星
_register(
    "天同", "命宫", "主星册·天同",
    category="personality", direction="吉", strength="强",
    text="天同星是个人和的星，一看今年正好天同，合伙吉。",
)

# 廉贞：北斗桃花星，也主武官
_register(
    "廉贞", "命宫", "主星册·廉贞",
    category="personality", direction="中性", strength="中",
    text="廉贞星是桃花星，也代表武官带，武官星在边疆去打仗。",
)

# 天府：南斗帝星，文官教星
_register(
    "天府", "命宫", "主星册·天府",
    category="career", direction="吉", strength="强",
    text="天府星是南斗星君，是个文官星，也是一个教星。很多天府坐命的人去当公务人员当教员。",
)
_register(
    "天府", "命宫", "主星册·天府",
    category="wealth", direction="吉", strength="强",
    text="天府星是很善于理财，又很厚道又拼命做事情，人又很善良的一种人，又非常善于理财的。",
)

# 太阴：中天主富星
_register(
    "太阴", "命宫", "主星册·太阴",
    category="personality", direction="吉", strength="强",
    text="如果女命女孩子坐太阴星很漂亮。美的像月里嫦娥一样。两只眼睛呀像月亮一样那么大。",
)
_register(
    "太阴", "命宫", "主星册·太阴",
    category="wealth", direction="吉", strength="强",
    text="太阴在命宫的女孩子主富贵，皮肤白细细，这是水澄桂萼格。",
)

# 贪狼：北斗桃花/财气
_register(
    "贪狼", "命宫", "主星册·贪狼",
    category="personality", direction="中性", strength="中",
    text="贪狼星是属于桃花星，主桃花也指的是酒、财、气，通通在这个酒、色、财、气、赌里面。",
)
_register(
    "贪狼", "命宫", "主星册·贪狼",
    category="fortune", direction="中性", strength="中",
    text="贪狼入命的人他有生杀之权，如果还有天魁星来会，文武双全。",
)

# 巨门：北斗暗星，庙旺能言善道，落陷主是非
_register(
    "巨门", "命宫", "主星册·巨门",
    category="personality", direction="吉", strength="强",
    text="巨门星如果是庙旺，就是能言善道口才非常好。那巨富的人再逢到巨门星入庙的时候，代表他豪门宅地。",
)
_register(
    "巨门", "命宫", "主星册·巨门",
    category="personality", direction="凶", strength="弱",
    text="巨门星落陷的话问题就来了，这个巨门就是门很大，监狱的门也还是大但是是关到的，落陷要坐在牢里。",
)

# 天相：南斗印星，佐才
_register(
    "天相", "命宫", "主星册·天相",
    category="career", direction="吉", strength="强",
    text="天相星是天上的宰相，是一个佐才星。你如果是天相入命的人你适合去当人家的助理当人家的秘书去当师爷。",
)
_register(
    "天相", "命宫", "主星册·天相",
    category="personality", direction="吉", strength="强",
    text="天相入命的人从来不去想权位，她只是很好，她是很好的辅佐的人才，位高无权。",
)

# 天梁：南斗阴贵星，文武双全
_register(
    "天梁", "命宫", "主星册·天梁",
    category="career", direction="吉", strength="强",
    text="天梁星是文武双全，允文允武的星。所以很多人武官天梁星，文官也有天梁星。",
)
_register(
    "天梁", "命宫", "主星册·天梁",
    category="health", direction="吉", strength="强",
    text="天梁星是阳星，化权的时候是武官权，像司法官外交官，大部分人的司法官是天梁星化权的。",
)

# 七杀：南斗杀星，将星
_register(
    "七杀", "命宫", "主星册·七杀",
    category="career", direction="吉", strength="强",
    text="七杀入命的人目大，做事情性子很急。这个如果在命宫有七杀在午，这也称为将星。",
)
_register(
    "七杀", "命宫", "主星册·七杀",
    category="personality", direction="中性", strength="中",
    text="七杀、破军跟贪狼这三颗星，全部主的是武官，主的是耗主的是劳。",
)

# 破军：北斗杀星，流浪在外
_register(
    "破军", "命宫", "主星册·破军",
    category="personality", direction="中性", strength="中",
    text="破军星比较孤僻，个性很孤僻，非常的孤，一个人孤芳自赏。吃五谷杂粮怎么吃都不胖。",
)
_register(
    "破军", "命宫", "主星册·破军",
    category="fortune", direction="中性", strength="中",
    text="破军星是要流浪在外要走天下，技术专长捧着饭碗走天下。对钱财不重利，男人女人都一样。",
)

# 文昌文曲：六吉星，文星
_register(
    "文昌", "命宫", "主星册·文昌文曲",
    category="career", direction="吉", strength="强",
    text="文昌星代表的是科甲读书考试。没有会到，就不是金榜题名了。",
)
_register(
    "文曲", "命宫", "主星册·文昌文曲",
    category="career", direction="吉", strength="强",
    text="文曲星主的是才艺博学，博学多能的人。完全着重在读书文笔才华。",
)

# 左辅右弼：六吉星，辅星
_register(
    "左辅", "命宫", "主星册·左辅右弼",
    category="career", direction="吉", strength="强",
    text="左辅和右弼是辅助紫微星的，只要是看到紫微星出现的时候，如果有辅弼来会，这紫微星就变成君王诸侯之相。",
)
_register(
    "右弼", "命宫", "主星册·左辅右弼",
    category="career", direction="吉", strength="强",
    text="我生下来就是辅弼之才，我当你的助手，我当你的秘书，我当你的助教，很好。",
)

# ============================================================================
# 六煞星断言
# ============================================================================

_register(
    "擎羊", "命宫", "主星册·六杀",
    category="personality", direction="凶", strength="中",
    text="六杀出现的时候，它在你的命宫有人的宫，基本上脱离不了通通是杀星。",
)
_register(
    "陀罗", "命宫", "主星册·六杀",
    category="personality", direction="凶", strength="中",
    text="六杀出现的时候，它在你的命宫有人的宫，基本上脱离不了通通是杀星。",
)
_register(
    "火星", "命宫", "主星册·六杀",
    category="personality", direction="凶", strength="中",
    text="六杀出现的时候，它在你的命宫有人的宫，基本上脱离不了通通是杀星。",
)
_register(
    "铃星", "命宫", "主星册·六杀",
    category="personality", direction="凶", strength="中",
    text="六杀出现的时候，它在你的命宫有人的宫，基本上脱离不了通通是杀星。",
)
_register(
    "天空", "命宫", "主星册·六杀",
    category="fortune", direction="凶", strength="中",
    text="六杀出现的时候，如果在命宫有人的宫，基本上脱离不了通通是杀星。",
)
_register(
    "地劫", "命宫", "主星册·六杀",
    category="fortune", direction="凶", strength="中",
    text="六杀出现的时候，如果在命宫有人的宫，基本上脱离不了通通是杀星。",
)

# ============================================================================
# 特殊辅星断言
# ============================================================================

_register(
    "禄存", "命宫", "主星册·禄存",
    category="wealth", direction="吉", strength="强",
    text="禄存星同于化禄，禄存最重要的是指的是财星。禄存星在命，这种人就是标准的小气。",
)
_register(
    "天魁", "命宫", "主星册·天魁天钺",
    category="career", direction="吉", strength="强",
    text="天魁天钺这两颗星呢也是主科甲读书星，读书星如果有个人的命里面文昌文曲也来会，天魁天钺也来会。",
)
_register(
    "天钺", "命宫", "主星册·天魁天钺",
    category="career", direction="吉", strength="强",
    text="天魁天钺这两颗星呢也是主科甲读书星，读书星如果有个人的命里面文昌文曲也来会。",
)
_register(
    "红鸾", "命宫", "主星册·红鸾天喜",
    category="marriage", direction="吉", strength="强",
    text="红鸾天喜星，顾名思义就是这样红鸾心动嘛，中国人说红鸾心动这个成语是从斗数里面来的。",
)
_register(
    "天喜", "命宫", "主星册·红鸾天喜",
    category="marriage", direction="吉", strength="强",
    text="红鸾天喜星代表喜庆的星，天喜红鸾星一定相对。",
)

# ============================================================================
# 庙旺利陷总则断言
# ============================================================================

_register(
    "庙旺利陷", "总论", "主星册·庙旺利陷",
    category="fortune", direction="中性", strength="强",
    text="所有的星在庙旺的时候都是最好，在利的时候是平平，在陷的时候是最差。如果你遇到杀星在陷地的话，那是差中更差，凶中之凶。",
)
_register(
    "庙旺利陷", "总论", "主星册·庙旺利陷",
    category="fortune", direction="中性", strength="强",
    text="一个星在里面如果不亮的时候，它没有其他吉星来会，你看只有一个杀星，那杀星就很强了。",
)

# ============================================================================
# 格局断言
# ============================================================================

_register(
    "日月反背", "格局", "格局册·必定成格",
    category="fortune", direction="中性", strength="强",
    text="日月反背主披星戴月，工作常常白天忙完晚上比白天还忙。这是六亲不靠，靠不到父母亲。",
)
_register(
    "杀破狼", "格局", "格局册·凶格",
    category="fortune", direction="凶", strength="中",
    text="七杀、破军跟贪狼这三颗星，全部主的是武官，主的是耗主的是劳。流年逢到这两颗星的话，主劳辛苦的奔波劳碌。",
)
_register(
    "半空折翅", "格局", "格局册·凶格",
    category="fortune", direction="凶", strength="强",
    text="有的人命很好就限不好，就半空折翅。不到30岁就走人了。",
)

# ============================================================================
# 四化断言
# ============================================================================

_register(
    "化科", "四化", "四化册·化科",
    category="career", direction="吉", strength="强",
    text="科本身，第一个科名，比如说我们参加考试金榜题名，这是一个科。还有我们文章写的很好，文笔写的很好也是科。",
)
_register(
    "化权", "四化", "四化册·化权",
    category="career", direction="吉", strength="强",
    text="它代表的是官印。当官的时候我们有个印盖一下，那个就是官印。第二个它代表的是性刚，个性很刚。命里面有化权的人，先天上面来说，这种人天生的就是一个领导者。",
)
_register(
    "化禄", "四化", "四化册·化禄",
    category="wealth", direction="吉", strength="强",
    text="禄就是财，钱财。禄是性守，性比较守。生下来的话，权禄这是豪门，巨富啊，生在家里面一定很有钱。",
)
_register(
    "化忌", "四化", "四化册·化忌",
    category="fortune", direction="凶", strength="强",
    text="这个忌我们意思就是说有凶星在兄弟宫。这忌是一个杀星。化忌代表劫杀。第二个化忌代表想不开。",
)

# ============================================================================
# 疾厄断言
# ============================================================================

_register(
    "疾厄", "疾厄", "疾厄册·核心方法论",
    category="health", direction="中性", strength="强",
    text="诸位看斗数上面的疾厄宫，参考可以。但是你真的批的时候他就没有用。我们算命要讲致命伤。",
)

# ============================================================================
# 十二宫总断言
# ============================================================================

_register(
    "命宫", "命宫", "十二宫册·命宫",
    category="personality", direction="中性", strength="强",
    text="我们在看命宫的时候，命宫讲的是就是你本人你自己，讲的你的先天。什么叫做先天，生下来你是什么咖，讲的是先天。从命宫一看就已经知道成败。",
)
_register(
    "夫妻宫", "夫妻宫", "十二宫册·夫妻宫",
    category="marriage", direction="中性", strength="强",
    text="夫妻顾名思义就是看她的婚姻。如果是光论宫的时候，你光看夫妻宫你大错特错，一定要看福德宫。",
)
_register(
    "财帛宫", "财帛宫", "十二宫册·财帛宫",
    category="wealth", direction="中性", strength="强",
    text="财帛是什么，你到私人企业你自己去做生意当老板。有的星代表财。还有财帛宫就是财星，也是家财万贯。",
)
_register(
    "官禄宫", "官禄宫", "十二宫册·官禄宫",
    category="career", direction="中性", strength="Strong",
    text="官禄，你到公家单位去领固定的薪水。有的星代表官，他带个印，所以当官的有个官印。官星一定要进入官禄宫最好。财星要进入财帛宫最好。叫做适得其所，叫做正位。",
)
_register(
    "迁移宫", "迁移宫", "十二宫册·迁移宫",
    category="fortune", direction="中性", strength="强",
    text="有的人他命中注定他要到迁移。有的人必须要到外地经历一圈，回来以后他才会好。",
)
_register(
    "福德宫", "福德宫", "十二宫册·福德宫",
    category="fortune", direction="中性", strength="强",
    text="祸福无门，咎由自取。我曾经批过夫妻宫很好，那福德宫很烂，散夫妻要散。同时看看福德宫。福德宫代表夫妻的关系，也代表一世的福禄。",
)


# ===========================================================================
# 查询接口
# ===========================================================================

def get_assertion(star: str, palace: str) -> Optional[NihaiAssertion]:
    """按星×宫查询断言.

    Args:
        star: 主星名（如 "紫微"）
        palace: 宫位名（如 "命宫"）

    Returns:
        NihaiAssertion 或 None（未命中则不产生断言）
    """
    return _NIHAI_ASSERTIONS.get((star, palace))


def get_all_assertions() -> List[NihaiAssertion]:
    """返回全部断言条目（供测试和审计用）."""
    return list(_NIHAI_ASSERTIONS.values())


def count_assertions() -> int:
    """返回断言条目总数."""
    return len(_NIHAI_ASSERTIONS)


def get_assertions_by_category(category: str) -> List[NihaiAssertion]:
    """按类别过滤断言."""
    return [a for a in _NIHAI_ASSERTIONS.values() if a.category == category]


# ===========================================================================
# 公开导出
# ===========================================================================

__all__ = [
    "NihaiAssertion",
    "get_assertion",
    "get_all_assertions",
    "count_assertions",
    "get_assertions_by_category",
]
