with open('engines/axis_xiuqi.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 加b8字段
old_dataclass = '''@dataclass
class XiuqiResult:
    pattern_root: Optional[str]
    pattern_type: str
    b1a: bool
    b1b: bool
    b2: bool
    b3: bool
    b4: bool
    b5: bool  # 化神支局全
    b6: bool  # G4：无克化神透干
    b7: bool  # G8：财星不超标（财透一位虚浮尚可，两位/根深则转格）
    score: int
    gate_debug: List[str]'''

new_dataclass = '''@dataclass
class XiuqiResult:
    pattern_root: Optional[str]
    pattern_type: str
    b1a: bool
    b1b: bool
    b2: bool
    b3: bool
    b4: bool
    b5: bool  # 化神支局全
    b6: bool  # G4：无克化神透干
    b7: bool  # G8：财星不超标（财透一位虚浮尚可，两位/根深则转格）
    b8: bool  # G7：日主有根→降档（不是硬闸，是减项）
    score: int
    gate_debug: List[str]'''

content = content.replace(old_dataclass, new_dataclass)

# 2. 早期return加b8=False
old_early = 'return XiuqiResult(None, "化气型", False, False, False, False, False, False, False, False, 0, [])'
new_early = 'return XiuqiResult(None, "化气型", False, False, False, False, False, False, False, False, False, 0, [])'
content = content.replace(old_early, new_early)

with open('engines/axis_xiuqi.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
