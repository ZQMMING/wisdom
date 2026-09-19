# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\special_pattern.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 修复辛未辛丑戊辰壬戌: 四库全(dm_ben_eff>=4)时食伤透干有根是泄秀不是过泄, 仍应判专旺格
old = "    guo_xie = (ss_stem >= 2 and ss_ben >= 1)   # #PCT-MARK 食伤透干有根成党=过泄/两气成象, 不判纯一行专旺"
new = "    guo_xie = (ss_stem >= 2 and ss_ben >= 1 and dm_ben_eff <= 3)   # #PCT-MARK 食伤透干有根成党=过泄/两气成象, 不判纯一行专旺; 但日主本气根>=4(如四库全)时食伤只是泄秀仍判专旺(辛未辛丑戊辰壬戌稼穑格用辛金吐秀)"

content = content.replace(old, new)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('专旺格过泄判断修复完成')
