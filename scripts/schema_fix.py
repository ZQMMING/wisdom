"""Schema 多引擎兼容修复（Phase 3 全引擎正式化前置）。

1. rule/source schema: id pattern [A-Z]{4} -> [A-Z]{3,4}（DTS 三字母缩写）
2. rule schema scope 枚举 + decade（V2.22 原文 scope 为 string；数据实际值 natal/decade）
3. rule schema preconditions.conditions 去掉 minItems（空 conditions = 无条件恒真规则）
"""

import json
from pathlib import Path

ROOT = Path(r"D:\shuntian-ziping-p0")

# 1. source.schema.json
sp = ROOT / "shared_schema" / "source.schema.json"
s = json.loads(sp.read_text(encoding="utf-8"))
s["properties"]["source_id"]["pattern"] = "^[A-Z]{3,4}-[0-9]{3}-[0-9]{3}$"
s["properties"]["text_id"]["pattern"] = "^[A-Z]{3,4}-T-[0-9]{3}-[0-9]{3}$"
s["properties"]["resource_id"]["pattern"] = "^SRC-[A-Z]{3,4}-[0-9]{3}$"
s["properties"]["logical_uri"]["pattern"] = "^source://[a-z]{3,4}/[0-9]{3}/[0-9]{3}$"
s["properties"]["relative_path"]["pattern"] = "^sources/[a-z]{3,4}/chapter_[0-9]{3}\\.md$"
sp.write_text(json.dumps(s, ensure_ascii=False, indent=2), encoding="utf-8")

# 2. rule.schema.json
rp = ROOT / "shared_schema" / "rule.schema.json"
r = json.loads(rp.read_text(encoding="utf-8"))
r["properties"]["rule_id"]["pattern"] = "^(CAND-)?[A-Z]{3,4}-[0-9]{3}$"
r["properties"]["source_ids"]["items"]["pattern"] = "^[A-Z]{3,4}-[0-9]{3}-[0-9]{3}$"
r["properties"]["scope"]["enum"] = ["natal", "dayun", "liunian", "liuyue", "decade"]
del r["$defs"]["preconditions"]["properties"]["conditions"]["minItems"]
rp.write_text(json.dumps(r, ensure_ascii=False, indent=2), encoding="utf-8")

print("schema 已更新")
print("source_id pattern:", s["properties"]["source_id"]["pattern"])
print("rule_id pattern:", r["properties"]["rule_id"]["pattern"])
print("scope enum:", r["properties"]["scope"]["enum"])
print("conditions minItems 已移除")
