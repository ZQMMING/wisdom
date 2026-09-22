# -*- coding: utf-8 -*-
"""验证sources.dts.jsonl是从哪个版本切片的"""
import json, re, collections as c
from pathlib import Path
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

JSONL = Path(r"D:\shuntian-ziping-p0\registries\source\sources.dts.jsonl")
DTS_LIU = Path(r"D:\顺天系统资料\豆包资料\六部经典校对版\DTS_滴天髓_原文合原注_京图撰刘基注.md")
DTS_REN = Path(r"D:\顺天系统资料\豆包资料\六部经典校对版\纯原著\DTS_滴天髓阐微_任铁樵注_纯原著.md")

REN_MARKERS = [r"任氏曰", r"铁樵按", r"铁樵曰", r"从旺者", r"从强者", r"从气者", r"从势者", r"任铁樵"]

def count_chapters(md_path):
    """粗略统计章节数"""
    txt = md_path.read_text(encoding="utf-8")
    # 以 "第.*章" 或数字章节计数
    return len(re.findall(r"(?m)^#+\s*(?:第[一二三四五六七八九十\d]+章|\d+[.、])", txt))

def count_chapters_simple(md_path):
    """更简单的章节统计"""
    txt = md_path.read_text(encoding="utf-8")
    # 统计"第X章"出现次数
    return len(re.findall(r"第[一二三四五六七八九十\d]+章", txt))

def main():
    print("=" * 60)
    print("DTS版本审计")
    print("=" * 60)
    
    # 1. 源文件章节数
    print("\n【1. 源文件章节数】")
    print(f"  刘基注版: {count_chapters_simple(DTS_LIU)} 章")
    print(f"  任氏版: {count_chapters_simple(DTS_REN)} 章")
    
    # 2. jsonl统计
    print("\n【2. sources.dts.jsonl 统计】")
    chapters = set()
    layers = c.Counter()
    books = c.Counter()
    hits = []
    total_chars = 0
    
    for i, line in enumerate(JSONL.read_text(encoding="utf-8").splitlines()):
        if not line.strip():
            continue
        rec = json.loads(line)
        chapters.add(rec.get("chapter") or rec.get("loc", ""))
        layers[rec.get("text_layer")] += 1
        books[rec.get("source_book", "")] += 1
        txt = str(rec.get("text", ""))
        total_chars += len(txt)
        
        for p in REN_MARKERS:
            if re.search(p, txt):
                hits.append((i+1, p, txt[:80]))
                break
    
    print(f"  总记录数: {sum(layers.values())}")
    print(f"  总字符数: {total_chars:,}")
    print(f"  章节(去重)数: {len(chapters)}")
    print(f"  text_layer 分布: {dict(layers)}")
    print(f"  source_book 分布: {dict(books)}")
    
    # 3. 任氏标记命中
    print("\n【3. 任氏标记命中】")
    print(f"  命中条数: {len(hits)}")
    if hits:
        print("  前10条样本:")
        for ln, p, s in hits[:10]:
            print(f"    line {ln:5d} [{p}] {s}")
    
    # 4. 结论
    print("\n【4. 结论】")
    if len(hits) > 0:
        print("  ❌ 疑似混入任氏版")
    else:
        print("  ✅ 未见任氏标记")
    
    # 章节数对比
    print(f"\n  章节数对比: jsonl={len(chapters)}, 刘基注版={count_chapters_simple(DTS_LIU)}, 任氏版={count_chapters_simple(DTS_REN)}")
    if abs(len(chapters) - count_chapters_simple(DTS_LIU)) < 10:
        print("  ✅ 章节数接近刘基注版")
    elif abs(len(chapters) - count_chapters_simple(DTS_REN)) < 10:
        print("  ❌ 章节数接近任氏版")
    else:
        print("  ⚠️ 章节数两者都不接近，需人工核对")

if __name__ == "__main__":
    main()
