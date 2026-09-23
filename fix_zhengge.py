with open('engines/special_pan.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 加正格族import
content = content.replace(
    'from engines.huaqi_grade import huaqi_pan',
    'from engines.huaqi_grade import huaqi_pan\nfrom engines.zhengge_gates import zhengge_f0'
)

# 改正格族兜底
content = content.replace(
    '    # 第四步：正格族（兜底）\n    return ("正格", "UNKNOWN", "正格族待接入")',
    '''    # 第四步：正格族（兜底）
    f0_ok, f0_reason = zhengge_f0(branches)
    if not f0_ok:
        return ("正格", "REJECT", f0_reason)
    
    # TODO: 接入L1/L2/L3
    return ("正格", "MID_1", "正格·F0通过待L1/L2/L3")'''
)

with open('engines/special_pan.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
