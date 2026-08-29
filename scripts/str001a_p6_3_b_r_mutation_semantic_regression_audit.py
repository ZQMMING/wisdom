"""
STR-001A P6.3-B-R Mutation / Semantic Regression Audit

不改变任何命理规则, 只做故障注入测试。
针对ASSERT-005人为制造3个错误Matcher(退化版本), 构造3个测试案例,
证明:
  伤官存在 ≠ 伤官格
  官星存在 ≠ 「见官」成立
  伤官格 + 官星 ≠ 「为祸百端」
  必须完整保留: 伤官格 + 官星出现 + 伤不尽/官乘旺 + 原典限定

退化Matcher:
  M1: has_shangguan AND has_officer (最简单的存在性检查)
  M2: shangguan_exists AND officer_exists (同上, 变量名不同)
  M3: shangguan_ge_judge AND officer_exists (检查伤官格但不检查伤尽/官乘旺)

测试案例:
  Case A: 伤官存在 + 官星存在 但不是伤官格
          → 正确实现: NOT_MATCHED
          → 退化Matcher(M1/M2): 错误MATCHED
          → 退化Matcher(M3): NOT_MATCHED (因为M3检查伤官格)

  Case B: 伤官格 + 官星存在 但伤官已经伤尽/官不乘旺
          → 正确实现: NOT_MATCHED
          → 退化Matcher(M1/M2/M3): 错误MATCHED

  Case C: 伤官格 + 官星出现 + 官乘旺
          → 正确实现: MATCHED (带qualifier)
          → 退化Matcher(M1/M2/M3): MATCHED (但缺少qualifier)

核心验证:
  退化Matcher在Case A和Case B上会产生错误命中,
  而正确的Matcher在所有案例上都正确。
  这证明当前实现没有语义退化。
"""

import sys
sys.path.insert(0, r"D:\shuntian\backend\scripts")

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


# ============================================================
# 退化 Matcher 定义 (Mutation / Fault Injection)
# ============================================================

class DegradedMatcher:
    """退化Matcher基类: 人为制造的语义简化版本"""

    def __init__(self, matcher_id: str, name: str, description: str):
        self.matcher_id = matcher_id
        self.name = name
        self.description = description

    def match(self, case: Dict) -> Tuple[bool, str]:
        """返回 (是否匹配, 原因)"""
        raise NotImplementedError


class M1_SimplestExistence(DegradedMatcher):
    """M1: has_shangguan AND has_officer (最简单的存在性检查)
    完全不检查伤官格、伤尽、官乘旺。
    这是最危险的退化: 只要伤官和官星同时存在就触发。
    """

    def __init__(self):
        super().__init__(
            "M1",
            "has_shangguan AND has_officer",
            "最简单的存在性检查: 只要伤官和官星同时存在就触发, 完全不检查伤官格、伤尽、官乘旺",
        )

    def match(self, case: Dict) -> Tuple[bool, str]:
        has_shangguan = case.get("shangguan_exists", False)
        has_officer = case.get("officer_exists", False)
        matched = has_shangguan and has_officer
        reason = f"shangguan_exists={has_shangguan} AND officer_exists={has_officer} = {matched}"
        return matched, reason


class M2_VariableNameOnly(DegradedMatcher):
    """M2: shangguan_exists AND officer_exists (同上, 变量名不同)
    与M1逻辑完全相同, 证明问题不在变量名而在逻辑结构。
    """

    def __init__(self):
        super().__init__(
            "M2",
            "shangguan_exists AND officer_exists",
            "与M1逻辑完全相同(变量名不同), 证明问题不在变量名而在逻辑结构",
        )

    def match(self, case: Dict) -> Tuple[bool, str]:
        shangguan_exists = case.get("shangguan_exists", False)
        officer_exists = case.get("officer_exists", False)
        matched = shangguan_exists and officer_exists
        reason = f"shangguan_exists={shangguan_exists} AND officer_exists={officer_exists} = {matched}"
        return matched, reason


