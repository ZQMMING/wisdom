"""P5-A Assertion-to-Guidance Mapping - 断言到指引的确定性映射.

这是P5-A的核心: 将CanonicalAssertion/AssertionCluster映射为GuidanceAtom.

硬契约:
  - deterministic, 不引入AI自由推理
  - 基于domain + semantic_family + direction的映射规则
  - 不允许从direction偷换成吉凶
  - 所有GuidanceAtom可追溯回source_assertion_ids
  - 不创造Evidence

映射逻辑:
  1. 按domain分组
  2. 按semantic_family查找映射模板
  3. 根据direction选择对应的opportunities/cautions/actions/avoid
  4. 组装为GuidanceAtom
"""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Optional

from ..reasoning.assertion import CanonicalAssertion
from ..reasoning.assertion_cluster import AssertionCluster
from .guidance_atom import (
    GuidanceAtom,
    DIRECTION_LABELS,
    DIRECTION_DESCRIPTIONS,
    make_guidance_id,
    validate_guidance_contract,
)

log = logging.getLogger(__name__)


# 映射模板: semantic_family -> {direction -> {theme, opportunities, cautions, actions, avoid}}
# 这是P5-A的核心映射规则, deterministic
MAPPING_TEMPLATES = {
    # === OUTPUT_EXPRESSION 输出/表达类 ===
    "OUTPUT_EXPRESSION": {
        "supportive": {
            "theme": "输出与表达窗口",
            "opportunities": [
                "适合将已有经验、知识或能力转化为可见的成果",
                "公开表达、项目推进、产品化等事项容易获得正向反馈",
                "个人能力和专业判断更容易被他人认可",
            ],
            "cautions": [
                "输出增加时注意质量与节奏的平衡",
                "避免因表达欲增强而忽视他人反馈",
            ],
            "actions": [
                "优先推进一个已经成熟的项目或作品",
                "把积累的经验整理成可分享的形式",
                "主动争取表达和展示的机会",
            ],
            "avoid": [
                "同时铺开太多新方向导致精力分散",
                "只输出不沉淀, 缺乏长期积累",
            ],
        },
        "caution": {
            "theme": "输出节奏需调整",
            "opportunities": [
                "可以通过调整表达方式获得更好的效果",
                "适合复盘过去的输出并优化方法",
            ],
            "cautions": [
                "当前输出容易遇到阻力或反馈不及预期",
                "表达过于直接可能引发误解或冲突",
                "过度输出可能消耗过多精力",
            ],
            "actions": [
                "先检查输出的目标和受众是否匹配",
                "调整表达方式, 增加倾听和反馈环节",
                "控制输出节奏, 留出反思和调整的空间",
            ],
            "avoid": [
                "强行推进不被接受的表达",
                "因反馈不佳而完全停止输出",
            ],
        },
        "neutral": {
            "theme": "输出与表达平稳期",
            "opportunities": [
                "适合按常规节奏推进表达和输出",
                "可以尝试新的表达形式但不必急于求成",
            ],
            "cautions": [
                "没有明显的外部推力, 需要主动设定目标",
            ],
            "actions": [
                "保持稳定的输出节奏",
                "为下一阶段的输出做准备和积累",
            ],
            "avoid": [
                "因缺乏外部反馈而放弃输出",
            ],
        },
    },

    # === RESOURCE_WEALTH 资源/财富类 ===
    "RESOURCE_WEALTH": {
        "supportive": {
            "theme": "资源转化窗口",
            "opportunities": [
                "已有资源、客户、技能或项目容易产生实际价值",
                "收入结构调整、资产配置等事项有较好的条件",
                "商业合作和资源整合容易达成",
            ],
            "cautions": [
                "资源增加时注意风险分散和长期规划",
                "避免因短期收益而忽视可持续性",
            ],
            "actions": [
                "把已有资源重新组合以产生新的价值",
                "优先推进回报明确的项目或合作",
                "梳理收入结构, 优化资源配置效率",
            ],
            "avoid": [
                "没有资源基础就盲目扩大投入",
                "把所有资源集中在单一方向",
            ],
        },
        "caution": {
            "theme": "资源管理需谨慎",
            "opportunities": [
                "适合梳理和优化现有资源的使用效率",
                "可以通过规范管理减少不必要的损耗",
            ],
            "cautions": [
                "大额支出或投资需要更严格的评估",
                "合作中的利益分配容易产生分歧",
                "资源流动可能出现延迟或不确定性",
            ],
            "actions": [
                "先算清楚哪些资源真正产生回报",
                "合同和财务安排务必明确书面化",
                "保留足够的流动性应对不确定情况",
            ],
            "avoid": [
                "在信息不充分时做大额财务决定",
                "因人情关系而忽视利益边界",
            ],
        },
        "neutral": {
            "theme": "资源与财富平稳期",
            "opportunities": [
                "适合按常规节奏管理资源和财务",
                "可以为下一阶段的资源积累做规划",
            ],
            "cautions": [
                "没有明显的外部机会, 需要主动寻找",
            ],
            "actions": [
                "保持稳定的资源管理习惯",
                "学习和准备新的资源获取方式",
            ],
            "avoid": [
                "因缺乏机会而放松财务管理",
            ],
        },
    },

    # === CONSTRAINT_RULE 约束/规则类 ===
    "CONSTRAINT_RULE": {
        "supportive": {
            "theme": "规则与制度助力期",
            "opportunities": [
                "清晰的规则和制度有助于推进目标",
                "适合建立流程、规范和长期机制",
                "权责明确的合作容易达成稳定成果",
            ],
            "cautions": [
                "规则增加时注意灵活性和适应性",
                "避免过度依赖制度而忽视实际情况",
            ],
            "actions": [
                "把重要事项纳入清晰的流程和规范",
                "合作前明确角色、权责和利益分配",
                "利用规则和制度帮助自己完成目标",
            ],
            "avoid": [
                "因规则限制而放弃合理的创新尝试",
                "只建规则不执行",
            ],
        },
        "caution": {
            "theme": "规则与责任压力期",
            "opportunities": [
                "适合梳理和优化现有的规则和责任结构",
                "可以通过明确边界减少不必要的压力",
            ],
            "cautions": [
                "外部规则、制度或责任要求可能增加",
                "权责不清容易导致纠纷或额外负担",
                "过度约束可能限制行动空间",
            ],
            "actions": [
                "先确认自己的责任边界和权力范围",
                "把模糊的规则和约定明确化、书面化",
                "学会利用规则保护自己的合理权益",
            ],
            "avoid": [
                "在权责不清时承担过多责任",
                "因害怕规则而不敢行动",
            ],
        },
        "neutral": {
            "theme": "规则与责任平稳期",
            "opportunities": [
                "适合按现有规则和流程推进事项",
                "可以逐步优化和完善制度",
            ],
            "cautions": [
                "没有明显的外部压力, 但也不要忽视规范",
            ],
            "actions": [
                "保持对规则和责任的清晰认知",
                "逐步建立更完善的流程和机制",
            ],
            "avoid": [
                "因平稳而忽视规则和边界",
            ],
        },
    },

    # === CHANGE_TRANSFORMATION 变化/转型类 ===
    "CHANGE_TRANSFORMATION": {
        "supportive": {
            "theme": "结构转型启动期",
            "opportunities": [
                "适合重新调整工作模式、资源配置或生活结构",
                "旧模式的改变容易打开新的空间",
                "转型和升级有较好的外部条件支持",
            ],
            "cautions": [
                "转型期注意节奏, 避免一次性改变太多",
                "新旧模式交替时容易出现短暂的混乱",
            ],
            "actions": [
                "先清理低效或过时的结构和模式",
                "把已有资源放进新的组织方式中",
                "分阶段推进转型, 每阶段确认效果",
            ],
            "avoid": [
                "为了变化而变化, 没有明确目标",
                "同时铺开太多新方向导致资源分散",
            ],
        },
        "caution": {
            "theme": "结构变化需应对",
            "opportunities": [
                "变化中可能出现新的机会和空间",
                "适合主动调整以适应外部变化",
            ],
            "cautions": [
                "外部环境或内部结构可能发生明显变化",
                "原有模式可能不再适用, 需要及时调整",
                "变化过程中容易出现不确定性和压力",
            ],
            "actions": [
                "先评估变化对自己的具体影响",
                "主动调整策略和方法以适应新情况",
                "保留足够的灵活性和备选方案",
            ],
            "avoid": [
                "抗拒变化而坚持过时的模式",
                "在变化中仓促做不可逆的决定",
            ],
        },
        "neutral": {
            "theme": "结构平稳过渡期",
            "opportunities": [
                "适合按现有节奏推进, 同时观察变化趋势",
                "可以为下一阶段的调整做准备",
            ],
            "cautions": [
                "没有明显的外部变化, 但也不要忽视潜在趋势",
            ],
            "actions": [
                "保持对环境变化的观察和感知",
                "逐步为可能的转型做准备",
            ],
            "avoid": [
                "因平稳而忽视长期趋势的变化",
            ],
        },
    },

    # === RELATION_CONNECTION 关系/感情类 ===
    "RELATION_CONNECTION": {
        "supportive": {
            "theme": "关系与连接发展期",
            "opportunities": [
                "适合建立和深化重要的人际关系",
                "合作、伙伴关系等事项有较好的发展条件",
                "人际连接容易带来新的机会和支持",
            ],
            "cautions": [
                "关系增加时注意边界和质量",
                "避免因人情而忽视自身需求",
            ],
            "actions": [
                "主动维护和深化重要的关系",
                "在合作中明确双方的期望和边界",
                "通过真诚沟通建立长期信任",
            ],
            "avoid": [
                "为了维持关系而过度妥协",
                "同时建立太多浅层关系而忽视深度",
            ],
        },
        "caution": {
            "theme": "关系与连接需调整",
            "opportunities": [
                "适合梳理和优化现有的人际关系",
                "可以通过沟通解决长期存在的问题",
            ],
            "cautions": [
                "关系中可能出现分歧、误解或张力",
                "合作中的利益和责任分配容易产生矛盾",
                "过度投入关系可能影响个人空间",
            ],
            "actions": [
                "先把真正的问题说清楚, 而不是回避",
                "重新确认双方的边界和期望",
                "给关系留出调整和修复的空间",
            ],
            "avoid": [
                "因关系出现问题就做不可逆的决定",
                "把所有问题都归咎于对方",
            ],
        },
        "neutral": {
            "theme": "关系与连接平稳期",
            "opportunities": [
                "适合按常规节奏维护人际关系",
                "可以为下一阶段的关系发展做准备",
            ],
            "cautions": [
                "没有明显的外部推动, 需要主动维护",
            ],
            "actions": [
                "保持对重要关系的关注和维护",
                "逐步深化有价值的人际连接",
            ],
            "avoid": [
                "因忙碌而忽视重要的关系",
            ],
        },
    },

    # === REFLECTION_GROWTH 反思/成长类 ===
    "REFLECTION_GROWTH": {
        "supportive": {
            "theme": "成长与定位清晰期",
            "opportunities": [
                "适合重新确认自己的方向和定位",
                "学习、反思和能力提升有较好的条件",
                "过去的经验容易转化为新的认知和能力",
            ],
            "cautions": [
                "成长过程中注意实践和落地",
                "避免只思考不行动",
            ],
            "actions": [
                "花时间梳理自己的优势和方向",
                "把学习和反思的成果应用到实际中",
                "设定清晰的成长目标和路径",
            ],
            "avoid": [
                "陷入过度思考而迟迟不行动",
                "盲目追求不适合自己的方向",
            ],
        },
        "caution": {
            "theme": "成长与定位需反思",
            "opportunities": [
                "适合深入反思过去的模式和选择",
                "可以通过调整认知获得新的成长空间",
            ],
            "cautions": [
                "可能对现有方向产生疑问或不确定",
                "过去有效的方法未必适合下一阶段",
                "过度反思可能导致行动迟滞",
            ],
            "actions": [
                "先确认哪些东西应该保留, 哪些需要调整",
                "把反思转化为具体的行动调整",
                "给自己留出探索和试错的空间",
            ],
            "avoid": [
                "因不确定而完全停止行动",
                "盲目否定过去的所有经验",
            ],
        },
        "neutral": {
            "theme": "成长与定位平稳期",
            "opportunities": [
                "适合按现有节奏学习和成长",
                "可以为下一阶段的定位做准备",
            ],
            "cautions": [
                "没有明显的外部推动, 需要主动设定目标",
            ],
            "actions": [
                "保持学习和反思的习惯",
                "逐步明确下一阶段的成长方向",
            ],
            "avoid": [
                "因缺乏方向而放松成长投入",
            ],
        },
    },

    # === STABILITY_SUPPORT 稳定/支持类 ===
    "STABILITY_SUPPORT": {
        "supportive": {
            "theme": "稳定与支持增强期",
            "opportunities": [
                "适合建立和巩固稳定的基础和结构",
                "家庭、团队或内部系统的支持容易增强",
                "长期经营和积累有较好的条件",
            ],
            "cautions": [
                "稳定时注意不要变得僵化",
                "避免因舒适而忽视潜在的变化",
            ],
            "actions": [
                "优先巩固和完善已有的基础和结构",
                "投入时间维护重要的支持系统",
                "为长期目标建立稳定的执行机制",
            ],
            "avoid": [
                "因稳定而停止创新和调整",
                "忽视外部环境的潜在变化",
            ],
        },
        "caution": {
            "theme": "稳定与支持需维护",
            "opportunities": [
                "适合梳理和修复现有的支持系统",
                "可以通过主动维护增强稳定性",
            ],
            "cautions": [
                "原有稳定结构可能出现松动或压力",
                "支持系统可能需要更多的投入和维护",
                "过度追求稳定可能限制发展空间",
            ],
            "actions": [
                "先确认哪些基础和支持系统需要维护",
                "主动投入时间修复和巩固重要关系",
                "在稳定中保留一定的灵活性",
            ],
            "avoid": [
                "忽视已经出现的不稳定信号",
                "为了维持稳定而拒绝必要的改变",
            ],
        },
        "neutral": {
            "theme": "稳定与支持平稳期",
            "opportunities": [
                "适合按现有节奏维护稳定和支持系统",
                "可以为下一阶段的巩固做准备",
            ],
            "cautions": [
                "没有明显的外部压力, 但也不要忽视维护",
            ],
            "actions": [
                "保持对支持系统的定期维护",
                "逐步巩固和完善基础结构",
            ],
            "avoid": [
                "因平稳而忽视长期维护",
            ],
        },
    },

    # === ACTION_EXECUTION 行动/执行类 ===
    "ACTION_EXECUTION": {
        "supportive": {
            "theme": "行动与执行推进期",
            "opportunities": [
                "适合主动推进已经规划好的事项",
                "执行和落地容易获得实际成果",
                "行动力和效率容易提升",
            ],
            "cautions": [
                "行动增加时注意方向和质量",
                "避免因效率提升而忽视细节",
            ],
            "actions": [
                "优先推进一个明确的目标或项目",
                "把计划分解为可执行的具体步骤",
                "保持稳定的执行节奏",
            ],
            "avoid": [
                "同时推进太多目标导致分散",
                "只行动不反思方向是否正确",
            ],
        },
        "caution": {
            "theme": "行动与执行需调整",
            "opportunities": [
                "适合复盘和优化执行方法",
                "可以通过调整节奏提高效率",
            ],
            "cautions": [
                "行动可能遇到阻力或效率下降",
                "方向不明确时容易做无用功",
                "过度行动可能导致精力透支",
            ],
            "actions": [
                "先确认行动的目标和方向是否正确",
                "调整执行方法和节奏以适应情况",
                "留出休息和反思的时间",
            ],
            "avoid": [
                "在方向不明确时盲目行动",
                "因效率下降而完全停止推进",
            ],
        },
        "neutral": {
            "theme": "行动与执行平稳期",
            "opportunities": [
                "适合按常规节奏推进事项",
                "可以为下一阶段的行动做准备",
            ],
            "cautions": [
                "没有明显的外部推动, 需要主动设定目标",
            ],
            "actions": [
                "保持稳定的执行习惯",
                "逐步优化执行方法和效率",
            ],
            "avoid": [
                "因缺乏动力而拖延重要事项",
            ],
        },
    },

    # === HEALTH_CAUTION 健康类 ===
    "HEALTH_CAUTION": {
        "supportive": {
            "theme": "健康与精力管理期",
            "opportunities": [
                "适合建立和巩固健康的生活习惯",
                "精力和恢复能力容易提升",
                "身体状态的调整有较好的条件",
            ],
            "cautions": [
                "健康改善时注意长期坚持",
                "避免因状态好而过度消耗",
            ],
            "actions": [
                "优先建立规律的作息和运动习惯",
                "关注身体发出的信号并及时调整",
                "为长期健康建立可持续的习惯",
            ],
            "avoid": [
                "因状态好而忽视休息和恢复",
                "尝试极端或不可持续的健康方法",
            ],
        },
        "caution": {
            "theme": "健康与精力需关注",
            "opportunities": [
                "适合主动调整生活节奏和健康习惯",
                "可以通过早期干预避免更大的问题",
            ],
            "cautions": [
                "精力可能下降或身体发出需要关注的信号",
                "长期透支可能影响工作和生活质量",
                "压力和疲劳可能累积",
            ],
            "actions": [
                "先检查作息、饮食和运动是否需要调整",
                "主动安排休息和恢复的时间",
                "如有持续不适, 及时寻求专业医疗建议",
            ],
            "avoid": [
                "忽视身体发出的持续信号",
                "用极端方式快速解决健康问题",
            ],
        },
        "neutral": {
            "theme": "健康与精力平稳期",
            "opportunities": [
                "适合按常规节奏维护健康",
                "可以为下一阶段的健康管理做准备",
            ],
            "cautions": [
                "没有明显的问题, 但也不要忽视日常维护",
            ],
            "actions": [
                "保持健康的生活习惯",
                "定期关注身体状态和精力水平",
            ],
            "avoid": [
                "因没有问题而忽视健康管理",
            ],
        },
    },
}

