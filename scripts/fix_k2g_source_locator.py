"""修复 K2G 证据文件的 source_locator 和 editions.json"""
import json
from pathlib import Path

EV_DIR = Path("data/evidence")
KB_DIR = Path("data/knowledge")

# 为 K2G 证据文件分配合理的 source_locator
# E-K2G-DAYUN-002: 涉及三命通会论官杀
K2G_LOCATORS = {
    "E-K2G-DAYUN-002.json": {
        "work": "三命通会",
        "edition": "通行本",
        "chapter": "论官杀",
    },
    "E-K2G-SHIPI-000.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "十神定义",
    },
    "E-K2G-SHIPI-005.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "刑冲合害",
    },
    "E-K2G-SHIPI-006.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "刑冲合害",
    },
    "E-K2G-SHIPI-007.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "刑冲合害",
    },
    "E-K2G-SHIPI-008.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "刑冲合害",
    },
    "E-K2G-SHIPI-009.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "刑冲合害",
    },
    "E-K2G-SHIPI-010.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "刑冲合害",
    },
    "E-K2G-SHIPI-011.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "刑冲合害",
    },
    "E-K2G-SHIPI-012.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "刑冲合害",
    },
    "E-K2G-SHIPI-013.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "刑冲合害",
    },
    "E-K2G-SHIPI-014.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "刑冲合害",
    },
    "E-K2G-SHIPI-015.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "刑冲合害",
    },
    "E-K2G-SHIPI-016.json": {
        "work": "工程种子",
        "edition": "v1.0",
        "chapter": "刑冲合害",
    },
}

fixed = 0
for fpath, loc in K2G_LOCATORS.items():
    f = EV_DIR / fpath
    if not f.exists():
        continue
    d = json.load(open(f, encoding="utf-8"))
    d["source_locator"] = loc
    d["provenance_note"] = f"M2-B K2G 批次新增; {d.get('provenance_note', '')}".strip("; ").strip()
    f.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fixed += 1

print(f"Fixed {fixed} evidence files")

# 添加缺失的 edition 到 knowledge base
editions_path = KB_DIR / "editions.json"
with open(editions_path, encoding="utf-8") as f:
    editions_data = json.load(f)

existing_ids = {e["edition_id"] for e in editions_data["items"]}
new_editions = [
    {"edition_id": "EDITION-SANMING-TONGHUI-LUNGUANSHA", "book_id": "SANMING-TONGHUI", "title": "三命通会(论官杀篇)", "pinned": True, "commentator": "万民英", "source_type": "classical_text", "status": "draft", "version": "1.0.0"},
    {"edition_id": "EDITION-K2G-XINGCHONGHEHAI", "book_id": "K2G", "title": "K2G 十神刑冲合害汇编", "pinned": False, "commentator": "工程种子", "source_type": "engineering_seed", "status": "draft", "version": "1.0.0"},
]

added = 0
for ed in new_editions:
    if ed["edition_id"] not in existing_ids:
        editions_data["items"].append(ed)
        added += 1

editions_path.write_text(json.dumps(editions_data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(f"Added {added} new editions")