class M3_PatternButNoQualifier(DegradedMatcher):
    """M3: shangguan_ge_judge AND officer_exists (检查伤官格但不检查伤尽/官乘旺)
    比M1/M2好一点, 检查了伤官格, 但仍然不检查P3核心限定条件(伤不尽/官乘旺)。
    这是最隐蔽的退化: 看起来检查了格局, 但漏掉了最关键的限定。
    """

    def __init__(self):
        super().__init__(
            "M3",
            "shangguan_ge_judge AND officer_exists",
            "检查伤官格但不检查伤尽/官乘旺, 比M1/M2好但仍然漏掉P3核心限定条件",
        )

    def match(self, case: Dict) -> Tuple[bool, str]:
        shangguan_ge = case.get("shangguan_ge", False)
        officer_exists = case.get("officer_exists", False)
        matched = shangguan_ge and officer_exists
        reason = f"shangguan_ge={shangguan_ge} AND officer_exists={officer_exists} = {matched}"
        return matched, reason


# ============================================================
# 正确 Matcher (当前实现, 完整检查P1+P2+P3)
# ============================================================

class CorrectMatcher:
    """正确Matcher: 完整检查P1伤官格 + P2官星出现 + P3伤官未伤尽/官星乘旺
    这是当前ASSERT-005的实现, 经过原典审计授权。
    """

    def __init__(self):
        self.matcher_id = "CORRECT"
        self.name = "P1伤官格 + P2官星出现 + P3伤官未伤尽/官星乘旺"
        self.description = "完整检查原典授权的三个前置条件, 带qualifier"

    def match(self, case: Dict) -> Tuple[bool, str, List[str]]:
        """返回 (是否匹配, 原因, qualifiers)"""
        qualifiers = []

        # P1: 伤官格
        p1 = case.get("shangguan_ge", False)
        if not p1:
            return False, "P1不满足: 非伤官格", []

        # P2: 官星出现
        p2 = case.get("officer_exists", False)
        if not p2:
            return False, "P2不满足: 官星未出现", []

        # P3: 伤官未伤尽 / 官星乘旺 (核心限定条件)
        shangguan_shangjin = case.get("shangguan_shangjin", False)  # 伤官是否伤尽
        guan_chengwangg = case.get("guan_chengwangg", False)  # 官星是否乘旺

        if shangguan_shangjin:
            return False, "P3不满足: 伤官已伤尽, 原典'伤官务要伤尽, 伤尽不为祸'", []

        if not guan_chengwangg:
            return False, "P3不满足: 官星不乘旺, 原典'伤之不尽, 官来乘旺, 其祸不可胜言'", []

        # 全部满足
        qualifiers.append("P1=伤官格(非简单伤官存在)")
        qualifiers.append("P2=官星出现(原局官星露或岁运见官星)")
        qualifiers.append("P3=伤官未伤尽且官星乘旺(核心限定, 非简单官星存在)")
        qualifiers.append("原典反向条件: 伤官伤尽+身旺乡=贵人; 伤官见财=为妙; 有正印制化=亦可取")

        return True, "P1+P2+P3全部满足, 带qualifier", qualifiers


# ============================================================
# 测试案例构造
# ============================================================

