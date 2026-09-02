"""Shuntian Ziwei Dependency Adapter.

This module provides a compatibility layer for iztro 2.6.0 decadal direction bug.

BUG DESCRIPTION:
    iztro 2.6.0 palace.js:163 computes decadal direction using:
        GENDER[gender] === earthlyBranch.yinYang ? forward : reverse
    
    Traditional rule (《紫微斗数全书》):
        阳男阴女顺，阴男阳女逆
        (based on heavenly stem yinYang + gender)

ADAPTER PURPOSE:
    Isolate the discrepancy without modifying:
    - ziwei_engine.py (wrapper, should remain thin)
    - node_modules/iztro (upstream dependency)
    - Other calculation logic

ARCHITECTURE:
    iztro raw output
        ↓
    ShuntianZiweiDependencyAdapter
        ↓
    Canonical decadal direction (传统规则)
        ↓
    Signal Layer

UPSTREAM ISSUE:
    See docs/audit/upstream-issue-template.md
"""

from __future__ import annotations
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Literal

logger = logging.getLogger(__name__)


# ============================================================================
# CONSTANTS
# ============================================================================

class Direction(Enum):
    """Decadal direction enum."""
    FORWARD = "forward"  # 顺
    REVERSE = "reverse"  # 逆


# Heavenly stems with yin/yang classification
# 阳干: 甲丙戊庚壬 (positions 0,2,4,6,8)
# 阴干: 乙丁己辛癸 (positions 1,3,5,7,9)
STEMS = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
YANG_STEMS = {'甲', '丙', '戊', '庚', '壬'}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass(frozen=True)
class DecadalDirectionResult:
    """Result of decadal direction computation."""
    
    # Input
    year: int
    gender: Literal['male', 'female']
    year_stem: str
    year_branch: str
    
    # iztro raw output (the bug)
    iztro_direction: Direction
    
    # Independent expected (traditional rule)
    expected_direction: Direction
    
    # Adapter correction
    corrected_direction: Direction
    
    # Audit trail
    has_discrepancy: bool
    
    @property
    def is_corrected(self) -> bool:
        """True if adapter had to correct the direction."""
        return self.has_discrepancy
    
    def to_dict(self) -> dict:
        """Serialize for audit logging."""
        return {
            'year': self.year,
            'gender': self.gender,
            'year_stem': self.year_stem,
            'year_branch': self.year_branch,
            'iztro_direction': self.iztro_direction.value,
            'expected_direction': self.expected_direction.value,
            'corrected_direction': self.corrected_direction.value,
            'has_discrepancy': self.has_discrepancy,
        }


# ============================================================================
# INDEPENDENT ORACLE
# ============================================================================

def compute_expected_direction(year: int, gender: Literal['male', 'female']) -> Direction:
    """Compute expected decadal direction from traditional rules.
    
    Rule: 阳男阴女顺，阴男阳女逆
    Based on year stem yin/yang + gender.
    
    Args:
        year: Birth year (solar or lunar, doesn't matter for stem calculation)
        gender: 'male' or 'female'
    
    Returns:
        Direction.FORWARD or Direction.REVERSE
    """
    # Calculate year stem (4 AD = 甲子, index 0)
    stem_idx = (year - 4) % 10
    stem = STEMS[stem_idx]
    
    # Determine yin/yang from stem
    stem_yinyang = 'yang' if stem in YANG_STEMS else 'yin'
    
    # Apply traditional rule
    if stem_yinyang == 'yang' and gender == 'male':
        return Direction.FORWARD
    elif stem_yinyang == 'yang' and gender == 'female':
        return Direction.REVERSE
    elif stem_yinyang == 'yin' and gender == 'male':
        return Direction.REVERSE
    else:  # yin + female
        return Direction.FORWARD


def get_year_stem_branch(year: int) -> tuple[str, str]:
    """Get year stem and branch from year number.
    
    Args:
        year: Solar year
    
    Returns:
        (stem, branch) tuple
    """
    stem_idx = (year - 4) % 10
    branch_idx = (year - 4) % 12
    
    branches = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
    
    return STEMS[stem_idx], branches[branch_idx]


# ============================================================================
# ADAPTER CLASS
# ============================================================================