# 默认模板(当semantic_family未匹配时使用)
DEFAULT_TEMPLATE = {
    "supportive": {
        "theme": "有利条件期",
        "opportunities": ["当前结构中存在可利用的有利条件", "适合主动推进相关事项"],
        "cautions": ["注意节奏和质量的平衡"],
        "actions": ["优先推进已经成熟的事项", "把已有资源转化为实际成果"],
        "avoid": ["同时铺开太多新方向", "因顺利而忽视细节"],
    },
    "caution": {
        "theme": "需谨慎处理期",
        "opportunities": ["适合梳理和优化现有方法", "可以通过调整获得更好的效果"],
        "cautions": ["当前结构中存在需要注意的压力或变化", "适合谨慎处理相关事项"],
        "actions": ["先评估具体情况再行动", "调整方法以适应当前结构"],
        "avoid": ["在信息不充分时做重大决定", "因压力而完全停止行动"],
    },
    "neutral": {
        "theme": "平稳推进期",
        "opportunities": ["适合按常规节奏推进事项", "可以为下一阶段做准备"],
        "cautions": ["没有明显的外部推动, 需要主动设定目标"],
        "actions": ["保持稳定的节奏", "逐步为下一阶段做准备"],
        "avoid": ["因缺乏动力而拖延重要事项"],
    },
}


