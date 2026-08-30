"""
TenGod to Stem Mapper - 十神到天干映射器

实现十神语义到实际天干的确定性映射
以及天干到藏干/根气的验证

映射规则（基于子平真诠、滴天髓等原典）：
- 日干为基准
- 十神 = 日干与其他天干的关系

"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Set, Optional
import logging

logger = logging.getLogger(__name__)

# 天干五行属性
STEM_WUXING = {
    "JIA": "WOOD",   # 甲木
    "YI": "WOOD",    # 乙木
    "BING": "FIRE",  # 丙火
    "DING": "FIRE",  # 丁火
    "WU": "EARTH",   # 戊土
    "JI": "EARTH",   # 己土
    "GENG": "METAL", # 庚金
    "XIN": "METAL",  # 辛金
    "REN": "WATER",  # 壬水
    "GUI": "WATER",  # 癸水
}

# 十神名称映射到天干（示例）
# 假设日干为甲木
TEN_GOD_TO_STEM_MAPPING = {
    "JIANSHI": "JIA",      # 比肩 = 同五行同性
    "JIECAI": "YI",       # 劫财 = 同五行异性
    "SHANGGUAN": "DING",  # 伤官 = 我生者
    "SHISHEN": "BING",    # 食神 = 我生者
    "ZICAI": "JI",        # 正财 = 我克者
    "PIANCAI": "WU",      # 偏财 = 我克者
    "ZHENGGUAN": "XIN",   # 正官 = 克我者
    "QISHA": "GENG",      # 七煞 = 克我者
    "ZHENYIN": "GUI",     # 正印 = 生我者
    "PIANYIN": "REN",     # 偏印 = 生我者
    # 支持常见别名
    "YIN_XING": "REN",    # 印星 = 偏印（通用）
    "SHANGGUAN_XING": "DING",  # 伤官星
    "SHISHEN_XING": "BING",   # 食神星
}

# 地支藏干（标准）
BRANCH_HIDDEN_STEMS = {
    "ZIW": {"GUI"},           # 子藏癸
    "CHOU": {"JI", "XIN", "GUI"},  # 丑藏己辛癸
    "YIN": {"JIA", "BING", "WU"},  # 寅藏甲丙戊
    "MAO": {"YI"},           # 卯藏乙
    "CHEN": {"WU", "YI", "GUI"},   # 辰藏戊乙癸
    "SI": {"BING", "WU", "GENG"},  # 巳藏丙戊庚
    "WU": {"WU", "DING", "JI"},   # 午藏戊丁己
    "WEI": {"JI", "DING", "YI"},  # 未藏己丁乙
    "SHEN": {"GENG", "REN", "WU"}, # 申藏庚壬戊
    "YOU": {"XIN"},          # 酉藏辛
    "XU": {"WU", "XIN", "DING"},  # 戌藏戊辛丁
    "HAI": {"REN", "JIA"},   # 亥藏壬甲
}

# 根气定义：某天干在地支中的根
STEM_ROOT_MAP = {
    # 木
    "JIA": {"YIN", "MAO", "CHEN", "HAI"},      # 甲木根
    "YI": {"MAO", "CHEN", "WEI", "HAI"},       # 乙木根
    # 火
    "BING": {"SI", "WU", "CHEN", "XU"},        # 丙火根
    "DING": {"WU", "SI", "WEI", "XU"},         # 丁火根
    # 土
    "WU": {"CHEN", "WU", "XU", "WEI"},         # 戊土根
    "JI": {"CHOU", "WEI", "CHEN", "XU"},       # 己土根
    # 金
    "GENG": {"SHEN", "YOU", "XU", "CHOU"},     # 庚金根
    "XIN": {"YOU", "CHOU", "WU", "SI"},        # 辛金根
    # 水
    "REN": {"HAI", "ZI", "SHEN", "CHEN"},      # 壬水根
    "GUI": {"ZI", "HAI", "CHOU", "CHEN"},      # 癸水根
}


@dataclass
class TenGodToStemMapper:
    """十神到天干的映射器"""
    
    mapper_id: str = "TEN_GOD_MAPPER_001"
    description: str = "TenGod -> Stem mapping based on classical texts"
    
    def __post_init__(self):
        self._mapping = TEN_GOD_TO_STEM_MAPPING.copy()
        self._log_initialization()
    
    def _log_initialization(self):
        logger.info(
            f"[TenGodMapper] Initialized mapper_id={self.mapper_id}, "
            f"mapping entries={len(self._mapping)}"
        )
    
    def map_ten_god_to_stem(
        self, 
        ten_god_name: str,
        day_master: str = "JIA"  # 默认日干为甲木
    ) -> Optional[str]:
        """
        将十神名称映射到天干
        
        Args:
            ten_god_name: 十神名称（如 "SHANGGUAN", "YIN_XING"）
            day_master: 日干（如 "JIA"）
        
        Returns:
            对应的天干名称（如 "DING"），如果无法映射则返回 None
        """
        # 标准化输入
        ten_god_upper = ten_god_name.upper().strip()
        
        # 直接查找映射
        if ten_god_upper in self._mapping:
            stem = self._mapping[ten_god_upper]
            logger.debug(
                f"[TenGodMapper] Mapped {ten_god_upper} -> {stem}"
            )
            return stem
        
        # 尝试基于日干动态计算
        stem = self._calculate_stem_from_tengod(ten_god_upper, day_master)
        if stem:
            logger.debug(
                f"[TenGodMapper] Calculated {ten_god_upper} (day={day_master}) -> {stem}"
            )
            return stem
        
        logger.warning(
            f"[TenGodMapper] Cannot map ten_god={ten_god_upper} to any stem"
        )
        return None
    
    def _calculate_stem_from_tengod(
        self, 
        ten_god: str, 
        day_master: str
    ) -> Optional[str]:
        """
        基于日干动态计算十神对应的天干
        
        规则：
        - 比肩/劫财：同五行
        - 食神/伤官：我生者
        - 正财/偏财：我克者
        - 正官/七煞：克我者
        - 正印/偏印：生我者
        """
        day_wuxing = STEM_WUXING.get(day_master)
        if not day_wuxing:
            return None
        
        # 五行动态关系
        WUXING_GENERATES = {
            "WOOD": "FIRE",
            "FIRE": "EARTH",
            "EARTH": "METAL",
            "METAL": "WATER",
            "WATER": "WOOD",
        }
        
        WUXING_OVERCOMES = {
            "WOOD": "EARTH",
            "EARTH": "WATER",
            "WATER": "FIRE",
            "FIRE": "METAL",
            "METAL": "WOOD",
        }
        
        target_wuxing = None
        
        if ten_god in ["JIANSHI", "JIECAI"]:
            # 比肩/劫财：同五行
            target_wuxing = day_wuxing
        elif ten_god in ["SHISHEN", "SHISHEN_XING"]:
            # 食神：我生者
            target_wuxing = WUXING_GENERATES.get(day_wuxing)
        elif ten_god in ["SHANGGUAN", "SHANGGUAN_XING"]:
            # 伤官：我生者
            target_wuxing = WUXING_GENERATES.get(day_wuxing)
        elif ten_god in ["ZICAI", "PIANCAI"]:
            # 正财/偏财：我克者
            target_wuxing = WUXING_OVERCOMES.get(day_wuxing)
        elif ten_god in ["ZHENGGUAN", "QISHA"]:
            # 正官/七煞：克我者
            target_wuxing = WUXING_OVERCOMES.get(day_wuxing)
        elif ten_god in ["ZHENYIN", "PIANYIN", "YIN_XING"]:
            # 正印/偏印：生我者
            target_wuxing = _reverse(WUXING_GENERATES, day_wuxing)
        
        if not target_wuxing:
            return None
        
        # 找到对应五行的天干
        stems_for_wuxing = [
            s for s, w in STEM_WUXING.items() if w == target_wuxing
        ]
        
        if len(stems_for_wuxing) == 1:
            return stems_for_wuxing[0]
        elif len(stems_for_wuxing) > 1:
            # 需要更多上下文确定具体天干
            # 这里简化处理，返回第一个
            return stems_for_wuxing[0]
        
        return None
    
    def check_has_root(
        self,
        ten_god_name: str,
        branches: Dict[str, int],
        day_master: str = "JIA"
    ) -> bool:
        """
        检查某十神是否有根
        
        Args:
            ten_god_name: 十神名称
            branches: 地支分布（如 {"YIN": 1, "MAO": 1}）
            day_master: 日干
        
        Returns:
            True = 有根，False = 无根
        """
        # 步骤1：映射十神到天干
        stem = self.map_ten_god_to_stem(ten_god_name, day_master)
        if not stem:
            logger.warning(
                f"[TenGodMapper] Cannot map {ten_god_name} to stem, cannot check root"
            )
            return False
        
        # 步骤2：检查该天干在地支中是否有根
        roots = STEM_ROOT_MAP.get(stem, set())
        
        # 检查是否有匹配的地支
        for branch in branches.keys():
            if branch.upper() in roots:
                logger.debug(
                    f"[TenGodMapper] {ten_god_name} -> {stem} has root in {branch}"
                )
                return True
        
        logger.debug(
            f"[TenGodMapper] {ten_god_name} -> {stem} has no root in {list(branches.keys())}"
        )
        return False
    
    def get_root_stems(self, ten_god_name: str, day_master: str = "JIA") -> Set[str]:
        """
        获取某十神的根气所在天干
        
        Returns:
            根气所在的地支集合
        """
        stem = self.map_ten_god_to_stem(ten_god_name, day_master)
        if not stem:
            return set()
        
        return STEM_ROOT_MAP.get(stem, set()).copy()


def _reverse(d: Dict[str, str], value: str) -> Optional[str]:
    """反向查找字典中的键"""
    for k, v in d.items():
        if v == value:
            return k
    return None


if __name__ == "__main__":
    # 测试映射器
    mapper = TenGodToStemMapper()
    
    print("=== TenGodMapper Test ===")
    print()
    
    # 测试十神->天干映射
    test_cases = [
        ("SHANGGUAN", "JIA"),
        ("YIN_XING", "JIA"),
        ("JIANSHI", "JIA"),
        ("ZHENGGUAN", "JIA"),
        ("ZICAI", "JIA"),
    ]
    
    for ten_god, day in test_cases:
        stem = mapper.map_ten_god_to_stem(ten_god, day)
        print(f"{ten_god} (day={day}) -> {stem}")
    
    print()
    
    # 测试根气检查
    branches = {"YIN": 1, "MAO": 1, "WU": 1}
    
    for ten_god, day in test_cases:
        has_root = mapper.check_has_root(ten_god, branches, day)
        print(f"{ten_god} has root in {branches}: {has_root}")