class ShuntianZiweiDependencyAdapter:
    """Adapter for iztro 2.6.0 decadal direction discrepancy.
    
    This adapter:
    1. Accepts raw iztro output
    2. Compares with independent oracle
    3. Returns corrected direction when needed
    4. Maintains audit trail for verification
    """
    
    # Metadata for audit
    DEPENDENCY = 'iztro'
    VERSION = '2.6.0'
    KNOWN_DISCREPANCY = 'decadal_direction'
    POLICY = 'SHUNTIAN_TRADITIONAL'
    
    def __init__(self, enable_audit: bool = True):
        """Initialize adapter.
        
        Args:
            enable_audit: If True, log discrepancy events
        """
        self.enable_audit = enable_audit
    
    def adapt(
        self,
        year: int,
        gender: Literal['male', 'female'],
        iztro_direction: Direction,
    ) -> DecadalDirectionResult:
        """Apply correction to iztro decadal direction.
        
        Args:
            year: Birth year
            gender: 'male' or 'female'
            iztro_direction: Raw direction from iztro
        
        Returns:
            DecadalDirectionResult with audit trail
        """
        # Compute independent expected
        expected = compute_expected_direction(year, gender)
        
        # Get stem/branch for audit
        stem, branch = get_year_stem_branch(year)
        
        # Check for discrepancy
        has_discrepancy = (iztro_direction != expected)
        
        # Apply correction if needed
        corrected = expected if has_discrepancy else iztro_direction
        
        # Log if needed
        if self.enable_audit and has_discrepancy:
            logger.warning(
                f"[ZiweiAdapter] Decadal direction discrepancy detected: "
                f"year={year}, gender={gender}, stem={stem}, "
                f"iztro={iztro_direction.value}, expected={expected.value}"
            )
        
        return DecadalDirectionResult(
            year=year,
            gender=gender,
            year_stem=stem,
            year_branch=branch,
            iztro_direction=iztro_direction,
            expected_direction=expected,
            corrected_direction=corrected,
            has_discrepancy=has_discrepancy,
        )
    
    def adapt_from_chart(
        self,
        full_chart: dict,
    ) -> dict:
        """Adapt full chart output, correcting decadal directions.
        
        Args:
            full_chart: Raw output from ZiweiEngine.full_chart()
        
        Returns:
            Adapted chart with corrected decadal directions
        """
        # Extract year from lunar_date (first element)
        # Note: This assumes the chart data includes lunar_date
        # In practice, caller should pass year separately
        
        # For now, return as-is (caller handles adaptation)
        return full_chart
    
    def get_metadata(self) -> dict:
        """Return adapter metadata for audit."""
        return {
            'dependency': self.DEPENDENCY,
            'version': self.VERSION,
            'known_discrepancy': self.KNOWN_DISCREPANCY,
            'policy': self.POLICY,
            'description': 'Isolates iztro 2.6.0 decadal direction bug',
        }


# ============================================================================
# MODULE-LEVEL HELPERS
# ============================================================================

# Singleton adapter instance
_adapter: ShuntianZiweiDependencyAdapter | None = None


def get_adapter() -> ShuntianZiweiDependencyAdapter:
    """Get singleton adapter instance."""
    global _adapter
    if _adapter is None:
        _adapter = ShuntianZiweiDependencyAdapter()
    return _adapter


def adapt_decadal_direction(
    year: int,
    gender: Literal['male', 'female'],
    iztro_direction: Direction,
) -> DecadalDirectionResult:
    """Convenience function to adapt decadal direction.
    
    Args:
        year: Birth year
        gender: 'male' or 'female'
        iztro_direction: Raw direction from iztro
    
    Returns:
        DecadalDirectionResult with audit trail
    """
    return get_adapter().adapt(year, gender, iztro_direction)


# ============================================================================
# TEST CASES (for verification)
# ============================================================================

CANONICAL_CASES = [
    # (name, year, gender, expected_direction)
    ('阳男甲辰', 2024, 'male', Direction.FORWARD),
    ('阳女甲辰', 2024, 'female', Direction.REVERSE),
    ('阴男乙巳', 2025, 'male', Direction.REVERSE),
    ('阴女乙巳', 2025, 'female', Direction.FORWARD),
]


def verify_canonical_cases() -> list[dict]:
    """Verify adapter against canonical test cases.
    
    Returns:
        List of test result dicts
    """
    results = []
    
    for name, year, gender, expected in CANONICAL_CASES:
        # Simulate iztro output (always opposite for demonstration)
        # In reality, this would come from actual iztro call
        stem = get_year_stem_branch(year)[0]
        stem_yinyang = 'yang' if stem in YANG_STEMS else 'yin'
        
        # iztro would output opposite
        if (stem_yinyang == 'yang' and gender == 'male') or \
           (stem_yinyang == 'yin' and gender == 'female'):
            iztro_dir = Direction.REVERSE  # wrong
        else:
            iztro_dir = Direction.FORWARD  # wrong
        
        # Apply adapter
        result = adapt_decadal_direction(year, gender, iztro_dir)
        
        results.append({
            'name': name,
            'year': year,
            'gender': gender,
            'iztro_direction': iztro_dir.value,
            'expected_direction': expected.value,
            'corrected_direction': result.corrected_direction.value,
            'match': result.corrected_direction == expected,
        })
    
    return results
