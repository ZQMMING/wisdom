"""验证 Corpus Adapter。"""
import sys
sys.path.insert(0, r"D:\shuntian\backend\src")

from tongshu.corpus.adapter import FiveClassicsCorpusAdapter

# 加载 Corpus
adapter = FiveClassicsCorpusAdapter()
adapter.load()

# 统计
stats = adapter.get_statistics()
print("=== Corpus 统计 ===")
print("经典数:", stats["total_classics"])
print("条目数:", stats["total_entries"])
print("分类数:", stats["total_categories"])
print("标签数:", stats["total_tags"])
print()

print("=== 各经典条目数 ===")
for cid, info in stats["by_classic"].items():
    name = info["name"]
    count = info["entry_count"]
    cats = info["categories"]
    print(f"  {cid} ({name}): {count} 条, 分类: {cats}")
print()

print("=== 所有分类 ===")
for cat in adapter.get_all_categories():
    print(f"  {cat}")
print()

# 按关键词检索
print('=== 检索"得时" ===')
results = adapter.search_by_keyword("得时")
print(f"找到 {len(results)} 条:")
for r in results[:5]:
    text = r.original_text[:50] if r.original_text else ""
    print(f"  [{r.classic_name}] {r.entry_id}: {text}...")
print()

print('=== 检索"有根" ===')
results = adapter.search_by_keyword("有根")
print(f"找到 {len(results)} 条")
for r in results[:3]:
    text = r.original_text[:50] if r.original_text else ""
    print(f"  [{r.classic_name}] {r.entry_id}: {text}...")
print()

print('=== 检索"调候" ===')
results = adapter.search_by_keyword("调候")
print(f"找到 {len(results)} 条")
for r in results[:3]:
    text = r.original_text[:50] if r.original_text else ""
    print(f"  [{r.classic_name}] {r.entry_id}: {text}...")
print()

print("Corpus Adapter 验证通过")
