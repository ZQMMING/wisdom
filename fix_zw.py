with open('engines/zhuanwang_gates.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''    # 算印比势
    yin_wx = WUXING_OF[day_wx]["印"]
    bi_wx = WUXING_OF[day_wx]["比"]
    yin_shi = shi(branches, stems, yin_wx, branches[1])
    bi_shi = shi(branches, stems, bi_wx, branches[1])
    yin_bi_shi = yin_shi + bi_shi

    # 算官杀/财势
    guan_sha_wx = WUXING_OF[day_wx]["官杀"]
    cai_wx = WUXING_OF[day_wx]["财"]'''

new = '''    # 算印比势（比劫=日主同五行）
    yin_wx = WUXING_OF[day_wx]["印"]
    bi_wx = day_wx  # 比劫=日主同五行
    yin_shi = shi(branches, stems, yin_wx, branches[1])
    bi_shi = shi(branches, stems, bi_wx, branches[1])
    yin_bi_shi = yin_shi + bi_shi

    # 算官杀/财势
    guan_sha_wx = WUXING_OF[day_wx]["官杀"]
    cai_wx = WUXING_OF[day_wx]["财"]'''

content = content.replace(old, new)

with open('engines/zhuanwang_gates.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
