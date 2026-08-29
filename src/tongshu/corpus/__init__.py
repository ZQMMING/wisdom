"""五经 Corpus 模块 — FOR-BAZI 五经语料库访问、审计、检索、交叉验证。"""
from .adapter import FiveClassicsCorpusAdapter, ClassicEntry, ClassicMeta
from .retrieval import EvidenceCandidateRetriever, EvidenceCandidate, CONCEPT_KEYWORD_MAP

__all__ = [
    "FiveClassicsCorpusAdapter",
    "ClassicEntry",
    "ClassicMeta",
    "EvidenceCandidateRetriever",
    "EvidenceCandidate",
    "CONCEPT_KEYWORD_MAP",
]