class AssertionGuidanceMapper:
    """Assertion到Guidance的确定性映射器.

    输入: CanonicalAssertion[] 或 AssertionCluster[]
    输出: GuidanceAtom[]

    硬契约:
      - deterministic, 不引入AI自由推理
      - 基于domain + semantic_family + direction的映射规则
      - 不允许从direction偷换成吉凶
      - 所有GuidanceAtom可追溯回source_assertion_ids
    """

    def __init__(self):
        self._templates = MAPPING_TEMPLATES
        self._default_template = DEFAULT_TEMPLATE

    def map_from_assertions(
        self,
        assertions: list[CanonicalAssertion],
        case_id: str,
    ) -> list[GuidanceAtom]:
        """从CanonicalAssertion列表映射为GuidanceAtom列表.

        按domain + semantic_family + direction分组, 每组生成一个GuidanceAtom.
        """
        if not assertions:
            return []

        # 按(domain, semantic_family, direction)分组
        grouped: dict[tuple, list[CanonicalAssertion]] = defaultdict(list)
        for a in assertions:
            # 从semantic推断semantic_family(简化: 用semantic的前缀)
            semantic_family = self._infer_family(a.semantic)
            key = (a.domain, semantic_family, a.direction)
            grouped[key].append(a)

        # 为每组生成GuidanceAtom
        atoms = []
        for (domain, family, direction), group_assertions in grouped.items():
            atom = self._build_atom(
                case_id=case_id,
                domain=domain,
                semantic_family=family,
                direction=direction,
                assertions=group_assertions,
            )
            if atom:
                atoms.append(atom)

        # 验证契约
        errors = validate_guidance_contract(atoms)
        if errors:
            for e in errors:
                log.error("Guidance contract violation: %s", e)

        log.info(
            "AssertionGuidanceMapper: %d assertions -> %d guidance atoms",
            len(assertions), len(atoms),
        )
        return atoms

    def map_from_clusters(
        self,
        clusters: list[AssertionCluster],
        case_id: str,
    ) -> list[GuidanceAtom]:
        """从AssertionCluster列表映射为GuidanceAtom列表.

        每个cluster生成一个GuidanceAtom, direction取cluster中最多的direction.
        """
        if not clusters:
            return []

        atoms = []
        for cluster in clusters:
            # 取cluster中最多的direction
            from collections import Counter
            direction_counts = Counter(a.direction for a in cluster.assertions)
            dominant_direction = direction_counts.most_common(1)[0][0] if direction_counts else "neutral"

            atom = self._build_atom(
                case_id=case_id,
                domain=cluster.domain,
                semantic_family=cluster.semantic_family,
                direction=dominant_direction,
                assertions=cluster.assertions,
                cluster=cluster,
            )
            if atom:
                atoms.append(atom)

        # 验证契约
        errors = validate_guidance_contract(atoms)
        if errors:
            for e in errors:
                log.error("Guidance contract violation: %s", e)

        log.info(
            "AssertionGuidanceMapper: %d clusters -> %d guidance atoms",
            len(clusters), len(atoms),
        )
        return atoms

    def _infer_family(self, semantic: str) -> str:
        """从semantic推断semantic_family."""
        # 简单的前缀匹配
        family_map = {
            "OUTPUT": "OUTPUT_EXPRESSION",
            "EXPRESSION": "OUTPUT_EXPRESSION",
            "CREATIVITY": "OUTPUT_EXPRESSION",
            "VISIBILITY": "OUTPUT_EXPRESSION",
            "AUTONOMY": "OUTPUT_EXPRESSION",
            "RESOURCE": "RESOURCE_WEALTH",
            "WEALTH": "RESOURCE_WEALTH",
            "ASSET": "RESOURCE_WEALTH",
            "ABUNDANCE": "RESOURCE_WEALTH",
            "STABILITY": "STABILITY_SUPPORT",
            "SUPPORT": "STABILITY_SUPPORT",
            "ENDURANCE": "STABILITY_SUPPORT",
            "CONSTRAINT": "CONSTRAINT_RULE",
            "DISCIPLINE": "CONSTRAINT_RULE",
            "RULE": "CONSTRAINT_RULE",
            "RESPONSIBILITY": "CONSTRAINT_RULE",
            "CHANGE": "CHANGE_TRANSFORMATION",
            "TRANSFORMATION": "CHANGE_TRANSFORMATION",
            "VOLATILITY": "CHANGE_TRANSFORMATION",
            "DISRUPTION": "CHANGE_TRANSFORMATION",
            "REFLECTION": "REFLECTION_GROWTH",
            "AWARENESS": "REFLECTION_GROWTH",
            "INSIGHT": "REFLECTION_GROWTH",
            "CONTEMPLATION": "REFLECTION_GROWTH",
            "INITIATIVE": "REFLECTION_GROWTH",
            "RELATION": "RELATION_CONNECTION",
            "SOCIAL": "RELATION_CONNECTION",
            "CONNECTION": "RELATION_CONNECTION",
            "PARTNERSHIP": "RELATION_CONNECTION",
            "HARMONY": "RELATION_CONNECTION",
            "ATTRACT": "RELATION_CONNECTION",
            "TENSION": "RELATION_CONNECTION",
            "CONFLICT": "RELATION_CONNECTION",
            "ACTION": "ACTION_EXECUTION",
            "EXECUTION": "ACTION_EXECUTION",
            "MOVEMENT": "ACTION_EXECUTION",
            "HEALTH": "HEALTH_CAUTION",
            "CAUTION": "HEALTH_CAUTION",
            "PREVENTION": "HEALTH_CAUTION",
            "VULNERABILITY": "HEALTH_CAUTION",
        }

        for prefix, family in family_map.items():
            if semantic.startswith(prefix) or prefix in semantic:
                return family

        return "REFLECTION_GROWTH"  # 默认

    def _build_atom(
        self,
        case_id: str,
        domain: str,
        semantic_family: str,
        direction: str,
        assertions: list[CanonicalAssertion],
        cluster: Optional[AssertionCluster] = None,
    ) -> Optional[GuidanceAtom]:
        """构建一个GuidanceAtom."""
        # 查找模板
        template = self._templates.get(semantic_family, self._default_template)
        direction_template = template.get(direction, template.get("neutral", {}))

        if not direction_template:
            return None

        # 收集来源信息
        source_assertion_ids = [a.assertion_id for a in assertions]
        source_engines = list(set(
            eng for a in assertions for eng in a.source_engines
        ))
        source_clusters = [cluster.cluster_id] if cluster else []

        # intensity取平均值
        avg_intensity = sum(a.intensity for a in assertions) / len(assertions) if assertions else 50

        # temporal_scope取第一个
        temporal_scope = assertions[0].temporal_scope if assertions else "birth"

        theme = direction_template.get("theme", "平稳期")

        return GuidanceAtom(
            guidance_id=make_guidance_id(case_id, domain, theme),
            case_id=case_id,
            domain=domain,
            theme=theme,
            direction_label=DIRECTION_LABELS.get(direction, "无明显方向性偏移"),
            direction_description=DIRECTION_DESCRIPTIONS.get(direction, ""),
            opportunities=direction_template.get("opportunities", []),
            cautions=direction_template.get("cautions", []),
            actions=direction_template.get("actions", []),
            avoid=direction_template.get("avoid", []),
            source_assertion_ids=source_assertion_ids,
            source_engines=source_engines,
            source_clusters=source_clusters,
            temporal_scope=temporal_scope,
            intensity=int(avg_intensity),
            status="P5_MAPPED",
        )

    def get_stats(self, atoms: list[GuidanceAtom]) -> dict:
        """统计GuidanceAtom信息."""
        from collections import Counter
        by_domain = Counter(a.domain for a in atoms)
        by_direction = Counter(a.direction_label for a in atoms)
        by_theme = Counter(a.theme for a in atoms)
        by_engine_coverage = Counter()
        for a in atoms:
            for eng in a.source_engines:
                by_engine_coverage[eng] += 1

        return {
            "total": len(atoms),
            "by_domain": dict(by_domain),
            "by_direction_label": dict(by_direction),
            "by_theme": dict(by_theme),
            "engine_coverage": dict(by_engine_coverage),
            "avg_intensity": sum(a.intensity for a in atoms) / len(atoms) if atoms else 0,
        }
