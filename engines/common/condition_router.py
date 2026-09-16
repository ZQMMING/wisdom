# -*- coding: utf-8 -*-
"""PATCH-141F Condition Router: PZZQ条件词 -> Root/Transparent/Combination Evaluator
只路由, 不新增旺衰事实/算法. 复合/未注册=UNKNOWN."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from engines.common.root_condition_evaluator import eval_root
from engines.common.transparent_condition_evaluator import eval_transparent
from engines.common.combination_condition_evaluator import eval_combination
from engines.common.deling_rule import eval_de_ling

# 条件词 -> evaluator名 (仅路由, 语义边界由各evaluator的registry保证)
ROUTE = {
    '有根': 'root', '通根': 'root', '无根': 'root', '根深': 'root', '根浅': 'root',
    '财有根': 'root', '身有根': 'root', '官有根': 'root', '印有根': 'root', '无气': 'root',
    '财透': 'transparent', '官透': 'transparent', '印透': 'transparent',
    '食神透': 'transparent', '伤官透': 'transparent', '杀透': 'transparent',
    '官杀透': 'transparent', '财官双透': 'transparent',
    '见财': 'transparent', '见印': 'transparent', '见官': 'transparent',
}
for pair in ['子丑','寅亥','卯戌','辰酉','巳申','午未']:
    ROUTE[pair+'合'] = 'combination'
for pair in ['子午','丑未','寅申','卯酉','辰戌','巳亥']:
    ROUTE[pair+'冲'] = 'combination'
for pair in ['甲己','乙庚','丙辛','丁壬','戊癸']:
    ROUTE[pair+'合'] = 'combination'
for ju in ['申子辰合水','亥卯未合木','寅午戌合火','巳酉丑合金',
           '寅卯辰三会木','巳午未三会火','申酉戌三会金','亥子丑三会水']:
    ROUTE[ju] = 'combination'


def route_condition(condition_text, facts):
    """返回三态. 未路由/复合/身强身弱=UNKNOWN."""
    if condition_text in ('身强','身弱'):
        return {"condition": condition_text, "status": "UNKNOWN",
                "reason": "not_single_condition_or_not_implemented"}
    if condition_text in ('得令','失令'):
        return eval_de_ling(condition_text, facts)
    ev = ROUTE.get(condition_text)
    if ev == 'root':
        return eval_root(condition_text, facts)
    if ev == 'transparent':
        return eval_transparent(condition_text, facts)
    if ev == 'combination':
        return eval_combination(condition_text, facts)
    return {"condition": condition_text, "status": "UNKNOWN", "reason": "no_router"}


if __name__ == '__main__':
    import io, json
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    from engines.common.l0_fact_builder import build
    gc001 = build({'year': ['癸','亥'], 'month': ['壬','戌'], 'day': ['乙','未'], 'hour': ['壬','午']})
    for c in ['有根','财有根','财透','官透','午未合','合化木','身强','得令','火星']:
        print(c, '->', json.dumps(route_condition(c, gc001), ensure_ascii=False))
