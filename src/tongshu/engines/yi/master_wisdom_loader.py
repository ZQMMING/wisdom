# -*- coding: utf-8 -*-
"""大师智慧加载器 — 南怀瑾/曾仕强易经哲学观点补充解读.

数据来源:
- 南怀瑾《易经杂说》《系传别讲》(劝学网整理版, github.com/big-dollar)
- 曾仕强《易经的智慧6》(陕西师大出版社, OCR版)

定位: 哲学性/人生智慧补充解读, 非结构化断言.
与傅佩荣结构化多维度断言(时运/财运等)互补.

核心观点按主题分类:
- 易经哲学三原则: 变易/不易/简易
- 人生智慧: 时位/进退/吉凶/祸福
- 决策智慧: 知几/守正/持中
- 修养智慧: 谦德/自强/厚德
"""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Optional

# 数据文件路径
_DATA_PATH = Path("data/tiaohou/master_wisdom.json")

# 大师信息
MASTERS = {
    "nanhuaijin": {
        "name": "南怀瑾",
        "works": ["《易经杂说》", "《易经系传别讲》"],
        "source": "github.com/big-dollar (劝学网整理版)",
    },
    "zengshiqiang": {
        "name": "曾仕强",
        "works": ["《易经的智慧6》"],
        "source": "陕西师大出版社 (OCR版)",
    },
}

# 核心智慧观点库(人工精选, 按主题分类)
WISDOM_LIBRARY = {
    "变易": {
        "nanhuaijin": "《易经》告诉我们, 宇宙万物没有一样东西是不变的. 变易是宇宙的根本法则, 但变中有不变, 这就是'不易'.",
        "zengshiqiang": "一切都在变, 只有变是不变的. 懂得变的道理, 才能在变化中找到不变的原则.",
    },
    "不易": {
        "nanhuaijin": "虽然万物都在变, 但变的法则本身是不变的. 掌握了不变的法则, 就能应对万变.",
        "zengshiqiang": "变易是现象, 不易是本体. 现象千变万化, 本体始终如一.",
    },
    "简易": {
        "nanhuaijin": "最高深的道理往往是最简单的. 易经的智慧就是把复杂的宇宙人生简化为几个基本原则.",
        "zengshiqiang": "真正的智慧是简单的. 简单到人人都能懂, 但做到却很难.",
    },
    "时位": {
        "nanhuaijin": "易经最重要的两个概念是'时'和'位'. 时就是时间、时机, 位就是空间、位置. 时位不同, 吉凶就不同.",
        "zengshiqiang": "人生最重要的是把握时和位. 时不到, 位不当, 再努力也没用. 时到了, 位对了, 自然成功.",
    },
    "进退": {
        "nanhuaijin": "知进退存亡而不失其正者, 其唯圣人乎. 该进则进, 该退则退, 这是人生的大智慧.",
        "zengshiqiang": "进要进得有道理, 退要退得有价值. 进退之间, 体现的是一个人的修养和智慧.",
    },
    "吉凶": {
        "nanhuaijin": "吉凶者, 失得之象也. 吉凶不是绝对的, 而是相对的. 吉中有凶, 凶中有吉, 关键在于如何应对.",
        "zengshiqiang": "没有绝对的吉, 也没有绝对的凶. 吉时不要得意忘形, 凶时不要灰心丧气. 吉凶转化, 全在人为.",
    },
    "祸福": {
        "nanhuaijin": "祸兮福之所倚, 福兮祸之所伏. 祸福相依, 这是易经的核心智慧.",
        "zengshiqiang": "福来的时候要警惕, 祸来的时候要镇定. 祸福无门, 唯人自招.",
    },
    "知几": {
        "nanhuaijin": "知几其神乎. 几就是事物变化的细微征兆. 能看到几, 就能提前应对, 这就是神.",
        "zengshiqiang": "几者, 动之微, 吉之先见者也. 看到细微的变化, 就能预知吉凶, 这是最高的智慧.",
    },
    "守正": {
        "nanhuaijin": "贞者, 正也. 守正就是坚守正道. 无论环境如何变化, 坚守正道的人最终会得到好的结果.",
        "zengshiqiang": "正就是正当、正当. 走正道, 做正事, 得正果. 守正不是固执, 而是坚持原则.",
    },
    "持中": {
        "nanhuaijin": "中庸之道是易经的核心. 持中就是不偏不倚, 不过度也不不及. 恰到好处, 就是中.",
        "zengshiqiang": "中是天下之大本, 和是天下之达道. 持中致和, 是人生的最高境界.",
    },
    "谦德": {
        "nanhuaijin": "谦卦六爻皆吉, 这在易经中是唯一的. 谦虚是美德, 也是保身之道. 满招损, 谦受益.",
        "zengshiqiang": "谦虚使人进步, 骄傲使人落后. 谦卦告诉我们, 谦虚的人处处逢凶化吉.",
    },
    "自强": {
        "nanhuaijin": "天行健, 君子以自强不息. 天道运行刚健不息, 君子应该效法天道, 自强不息.",
        "zengshiqiang": "自强不是逞强, 而是自我完善. 自强不息的人, 才能不断进步, 最终成就大业.",
    },
    "厚德": {
        "nanhuaijin": "地势坤, 君子以厚德载物. 大地宽厚包容, 君子应该效法大地, 厚德载物.",
        "zengshiqiang": "厚德才能载物. 品德深厚的人, 才能承载大事. 德薄而位尊, 知小而谋大, 力小而任重, 鲜不及矣.",
    },
    "潜龙": {
        "nanhuaijin": "潜龙勿用. 初爻位置太低, 时机未到, 应该潜藏等待, 不要妄动. 这是养精蓄锐的阶段.",
        "zengshiqiang": "潜龙勿用不是不用, 而是时候未到, 不宜大用. 潜龙阶段要好好学习, 积累实力, 等待时机.",
    },
    "见龙": {
        "nanhuaijin": "见龙在田, 利见大人. 九二位置得当, 已经崭露头角, 有利于见到有德有位的人.",
        "zengshiqiang": "见龙在田, 已经初露锋芒. 这个时候要善于表现自己, 但也要注意不要过于张扬.",
    },
    "飞龙": {
        "nanhuaijin": "飞龙在天, 利见大人. 九五至尊, 已经达到人生的巅峰, 大展宏图.",
        "zengshiqiang": "飞龙在天, 是人生最辉煌的时刻. 但越是在高位, 越要谨慎, 因为物极必反.",
    },
    "亢龙": {
        "nanhuaijin": "亢龙有悔. 上九位置太高, 已经过了头, 必然会有悔恨. 这是物极必反的道理.",
        "zengshiqiang": "亢龙有悔告诉我们, 凡事不要做过头. 到了极点就要知道收敛, 否则必然后悔.",
    },
}