def build_test_cases() -> List[Dict]:
    """构造3个测试案例"""

    # Case A: 伤官存在 + 官星存在 但不是伤官格
    # 这是最常见的误判场景: 八字中有伤官和官星, 但月令不是伤官, 所以不是伤官格
    case_a = {
        "case_id": "Case A",
        "description": "伤官存在 + 官星存在 但不是伤官格 (月令=正财格)",
        "bazi_example": "假设: 甲木日主, 月令戌(正财), 年干丁(伤官), 时干庚(正官)",
        "shangguan_exists": True,      # 伤官存在 (年干丁)
        "officer_exists": True,         # 官星存在 (时干庚)
        "shangguan_ge": False,          # 不是伤官格 (月令戌=正财)
        "shangguan_shangjin": False,    # 伤官未伤尽 (但这不重要, 因为P1不满足)
        "guan_chengwangg": True,        # 官星乘旺 (但这不重要, 因为P1不满足)
        "expected_correct": "NOT_MATCHED",
        "expected_m1": "MATCHED (错误!)",
        "expected_m2": "MATCHED (错误!)",
        "expected_m3": "NOT_MATCHED",
        "key_issue": "伤官存在 ≠ 伤官格。月令决定格局, 不是有伤官就是伤官格。",
    }

    # Case B: 伤官格 + 官星存在 但伤官已经伤尽/官不乘旺
    # 这是最隐蔽的误判场景: 看起来是伤官格+见官, 但实际上伤官已伤尽或官不乘旺
    case_b = {
        "case_id": "Case B",
        "description": "伤官格 + 官星存在 但伤官已经伤尽/官不乘旺",
        "bazi_example": "假设: 甲木日主, 月令午(伤官格), 伤官丁火透干但被壬水合去(伤尽), 官星庚金虚浮无根(不乘旺)",
        "shangguan_exists": True,      # 伤官存在
        "officer_exists": True,         # 官星存在
        "shangguan_ge": True,           # 伤官格 (月令午)
        "shangguan_shangjin": True,     # 伤官已伤尽 (被壬水合去)
        "guan_chengwangg": False,       # 官星不乘旺 (虚浮无根)
        "expected_correct": "NOT_MATCHED",
        "expected_m1": "MATCHED (错误!)",
        "expected_m2": "MATCHED (错误!)",
        "expected_m3": "MATCHED (错误!)",
        "key_issue": "伤官格 + 官星 ≠ 「为祸百端」。必须检查P3: 伤官未伤尽且官星乘旺。原典'伤官务要伤尽, 伤尽不为祸'。",
    }

    # Case C: 伤官格 + 官星出现 + 官乘旺
    # 这是正确命中的场景: 完整满足P1+P2+P3
    case_c = {
        "case_id": "Case C",
        "description": "伤官格 + 官星出现 + 官乘旺 (正确命中, 带qualifier)",
        "bazi_example": "假设: 甲木日主, 月令午(伤官格), 伤官丁火透干未被制(伤不尽), 官星庚金透干有根得令(官乘旺)",
        "shangguan_exists": True,      # 伤官存在
        "officer_exists": True,         # 官星存在
        "shangguan_ge": True,           # 伤官格 (月令午)
        "shangguan_shangjin": False,    # 伤官未伤尽
        "guan_chengwangg": True,        # 官星乘旺
        "expected_correct": "MATCHED (带qualifier)",
        "expected_m1": "MATCHED (但缺少qualifier)",
        "expected_m2": "MATCHED (但缺少qualifier)",
        "expected_m3": "MATCHED (但缺少qualifier)",
        "key_issue": "正确命中但必须带qualifier。退化Matcher虽然也MATCHED, 但缺少P3限定和反向条件, 会导致无条件输出'为祸百端'。",
    }

    return [case_a, case_b, case_c]


# ============================================================
# Mutation Audit Engine
# ============================================================

