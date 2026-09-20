# -*- coding: utf-8 -*-
p = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(p, encoding='utf-8') as f:
    lines = f.readlines()

# 修改第230行（索引229）的炎上格最后一个分支
for i, line in enumerate(lines):
    if '炎上格纯无官杀透，顺食伤土泄秀导势' in line:
        lines[i] = "            else:\n"
        lines.insert(i+1, "                if stem(sw)>=1 or cs(sw):\n")
        lines.insert(i+2, "                    P(sw,'ZHUANWANG','炎上格纯无官杀透，食伤透干成势，顺食伤土泄秀导势'); S(yw,'顺印')\n")
        lines.insert(i+3, "                else:\n")
        lines.insert(i+4, "                    P(t['bi'],'ZHUANWANG','炎上格纯无官杀透、食伤未透，顺比劫火为用(顺势不取制衡)'); S(sw,'食伤顺泄'); S(yw,'印生扶')\n")
        print(f'修改第{i+1}行炎上格分支完成')
        break

with open(p, 'w', encoding='utf-8', newline='') as f:
    f.writelines(lines)
print('yongshen_engine.py V4.34完成(炎上格食伤未透用比劫火顺势)')
