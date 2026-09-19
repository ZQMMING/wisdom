# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 在B6扶抑路径最后增加兜底, 确保所有命例都有primary输出
old = """        for w in hou:
            if w!=primary: S(w,'调候候神(《穷通宝鉴》次序)')"""

new = """        for w in hou:
            if w!=primary: S(w,'调候候神(《穷通宝鉴》次序)')
        # 兜底: 所有路径都不满足时, 确保有primary输出(避免None)
        if primary is None:
            if hou:
                P(sorted(hou)[0],'QIHOU','兜底取调候候神(所有结构化路径未命中)')
            elif tier in WANG_TIER:
                P(t['shi'],'FUYI','兜底身旺食伤泄秀')
            elif tier in SHUAI_TIER:
                P(t['yin'],'FUYI','兜底身弱用印扶身')
            else:
                P(t['shi'],'FUYI','兜底中和取食伤泄秀')"""

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('兜底路径添加完成')