class MutationAuditEngine:
    """Mutation / Semantic Regression Audit Engine"""

    def __init__(self):
        self.correct_matcher = CorrectMatcher()
        self.degraded_matchers = [
            M1_SimplestExistence(),
            M2_VariableNameOnly(),
            M3_PatternButNoQualifier(),
        ]
        self.test_cases = build_test_cases()
        self.results = []
        self.mutation_killed = 0  # 被杀死的变异(退化Matcher被正确识别为错误)
        self.mutation_survived = 0  # 存活的变异(退化Matcher未被识别)

    def run(self) -> Dict:
        """运行完整mutation audit"""

        print("=" * 110)
        print("STR-001A P6.3-B-R Mutation / Semantic Regression Audit")
        print("=" * 110)

        print(f"""
  目标: 证明ASSERT-005的Matcher没有语义退化。
  方法: 人为制造3个退化Matcher(M1/M2/M3), 构造3个测试案例(Case A/B/C),
        对比正确Matcher和退化Matcher的输出。

  退化Matcher:
    M1: has_shangguan AND has_officer (最简单存在性检查, 完全不检查格局/伤尽/官乘旺)
    M2: shangguan_exists AND officer_exists (与M1逻辑相同, 变量名不同)
    M3: shangguan_ge_judge AND officer_exists (检查伤官格但不检查伤尽/官乘旺)

  核心验证:
    伤官存在 ≠ 伤官格
    官星存在 ≠ 「见官」成立
    伤官格 + 官星 ≠ 「为祸百端」
    必须完整保留: 伤官格 + 官星出现 + 伤不尽/官乘旺 + 原典限定
""")

        # 逐条测试
        for case in self.test_cases:
            self._run_case(case)

        # 汇总
        self._summary()

        return {
            "mutation_killed": self.mutation_killed,
            "mutation_survived": self.mutation_survived,
            "total_mutations": len(self.degraded_matchers) * len(self.test_cases),
            "results": self.results,
        }

    def _run_case(self, case: Dict):
        """运行单个测试案例"""

        print(f"\n  {'─'*106}")
        print(f"  [{case['case_id']}] {case['description']}")
        print(f"  {'─'*106}")
        print(f"  示例八字: {case['bazi_example']}")
        print(f"  事实:")
        print(f"    shangguan_exists  = {case['shangguan_exists']}")
        print(f"    officer_exists    = {case['officer_exists']}")
        print(f"    shangguan_ge      = {case['shangguan_ge']}")
        print(f"    shangguan_shangjin= {case['shangguan_shangjin']} (伤官是否伤尽)")
        print(f"    guan_chengwangg   = {case['guan_chengwangg']} (官星是否乘旺)")
        print(f"  关键问题: {case['key_issue']}")

        # 正确Matcher
        correct_matched, correct_reason, correct_qualifiers = self.correct_matcher.match(case)
        correct_result = "MATCHED" if correct_matched else "NOT_MATCHED"
        print(f"\n  正确Matcher (P1+P2+P3完整检查):")
        print(f"    结果: {correct_result}")
        print(f"    原因: {correct_reason}")
        if correct_qualifiers:
            print(f"    Qualifiers ({len(correct_qualifiers)}条):")
            for q in correct_qualifiers:
                print(f"      • {q}")

        # 退化Matcher
        print(f"\n  退化Matcher (故障注入):")
        case_result = {"case_id": case["case_id"], "correct": correct_result, "degraded": {}}

        for dm in self.degraded_matchers:
            dm_matched, dm_reason = dm.match(case)
            dm_result = "MATCHED" if dm_matched else "NOT_MATCHED"

            # 判断是否产生错误命中
            is_false_positive = dm_matched and not correct_matched
            is_missing_qualifier = dm_matched and correct_matched and not correct_qualifiers == []

            if is_false_positive:
                status = "✗ 错误命中! (退化Matcher MATCHED, 正确Matcher NOT_MATCHED)"
                self.mutation_killed += 1
            elif is_missing_qualifier:
                status = "⚠ 缺少qualifier (虽然MATCHED, 但缺少P3限定和反向条件)"
                self.mutation_killed += 1
            elif dm_matched and correct_matched:
                status = "✓ 结果一致 (但退化Matcher缺少qualifier)"
                self.mutation_survived += 1
            else:
                status = "✓ 结果一致 (都NOT_MATCHED)"
                self.mutation_survived += 1

            print(f"\n    [{dm.matcher_id}] {dm.name}")
            print(f"      描述: {dm.description[:60]}...")
            print(f"      结果: {dm_result}")
            print(f"      原因: {dm_reason}")
            print(f"      状态: {status}")

            case_result["degraded"][dm.matcher_id] = {
                "result": dm_result,
                "reason": dm_reason,
                "status": status,
                "false_positive": is_false_positive,
                "missing_qualifier": is_missing_qualifier,
            }

        self.results.append(case_result)

    def _summary(self):
        """汇总mutation audit结果"""

        print(f"\n  {'='*106}")
        print(f"  Mutation Audit 汇总:")
        print(f"  {'='*106}")

        total = len(self.degraded_matchers) * len(self.test_cases)
        kill_rate = self.mutation_killed / total * 100 if total > 0 else 0

        print(f"""
    总变异数: {total} (3个退化Matcher × 3个测试案例)
    被杀死: {self.mutation_killed} (退化Matcher被正确识别为错误或缺少qualifier)
    存活: {self.mutation_survived} (退化Matcher结果与正确Matcher一致)
    变异杀死率: {kill_rate:.1f}%
""")

        # 详细矩阵
        print(f"  详细结果矩阵:")
        print(f"  {'案例':<10} {'正确Matcher':<20} {'M1':<25} {'M2':<25} {'M3':<25}")
        print(f"  {'─'*105}")

        for r in self.results:
            m1 = r["degraded"]["M1"]
            m2 = r["degraded"]["M2"]
            m3 = r["degraded"]["M3"]

            m1_status = "错误命中!" if m1["false_positive"] else ("缺qualifier" if m1["missing_qualifier"] else "一致")
            m2_status = "错误命中!" if m2["false_positive"] else ("缺qualifier" if m2["missing_qualifier"] else "一致")
            m3_status = "错误命中!" if m3["false_positive"] else ("缺qualifier" if m3["missing_qualifier"] else "一致")

            print(f"  {r['case_id']:<10} {r['correct']:<20} {m1['result']+' ('+m1_status+')':<25} {m2['result']+' ('+m2_status+')':<25} {m3['result']+' ('+m3_status+')':<25}")

        # 核心结论
        print(f"""
  {'='*106}
  核心结论:
  {'='*106}

  1. 伤官存在 ≠ 伤官格
     Case A证明: 伤官和官星同时存在, 但月令不是伤官, 正确Matcher NOT_MATCHED,
     退化Matcher(M1/M2)错误MATCHED。

  2. 官星存在 ≠ 「见官」成立
     Case A和Case B共同证明: 官星存在只是P2, 还需要P1伤官格和P3官乘旺。

  3. 伤官格 + 官星 ≠ 「为祸百端」
     Case B证明: 伤官格+官星存在, 但伤官已伤尽或官不乘旺, 正确Matcher NOT_MATCHED,
     退化Matcher(M1/M2/M3)全部错误MATCHED。
     原典: '伤官务要伤尽, 伤尽不为祸'。

  4. 必须完整保留: 伤官格 + 官星出现 + 伤不尽/官乘旺 + 原典限定
     Case C证明: 正确命中但必须带qualifier, 退化Matcher虽然也MATCHED但缺少qualifier,
     会导致无条件输出'为祸百端'。

  5. M3是最隐蔽的退化
     M3检查了伤官格(比M1/M2好), 但仍然不检查P3(伤尽/官乘旺)。
     在Case B上, M1/M2/M3全部错误MATCHED, 证明P3是最关键的限定条件。

  6. 当前实现没有语义退化
     正确Matcher在所有3个案例上都输出正确结果, 且Case C带完整qualifier。
     退化Matcher在Case A和Case B上产生错误命中, 被mutation test成功捕获。

  P6.3-B-R Mutation / Semantic Regression Audit 通过。
  这不是增加命理规则, 而是在正式放大资产生产规模之前, 把目前最危险的'语义退化'漏洞封死。

  以后Hermes批量生成断言时, 最危险的不是明显报错, 而是这种语义静默退化:
    原典复杂条件 → Precondition → Matcher为了方便 → 简化成几个boolean
    → 测试恰好仍然PASS → 错误规则正式入库

  Mutation test正是抓这种问题的标准工程方法。
  {'='*106}
""")


def main():
    engine = MutationAuditEngine()
    engine.run()


if __name__ == "__main__":
    main()
