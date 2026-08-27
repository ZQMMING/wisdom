# -*- coding: utf-8 -*-
"""全量跑通：对 40 个 SAMPLE case 生成关系式解释，注入到 case 文件（评分任务前）。
不破坏原始排盘段，仅新增"关系式解释（系统输出）"段落。"""
import sys, re
from pathlib import Path
sys.path.insert(0, r"D:\TODAY\backend\src")

from tongshu.yi import YiAdapter, YiAdapterInput, YiInterpretationEngine

CASES = Path(r"D:\TODAY\backend\dataset\accuracy\expert_pilot\cases_v2")
# 爻位字（不含"六/九"，它们表示阴阳属性）：上五 四 三 二 初
YAO_POS = {"上": 5, "五": 4, "四": 3, "三": 2, "二": 1, "初": 0}

def parse_yuan_idx(yuantang):
    for k in "上五四三二初":
        if k in yuantang:
            return YAO_POS[k]
    return 0

def grab(txt, key):
    i = txt.find(key)
    if i == -1:
        return ""
    j = txt.find(":", i)
    if j == -1:
        j = txt.find("：", i)
    if j == -1:
        return ""
    seg = txt[j+1:]
    line_end = seg.find("\n")
    if line_end != -1:
        seg = seg[:line_end]
    return seg.strip(" *-–\t")

def clean_hex(s):
    # 去掉括号说明，仅保留卦名，如 "巽为风（上卦巽，下卦巽）" -> "巽为风"
    if "（" in s:
        s = s.split("（")[0]
    return s.strip()

def clean_yuan(s):
    # "上六（阴）" -> "上六"
    if "（" in s:
        s = s.split("（")[0]
    return s.strip()

engine = YiInterpretationEngine()
done = 0
for cf in sorted(CASES.glob("SAMPLE_*_BLIND.md")):
    txt = cf.read_text(encoding="utf-8")
    prenatal = clean_hex(grab(txt, "先天卦"))
    postnatal = clean_hex(grab(txt, "后天卦"))
    yuantang = clean_yuan(grab(txt, "元堂"))
    idx = parse_yuan_idx(yuantang)
    inp = YiAdapterInput(heluo_prenatal_hexagram=prenatal, heluo_postnatal_hexagram=postnatal,
                         heluo_yuantang_index=idx, heluo_yuantang=yuantang)
    struct = YiAdapter.adapt(inp)
    if struct.status.name != "VALID":
        print(f"{cf.stem} structure={struct.status.name} skip", flush=True)
        continue
    interp = engine.interpret(struct)
    # 构造解释段落
    block = (f"### 关系式解释（系统输出）\n\n"
             f"- 本命卦：{struct.truth_hexagram}，元堂{struct.position_name}\n"
             f"- 状态：{interp.state}\n"
             f"- 机会：{interp.opportunity}\n"
             f"- 风险：{interp.risk}\n"
             f"- 化解：{interp.remediation}\n"
             f"- 行动：{interp.action}\n"
             f"- 方向：{interp.directional_label.value}，置信度 {interp.confidence}\n\n")
    # 在 "评分任务" 前插入；若已有旧解释段先删除，避免重复
    marker = "## 评分任务"
    txt = re.sub(r"### 关系式解释（系统输出）\n.*?(?=\n## 评分任务|\Z)", "", txt, flags=re.S)
    if marker in txt:
        txt = txt.replace(marker, block + marker, 1)
    else:
        txt = txt + "\n" + block
    cf.write_text(txt, encoding="utf-8")
    done += 1
    print(f"[{done}] {cf.stem} 注入解释（{struct.truth_hexagram}·{struct.position_name}）", flush=True)

print(f"\nDONE 注入 {done} 个 case")
