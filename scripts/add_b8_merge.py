with open('engines/special_merge.py', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''        if not x.b7:
            return (None, None, "REJECT", 0)  # TODO: rebase to 正格族 once available
        # B独足 → 化气型
        # 争合降档：b1b=True → MID
        if x.b1b:
            conf = "MID"
        else:
            conf = "CONFIRMED" if x.b5 else "MID"
        return (x.pattern_root, "化气型", conf, x.score)'''

new = '''        if not x.b7:
            return (None, None, "REJECT", 0)  # TODO: rebase to 正格族 once available
        # B独足 → 化气型
        # 降档条件：争合(b1b) 或 日主有根(b8) → MID
        if x.b1b or x.b8:
            conf = "MID"
        else:
            conf = "CONFIRMED" if x.b5 else "MID"
        return (x.pattern_root, "化气型", conf, x.score)'''

content = content.replace(old, new)

with open('engines/special_merge.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('done')
