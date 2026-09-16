# -*- coding: utf-8 -*-
"""河洛参评诗断解层 L3 查表器（运行时索引）。

裁决（2026-09-17）：
- 金/土部：主键 = no（千百十零号，如 "3306"），由起数 total 直接给出。
- 水/火/木部：主键 = (part_en, header)，header = 日支 + 时支（如 寅巳）。
- canping_no / mark 不作运行时主键，仅 provenance/cross-check。
- 三态 fail-closed：0 命中 -> NOT_FOUND；1 命中 -> FOUND；>1 命中 -> AMBIGUOUS，绝不猜选。

本模块只读 Frozen 释义库，不复制内容、不重算八字。
"""
from __future__ import annotations

import json
import os
from threading import Lock

_PART_CN_TO_EN = {
    "金部": "jin", "土部": "tu",
    "水部": "water", "火部": "fire", "木部": "wood",
}
_JINTU_PARTS = {"jin", "tu"}

_jintu_idx: dict = {}      # no(str) -> item
_shmu_idx: dict = {}       # (part_en, header) -> [item,...]
_loaded = False
_lock = Lock()


def _data_path() -> str:
    # data/heluo/canping/canping_jingyi_full.json
    here = os.path.dirname(os.path.abspath(__file__))
    # src/tongshu/engines/heluo -> D:\shuntian
    root = os.path.abspath(os.path.join(here, "..", "..", "..", ".."))
    return os.path.join(root, "data", "heluo", "canping", "canping_jingyi_full.json")


def _load() -> None:
    global _loaded
    with _lock:
        if _loaded:
            return
        with open(_data_path(), encoding="utf-8") as f:
            lib = json.load(f)
        for it in lib.get("items", []):
            part = it.get("part")
            no = it.get("no")
            header = it.get("header")
            if part in _JINTU_PARTS and no and not str(no).startswith("p"):
                # 金土部 no = 千百十零号字符串
                _jintu_idx.setdefault(str(no), it)
            elif header:
                _shmu_idx.setdefault((part, header), []).append(it)
        _loaded = True


def _attach_base(item: dict, *, strategy: str, part: str, header=None, no=None) -> dict:
    page_col = item.get("no", "")
    page = column = None
    if page_col.startswith("p") and "-c" in page_col:
        try:
            page_s, col_s = page_col[1:].split("-c")
            page, column = int(page_s), int(col_s)
        except ValueError:
            pass
    return {
        "status": "FOUND",
        "lookup_key": {
            "strategy": strategy,
            "part": part,
            "header": header,
            "no": no,
        },
        "source": {
            "resource_id": page_col,
            "page": page,
            "column": column,
        },
        "source_text": item.get("source_text"),
        "jingyi": item.get("jingyi"),
        "modern_explanation": item.get("modern_explanation"),
        "semantic_tags": item.get("semantic_tags"),
        "evidence_basis": item.get("evidence_basis"),
    }


def lookup(part_cn: str, *, day_zhi: str | None = None,
           hour_zhi: str | None = None, no=None) -> dict:
    """运行时查表。part_cn 为中文部名（金部/木部...）。

    返回三态 dict（FOUND / CANPING_NOT_FOUND / CANPING_KEY_AMBIGUOUS）。
    """
    _load()
    part_en = _PART_CN_TO_EN.get(part_cn)
    if part_en is None:
        return {"status": "CANPING_NOT_FOUND",
                "lookup_key": {"strategy": "unknown_part", "part": part_cn}}

    if part_en in _JINTU_PARTS:
        strategy = "no_lookup"
        key = str(no) if no is not None else None
        item = _jintu_idx.get(key) if key else None
        if item is None:
            return {"status": "CANPING_NOT_FOUND",
                    "lookup_key": {"strategy": strategy, "part": part_en, "no": key}}
        return _attach_base(item, strategy=strategy, part=part_en, no=key)

    # 水火木：(part, 日支+时支)
    strategy = "part_header"
    header = (day_zhi or "") + (hour_zhi or "")
    cands = _shmu_idx.get((part_en, header), [])
    if len(cands) == 0:
        return {"status": "CANPING_NOT_FOUND",
                "lookup_key": {"strategy": strategy, "part": part_en, "header": header}}
    if len(cands) == 1:
        return _attach_base(cands[0], strategy=strategy, part=part_en, header=header)
    return {
        "status": "CANPING_KEY_AMBIGUOUS",
        "lookup_key": {"strategy": strategy, "part": part_en, "header": header},
        "candidates": [c.get("no") for c in cands],
    }


def index_stats() -> dict:
    """全量索引体检（Gate C-03）。"""
    _load()
    amb = {k: v for k, v in _shmu_idx.items() if len(v) > 1}
    return {
        "jintu_no_indexed": len(_jintu_idx),
        "jintu_no_unique": len(_jintu_idx) == len(_jintu_idx),  # dict 已去重
        "shmu_header_keys": len(_shmu_idx),
        "shmu_unique_keys": sum(1 for v in _shmu_idx.values() if len(v) == 1),
        "shmu_ambiguous_keys": len(amb),
        "shmu_ambiguous_rows": sum(len(v) for v in amb.values()),
        "ambiguous": [
            {"part": k[0], "header": k[1], "candidates": [c.get("no") for c in v]}
            for k, v in sorted(amb.items())
        ],
    }
