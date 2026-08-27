# -*- coding: utf-8 -*-
"""傅佩荣64卦多维度断言解析器.

从 D:\today\大师文集\傅佩荣\Book-of-Changes-master\*_cn.md 中提取:
- 时运/财运/家宅/事业/婚恋/疾病/诉讼/出行 等多维度断言
- 卦辞/象传/彖传/爻辞

输出: data/tiaohou/fupeirong_64gua_dimensions.json
"""
from __future__ import annotations

import json
import re
from pathlib import Path

# 源目录
SOURCE_DIR = Path(r"D:\today\大师文集\傅佩荣\Book-of-Changes-master")
# 输出文件
OUTPUT_FILE = Path("data/tiaohou/fupeirong_64gua_dimensions.json")

# 多维度关键词
DIMENSIONS = {
    "时运": "fortune",
    "财运": "wealth",
    "家宅": "home",
    "事业": "career",
    "婚恋": "marriage",
    "疾病": "health",
    "诉讼": "lawsuit",
    "出行": "travel",
}

# 卦名映射(从文件名URL编码→中文)
# 文件名格式: e4b8ade5ad9azhongfu_cn.md (URL编码的hex)
def url_decode_filename(filename: str) -> str:
    """从URL编码文件名提取卦名."""
    # 去掉_cn.md后缀
    name = filename.replace("_cn.md", "")
    # 将e4b8ad...转为bytes再decode为utf-8
    try:
        # 每两个hex字符为一个byte
        hex_str = name.replace("e", " e").strip()
        # 更简单的方法: 直接用bytes.fromhex
        raw = bytes.fromhex(name)
        return raw.decode("utf-8")
    except Exception:
        return name


def parse_gua_file(filepath: Path) -> dict:
    """解析单个卦文件, 提取多维度断言."""
    content = filepath.read_text(encoding="utf-8", errors="ignore")
    lines = content.split("\n")

    result = {
        "name": "",
        "number": 0,
        "symbol": "",
        "gua_ci": "",
        "xiang_zhuan": "",
        "tuan_zhuan": "",
        "yao_ci": [],
        "dimensions": {},  # 多维度断言
    }

    # 提取卦名(第一行 # 卦名)
    for line in lines[:10]:
        m = re.match(r"^#\s+(.+?)\s*[䷀-䷿]?\s*$", line)
        if m:
            result["name"] = m.group(1).strip()
            break

    # 提取卦序
    for line in lines[:30]:
        m = re.search(r"卦序[：:]\s*(\d+)", line)
        if m:
            result["number"] = int(m.group(1))
            break

    # 提取卦象符号
    for line in lines[:10]:
        m = re.search(r"[䷀-䷿]", line)
        if m:
            result["symbol"] = m.group(0)
            break

    # 提取卦辞
    in_guaci = False
    guaci_lines = []
    for line in lines:
        if "卦辞原文" in line:
            in_guaci = True
            continue
        if in_guaci:
            if line.startswith("```") or line.startswith("###") or line.startswith("##"):
                if guaci_lines:
                    result["gua_ci"] = "\n".join(guaci_lines).strip()
                in_guaci = False
                continue
            if line.strip() and not line.startswith("〖"):
                guaci_lines.append(line.strip())

    # 提取多维度断言 (格式: - 时运：... 或 时运：...)
    current_yao = ""
    for i, line in enumerate(lines):
        # 检测爻位标题
        yao_match = re.match(r"^###?\s*([一二三四五六上初][阴阳])\s*$", line.strip())
        if yao_match:
            current_yao = yao_match.group(1)
            continue

        # 检测多维度断言
        for cn_dim, en_dim in DIMENSIONS.items():
            # 格式1: - 时运：...
            m1 = re.match(rf"^[-*]\s*{cn_dim}[：:]\s*(.+)$", line.strip())
            # 格式2: 时运：...
            m2 = re.match(rf"^{cn_dim}[：:]\s*(.+)$", line.strip())
            m = m1 or m2
            if m:
                text = m.group(1).strip()
                if en_dim not in result["dimensions"]:
                    result["dimensions"][en_dim] = []
                result["dimensions"][en_dim].append({
                    "yao": current_yao,
                    "text": text,
                })

    return result


def main():
    print("=" * 60)
    print("傅佩荣64卦多维度断言解析器")
    print("=" * 60)

    if not SOURCE_DIR.exists():
        print(f"错误: 源目录不存在 {SOURCE_DIR}")
        return

    files = sorted(SOURCE_DIR.glob("*_cn.md"))
    print(f"找到 {len(files)} 个卦文件")

    all_gua = []
    for f in files:
        try:
            gua = parse_gua_file(f)
            if gua["name"]:
                all_gua.append(gua)
                dim_count = sum(len(v) for v in gua["dimensions"].values())
                print(f"  {gua['number']:2d}. {gua['name']:6s} - {dim_count}条多维度断言")
        except Exception as e:
            print(f"  错误: {f.name} - {e}")

    # 按卦序排序
    all_gua.sort(key=lambda x: x["number"])

    # 统计
    total_dims = sum(sum(len(v) for v in g["dimensions"].values()) for g in all_gua)
    print(f"\n总计: {len(all_gua)}卦, {total_dims}条多维度断言")

    # 各维度统计
    dim_stats = {}
    for g in all_gua:
        for dim, items in g["dimensions"].items():
            dim_stats[dim] = dim_stats.get(dim, 0) + len(items)
    print("\n各维度统计:")
    for dim, count in sorted(dim_stats.items(), key=lambda x: -x[1]):
        cn_name = next((k for k, v in DIMENSIONS.items() if v == dim), dim)
        print(f"  {cn_name}({dim}): {count}条")

    # 保存
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    output = {
        "source": "傅佩荣《Book-of-Changes》64卦解读",
        "source_url": "github.com/fortune-fun/Book-of-Changes",
        "total_gua": len(all_gua),
        "total_dimensions": total_dims,
        "dimensions": DIMENSIONS,
        "gua": all_gua,
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n已保存到: {OUTPUT_FILE}")
    print(f"文件大小: {OUTPUT_FILE.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
