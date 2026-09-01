#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
补全 QTBJ 和 YHZP 证据的语义字段 (observation_dimension, relation_semantics)
- QTBJ: 所有文件的 observation_dimension 为空，relation_semantics 已有值
- YHZP: 4个根级文件(E-YHZP-101~104-001)使用 M2-B schema，缺少语义字段
"""
import json
from pathlib import Path
from datetime import datetime, timezone

BASE = Path("C:/Users/wisdom/wisdom/data/evidence")
QTB_DIR = BASE / "qiong_tong_bao_jian"
YHZP_DIR = BASE / "yuan_hai_zi_ping"
ROOT_YHZP = [BASE / f"E-YHZP-{i:03d}-001.json" for i in range(101, 105)]

UPDATED = {"qtbj": 0, "yhzp": 0}
ERRORS = {"qtbj": [], "yhzp": []}


def read_json(path: Path) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: Path, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ──────────────────────────────────────────────
# QTBJ: 填充 observation_dimension
#   evidence_type = ADJ  →  observation_dimension = "ADJ"
#   evidence_type = TEM  →  observation_dimension = "TEM"
# relation_semantics 已存在，保留不覆盖
# ──────────────────────────────────────────────
def complete_qtbj():
    print("=" * 60)
    print("QTBJ 语义字段补全")
    print("=" * 60)

    files = sorted(QTB_DIR.glob("*.json"))
    print(f"发现 {len(files)} 个文件")

    for fpath in files:
        try:
            data = read_json(fpath)
            etype = data.get("evidence_type", "")
            obs_dim = data.get("observation_dimension", "")
            rel_sem = data.get("relation_semantics", "")

            # 只有 observation_dimension 为空才修改
            if not obs_dim and etype in ("ADJ", "TEM"):
                data["observation_dimension"] = etype
                write_json(fpath, data)
                UPDATED["qtbj"] += 1
            elif not obs_dim:
                ERRORS["qtbj"].append(f"{fpath.name}: unknown evidence_type={etype}")
        except Exception as e:
            ERRORS["qtbj"].append(f"{fpath.name}: {e}")

    print(f"  已更新: {UPDATED['qtbj']}")
    if ERRORS["qtbj"]:
        print(f"  错误 ({len(ERRORS['qtbj'])}): {ERRORS['qtbj'][:5]}")


# ──────────────────────────────────────────────
# YHZP 根级文件: 添加 observation_dimension & relation_semantics
# 基于 rule_refs 和 citation 内容推断
# ──────────────────────────────────────────────
YHZP_ROOT_MAP = {
    "E-YHZP-101-001": {
        "observation_dimension": "DAYMASTER_STRONG",
        "relation_semantics": "CONSTRAINT",
        "reason": "阳刃=日主帝旺，性烈须制伏→CONSTRAINT"
    },
    "E-YHZP-102-001": {
        "observation_dimension": "MONTH_BRANCH_DOMINANT",
        "relation_semantics": "CONTEXT",
        "reason": "子时日界规则，决定大运起法背景→CONTEXT"
    },
    "E-YHZP-103-001": {
        "observation_dimension": "TEN_GODS_BALANCE",
        "relation_semantics": "SUPPORT",
        "reason": "五鼠遁起时诀，支持时柱计算→SUPPORT"
    },
    "E-YHZP-104-001": {
        "observation_dimension": "DAYMASTER_STRONG",
        "relation_semantics": "SUPPORT",
        "reason": "建禄/月劫=身旺，取用透干用财官→SUPPORT"
    },
}


def complete_yhzp_root():
    print("\n" + "=" * 60)
    print("YHZP 根级文件语义字段补全")
    print("=" * 60)

    for fpath in ROOT_YHZP:
        if not fpath.exists():
            ERRORS["yhzp"].append(f"{fpath.name}: file not found")
            continue

        try:
            data = read_json(fpath)
            eid = data.get("evidence_id", "")
            mapping = YHZP_ROOT_MAP.get(eid)

            if not mapping:
                ERRORS["yhzp"].append(f"{eid}: no mapping found")
                continue

            # 添加缺失的语义字段
            if "observation_dimension" not in data:
                data["observation_dimension"] = mapping["observation_dimension"]
            if "relation_semantics" not in data:
                data["relation_semantics"] = mapping["relation_semantics"]

            # 更新 provenance_note 记录本次补全
            provenance = data.get("provenance_note", "")
            if "semantic_field_completed" not in provenance:
                data["provenance_note"] = (
                    provenance + " | semantic_field_completed: "
                    f"obs_dim={mapping['observation_dimension']}, "
                    f"rel_sem={mapping['relation_semantics']} "
                    f"({mapping['reason']})"
                )

            write_json(fpath, data)
            UPDATED["yhzp"] += 1
            print(f"  ✓ {eid}: obs_dim={mapping['observation_dimension']}, "
                  f"rel_sem={mapping['relation_semantics']}")

        except Exception as e:
            ERRORS["yhzp"].append(f"{fpath.name}: {e}")

    print(f"  已更新: {UPDATED['yhzp']}")
    if ERRORS["yhzp"]:
        print(f"  错误 ({len(ERRORS['yhzp'])}): {ERRORS['yhzp'][:5]}")


# ──────────────────────────────────────────────
# 验证
# ──────────────────────────────────────────────
def validate():
    print("\n" + "=" * 60)
    print("验证结果")
    print("=" * 60)

    # QTBJ 验证
    qtbj_files = sorted(QTB_DIR.glob("*.json"))
    qtbj_missing_obs = 0
    qtbj_missing_sem = 0
    for f in qtbj_files:
        data = read_json(f)
        if not data.get("observation_dimension"):
            qtbj_missing_obs += 1
        if not data.get("relation_semantics"):
            qtbj_missing_sem += 1

    print(f"QTBJ: 总文件={len(qtbj_files)}, "
          f"observation_dimension缺失={qtbj_missing_obs}, "
          f"relation_semantics缺失={qtbj_missing_sem}")

    # YHZP 验证
    yhzp_files = sorted(YHZP_DIR.glob("E-YHZP-*.json"))
    yhzp_missing_obs = 0
    yhzp_missing_sem = 0
    for f in yhzp_files:
        data = read_json(f)
        if not data.get("observation_dimension"):
            yhzp_missing_obs += 1
        if not data.get("relation_semantics"):
            yhzp_missing_sem += 1

    # 根级 YHZP
    for f in ROOT_YHZP:
        if f.exists():
            data = read_json(f)
            if not data.get("observation_dimension"):
                yhzp_missing_obs += 1
            if not data.get("relation_semantics"):
                yhzp_missing_sem += 1

    print(f"YHZP: 总文件={len(yhzp_files) + len(ROOT_YHZP)}, "
          f"observation_dimension缺失={yhzp_missing_obs}, "
          f"relation_semantics缺失={yhzp_missing_sem}")

    return qtbj_missing_obs == 0 and yhzp_missing_obs == 0


if __name__ == "__main__":
    complete_qtbj()
    complete_yhzp_root()
    success = validate()
    print(f"\n{'=' * 60}")
    print(f"完成! QTBJ更新={UPDATED['qtbj']}, YHZP更新={UPDATED['yhzp']}")
    print(f"验证结果: {'PASS' if success else 'FAIL'}")
    print(f"{'=' * 60}")
