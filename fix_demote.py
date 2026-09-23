with open('engines/cong_ge_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''def _demote_count(shi_dict: dict, family: str, month_branch: str, day_wx: str) -> int:
    """统计减项数量（每项-1）"""
    n = 0

    # 印比族的所从五行是印（比劫同五行，合并计算）
    if family == "印比":
        cong_wx = WUXING_OF[day_wx]["印"]
    else:
        cong_wx = WUXING_OF[day_wx][family]

    # 不当令
    if not _dangling(cong_wx, month_branch):
        n += 1

    # 旺神不纯：他神泄气
    if family == "官杀" and shi_dict.get("食伤", 0) > 0:
        n += 1
    if family == "财" and shi_dict.get("官杀", 0) > 0:
        n += 1
    if family == "食伤" and shi_dict.get("官杀", 0) > 0:
        n += 1
    if family == "印比" and (shi_dict.get("财", 0) > 0 or shi_dict.get("官杀", 0) > 0):
        n += 1

    return n'''

new = '''def _demote_count(shi_dict: dict, family: str, month_branch: str, day_wx: str, stems: list = None) -> int:
    """统计减项数量（每项-1）"""
    n = 0

    # 印比族的所从五行是印（比劫同五行，合并计算）
    if family == "印比":
        cong_wx = WUXING_OF[day_wx]["印"]
    else:
        cong_wx = WUXING_OF[day_wx][family]

    # 不当令
    if not _dangling(cong_wx, month_branch):
        n += 1

    # 旺神不纯：他神泄气
    if family == "官杀" and shi_dict.get("食伤", 0) > 0:
        n += 1
    if family == "财" and shi_dict.get("官杀", 0) > 0:
        n += 1
    if family == "食伤" and shi_dict.get("官杀", 0) > 0:
        n += 1
    if family == "印比" and (shi_dict.get("财", 0) > 0 or shi_dict.get("官杀", 0) > 0):
        n += 1

    # 天干透一粒虚浮逆神（中等减项）
    if stems is not None:
        from spec.root_qi import STEM_WUXING
        from engines.cong_ge_gates import SHISHEN_CLASSES
        # 检查是否有逆神透干（不是印比，不是所从之神）
        reverse_shen = {
            "官杀": ["食伤", "印"],  # 从杀忌食伤、印
            "财": ["比", "印", "官杀"],  # 从财忌比劫、印、官杀
            "食伤": ["印", "官杀"],  # 从儿忌印、官杀
            "印比": ["官杀", "财"],  # 从强忌官杀、财
        }
        for shen in reverse_shen.get(family, []):
            cls = SHISHEN_CLASSES[day_wx][shen]
            for i, s in enumerate(stems):
                if i == 2:  # 跳过日干
                    continue
                if STEM_WUXING.get(s) in cls:
                    n += 1
                    break  # 每类逆神只算一次

    return n'''

content = content.replace(old, new)

# 还要改调用_demote_count的地方，传入stems
# F1从杀
content = content.replace(
    'demote = _demote_count(shi_dict, "官杀", month_branch, day_wx)',
    'demote = _demote_count(shi_dict, "官杀", month_branch, day_wx, stems)'
)
# F2从财
content = content.replace(
    'demote = _demote_count(shi_dict, "财", month_branch, day_wx)',
    'demote = _demote_count(shi_dict, "财", month_branch, day_wx, stems)'
)
# F3从儿
content = content.replace(
    'demote = _demote_count(shi_dict, "食伤", month_branch, day_wx)',
    'demote = _demote_count(shi_dict, "食伤", month_branch, day_wx, stems)'
)
# F4从强
content = content.replace(
    'demote = _demote_count(shi_dict, "印比", month_branch, day_wx)',
    'demote = _demote_count(shi_dict, "印比", month_branch, day_wx, stems)'
)

with open('engines/cong_ge_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