@lru_cache(maxsize=1)
def _load_all() -> dict:
    """加载大师智慧数据(缓存)."""
    if _DATA_PATH.exists():
        try:
            with open(_DATA_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # 如果数据文件不存在, 返回内置的智慧库
    return {"wisdom": WISDOM_LIBRARY, "masters": MASTERS}


def get_wisdom(topic: str) -> Optional[dict]:
    """获取指定主题的大师智慧观点.

    Args:
        topic: 主题(变易/不易/简易/时位/进退/吉凶/祸福/知几/守正/持中/谦德/自强/厚德/潜龙/见龙/飞龙/亢龙)

    Returns:
        {master: wisdom_text} 字典, 未找到返回 None.
    """
    data = _load_all()
    wisdom = data.get("wisdom", WISDOM_LIBRARY)
    return wisdom.get(topic)


def get_master_wisdom(master: str, topic: str) -> str:
    """获取指定大师指定主题的智慧观点.

    Args:
        master: 大师(nanhuaijin/zengshiqiang)
        topic: 主题

    Returns:
        智慧观点文本, 未找到返回空字符串.
    """
    wisdom = get_wisdom(topic)
    if not wisdom:
        return ""
    return wisdom.get(master, "")


def get_all_topics() -> list[str]:
    """获取所有可用主题."""
    data = _load_all()
    wisdom = data.get("wisdom", WISDOM_LIBRARY)
    return list(wisdom.keys())


def get_masters() -> dict:
    """获取大师信息."""
    data = _load_all()
    return data.get("masters", MASTERS)


def build_wisdom_advice(topics: list[str] | None = None) -> str:
    """从指定主题构建大师智慧建议文本.

    Args:
        topics: 主题列表, None=全部主题

    Returns:
        建议文本.
    """
    data = _load_all()
    wisdom = data.get("wisdom", WISDOM_LIBRARY)
    if topics:
        wisdom = {k: v for k, v in wisdom.items() if k in topics}
    parts = []
    for topic, masters in wisdom.items():
        for master, text in masters.items():
            master_name = MASTERS.get(master, {}).get("name", master)
            parts.append(f"[{master_name}·{topic}] {text}")
    return "；".join(parts)


def is_available() -> bool:
    """检查大师智慧数据是否可用."""
    return bool(_load_all())


def count_topics() -> int:
    """返回主题数."""
    data = _load_all()
    return len(data.get("wisdom", WISDOM_LIBRARY))


def save_to_file():
    """保存智慧库到数据文件."""
    _DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    data = {"wisdom": WISDOM_LIBRARY, "masters": MASTERS}
    with open(_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
