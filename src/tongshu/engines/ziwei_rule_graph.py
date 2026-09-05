"""紫微斗数规则图 — Z3 Rule Graph

职责：
  - 定义流派规则图数据结构
  - 支持不同流派加载不同的规则集
  - 规则节点带 method_id 约束

与 MethodProfile 的关系：
  - MethodProfile: 配置参数（四化表版本、空宫策略等）
  - RuleGraph: 断事规则（格局识别、四化解读等）

使用示例：
  from tongshu.engines.ziwei_rule_graph import RuleGraph, RuleNode
  
  # 加载三合派规则
  graph = RuleGraph.load("sanhe")
  
  # 查询命宫格局规则
  rules = graph.query_rules("pattern", target="命宫")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable, Iterator
from enum import Enum


# ============================================================================
# 类型定义
# ============================================================================

class RuleType(Enum):
    """规则类型枚举"""
    PATTERN = "pattern"           # 格局规则（星曜组合）
    MUTAGEN = "mutagen"           # 四化规则
    PALACE = "palace"             # 宫位规则
    INTERACTION = "interaction"   # 交互规则（宫位间关系）


MethodId = str  # "sanhe", "zhongzhou", "feixing", "qintian"


# ============================================================================
# 规则节点
# ============================================================================

@dataclass(frozen=True)
class RuleNode:
    """规则图节点
    
    Args:
        rule_id: 规则唯一标识（如 "ZW-PAT-001"）
        rule_type: 规则类型
        condition: 条件检查函数 (ZiweiFact) -> bool
        effect: 效果函数 (ZiweiFact) -> dict（可选）
        method_ids: 适用的流派集合
        priority: 优先级（越高越先执行）
        source_ref: 古籍出处引用
        evidence_id: 验证证据ID
        description: 规则描述
        version: 规则版本
    """
    
    rule_id: str
    rule_type: RuleType
    condition: Callable[[object], bool]
    effect: Callable[[object], dict] | None = None
    
    method_ids: tuple[MethodId, ...] = ("sanhe", "zhongzhou", "feixing", "qintian")
    priority: int = 0
    
    source_ref: str = ""
    evidence_id: str = ""
    description: str = ""
    version: str = "2026.09"
    
    def matches_method(self, method_id: MethodId) -> bool:
        """检查该规则是否适用于指定流派"""
        return method_id in self.method_ids


# ============================================================================
# 规则图
# ============================================================================

class RuleGraph:
    """规则图 — 管理规则节点集合
    
    支持：
    - 按流派筛选规则
    - 按规则类型查询
    - 按优先级排序执行
    """
    
    def __init__(self):
        self._nodes: dict[str, RuleNode] = {}
        self._method_index: dict[MethodId, list[str]] = {
            "sanhe": [],
            "zhongzhou": [],
            "feixing": [],
            "qintian": [],
        }
        self._type_index: dict[RuleType, list[str]] = {
            rt: [] for rt in RuleType
        }
    
    def add_rule(self, node: RuleNode) -> None:
        """添加规则节点"""
        if node.rule_id in self._nodes:
            raise ValueError(f"Rule ID already exists: {node.rule_id}")
        
        self._nodes[node.rule_id] = node
        
        # 更新索引
        for method_id in node.method_ids:
            if method_id in self._method_index:
                self._method_index[method_id].append(node.rule_id)
        
        if node.rule_type.value in self._type_index:
            self._type_index[node.rule_type.value].append(node.rule_id)
    
    def get_rule(self, rule_id: str) -> RuleNode | None:
        """根据 ID 获取规则"""
        return self._nodes.get(rule_id)
    
    def query_rules(
        self,
        rule_type: RuleType,
        method_id: MethodId | None = None,
    ) -> list[RuleNode]:
        """查询规则
        
        Args:
            rule_type: 规则类型
            method_id: 流派过滤（None 返回所有）
        
        Returns:
            按优先级排序的规则列表
        """
        type_key = rule_type.value
        nodes = [self._nodes[rid] for rid in self._type_index.get(type_key, []) 
                 if rid in self._nodes]
        
        if method_id:
            nodes = [n for n in nodes if n.matches_method(method_id)]
        
        return sorted(nodes, key=lambda n: n.priority, reverse=True)
    
    def execute_rules(
        self,
        fact: object,
        rule_type: RuleType,
        method_id: MethodId | None = None,
    ) -> list[dict]:
        """执行规则并收集结果
        
        Args:
            fact: ZiweiFact 实例
            rule_type: 规则类型
            method_id: 流派过滤
        
        Returns:
            规则结果列表 [{rule_id, matched, result}, ...]
        """
        rules = self.query_rules(rule_type, method_id)
        results = []
        
        for rule in rules:
            try:
                matched = rule.condition(fact)
                result = rule.effect(fact) if matched and rule.effect else {}
                results.append({
                    "rule_id": rule.rule_id,
                    "matched": matched,
                    "result": result,
                })
            except Exception as e:
                results.append({
                    "rule_id": rule.rule_id,
                    "matched": False,
                    "error": str(e),
                })
        
        return results
    
    def iter_rules(
        self,
        method_id: MethodId | None = None,
    ) -> Iterator[RuleNode]:
        """遍历所有规则（可按流派过滤）"""
        if method_id:
            for rid in self._method_index.get(method_id, []):
                if rid in self._nodes:
                    yield self._nodes[rid]
        else:
            yield from self._nodes.values()
    
    @classmethod
    def load_sanhe(cls) -> RuleGraph:
        """加载三合派规则集
        
        依据：《紫微斗数全书》《全集》
        """
        graph = cls()
        
        # === 格局规则 ===
        
        # ZW-PAT-001: 紫微独坐
        graph.add_rule(RuleNode(
            rule_id="ZW-PAT-001",
            rule_type=RuleType.PATTERN,
            condition=lambda f: _has_star_only(f, "紫微"),
            effect=lambda f: {"pattern": "紫微独坐", " palace": "命宫"},
            method_ids=("sanhe", "zhongzhou"),
            priority=100,
            source_ref="《紫微斗数全书》论紫微星",
            evidence_id="E-PAT-001",
            description="命宫独坐紫微星",
        ))
        
        # ZW-PAT-002: 天府独坐
        graph.add_rule(RuleNode(
            rule_id="ZW-PAT-002",
            rule_type=RuleType.PATTERN,
            condition=lambda f: _has_star_only(f, "天府"),
            effect=lambda f: {"pattern": "天府独坐", "palace": "命宫"},
            method_ids=("sanhe", "zhongzhou"),
            priority=100,
            source_ref="《紫微斗数全书》论天府星",
            evidence_id="E-PAT-002",
            description="命宫独坐天府星",
        ))
        
        # ZW-PAT-003: 杀破狼
        graph.add_rule(RuleNode(
            rule_id="ZW-PAT-003",
            rule_type=RuleType.PATTERN,
            condition=lambda f: _has_pattern(f, ["七杀", "破军", "贪狼"]),
            effect=lambda f: {"pattern": "杀破狼", "palace": "命宫"},
            method_ids=("sanhe", "zhongzhou"),
            priority=90,
            source_ref="《骨髓赋》杀破狼同行",
            evidence_id="E-PAT-003",
            description="命宫七杀、破军、贪狼同宫",
        ))
        
        # ZW-SIHUA-001: 生年禄入命
        graph.add_rule(RuleNode(
            rule_id="ZW-SIHUA-001",
            rule_type=RuleType.MUTAGEN,
            condition=lambda f: _sihua_in_palace(f, "禄", "命宫"),
            effect=lambda f: {"position": "命宫", "type": "禄", "source": "生年"},
            method_ids=("sanhe",),
            priority=80,
            source_ref="《紫微斗数全书》论四化",
            evidence_id="E-SIHUA-001",
            description="生年禄星落入命宫",
        ))
        
        # ZW-SIHUA-002: 生年忌入命
        graph.add_rule(RuleNode(
            rule_id="ZW-SIHUA-002",
            rule_type=RuleType.MUTAGEN,
            condition=lambda f: _sihua_in_palace(f, "忌", "命宫"),
            effect=lambda f: {"position": "命宫", "type": "忌", "source": "生年"},
            method_ids=("sanhe",),
            priority=80,
            source_ref="《紫微斗数全书》论四化",
            evidence_id="E-SIHUA-002",
            description="生年忌星落入命宫",
        ))
        
        return graph
    
    @classmethod
    def load_zhongzhou(cls) -> RuleGraph:
        """加载中州派规则集
        
        依据：王亭之《谈斗数》《紫微斗数讲义》
        """
        graph = cls.load_sanhe()  # 继承三合派基础规则
        
        # === 中州派特殊规则 ===
        
        # ZW-ZZ-001: 流昌流曲入命
        graph.add_rule(RuleNode(
            rule_id="ZW-ZZ-001",
            rule_type=RuleType.PATTERN,
            condition=lambda f: _has_star(f, "流昌") or _has_star(f, "流曲"),
            effect=lambda f: {"star": "流昌/流曲", "palace": "命宫"},
            method_ids=("zhongzhou",),
            priority=70,
            source_ref="王亭之《紫微斗数讲义》流昌流曲",
            evidence_id="E-ZZ-001",
            description="命宫见流昌或流曲",
        ))
        
        # ZW-ZZ-002: 空宫全借
        graph.add_rule(RuleNode(
            rule_id="ZW-ZZ-002",
            rule_type=RuleType.PALACE,
            condition=lambda f: f.soul_palace.is_empty if hasattr(f, 'soul_palace') else False,
            effect=lambda f: {"strategy": "full_borrow", "palace": "命宫"},
            method_ids=("zhongzhou",),
            priority=60,
            source_ref="王亭之《谈斗数》空宫借星",
            evidence_id="E-ZZ-002",
            description="命宫空宫时全借对宫主星",
        ))
        
        # ZW-ZZ-003: 戊干太阳化科
        graph.add_rule(RuleNode(
            rule_id="ZW-ZZ-003",
            rule_type=RuleType.MUTAGEN,
            condition=lambda f: _sihua_with_stem(f, "戊", "科", "太阳"),
            effect=lambda f: {"stem": "戊", "type": "科", "star": "太阳"},
            method_ids=("zhongzhou",),
            priority=50,
            source_ref="王亭之《谈斗数》戊干四化",
            evidence_id="E-ZZ-003",
            description="戊干太阳化科（中州派特殊）",
        ))
        
        return graph
    
    @classmethod
    def load_feixing(cls) -> RuleGraph:
        """加载飞星派规则集
        
        依据：梁若瑜《专论四化》《十八飞星秘仪》
        """
        graph = cls()  # 飞星派从头构建
        
        # === 飞化规则 ===
        
        # ZW-FX-001: 宫干飞禄
        graph.add_rule(RuleNode(
            rule_id="ZW-FX-001",
            rule_type=RuleType.MUTAGEN,
            condition=lambda f: True,  # 简化：实际需计算宫干飞化
            effect=lambda f: {"type": "gonggan_feilu", "palace": "命宫"},
            method_ids=("feixing",),
            priority=90,
            source_ref="梁若瑜《专论四化》宫干飞化",
            evidence_id="E-FX-001",
            description="宫干引发禄星飞化",
        ))
        
        # ZW-FX-002: 宫干飞忌
        graph.add_rule(RuleNode(
            rule_id="ZW-FX-002",
            rule_type=RuleType.MUTAGEN,
            condition=lambda f: True,
            effect=lambda f: {"type": "gonggan_feiji", "palace": "命宫"},
            method_ids=("feixing",),
            priority=90,
            source_ref="梁若瑜《专论四化》宫干飞化",
            evidence_id="E-FX-002",
            description="宫干引发忌星飞化",
        ))
        
        # ZW-FX-003: 命宫无小限
        graph.add_rule(RuleNode(
            rule_id="ZW-FX-003",
            rule_type=RuleType.PALACE,
            condition=lambda f: not getattr(f, 'use_xiaoxian', True),
            effect=lambda f: {"xiaoxian": False},
            method_ids=("feixing",),
            priority=10,
            source_ref="梁若瑜《十八飞星秘仪》",
            evidence_id="E-FX-003",
            description="飞星派不使用小限",
        ))
        
        return graph
    
    @classmethod
    def load_qintian(cls) -> RuleGraph:
        """加载钦天门规则集
        
        依据：蔡明宏《华山钦天四化紫微斗数飞星秘仪》
        """
        graph = cls()
        
        # === 钦天特殊规则 ===
        
        # ZW-QT-001: 向心忌
        graph.add_rule(RuleNode(
            rule_id="ZW-QT-001",
            rule_type=RuleType.INTERACTION,
            condition=lambda f: True,  # 简化
            effect=lambda f: {"type": "xiangxin_ji", "direction": "incoming"},
            method_ids=("qintian",),
            priority=95,
            source_ref="蔡明宏《华山钦天四化秘仪》向心忌",
            evidence_id="E-QT-001",
            description="他宫化忌入本命宫（向心忌）",
        ))
        
        # ZW-QT-002: 离心忌
        graph.add_rule(RuleNode(
            rule_id="ZW-QT-002",
            rule_type=RuleType.INTERACTION,
            condition=lambda f: True,
            effect=lambda f: {"type": "lixin_ji", "direction": "outgoing"},
            method_ids=("qintian",),
            priority=95,
            source_ref="蔡明宏《华山钦天四化秘仪》离心忌",
            evidence_id="E-QT-002",
            description="本命宫化忌入他宫（离心忌）",
        ))
        
        # ZW-QT-003: 立极宫
        graph.add_rule(RuleNode(
            rule_id="ZW-QT-003",
            rule_type=RuleType.PALACE,
            condition=lambda f: hasattr(f, 'soul_palace'),
            effect=lambda f: {"liji_gong": "命宫"},
            method_ids=("qintian",),
            priority=100,
            source_ref="蔡明宏《华山钦天四化秘仪》立极宫",
            evidence_id="E-QT-003",
            description="以命宫为立极宫",
        ))
        
        return graph
    
    @classmethod
    def load(cls, method_id: MethodId) -> RuleGraph:
        """加载指定流派的规则集
        
        Args:
            method_id: 流派标识
            
        Returns:
            RuleGraph 实例
        """
        loaders = {
            "sanhe": cls.load_sanhe,
            "zhongzhou": cls.load_zhongzhou,
            "feixing": cls.load_feixing,
            "qintian": cls.load_qintian,
        }
        
        loader = loaders.get(method_id)
        if not loader:
            raise ValueError(f"Unknown method_id: {method_id}")
        
        return loader()


# ============================================================================
# 辅助函数
# ============================================================================

def _get_soul_palace(fact: object) -> object | None:
    """获取命宫事实"""
    return getattr(fact, 'soul_palace', None)


def _has_star_only(fact: object, star_name: str) -> bool:
    """检查命宫是否独坐某星"""
    sp = _get_soul_palace(fact)
    if not sp or not hasattr(sp, 'major_stars'):
        return False
    return sp.major_stars == (star_name,)


def _has_pattern(fact: object, stars: list[str]) -> bool:
    """检查命宫是否包含指定星曜组合"""
    sp = _get_soul_palace(fact)
    if not sp or not hasattr(sp, 'major_stars'):
        return False
    return all(s in sp.major_stars for s in stars)


def _has_star(fact: object, star_name: str) -> bool:
    """检查命宫是否包含某星"""
    sp = _get_soul_palace(fact)
    if not sp:
        return False
    if hasattr(sp, 'major_stars') and star_name in sp.major_stars:
        return True
    if hasattr(sp, 'minor_stars') and star_name in sp.minor_stars:
        return True
    return False


def _sihua_in_palace(fact: object, sihua_type: str, palace_name: str) -> bool:
    """检查某四化是否落入指定宫位"""
    mutagen = getattr(fact, 'birth_mutagen', None)
    if not mutagen or not hasattr(mutagen, 'mutagens'):
        return False
    
    type_idx = {"禄": 0, "权": 1, "科": 2, "忌": 3}.get(sihua_type)
    if type_idx is None:
        return False
    
    sihua_star = mutagen.mutagens[type_idx]
    if not sihua_star:
        return False
    
    # 查找该星所在宫位
    for pname, pf in getattr(fact, 'palaces', {}).items():
        if pname == palace_name:
            stars = set(getattr(pf, 'major_stars', ())) | set(getattr(pf, 'minor_stars', ()))
            return sihua_star in stars
    
    return False


def _sihua_with_stem(fact: object, stem: str, sihua_type: str, star_name: str) -> bool:
    """检查特定天干的四化"""
    # 简化：中州派戊干太阳化科
    if stem != "戊":
        return False
    if sihua_type != "科":
        return False
    if star_name != "太阳":
        return False
    
    # 检查命宫天干是否为戊
    sp = _get_soul_palace(fact)
    if sp and hasattr(sp, 'heavenly_stem'):
        return sp.heavenly_stem == stem
    
    return False


# ============================================================================
# 导出
# ============================================================================

__all__ = [
    "RuleNode",
    "RuleType",
    "MethodId",
    "RuleGraph",
    "_get_soul_palace",
    "_has_star_only",
    "_has_pattern",
    "_has_star",
    "_sihua_in_palace",
    "_sihua_with_stem",
]
