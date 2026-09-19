# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\scripts\calc_yongshen_all_books.py'
with open(p, encoding='utf-8') as f:
    c = f.read()

# 完整重写extract_yongshen函数 - 修复版
old_func_start = "def extract_yongshen(raw):"
# 找到函数结束位置（return None后面的空行）
end_marker = "    return None\n\ndef run_engine"
end_idx = c.find(end_marker)
start_idx = c.find(old_func_start)

new_func = '''def extract_yongshen(raw):
    """从原文中提取用神判断 - V4优化版：先从命例正文提取，没有再从完整原文提取"""
    cut_markers = ['【原注】', '【任氏曰】', '【白话释意】', '【释义】']
    main_text = raw
    for marker in cut_markers:
        idx = main_text.find(marker)
        if idx > 0:
            main_text = main_text[:idx]

    def _extract(text):
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

    result = _extract(main_text)
    if result:
        return result
    return _extract(raw)

'''

# 替换：从start_idx到end_idx+len("    return None\n")，即保留后面的def run_engine
c = c[:start_idx] + new_func + c[end_idx + len("    return None\n"):]

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.write(c)
print('calc_yongshen_all_books.py V4修复版完成')
