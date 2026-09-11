# -*- coding: utf-8 -*-
"""盲派 L2 解层 EventJudgment — 事实吉凶判定引擎。

依据：《盲派生产规则.txt》V1-FINAL §57-59(应事归属/象→事/来源链)、
§60-64(五域事件结构)、§65(依赖链)、§68(UNDETERMINED 细分)、§69(证据链)、
§81(应期终枚举)、§82(BlindJudgment 最终对象)。
消费：L1 BlindBaziResult 全结构 + L1f YingqiResult（时间层）。
产出：EVENT_CANDIDATE 列表（术语枚举，事实吉凶；不拦截、不做现代语言修饰）。
铁律：全布尔/枚举禁评分；只消费 L1 不重算；子平/盲派独立。
吉凶词汇拦截点 = L3 映射层现代语言出口（本层后端全量输出）。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..engines.bazi_engine import BaziChart
from ..engines.blind_bazi_engine import BlindBaziResult, GROUP_CAI, GROUP_GUAN
from ..engines.blind_yingqi import YingqiResult
from ..reasoning.bazi_ten_gods import BRANCH_HIDDEN_STEMS, ten_god

METHOD_SCOPE = "DUAN_JIANYE"

# ── 吉凶方向术语枚举（事实吉凶，L3 映射层才拦截词汇）────────────
class JDGDirection:
    AUSPICIOUS = "AUSPICIOUS"        # 吉（财成/官清/库开）
    IN_AUSPICIOUS = "IN_AUSPICIOUS"  # 凶（官非/血光/禄伤）
    WARNING = "WARNING"              # 警示（反局/破而待救）
    NEUTRAL = "NEUTRAL"              # 中性（普通引动/未取财）
    UNDETERMINED = "UNDETERMINED"


# ── 事件状态（§59 缺链→UNDETERMINED；§68 细分）────────────────
class JdgStatus:
    ESTABLISHED = "ESTABLISHED"      # 来源链完整
    CANDIDATE = "CANDIDATE"          # 候选，待时间触发确认
    UNDETERMINED = "UNDETERMINED"


# ── 证据出处（案例集/口诀，§72 来源等级= AUTHOR_TEACHING_RECORD）──
EVIDENCE = {
    "BLIND-DJ-001": "官杀无制必犯官非（庚午辛未壬申癸酉 官非车祸离婚）",
    "BLIND-DJ-002": "禄怕见绝更怕穿害（戊申己未庚申辛巳 交通意外）",
    "BLIND-DJ-003": "羊刃逢冲血光之灾（庚午辛未壬申癸酉）",
    "BLIND-DJ-004": "配偶宫逢冲必离婚/配偶宫破星损（婚姻篇）",
    "BLIND-DJ-005": "墓库喜冲不冲不发（壬子辛亥壬辰丙午 辰库收水巨富）",
    "BLIND-DJ-006": "制尽杀星得天下（辛卯丁酉庚午丙子 乾隆 金水伤官制净）",
    "BLIND-DJ-007": "官杀当财/无官杀以伤官当财（辛卯辛丑丙辰甲午 车间主任）",
    "BLIND-DJ-008": "反局：做功方向与日主意向相反（己巳乙亥壬申丁未 牢狱）",
    "BLIND-DJ-009": "过河拆桥：先取后用（辛卯戊戌己亥癸酉 数亿大企业）",
}


@dataclass
class BlindJudgmentResult:
    """L2 解层结果：事件候选列表（术语枚举，事实吉凶）。"""
    event_candidates: List[Dict] = field(default_factory=list)
    matched_rule_ids: List[str] = field(default_factory=list)
    method_scope: str = METHOD_SCOPE
    status: str = JdgStatus.UNDETERMINED  # PRODUCED / PARTIAL / UNDETERMINED
    undetermined_reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'event_candidates': self.event_candidates,
            'matched_rule_ids': self.matched_rule_ids,
            'method_scope': self.method_scope,
            'status': self.status,
            'undetermined_reasons': self.undetermined_reasons,
        }


class BlindJudgmentEngine:
    """L2 解层引擎 — 消费 L1 全结构做事实吉凶事件判定（§65 依赖链末段）。"""

    def __init__(self):
        pass

    # ── 事件构造（§57-59 来源链：target_entity/palace/ten_god/work_id/trigger_id）──
    def _make_event(self, domain: str, event_type: str, direction: str,
                    structure_ref: str, rule_ids: List[str],
                    evidence: List[str], palace: str, ten_god: str,
                    work_id: Optional[str], trigger_id: Optional[str],
                    status: str = JdgStatus.ESTABLISHED,
                    detail: Optional[Dict] = None) -> Dict:
        source_chain = {
            'palace': palace or "UNDETERMINED",
            'ten_god': ten_god or "UNDETERMINED",
            'work_id': work_id or "UNDETERMINED",
            'trigger_id': trigger_id or "UNDETERMINED",
        }
        evt = {
            'domain': domain,
            'event_type': event_type,
            'direction': direction,
            'structure_ref': structure_ref,
            'source_chain': source_chain,
            'matched_rule_ids': rule_ids,
            'method_scope': METHOD_SCOPE,
            'evidence_refs': evidence,
            'status': status,
        }
        if detail:
            evt['detail'] = detail
        # §59：缺链 → UNDETERMINED（不因缺链静默输出）
        if not source_chain['palace'] or not source_chain['ten_god']:
            evt['status'] = JdgStatus.UNDETERMINED
        return evt

    def judge(self, chart: BaziChart, blind_result: BlindBaziResult,
              yingqi_result: Optional[YingqiResult] = None) -> BlindJudgmentResult:
        """解层主入口：L1 全结构 → 事实吉凶事件候选列表。"""
        result = BlindJudgmentResult()
        evts: List[Dict] = []
        rules: List[str] = []

        # ── ① 婚姻事件（消费 L1e EVT-MARRIAGE-001）────────────
        m = blind_result.marriage_event_structure or {}
        ms = m.get('marriage_state', 'UNDETERMINED')
        if ms == 'BROKEN':
            evts.append(self._make_event(
                'MARRIAGE', 'MARRIAGE_BROKEN', JDGDirection.IN_AUSPICIOUS,
                f"spouse_palace={m.get('spouse_palace')}(day)+star_weakened={m.get('spouse_star_weakened')}",
                ['EVT-MARRIAGE-001', 'JDG-MARRIAGE-001'], ['BLIND-DJ-004'],
                'day', 'spouse_star', 'EVT-MARRIAGE-001', None))
            rules.append('JDG-MARRIAGE-001')
        elif ms == 'CHALLENGED':
            evts.append(self._make_event(
                'MARRIAGE', 'MARRIAGE_CHALLENGED', JDGDirection.WARNING,
                f"palace_state={m.get('palace_state')}",
                ['EVT-MARRIAGE-001', 'JDG-MARRIAGE-002'], ['BLIND-DJ-004'],
                'day', 'spouse_star', 'EVT-MARRIAGE-001', None))
            rules.append('JDG-MARRIAGE-002')
        elif ms == 'HARMONIOUS':
            evts.append(self._make_event(
                'MARRIAGE', 'MARRIAGE_STABLE', JDGDirection.AUSPICIOUS,
                f"palace_state={m.get('palace_state')}+star_present={m.get('spouse_star_present')}",
                ['EVT-MARRIAGE-001', 'JDG-MARRIAGE-003'], ['BLIND-DJ-004'],
                'day', 'spouse_star', 'EVT-MARRIAGE-001', None))
            rules.append('JDG-MARRIAGE-003')

        # ── ② 财富事件（消费 L1e EVT-WEALTH-001）────────────
        w = blind_result.wealth_event_structure or {}
        ws = w.get('wealth_state', 'UNDETERMINED')
        if ws in ('DIRECTED_AND_ESTABLISHED', 'SUBSTITUTED_AND_ESTABLISHED'):
            evts.append(self._make_event(
                'WEALTH', 'WEALTH_ESTABLISHED', JDGDirection.AUSPICIOUS,
                f"wealth_state={ws}",
                ['EVT-WEALTH-001', 'JDG-WEALTH-001'],
                ['BLIND-DJ-005', 'BLIND-DJ-007'], 'day', 'wealth', 'EVT-WEALTH-001', None))
            rules.append('JDG-WEALTH-001')
        elif ws in ('DIRECTED_PARTIAL', 'SUBSTITUTED_CANDIDATE'):
            evts.append(self._make_event(
                'WEALTH', 'WEALTH_CANDIDATE', JDGDirection.NEUTRAL,
                f"wealth_state={ws}",
                ['EVT-WEALTH-001', 'JDG-WEALTH-002'], [], 'day', 'wealth', 'EVT-WEALTH-001', None))
            rules.append('JDG-WEALTH-002')
        elif ws == 'PRESENT_UNTAKEN':
            evts.append(self._make_event(
                'WEALTH', 'WEALTH_UNTAKEN', JDGDirection.NEUTRAL,
                "wealth_present=True+targeted=False",
                ['EVT-WEALTH-001', 'JDG-WEALTH-003'], [], 'day', 'wealth', 'EVT-WEALTH-001', None))
            rules.append('JDG-WEALTH-003')
        elif ws == 'ABSENT_NO_SUBSTITUTION':
            evts.append(self._make_event(
                'WEALTH', 'WEALTH_ABSENT', JDGDirection.UNDETERMINED,
                "wealth_present=False+no_substitution",
                ['EVT-WEALTH-001', 'JDG-WEALTH-004'], [], 'day', 'wealth', 'EVT-WEALTH-001', None))
            rules.append('JDG-WEALTH-004')

        # ── ③ 官贵事件（消费 L1e EVT-OFFICIAL-001 + OFF-001）──
        o = blind_result.official_event_structure or {}
        os_ = o.get('official_state', 'UNDETERMINED')
        if os_ == 'CONTROLLED_AND_CLEAN':
            evts.append(self._make_event(
                'OFFICIAL', 'OFFICIAL_ESTABLISHED', JDGDirection.AUSPICIOUS,
                f"official_state={os_}+completeness={o.get('control_completeness')}",
                ['EVT-OFFICIAL-001', 'JDG-OFFICIAL-001'], ['BLIND-DJ-006'],
                'month', 'officer', 'EVT-OFFICIAL-001', None))
            rules.append('JDG-OFFICIAL-001')
        elif os_ == 'CONTROLLED_PARTIAL':
            evts.append(self._make_event(
                'OFFICIAL', 'OFFICIAL_PARTIAL', JDGDirection.NEUTRAL,
                f"official_state={os_}（有制但制不净）",
                ['EVT-OFFICIAL-001', 'JDG-OFFICIAL-002'], ['BLIND-DJ-007'],
                'month', 'officer', 'EVT-OFFICIAL-001', None))
            rules.append('JDG-OFFICIAL-002')
        elif os_ == 'UNCONTROLLED':
            # OFF-001 官杀无制必犯官非（事实吉凶候选，非现代语言断语）
            evts.append(self._make_event(
                'OFFICIAL', 'OFFICIAL_OFFENSE_CANDIDATE', JDGDirection.IN_AUSPICIOUS,
                "officer_present=True+controlled=False（官杀无制）",
                ['EVT-OFFICIAL-001', 'JDG-OFFICIAL-003', 'OFF-001'], ['BLIND-DJ-001'],
                'month', 'officer', 'EVT-OFFICIAL-001', None))
            rules.append('JDG-OFFICIAL-003')

        # ── ④ 职业事件（消费 L1e EVT-OCCUPATION-001）──────────
        oc = blind_result.occupation_candidate or {}
        if oc.get('status') == 'CANDIDATE':
            evts.append(self._make_event(
                'OCCUPATION', 'OCCUPATION_DIRECTION_CANDIDATE', JDGDirection.NEUTRAL,
                f"work_types={oc.get('work_types')}+direction={oc.get('palace_direction')}",
                ['EVT-OCCUPATION-001', 'JDG-OCCUPATION-001'], [],
                'day', 'work_type', 'EVT-OCCUPATION-001', None,
                detail={'occupation_name': oc.get('occupation_name', 'UNDETERMINED')}))
            rules.append('JDG-OCCUPATION-001')

        # ── ⑤ 身体/疾病事件（消费 L1e EVT-BODY-001）──────────
        b = blind_result.body_event_candidate or {}
        bc = b.get('candidate', 'UNDETERMINED')
        if bc == 'LU_UNDER_ATTACK':
            evts.append(self._make_event(
                'BODY', 'BODY_LU_ATTACK', JDGDirection.IN_AUSPICIOUS,
                f"lu_present={b.get('lu_present')}+lu_attacked={b.get('lu_attacked')}（禄怕见绝更怕穿害）",
                ['EVT-BODY-001', 'JDG-BODY-001'], ['BLIND-DJ-002'],
                'day', 'lu', 'EVT-BODY-001', None))
            rules.append('JDG-BODY-001')
        elif bc == 'YANG_REN_CLASHED':
            evts.append(self._make_event(
                'BODY', 'BODY_YANG_REN_CLASH', JDGDirection.IN_AUSPICIOUS,
                f"yang_ren={b.get('yang_ren')}（羊刃逢冲）",
                ['EVT-BODY-001', 'JDG-BODY-002'], ['BLIND-DJ-003'],
                'day', 'yang_ren', 'EVT-BODY-001', None))
            rules.append('JDG-BODY-002')

        # ── ⑥ 反局事件（消费 L1b zheng_fan_ju）───────────────
        if blind_result.zheng_fan_ju == 'FAN_JU':
            evts.append(self._make_event(
                'PATTERN', 'REVERSED_PATTERN', JDGDirection.WARNING,
                f"zheng_fan_ju=FAN_JU detail={blind_result.zheng_fan_ju_detail}",
                ['VERIFY-BLIND-035', 'JDG-REVERSE-001'], ['BLIND-DJ-008'],
                'day', 'pattern', None, None))
            rules.append('JDG-REVERSE-001')

        # ── ⑦ 时间层事件（消费 L1f YingqiResult.triggers）────
        if yingqi_result is not None:
            for trg in yingqi_result.triggers:
                kind = trg.get('kind', '')
                src = trg.get('source', '')
                pos = trg.get('position', 'UNDETERMINED')
                br = trg.get('branch', 'UNDETERMINED')
                tg = trg.get('ten_god', '')
                # §57 来源链 ten_god：支引动取支主气（首藏干）对日主十神
                if not tg and br in BRANCH_HIDDEN_STEMS and BRANCH_HIDDEN_STEMS[br]:
                    tg = ten_god(chart.day_master, BRANCH_HIDDEN_STEMS[br][0][0])
                # §81 应期终枚举映射：非引动→CANDIDATE，主位穿冲刑反吟→TRIGGERED
                in_main = trg.get('in_main', False)
                severity = trg.get('severity', 'LOW')
                if kind in ('chuan', 'chong', 'sanxing', 'fanyin') and in_main:
                    evt_status = JdgStatus.ESTABLISHED
                else:
                    evt_status = JdgStatus.CANDIDATE
                # 方向映射（事实吉凶术语）
                if kind in ('muku_kai', 'sanhe', 'liuhe', 'lu') and in_main:
                    direction = JDGDirection.AUSPICIOUS
                elif kind in ('chuan', 'chong', 'sanxing', 'fanyin') and in_main:
                    direction = JDGDirection.IN_AUSPICIOUS
                elif kind == 'fuyin' and in_main:
                    # 伏吟主位：原局结构重演/加重（盲派应期：伏吟=重复引动）
                    direction = JDGDirection.WARNING
                else:
                    direction = JDGDirection.NEUTRAL
                evts.append(self._make_event(
                    'TIME', f"TIME_{kind.upper()}", direction,
                    trg.get('mech', ''),
                    ['JDG-TIME-001'], [],
                    pos, tg or 'branch', None,
                    f"{kind}:{src}:{pos}:{br}",
                    status=evt_status,
                    detail={'severity': severity, 'keyword': trg.get('keyword', '')}))
            rules.append('JDG-TIME-001')

        # ── 状态汇总 ──
        result.event_candidates = evts
        result.matched_rule_ids = list(dict.fromkeys(rules))
        result.status = 'PRODUCED' if evts else JdgStatus.UNDETERMINED
        if not evts:
            result.undetermined_reasons.append('FACT_MISSING: L1 无事件结构输出')
        return result


def judge_blind(chart: BaziChart, blind_result: BlindBaziResult,
                yingqi_result: Optional[YingqiResult] = None) -> BlindJudgmentResult:
    """便捷入口。"""
    return BlindJudgmentEngine().judge(chart, blind_result, yingqi_result)
