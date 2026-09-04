"""
P0-3.0 阶段1：五经 Corpus Adapter

【职责】统一读取 FOR-BAZI 五经 JSON，提供标准化访问接口，屏蔽各经典数据格式差异
【数据位置】D:/today/Canonical-Mining/FOR-BAZI五书JSON/
【核心原则】只做数据访问和标准化，不做辨证判断；原文保留，解析仅作参考

数据格式（统一后）：
  ClassicEntry:
    classic_id: str          # 经典ID（di_tian_sui/ziping_zhenquan/...）
    classic_name: str        # 经典名称
    entry_id: str            # 条目ID
    category: str            # 分类
    key: str                 # 关键词
    original_text: str       # 原文
    interpretation: str      # 解析（现代解释，仅作参考，非原典授权）
    likes_dislikes: str      # 喜忌
    source: str              # 出处
    tags: list[str]          # 标签
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Set


# ============================================================
# 数据结构
# ============================================================

def _sha256_text(text: str) -> str:
    """计算文本 sha256（防证据漂移，模块内部用）。"""
    import hashlib
    return hashlib.sha256((text or "").encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class ClassicEntry:
    """统一的经典条目数据结构。"""
    classic_id: str
    classic_name: str
    entry_id: str
    category: str
    key: str
    original_text: str
    interpretation: str
    likes_dislikes: str
    source: str
    tags: List[str] = field(default_factory=list)
    # ---- 验证溯源字段（P0-3.1 新增，用于 Evidence Governance）----
    source_locator: str = ""       # 原书定位：书/章节/段，如 "滴天髓·通神论·天道"
    source_version: str = ""       # 原书版本：如 "garychowcmu" / "maokuangbiao" / "四库文渊阁"
    source_hash: str = ""          # 原文 sha256，防止 Corpus 更新后证据漂移
    verification_status: str = "UNVERIFIED"  # UNVERIFIED/EXACT_MATCH/PARTIAL_MATCH/NOT_FOUND/CONFLICT
    verified_against: str = ""     # 对照的原始原典文件/段落数据文件
    verification_notes: str = ""   # 验证备注

    def to_dict(self) -> dict:
        return {
            "classic_id": self.classic_id,
            "classic_name": self.classic_name,
            "entry_id": self.entry_id,
            "category": self.category,
            "key": self.key,
            "original_text": self.original_text,
            "interpretation": self.interpretation,
            "likes_dislikes": self.likes_dislikes,
            "source": self.source,
            "tags": list(self.tags),
            "source_locator": self.source_locator,
            "source_version": self.source_version,
            "source_hash": self.source_hash,
            "verification_status": self.verification_status,
            "verified_against": self.verified_against,
            "verification_notes": self.verification_notes,
        }


@dataclass(frozen=True)
class ClassicMeta:
    """经典元数据。"""
    classic_id: str
    name: str
    author: str
    dynasty: str
    description: str
    file: str
    categories: List[str] = field(default_factory=list)


# ============================================================
# Corpus Adapter
# ============================================================

class FiveClassicsCorpusAdapter:
    """五经 Corpus 适配器 — 统一读取 FOR-BAZI 五经 JSON。

    用法：
        adapter = FiveClassicsCorpusAdapter()
        adapter.load()  # 加载全部五经

        # 获取所有经典元数据
        metas = adapter.get_all_classic_meta()

        # 获取某部经典的所有条目
        entries = adapter.get_entries_by_classic("di_tian_sui")

        # 按标签检索
        entries = adapter.search_by_tag("甲")

        # 按关键词检索（原文/解析/喜忌）
        entries = adapter.search_by_keyword("得时")

        # 按分类检索
        entries = adapter.get_entries_by_category("十干体性")
    """

    # 默认 Corpus 路径（本地数据）
    DEFAULT_CORPUS_PATH = Path(__file__).resolve().parents[3] / "data" / "canonical_mining" / "FOR-BAZI五书JSON"

    # 经典ID到名称的映射
    CLASSIC_ID_TO_NAME = {
        "di_tian_sui": "滴天髓",
        "ziping_zhenquan": "子平真诠",
        "qiongtong_baojian": "穷通宝鉴",
        "sanming_tonghui": "三命通会",
        "yuanhai_ziping": "渊海子平",
    }

    def __init__(self, corpus_path: Optional[Path] = None):
        self.corpus_path = corpus_path or self.DEFAULT_CORPUS_PATH
        self._index: Optional[dict] = None
        self._classics: Dict[str, dict] = {}  # classic_id -> raw json
        self._entries: Dict[str, ClassicEntry] = {}  # entry_id -> ClassicEntry
        self._classic_meta: Dict[str, ClassicMeta] = {}
        self._loaded = False

    # ============================================================
    # 加载
    # ============================================================

    def load(self) -> None:
        """加载全部五经 Corpus。"""
        if self._loaded:
            return

        # 1. 加载 index.json
        index_file = self.corpus_path / "index.json"
        if not index_file.exists():
            raise FileNotFoundError(f"Index file not found: {index_file}")

        with open(index_file, "r", encoding="utf-8") as f:
            self._index = json.load(f)

        # 2. 解析元数据
        for text_meta in self._index.get("texts", []):
            cid = text_meta["id"]
            self._classic_meta[cid] = ClassicMeta(
                classic_id=cid,
                name=text_meta.get("name", ""),
                author=text_meta.get("author", ""),
                dynasty=text_meta.get("dynasty", ""),
                description=text_meta.get("description", ""),
                file=text_meta.get("file", ""),
                categories=text_meta.get("categories", []),
            )

        # 3. 加载各经典 JSON
        for cid, meta in self._classic_meta.items():
            classic_file = self.corpus_path / meta.file
            if not classic_file.exists():
                print(f"Warning: Classic file not found: {classic_file}")
                continue

            with open(classic_file, "r", encoding="utf-8") as f:
                classic_data = json.load(f)

            self._classics[cid] = classic_data

            # 4. 解析条目
            entries = classic_data.get("entries", {})
            for entry_id, entry_data in entries.items():
                classic_entry = self._parse_entry(cid, entry_id, entry_data)
                if classic_entry is not None:
                    self._entries[entry_id] = classic_entry

        self._loaded = True
        print(f"Corpus loaded: {len(self._classic_meta)} classics, {len(self._entries)} entries")

    def _parse_entry(self, classic_id: str, entry_id: str, entry_data: dict) -> Optional[ClassicEntry]:
        """解析单条经典条目为统一格式。

        注意：不同经典的字段结构不同。
        - 滴天髓/穷通宝鉴/渊海子平：有"原文"字段
        - 子平真诠：部分条目无"原文"，用"取格/喜/忌/口诀/成格条件"等字段
        - 三命通会：部分条目无"原文"，用"宫位/断法"等字段
        """
        try:
            # 原文可能存在于"原文"或"全文"字段
            original_text = entry_data.get("原文", "") or entry_data.get("全文", "")

            # 若原文为空，尝试从其他字段构建候选原文（标记为构建文本，非原典逐字）
            derived_text = ""
            derived_from = []
            if not original_text:
                for f in ["取格", "成格条件", "口诀", "喜", "忌", "断法", "宫位", "取法"]:
                    val = entry_data.get(f)
                    if isinstance(val, str) and val.strip():
                        derived_text += val.strip() + "；"
                        derived_from.append(f)
                    elif isinstance(val, list):
                        derived_text += "".join(str(v) for v in val) + "；"
                        derived_from.append(f)

            return ClassicEntry(
                classic_id=classic_id,
                classic_name=self.CLASSIC_ID_TO_NAME.get(classic_id, classic_id),
                entry_id=entry_id,
                category=entry_data.get("category", ""),
                key=entry_data.get("key", ""),
                original_text=original_text,
                interpretation=entry_data.get("解析", ""),
                likes_dislikes=entry_data.get("喜忌", ""),
                source=entry_data.get("出处", ""),
                tags=entry_data.get("tags", []),
                verification_status=("DERIVED_TEXT" if (not original_text and derived_text) else "UNVERIFIED"),
                verification_notes=(
                    f"原文为空，从字段[{','.join(derived_from)}]构建候选文本（非原典逐字）"
                    if (not original_text and derived_text) else ""
                ),
                source_hash=_sha256_text(original_text or derived_text),
            )
        except Exception as e:
            print(f"Warning: Failed to parse entry {entry_id}: {e}")
            return None

    # ============================================================
    # 查询接口
    # ============================================================

    def get_all_classic_meta(self) -> List[ClassicMeta]:
        """获取所有经典元数据。"""
        self._ensure_loaded()
        return list(self._classic_meta.values())

    def get_classic_meta(self, classic_id: str) -> Optional[ClassicMeta]:
        """获取指定经典的元数据。"""
        self._ensure_loaded()
        return self._classic_meta.get(classic_id)

    def get_all_entries(self) -> List[ClassicEntry]:
        """获取所有条目。"""
        self._ensure_loaded()
        return list(self._entries.values())

    def get_entries_by_classic(self, classic_id: str) -> List[ClassicEntry]:
        """获取指定经典的所有条目。"""
        self._ensure_loaded()
        return [e for e in self._entries.values() if e.classic_id == classic_id]

    def get_entries_by_category(self, category: str) -> List[ClassicEntry]:
        """按分类获取条目。"""
        self._ensure_loaded()
        return [e for e in self._entries.values() if e.category == category]

    def get_entry_by_id(self, entry_id: str) -> Optional[ClassicEntry]:
        """按条目ID获取条目。"""
        self._ensure_loaded()
        return self._entries.get(entry_id)

    def get_all_categories(self) -> List[str]:
        """获取所有分类。"""
        self._ensure_loaded()
        return sorted(set(e.category for e in self._entries.values() if e.category))

    def get_all_tags(self) -> List[str]:
        """获取所有标签。"""
        self._ensure_loaded()
        all_tags: Set[str] = set()
        for e in self._entries.values():
            all_tags.update(e.tags)
        return sorted(all_tags)

    # ============================================================
    # 检索接口
    # ============================================================

    def search_by_tag(self, tag: str) -> List[ClassicEntry]:
        """按标签检索条目。"""
        self._ensure_loaded()
        tag_lower = tag.lower()
        return [e for e in self._entries.values() if any(t.lower() == tag_lower for t in e.tags)]

    def search_by_tags(self, tags: List[str], match_all: bool = False) -> List[ClassicEntry]:
        """按多个标签检索条目。

        Args:
            tags: 标签列表
            match_all: True=全部匹配（AND），False=任一匹配（OR）
        """
        self._ensure_loaded()
        tags_lower = set(t.lower() for t in tags)
        results = []
        for e in self._entries.values():
            entry_tags = set(t.lower() for t in e.tags)
            if match_all:
                if tags_lower.issubset(entry_tags):
                    results.append(e)
            else:
                if tags_lower.intersection(entry_tags):
                    results.append(e)
        return results

    def search_by_keyword(self, keyword: str, search_fields: Optional[List[str]] = None) -> List[ClassicEntry]:
        """按关键词检索条目。

        Args:
            keyword: 关键词
            search_fields: 搜索字段列表，可选 ["original_text", "interpretation", "likes_dislikes", "key", "category"]
                          默认搜索全部字段
        """
        self._ensure_loaded()
        if search_fields is None:
            search_fields = ["original_text", "interpretation", "likes_dislikes", "key", "category"]

        keyword_lower = keyword.lower()
        results = []
        for e in self._entries.values():
            matched = False
            for field in search_fields:
                value = getattr(e, field, "")
                if value and keyword_lower in str(value).lower():
                    matched = True
                    break
            if matched:
                results.append(e)
        return results

    def search_by_keywords(self, keywords: List[str], match_all: bool = False) -> List[ClassicEntry]:
        """按多个关键词检索条目。

        Args:
            keywords: 关键词列表
            match_all: True=全部匹配（AND），False=任一匹配（OR）
        """
        self._ensure_loaded()
        results = []
        for e in self._entries.values():
            all_text = " ".join([
                e.original_text, e.interpretation, e.likes_dislikes, e.key, e.category, " ".join(e.tags)
            ]).lower()
            if match_all:
                if all(kw.lower() in all_text for kw in keywords):
                    results.append(e)
            else:
                if any(kw.lower() in all_text for kw in keywords):
                    results.append(e)
        return results

    # ============================================================
    # 统计接口
    # ============================================================

    def get_statistics(self) -> dict:
        """获取 Corpus 统计信息。"""
        self._ensure_loaded()
        stats = {
            "total_classics": len(self._classic_meta),
            "total_entries": len(self._entries),
            "total_categories": len(self.get_all_categories()),
            "total_tags": len(self.get_all_tags()),
            "by_classic": {},
            "by_category": {},
        }

        # 按经典统计
        for cid, meta in self._classic_meta.items():
            entries = self.get_entries_by_classic(cid)
            stats["by_classic"][cid] = {
                "name": meta.name,
                "entry_count": len(entries),
                "categories": sorted(set(e.category for e in entries if e.category)),
            }

        # 按分类统计
        for cat in self.get_all_categories():
            entries = self.get_entries_by_category(cat)
            stats["by_category"][cat] = {
                "entry_count": len(entries),
                "classics": sorted(set(e.classic_id for e in entries)),
            }

        return stats

    # ============================================================
    # 内部方法
    # ============================================================

    def _ensure_loaded(self) -> None:
        """确保 Corpus 已加载。"""
        if not self._loaded:
            self.load()
