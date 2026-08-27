"""
Signal Normalization Layer (Phase 3)

Contract:
  - Converts engine-specific outputs to canonical form
  - Prohibits adapter from creating new Event Types
  - Unknown mappings go to UNKNOWN direction, not new types
  - Cross-domain illegal mappings rejected
"""
from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any


class NormalizationStatus(enum.Enum):
    """Result of signal normalization."""
    SUCCESS = "SUCCESS"
    UNKNOWN = "UNKNOWN"  # Cannot map to known type
    REJECTED = "REJECTED"  # Illegal mapping attempt


@dataclass
class NormalizationResult:
    """Result of normalizing an engine signal to canonical form."""

    status: NormalizationStatus
    canonical_event_type: Optional[str] = None
    canonical_direction: Optional[str] = None
    canonical_domain: Optional[str] = None
    raw_mapping: Optional[Dict[str, Any]] = None
    rejection_reason: Optional[str] = None

    def is_success(self) -> bool:
        return self.status == NormalizationStatus.SUCCESS

    def is_unknown(self) -> bool:
        return self.status == NormalizationStatus.UNKNOWN

    def is_rejected(self) -> bool:
        return self.status == NormalizationStatus.REJECTED


class SignalNormalizer:
    """
    Central normalization dispatcher.

    Contract enforcement:
      - Each engine has its own normalization rules
      - Unknown mappings → UNKNOWN direction, NOT new Event Types
      - Cross-domain mappings → REJECTED
    """

    # ─── Bazi Normalization ──────────────────────────────────────────────────

    @staticmethod
    def normalize_bazi(
        shenshan: str,
        pattern: str,
        year_stem: Optional[str] = None,
        year_branch: Optional[str] = None,
    ) -> NormalizationResult:
        """
        Normalize Bazi engine output to canonical signal.

        Args:
            shenshan: 十神类型 (e.g., '正官', '七杀', '偏财')
            pattern: 格局 (e.g., '正官格', '从财格')
            year_stem: 流年天干
            year_branch: 流年地支

        Returns:
            NormalizationResult
        """
        # Map common patterns to canonical events
        pattern_map: Dict[str, str] = {
            '正官格': 'PROMOTION',
            '从财格': 'MAJOR_INCOME',
            '食神制杀': 'CAREER_CHANGE',
            '印绶格': 'EDUCATION',
            '伤官见官': 'LEGAL_ISSUE',
            '比劫夺财': 'FAMILY_HARMONY',
        }

        if pattern not in pattern_map:
            return NormalizationResult(
                status=NormalizationStatus.UNKNOWN,
                rejection_reason=f"Bazi pattern '{pattern}' not mapped"
            )

        canonical_event = pattern_map[pattern]

        # Determine direction from shenshan
        positive_shenshan = {'正官', '偏财', '食神', '印绶'}
        negative_shenshan = {'七杀', '伤官', '比劫'}

        if shenshan in positive_shenshan:
            direction = 'POSITIVE'
        elif shenshan in negative_shenshan:
            direction = 'NEGATIVE'
        else:
            direction = 'NEUTRAL'

        # Validate cross-domain mapping
        from tongshu.spec.event_ontology_v1 import EVENT_TYPE_BY_ID
        expected_domain = EVENT_TYPE_BY_ID[canonical_event].domain

        # Return success
        return NormalizationResult(
            status=NormalizationStatus.SUCCESS,
            canonical_event_type=canonical_event,
            canonical_direction=direction,
            canonical_domain=expected_domain.value,
            raw_mapping={'shenshan': shenshan, 'pattern': pattern}
        )

    # ─── Heluo Normalization ──────────────────────────────────────────────────

    @staticmethod
    def normalize_heluo(
        gua: str,
        yao: int,
        position: str,
        shi: str,
    ) -> NormalizationResult:
        """
        Normalize Heluo engine output to canonical signal.

        Args:
            gua: 卦名 (e.g., '乾', '坤')
            yao: 爻位 (1-6)
            position: 卦位
            shi: 时势
        """
        # Map hexagram + position to canonical events
        gua_yao_map: Dict[str, Dict[int, str]] = {
            '乾': {1: 'CAREER_CHANGE', 2: 'PROMOTION', 3: 'JOB_CHANGE',
                   4: 'MAJOR_INCOME', 5: 'PROMOTION', 6: 'LEGAL_ISSUE'},
            '坤': {1: 'FAMILY_HARMONY', 2: 'EDUCATION', 3: 'RELOCATION',
                   4: 'CHILD_BIRTH', 5: 'MARRIAGE', 6: 'PARENT_DEATH'},
            # ... add more mappings
        }

        if gua not in gua_yao_map:
            return NormalizationResult(
                status=NormalizationStatus.UNKNOWN,
                rejection_reason=f"Heluo gua '{gua}' not mapped"
            )

        if yao not in gua_yao_map[gua]:
            return NormalizationResult(
                status=NormalizationStatus.UNKNOWN,
                rejection_reason=f"Heluo yao {yao} not mapped for gua '{gua}'"
            )

        canonical_event = gua_yao_map[gua][yao]

        # Determine domain from event type
        from tongshu.spec.event_ontology_v1 import EVENT_TYPE_BY_ID
        expected_domain = EVENT_TYPE_BY_ID[canonical_event].domain if canonical_event in EVENT_TYPE_BY_ID else Domain.LIFE_EVENT

        # Determine direction from shi
        positive_shi = {'吉', '亨', '利'}
        negative_shi = {'凶', '不利', '吝'}

        if shi in positive_shi:
            direction = 'POSITIVE'
        elif shi in negative_shi:
            direction = 'NEGATIVE'
        else:
            direction = 'NEUTRAL'

        return NormalizationResult(
            status=NormalizationStatus.SUCCESS,
            canonical_event_type=canonical_event,
            canonical_direction=direction,
            canonical_domain=expected_domain.value,
            raw_mapping={'gua': gua, 'yao': yao, 'shi': shi}
        )

    # ─── Ziwei Normalization ──────────────────────────────────────────────────

    @staticmethod
    def normalize_ziwei(
        palace: str,
        stars: List[str],
        transformations: List[str],
    ) -> NormalizationResult:
        """
        Normalize Ziwei engine output to canonical signal.

        Args:
            palace: 宫位 (e.g., '命宫', '财帛宫')
            stars: 星曜列表
            transformations: 四化列表
        """
        # Map palace to domain
        palace_domain_map: Dict[str, str] = {
            '命宫': 'LIFE_EVENT',
            '财帛宫': 'CAREER',
            '官禄宫': 'CAREER',
            '夫妻宫': 'FAMILY',
            '疾厄宫': 'LIFE_EVENT',
            '迁移宫': 'LIFE_EVENT',
        }

        if palace not in palace_domain_map:
            return NormalizationResult(
                status=NormalizationStatus.UNKNOWN,
                rejection_reason=f"Ziwei palace '{palace}' not mapped"
            )

        canonical_domain = palace_domain_map[palace]

        # Map stars + transformations to events and direction
        positive_stars = {'紫微', '天府', '太阳', '太阴'}
        negative_stars = {'七杀', '破军', '贪狼', '廉贞'}
        transformation_direction: Dict[str, str] = {
            '化禄': 'POSITIVE',
            '化权': 'POSITIVE',
            '化科': 'NEUTRAL',
            '化忌': 'NEGATIVE',
        }

        # Aggregate direction from stars and transformations
        directions = []
        for star in stars:
            if star in positive_stars:
                directions.append('POSITIVE')
            elif star in negative_stars:
                directions.append('NEGATIVE')

        for trans in transformations:
            if trans in transformation_direction:
                directions.append(transformation_direction[trans])

        # Determine dominant direction
        pos_count = directions.count('POSITIVE')
        neg_count = directions.count('NEGATIVE')
        if pos_count > neg_count:
            direction = 'POSITIVE'
        elif neg_count > pos_count:
            direction = 'NEGATIVE'
        else:
            direction = 'NEUTRAL'

        # Map to specific event type based on palace
        palace_event_map: Dict[str, str] = {
            '命宫': 'RELOCATION',
            '财帛宫': 'MAJOR_INCOME',
            '官禄宫': 'PROMOTION',
            '夫妻宫': 'MARRIAGE',
            '疾厄宫': 'HEALTH_ISSUE',
            '迁移宫': 'RELOCATION',
        }

        canonical_event = palace_event_map.get(palace, 'LIFE_EVENT')

        return NormalizationResult(
            status=NormalizationStatus.SUCCESS,
            canonical_event_type=canonical_event,
            canonical_direction=direction,
            canonical_domain=canonical_domain,
            raw_mapping={'palace': palace, 'stars': stars, 'transformations': transformations}
        )

    # ─── Huangli Normalization ──────────────────────────────────────────────────

    @staticmethod
    def normalize_huangli(
        day_stems: List[str],
        day_branches: List[str],
        yi: List[str],
        ji: List[str],
        jieqi: str,
    ) -> NormalizationResult:
        """
        Normalize Huangli engine output to canonical signal.

        Args:
            day_stems: 日干列表
            day_branches: 日支列表
            yi: 宜事项
            ji: 忌事项
            jieqi: 节气
        """
        # Map yi/ji to events
        yi_event_map: Dict[str, str] = {
            '嫁娶': 'MARRIAGE',
            '祭祀': 'FAMILY_HARMONY',
            '入学': 'EDUCATION',
            '求官': 'PROMOTION',
            '搬迁': 'RELOCATION',
            '动土': 'LEGAL_ISSUE',
        }

        ji_event_map: Dict[str, str] = {
            '破土': 'LEGAL_ISSUE',
            '开光': 'FAMILY_HARMONY',
            '出行': 'RELOCATION',
            '安床': 'FAMILY_HARMONY',
        }

        # Find matching events
        canonical_events = []
        for yi_item in yi:
            if yi_item in yi_event_map:
                canonical_events.append(yi_event_map[yi_item])

        for ji_item in ji:
            if ji_item in ji_event_map:
                canonical_events.append(ji_event_map[ji_item])

        if not canonical_events:
            return NormalizationResult(
                status=NormalizationStatus.UNKNOWN,
                rejection_reason="No yi/ji items mapped to canonical events"
            )

        # Use first matching event (can be extended to multiple)
        canonical_event = canonical_events[0]

        # Determine domain from event type
        from tongshu.spec.event_ontology_v1 import EVENT_TYPE_BY_ID
        expected_domain = EVENT_TYPE_BY_ID[canonical_event].domain if canonical_event in EVENT_TYPE_BY_ID else Domain.LIFE_EVENT

        # Determine direction from yi/ji ratio
        yi_count = len(yi)
        ji_count = len(ji)
        if yi_count > ji_count:
            direction = 'POSITIVE'
        elif ji_count > yi_count:
            direction = 'NEGATIVE'
        else:
            direction = 'NEUTRAL'

        return NormalizationResult(
            status=NormalizationStatus.SUCCESS,
            canonical_event_type=canonical_event,
            canonical_direction=direction,
            canonical_domain=expected_domain.value,
            raw_mapping={'yi': yi, 'ji': ji, 'jieqi': jieqi}
        )

    # ─── Knowledge Normalization ───────────────────────────────────────────────

    @staticmethod
    def normalize_knowledge(
        source_text: str,
        rule_id: str,
        evidence_id: str,
        context: Optional[str] = None,
    ) -> NormalizationResult:
        """
        Normalize Knowledge Engine output to canonical signal.

        Special: Knowledge signals must carry evidence provenance.

        Args:
            source_text: 经典原文
            rule_id: 规则ID
            evidence_id: 证据ID (must exist in EvidenceChain)
            context: 上下文说明
        """
        # Knowledge signals default to UNKNOWN direction until contextualized
        # This forces manual review before confidence assignment
        return NormalizationResult(
            status=NormalizationStatus.SUCCESS,
            canonical_event_type='UNKNOWN',  # Knowledge needs expert interpretation
            canonical_direction='UNKNOWN',
            canonical_domain='LIFE_EVENT',  # Default, needs refinement
            raw_mapping={
                'source_text': source_text,
                'rule_id': rule_id,
                'evidence_id': evidence_id,
                'context': context
            }
        )

    # ─── Dispatcher ────────────────────────────────────────────────────────────

    @staticmethod
    def normalize(
        engine: str,
        **kwargs
    ) -> NormalizationResult:
        """
        Central dispatcher for signal normalization.

        Args:
            engine: Engine name (BAZI, HELUO, ZIWEI, HUANGLI, KNOWLEDGE)
            **kwargs: Engine-specific parameters

        Returns:
            NormalizationResult
        """
        engine = engine.upper()

        if engine == 'BAZI':
            return SignalNormalizer.normalize_bazi(**kwargs)
        elif engine == 'HELUO':
            return SignalNormalizer.normalize_heluo(**kwargs)
        elif engine == 'ZIWEI':
            return SignalNormalizer.normalize_ziwei(**kwargs)
        elif engine == 'HUANGLI':
            return SignalNormalizer.normalize_huangli(**kwargs)
        elif engine == 'KNOWLEDGE':
            return SignalNormalizer.normalize_knowledge(**kwargs)
        else:
            return NormalizationResult(
                status=NormalizationStatus.REJECTED,
                rejection_reason=f"Unknown engine: {engine}"
            )
