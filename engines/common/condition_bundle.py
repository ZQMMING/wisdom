# -*- coding: utf-8 -*-
"""PATCH-141H-C Condition Bundle 三态聚合器
required条件逐项三态 -> 聚合. 非评分/非多数决. 不判成格."""


def aggregate_required(items):
    """items: [{'condition','status'},...].
    规则: 全SATISFIED->SATISFIED; 任一UNSATISFIED->UNSATISFIED; 无UNSATISFIED但有UNKNOWN->UNKNOWN."""
    stats = {}
    for it in items:
        stats[it['status']] = stats.get(it['status'], 0) + 1
    if stats.get('UNSATISFIED', 0) > 0:
        return {'bundle_status': 'UNSATISFIED', 'reason': 'required_unsatisfied', 'stats': stats}
    if stats.get('UNKNOWN', 0) > 0:
        return {'bundle_status': 'UNKNOWN', 'reason': 'has_unknown_required', 'stats': stats}
    if stats.get('SATISFIED', 0) == len(items) and items:
        return {'bundle_status': 'SATISFIED', 'reason': 'all_required_satisfied', 'stats': stats}
    return {'bundle_status': 'UNKNOWN', 'reason': 'no_required_conditions', 'stats': stats}


if __name__ == '__main__':
    import sys, io, json
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    demo = [
        [{'condition':'有根','status':'SATISFIED'},{'condition':'财透','status':'SATISFIED'}],
        [{'condition':'有根','status':'SATISFIED'},{'condition':'财透','status':'UNSATISFIED'}],
        [{'condition':'有根','status':'SATISFIED'},{'condition':'财有根','status':'UNKNOWN'}],
        [],
    ]
    for items in demo:
        print(json.dumps(aggregate_required(items), ensure_ascii=False))
