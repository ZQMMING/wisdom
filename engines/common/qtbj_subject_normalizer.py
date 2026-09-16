# -*- coding: utf-8 -*-
"""PATCH-131B QTBJ Subject Normalizer (纯解析器)

职责唯一: Phrase -> Registry Lookup -> Fact Binding -> Executable Fact
不读 Evidence/Assertion/其他经典; 不产 climate_state/strength/喜忌.
输出仅 facts[] (operator: eq/any_of) 或 ABSTAIN(reason).
"""
import json, io, os, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

_REG = os.path.join(os.path.dirname(__file__), '..', '..', 'registries', 'qtbj_phrase_registry_v1.json')


class _Reg:
    def __init__(self, path=_REG):
        with open(path, encoding='utf-8') as f:
            self.reg = json.load(f)
        self.stems = self.reg['stems']
        self.single = self.reg['months_single']
        self.anyof = self.reg['months_any_of']
        self.abstain = self.reg['abstain']


_R = None
def _reg():
    global _R
    if _R is None:
        _R = _Reg()
    return _R


def normalize_subject(subject: str) -> dict:
    """把 '乙木三冬' / '甲木正月' 解析为 facts[]. 不产任何 state."""
    r = _reg()
    s = (subject or '').strip()

    # 1. 拆 天干别名前缀 (甲木/乙木...)
    stem_hit = None
    for k in sorted(r.stems, key=len, reverse=True):
        if s.startswith(k):
            stem_hit = k
            break
    if not stem_hit:
        return {"status": "ABSTAIN", "reason": "no_stem_alias_match"}

    month_phrase = s[len(stem_hit):]

    # 2. 月名为整(跨月/单月/ABSTAIN表)查表, 不做模糊匹配
    facts = [{"fact": "day_stem", "operator": "eq", "value": r.stems[stem_hit]['value']}]

    if month_phrase == '':
        return {"status": "READY", "facts": facts}

    if month_phrase in r.single:
        facts.append({"fact": "month_branch", "operator": "eq", "value": r.single[month_phrase]['value']})
        return {"status": "READY", "facts": facts}

    if month_phrase in r.anyof:
        facts.append({"fact": "month_branch", "operator": "any_of", "value": list(r.anyof[month_phrase]['any_of'])})
        return {"status": "READY", "facts": facts}

    if month_phrase in r.abstain:
        return {"status": "ABSTAIN", "reason": r.abstain[month_phrase]['reason']}

    return {"status": "ABSTAIN", "reason": "month_phrase_not_in_registry:" + month_phrase}


if __name__ == '__main__':
    tests = ['甲木正月', '乙木三冬', '乙木初春', '丙火四月', '丁火夏月', '戊土', '庚金八月白露后']
    for t in tests:
        print(t, '->', json.dumps(normalize_subject(t), ensure_ascii=False))
