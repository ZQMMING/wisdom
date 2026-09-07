#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
断语库 → EngineEvidence 转换器

来源: data/classics/duanyu/01_按经典分/*.md（五部经典断语库，11,478条）
用途: 将断语转为标准 EngineEvidence JSON，补 ZIPING 等引擎的证据缺口
      （DTS-102/SMTH-102/YHZP-105 等 rule 存在但 evidence 缺失的情况）

格式说明:
- 断语库行格式: "**N.** 断语文本"（N 为该经典内序号）
- 按经典分: 滴天髓阐微/穷通宝鉴/三命通会/渊海子平/子平真诠
- 输出: data/evidence/<classic_id>/E-<PREFIX>-DUANYU-<seq>.json

用法:
  python scripts/convert_duanyu_to_evidence.py [--limit N] [--dry-run]

原则（V2）:
- Evidence 只保留事实，不产生 polarity/direction 判断
- provenance 完整: classic/work/chapter/source_hash
- Resource ID ≠ File Path（路径独立）
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DUANYU_DIR = REPO_ROOT / "data" / "classics" / "duanyu" / "01_按经典分"
OUTPUT_DIR = REPO_ROOT / "data" / "evidence"

# 经典映射: 文件名关键词 → (classic_id, classic_name, evidence前缀)
CLASSIC_MAP = [
    ("滴天髓", "di_tian_sui", "滴天髓", "DTS"),
    ("穷通宝鉴", "qiong_tong_bao_jian", "穷通宝鉴", "QTB"),
    ("三命通会", "san_ming_tong_hui", "三命通会", "SMTH"),
    ("渊海子平", "yuan_hai_zi_ping", "渊海子平", "YHZP"),
    ("子平真诠", "zi_ping_zhen_quan", "子平真诠", "ZPZ"),
]

# 断语行: "**N.** text"（注意: 数字后是 .** 而非 **. ）
LINE_RE = re.compile(r"^\*\*(\d+)\.\*\*\s*(.+)$")
# 小节标题: "## 《经典名》" 或 "## 类别名"
SECTION_RE = re.compile(r"^#+\s*(.+)$")


def sha256_hex(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def parse_duanyu_file(path: Path) -> list[dict]:
    """解析单个断语md文件，返回断语列表。"""
    items = []
    text = path.read_text(encoding="utf-8", errors="replace")
    current_section = ""
    for line in text.splitlines():
        m = SECTION_RE.match(line.strip())
        if m and "断语" not in m.group(1):
            current_section = m.group(1).strip()
        m2 = LINE_RE.match(line.strip())
        if m2:
            items.append({
                "seq": int(m2.group(1)),
                "text": m2.group(2).strip(),
                "section": current_section,
            })
    return items


def build_evidence(duanyu: dict, classic_id: str, classic_name: str, prefix: str) -> dict:
    """构建单个 EngineEvidence。"""
    eid = f"E-{prefix}-DUANYU-{duanyu['seq']:04d}"
    text = duanyu["text"]
    return {
        "evidence_id": eid,
        "classic_id": classic_id,
        "classic_name": classic_name,
        "evidence_type": "DUANYU",
        "observation_dimension": duanyu["section"] or "GENERAL",
        "relation_semantics": "",
        "original_text": text,
        "source_locator": {
            "classic": classic_id,
            "work": classic_name,
            "chapter": duanyu["section"] or "",
            "section": "",
            "passage_id": f"{prefix}_DUANYU_{duanyu['seq']:04d}",
            "source_hash": sha256_hex(text),
        },
        "evidence_text": {
            "original_text": text,
            "text_layer": "ORIGINAL",
            "context_before": "",
            "context_after": "",
        },
        "canonical_state": {},
        "authorization_level": "PENDING",
        "verification_status": "UNVERIFIED",
        "extraction_quality": 0.6,
        "notes": f"从五经断语库提取（{classic_name}），断语序号 {duanyu['seq']}，类别: {duanyu['section']}",
        "rule_refs": [],
        "citation": {
            "original_text": text,
            "language": "classical_chinese",
        },
        "source_layer": "classical_original",
        "evidence_strength": "primary",
        "version": "1.0.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "provenance": {
            "source": "五部经典断语库",
            "authorization": "PENDING_REVIEW",
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="每经典最多转换条数(0=全部)")
    ap.add_argument("--dry-run", action="store_true", help="仅统计不写入")
    args = ap.parse_args()

    if not DUANYU_DIR.is_dir():
        print(f"❌ 断语库目录不存在: {DUANYU_DIR}")
        return 1

    total_written = 0
    total_skipped = 0
    for fname in sorted(DUANYU_DIR.glob("*.md")):
        matched = None
        for keyword, cid, cname, prefix in CLASSIC_MAP:
            if keyword in fname.name:
                matched = (cid, cname, prefix)
                break
        if not matched:
            continue
        cid, cname, prefix = matched
        items = parse_duanyu_file(fname)
        if args.limit:
            items = items[: args.limit]

        out_dir = OUTPUT_DIR / cid
        written = 0
        skipped = 0
        for item in items:
            ev = build_evidence(item, cid, cname, prefix)
            out_path = out_dir / f"{ev['evidence_id']}.json"
            if args.dry_run:
                written += 1
                continue
            # 已存在同ID证据则跳过（不覆盖已有核验）
            if out_path.exists():
                skipped += 1
                continue
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path.write_text(json.dumps(ev, ensure_ascii=False, indent=2), encoding="utf-8")
            written += 1

        total_written += written
        total_skipped += skipped
        print(f"{cname}: 解析 {len(items)} 条 → 写入 {written} / 跳过 {skipped}")

    print("=" * 60)
    if args.dry_run:
        print(f"[dry-run] 可写入 {total_written} 条 Evidence（未实际写入）")
    else:
        print(f"✅ 共写入 {total_written} 条 Evidence（跳过已存在 {total_skipped} 条）")
        print(f"   输出目录: {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
