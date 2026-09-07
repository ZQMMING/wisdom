#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PATH_INDEPENDENCY_AUDIT — 路径独立性审计

P0 架构红线（2026-09-07 确立）：
  生产代码不得将运行时资源、数据库、配置、资料索引、模型、证据资产等
  绑定到开发机绝对路径（D:/ C:/ E:/ /Users/ /home/ /srv/ ...）。

允许：
  - 环境变量注入的根目录（settings.data_root 等）—— 配置绑定
  - Path(__file__).parent 的 package 内相对定位 —— 运行时相对定位
  - tmp_path / Path(__file__).parent/"fixtures"（测试）—— 相对 fixture

禁止（代码写死）：
  - "D:/shuntian/..."  "C:/Users/..."  "E:/..."  "/srv/..."  "/home/..."
  - sys.path.insert(0, "D:/shuntian/backend") 等硬编码
  - open("D:/shuntian/docs/xxx.json")
  - DB_PATH = "D:/shuntian/data/xxx.db"

用法:
  python scripts/path_independency_audit.py [--dir src tests scripts] [--fix]

退出码: 0 = 通过, 1 = 发现违规
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# 开发机/服务器绝对路径模式（Windows + Unix）
ABS_PATTERNS = [
    re.compile(r"['\"`]([A-Za-z]:[/\\\\][^'\"`]*?)['\"`]"),  # D:/ D:\ C:\
    re.compile(r"['\"`](/srv/|/home/|/root/|/opt/|/Users/|/var/)[^'\"`]*?['\"`]"),
    re.compile(r"['\"`](/d/|/c/|/e/)[^'\"`]*?['\"`]"),      # MSYS /d/ /c/
]

# 明确的开发机项目根（即使不带引号也应告警的 token）
HARDCODED_ROOTS = [
    "D:/shuntian", "D:\\\\shuntian", "/d/shuntian",
    "D:/today", "D:\\\\today", "/d/today",
    "D:/shuntian-NEW", "E:/shuntian", "E:\\\\shuntian",
]

# 相对定位关键字 —— 命中说明引用了"某个目录下"（需人工判读）
# 不是错误，但审计报告列出供确认
REPORTED_RELATIVE = re.compile(
    r"(?<!\.)Path\(__file__\)|PACKAGE_ROOT|DATA_ROOT|resource_root|RESOURCE_ROOT"
)

# 允许的相对 fixture（测试内 Path(__file__).parent / "fixtures"）
ALLOWED_RELATIVE = (
    ".parent",
    "parents[",
    "__file__",
    "tmp_path",
    '"fixtures"',
    "'fixtures'",
)


def audit_file(path: Path, fix: bool) -> list[str]:
    """审计单个文件，返回违规行描述。"""
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except Exception as e:
        return [f"{path}: 读取失败 {e}"]

    findings: list[str] = []
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        # 跳过纯注释行
        if stripped.startswith("//"):
            continue

        for pat in ABS_PATTERNS:
            m = pat.search(line)
            if m:
                # 跳过合法相对定位: Path(__file__).parent / "fixtures" 等
                if "__file__" in line or "tmp_path" in line:
                    continue
                # 跳过注释中的示例路径（如审计工具自身的文档字符串）
                if "P0 架构红线" in line or "禁止" in line or "不允许" in line:
                    continue
                # 跳过 _REPO_ROOT = Path(__file__) 形式的相对定位（注释里带 # D:/shuntian 说明不算违规）
                if "_REPO_ROOT = Path(__file__)" in line or "parents[" in line:
                    continue
                findings.append(f"{path}:{i}: 绝对路径 {m.group(1)}")
                break
        else:
            for root in HARDCODED_ROOTS:
                if root in line:
                    # 跳过 _REPO_ROOT = Path(__file__) 相对定位后的注释
                    if "parents[" in line and "#" in line:
                        continue
                    findings.append(f"{path}:{i}: 硬编码项目根 {root}")
                    break
    return findings


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", nargs="*", default=["src", "tests", "scripts"])
    ap.add_argument("--fix", action="store_true", help="TODO: 修复模式（预留）")
    args = ap.parse_args()

    all_findings: list[str] = []
    scanned = 0
    for d in args.dir:
        base = REPO_ROOT / d
        if not base.is_dir():
            print(f"[skip] {base} 不存在")
            continue
        for path in sorted(base.rglob("*.py")):
            if "__pycache__" in str(path):
                continue
            scanned += 1
            all_findings.extend(audit_file(path, args.fix))

    print(f"扫描 {scanned} 个 Python 文件")
    print("=" * 60)
    if not all_findings:
        print("✅ PATH INDEPENDENCY AUDIT: PASS — 未发现硬编码绝对路径")
        return 0

    print(f"❌ 发现 {len(all_findings)} 处潜在违规：")
    for f in all_findings:
        print(f"  {f}")
    print("=" * 60)
    print("说明：Path(__file__).parent 相对定位与 settings.* 配置绑定不算违规。")
    return 1


if __name__ == "__main__":
    sys.exit(main())
