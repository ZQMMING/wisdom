# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_all_books.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 完整重写extract_yongshen函数
old_func_start = "def extract_yongshen(raw):"
old_func_end = "    return None\n\ndef run_engine"

# 找到函数开始和结束位置
start_idx = c.find(old_func_start)
end_idx = c.find(old_func_end)

new_func = '''def extract_yongshen(raw):
    """从原文中提取用神判断 - V4优化版：先从命例正文提取，没有再从完整原文提取"""
    # V4: 先截断DTS通用注解(【原注】【任氏曰】)，避免被通用注解误提取
    # 保留徐乐吾曰、楠曰等命例专属注解
    cut_markers = ['【原注】', '【任氏曰】', '【白话释意】', '【释义】']
    main_text = raw
    for marker in cut_markers:
        idx = main_text.find(marker)
        if idx > 0:
            main_text = main_text[:idx]

    def _extract(text):
        # 高优先级模式: 明确的用神判断
        high_priority_patterns = [
            r'用神必在([甲乙丙丁戊己庚辛壬癸])',
            r'用神在([甲乙丙丁戊己庚辛壬癸])',
            r'以([甲乙丙丁戊己庚辛壬癸])为用神',
            r'用神是([甲乙丙丁戊己庚辛壬癸])',
            r'用神为([甲乙丙丁戊己庚辛壬癸])',
            r'专用([甲乙丙丁戊己庚辛壬癸])[水火木金土]?',
            r'专取([甲乙丙丁戊己庚辛壬癸])[水火木金土]?',
            r'专尚([甲乙丙丁戊己庚辛壬癸])[水火木金土]?',
            r'专以([甲乙丙丁戊己庚辛壬癸])[水火木金土]?为用',
            r'取([甲乙丙丁戊己庚辛壬癸])为用神',
            r'当以([甲乙丙丁戊己庚辛壬癸])为用神',
            r'必以([甲乙丙丁戊己庚辛壬癸])为用神',
            r'宜用([甲乙丙丁戊己庚辛壬癸])[水火木金土]?为用',
            r'用神必须([甲乙丙丁戊己庚辛壬癸])',
            r'用神专取([甲乙丙丁戊己庚辛壬癸])',
            r'用神专用([甲乙丙丁戊己庚辛壬癸])',
        ]
        for pat in high_priority_patterns:
            m = re.search(pat, text)
            if m:
                stem = m.group(1)
                return WX.get(stem, stem)

        # 中优先级模式: 以X为用、用X等
        medium_priority_patterns = [
            r'以([甲乙丙丁戊己庚辛壬癸])为用',
            r'当以([甲乙丙丁戊己庚辛壬癸])为用',
            r'必以([甲乙丙丁戊己庚辛壬癸])为用',
            r'宜用([甲乙丙丁戊己庚辛壬癸])',
            r'用([甲乙丙丁戊己庚辛壬癸])[水火木金土]为',
            r'用([甲乙丙丁戊己庚辛壬癸])[水火木金土]，',
            r'用([甲乙丙丁戊己庚辛壬癸])[水火木金土]。',
        ]
        for pat in medium_priority_patterns:
            m = re.search(pat, text)
            if m:
                stem = m.group(1)
                return WX.get(stem, stem)

        return None

    # 先从命例正文提取
    result = _extract(main_text)
    if result:
        return result
    # 正文没有，再从完整原文提取
    return _extract(raw)

def run_engine'''

c = c[:start_idx] + new_func + c[end_idx + len("    return None\n"):]

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('calc_yongshen_all_books.py V4完成(extract_yongshen完整重写)')
