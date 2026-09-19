# -*- coding: utf-8 -*-
file_path = r'D:\shuntian-ziping-p0\engines\common\yongshen_engine.py'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# 1. 移除P函数调试print
old1 = """    def P(w,path,note):
        nonlocal primary
        if w and w in WUXING and primary is None:
            if dm=='壬' and mz=='寅': print(f'DEBUG P: w={w}, path={path}, note={note[:40]}')
            primary=w; paths.append(path); notes[w]=note"""
new1 = """    def P(w,path,note):
        nonlocal primary
        if w and w in WUXING and primary is None:
            primary=w; paths.append(path); notes[w]=note"""
content = content.replace(old1, new1)

# 2. 在官杀制化路径前定义提纲不照变量
old2 = """        # ---------- B 官杀制化 / 食伤制杀 / 杀印相生 ----------
        zhi_ok=stem(t['shi'])>=1 and qi(t['shi']) and (tier in WANG_TIER or ben(t['shi'])>=1 or cs(t['shi']) or _dm_root_ok"""
new2 = """        # ---------- B 官杀制化 / 食伤制杀 / 杀印相生 ----------
        # 提纲不照: 月干不是月令本气五行, 印星透干有根(庚申戊寅壬子甲辰: 寅月本气甲木不透(月干戊), 庚金透干为用, 提纲不照)
        _month_stem = pillars['month'][0]
        _month_benqi_wx = BRANCH_WX.get(mz)
        _tigang_buzhao = bool(_month_benqi_wx) and _ganwx.get(_month_stem)!=_month_benqi_wx and stem(t['yin'])>=1 and (ben(t['yin'])>=1 or ling(t['yin']) in ('旺','相'))
        zhi_ok=stem(t['shi'])>=1 and qi(t['shi']) and (tier in WANG_TIER or ben(t['shi'])>=1 or cs(t['shi']) or _dm_root_ok"""
content = content.replace(old2, new2)

# 3. 第344行增加提纲不照排除条件
old3 = """                    if zhi_ok and ben(t['guan'])==0 and ling(t['shi'])=='旺':
                        # 身旺(旺极/太旺)+食伤当令+官杀虚透无根=伤官去官/食伤泄秀(L1080戊午壬戌丁卯癸卯):"""
new3 = """                    if zhi_ok and ben(t['guan'])==0 and ling(t['shi'])=='旺' and not _tigang_buzhao:
                        # 身旺(旺极/太旺)+食伤当令+官杀虚透无根=伤官去官/食伤泄秀(L1080戊午壬戌丁卯癸卯):"""
content = content.replace(old3, new3)

# 4. 在官杀制化路径的else分支增加提纲不照用印
old4 = """                    else:
                        if gs_rooted and hua_ok: P(t['yin'],'BINGYAO','身旺官杀虚透、印透有气，杀印相生(印化虚杀)')"""
new4 = """                    else:
                        if _tigang_buzhao:
                            P(t['yin'],'BINGYAO','提纲不照：月令本气不透，印星透干有根为用(透金为用神)'); S(t['bi'],'比劫帮身')
                        elif gs_rooted and hua_ok: P(t['yin'],'BINGYAO','身旺官杀虚透、印透有气，杀印相生(印化虚杀)')"""
content = content.replace(old4, new4)

with open(file_path, 'w', encoding='utf-8', newline='') as f:
    f.write(content)
print('提纲不照官杀制化路径修复完成')
