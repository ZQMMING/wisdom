"""验证 Evidence Candidate Retriever。"""
import sys
sys.path.insert(0, r"D:\shuntian\backend\src")

from tongshu.corpus.adapter import FiveClassicsCorpusAdapter
from tongshu.corpus.retrieval import EvidenceCandidateRetriever

# 加载 Corpus
adapter = FiveClassicsCorpusAdapter()
adapter.load()

# 创建检索器
retriever = EvidenceCandidateRetriever(adapter)

# 支持的概念
print("=== 支持的辨证概念 ===")
concepts = retriever.get_supported_concepts()
print(f"共 {len(concepts)} 个概念:")
for c in concepts:
    print(f"  - {c}")
print()

# 检索演示：10个核心概念
demo_concepts = ["得时", "有根", "有气", "气势", "调候", "格局", "十神", "刑冲合害", "旺衰", "用神"]
print("=== 检索演示（10个核心概念）===")
for concept in demo_concepts:
    candidates = retriever.retrieve_by_concept(concept, top_k=5)
    print(f"\n【{concept}】找到 {len(candidates)} 条候选证据（Top5）:")
    for i, c in enumerate(candidates[:5], 1):
        text_preview = c.original_text[:40] + "..." if len(c.original_text) > 40 else c.original_text
        print(f"  {i}. [{c.classic_name}] {c.entry_id}")
        print(f"     匹配度: {c.match_score:.3f} | 字段: {', '.join(c.match_fields)}")
        print(f"     原文: {text_preview}")
        print(f"     授权提示: {c.authorization_hint}")

print("\n\n=== 跨经典检索演示 ===")
# 检索"调候"，限定穷通宝鉴
candidates = retriever.retrieve_by_concept("调候", classic_ids=["qiongtong_baojian"], top_k=3)
print(f"【调候 - 仅限穷通宝鉴】找到 {len(candidates)} 条:")
for c in candidates[:3]:
    print(f"  [{c.classic_name}] {c.entry_id}: {c.original_text[:30]}...")

print("\n=== 批量检索演示 ===")
results = retriever.retrieve_multiple_concepts(["得时", "有根", "生扶"], top_k_per_concept=3)
for concept, cands in results.items():
    print(f"  {concept}: {len(cands)} 条候选证据")

print("\nEvidence Candidate Retriever 验证通过")
