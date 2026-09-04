"""
P2.5 Property/Invariant Tests for Bazi Engine

验证计算规则的数学性质，确保计算层正确性。
"""

import pytest
from src.tongshu.engines.bazi_engine import (
    BRANCH_CLASH,
    BRANCH_HARM,
    BRANCH_HE,
    BRANCH_SANHE,
    BRANCH_SANXING,
    PEACH_BLOSSOM_DIRECT,
    EARTHLY_BRANCHES,
    HEAVENLY_STEMS,
    STEM_ELEMENT,
    STEM_POLARITY,
)


class TestSymmetry:
    """测试关系的对称性"""

    def test_clash_symmetry(self):
        """六冲关系必须对称"""
        for a, b in BRANCH_CLASH.items():
            assert BRANCH_CLASH[b] == a, f"Clash not symmetric: {a}-{b}"

    def test_harm_symmetry(self):
        """六害关系必须对称"""
        for a, b in BRANCH_HARM.items():
            assert BRANCH_HARM[b] == a, f"Harm not symmetric: {a}-{b}"

    def test_he_symmetry(self):
        """六合关系通过对称的frozenset定义"""
        for pair in BRANCH_HE.keys():
            assert len(pair) == 2, f"He pair should have 2 elements: {pair}"


class TestNoSelfRelation:
    """测试不存在自关系"""

    def test_no_self_clash(self):
        """地支不能与自己冲"""
        for b in EARTHLY_BRANCHES:
            assert BRANCH_CLASH.get(b) != b, f"Self-clash detected: {b}"

    def test_no_self_harm(self):
        """地支不能与自己害"""
        for b in EARTHLY_BRANCHES:
            assert BRANCH_HARM.get(b) != b, f"Self-harm detected: {b}"


class TestCompleteness:
    """测试关系覆盖的完备性"""

    def test_all_branches_in_clash(self):
        """所有地支都必须出现在六冲关系中"""
        covered = set()
        for a, b in BRANCH_CLASH.items():
            covered.add(a)
            covered.add(b)
        assert covered == set(EARTHLY_BRANCHES), \
            f"Missing branches in clash: {set(EARTHLY_BRANCHES) - covered}"

    def test_all_branches_in_harm(self):
        """所有地支都必须出现在六害关系中"""
        covered = set()
        for a, b in BRANCH_HARM.items():
            covered.add(a)
            covered.add(b)
        assert covered == set(EARTHLY_BRANCHES), \
            f"Missing branches in harm: {set(EARTHLY_BRANCHES) - covered}"

    def test_all_branches_in_he(self):
        """所有地支都必须出现在六合关系中"""
        covered = set()
        for pair in BRANCH_HE.keys():
            covered.update(pair)
        assert covered == set(EARTHLY_BRANCHES), \
            f"Missing branches in he: {set(EARTHLY_BRANCHES) - covered}"


class TestElementConsistency:
    """测试五行映射的一致性"""

    def test_all_stems_have_element(self):
        """所有天干都必须有五行属性"""
        for stem in HEAVENLY_STEMS:
            assert stem in STEM_ELEMENT, f"Missing element for stem: {stem}"

    def test_all_branches_have_element(self):
        """所有地支都必须有五行属性"""
        for branch in EARTHLY_BRANCHES:
            el = _branch_element(branch)
            assert el in ("WOOD", "FIRE", "EARTH", "METAL", "WATER"), \
                f"Invalid element for {branch}: {el}"

    def test_element_consistency(self):
        """同一五行的天干数量必须一致"""
        element_counts = {}
        for stem, el in STEM_ELEMENT.items():
            element_counts[el] = element_counts.get(el, 0) + 1
        # 每行应有2个天干
        for el, count in element_counts.items():
            assert count == 2, f"Element {el} has {count} stems, expected 2"


class TestPolarityConsistency:
    """测试阴阳属性的一致性"""

    def test_all_stems_have_polarity(self):
        """所有天干都必须有阴阳属性"""
        for stem in HEAVENLY_STEMS:
            assert stem in STEM_POLARITY, f"Missing polarity for stem: {stem}"

    def test_polarity_alternates(self):
        """阴阳必须交替出现"""
        polarities = [STEM_POLARITY[s] for s in HEAVENLY_STEMS]
        for i in range(len(polarities) - 1):
            assert polarities[i] != polarities[i + 1], \
                f"Polarity not alternating at {i}: {polarities[i]} -> {polarities[i+1]}"


class TestPeachBlossom:
    """测试桃花定义"""

    def test_peach_blossom_direct(self):
        """桃花直接定义应为子午卯酉"""
        assert PEACH_BLOSSOM_DIRECT == {"ZI", "WU", "MAO", "YOU"}

    def test_peach_blossom_count(self):
        """桃花地支数量应为4"""
        assert len(PEACH_BLOSSOM_DIRECT) == 4


class TestBranchElementMapping:
    """测试地支五行映射"""

    def test_wood_branches(self):
        """木支应为寅卯"""
        wood_branches = [b for b in EARTHLY_BRANCHES if _branch_element(b) == "WOOD"]
        assert set(wood_branches) == {"YIN", "MAO"}

    def test_fire_branches(self):
        """火支应为巳午"""
        fire_branches = [b for b in EARTHLY_BRANCHES if _branch_element(b) == "FIRE"]
        assert set(fire_branches) == {"SI", "WU"}

    def test_earth_branches(self):
        """土支应为辰戌丑未"""
        earth_branches = [b for b in EARTHLY_BRANCHES if _branch_element(b) == "EARTH"]
        assert set(earth_branches) == {"CHEN", "XU", "CHOU", "WEI"}

    def test_metal_branches(self):
        """金支应为申酉"""
        metal_branches = [b for b in EARTHLY_BRANCHES if _branch_element(b) == "METAL"]
        assert set(metal_branches) == {"SHEN", "YOU"}

    def test_water_branches(self):
        """水支应为子亥"""
        water_branches = [b for b in EARTHLY_BRANCHES if _branch_element(b) == "WATER"]
        assert set(water_branches) == {"ZI", "HAI"}


def _branch_element(b: str) -> str:
    """辅助函数：获取地支五行"""
    if b in ("YIN", "MAO"):
        return "WOOD"
    if b in ("SI", "WU"):
        return "FIRE"
    if b in ("CHEN", "XU", "CHOU", "WEI"):
        return "EARTH"
    if b in ("SHEN", "YOU"):
        return "METAL"
    return "WATER"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
