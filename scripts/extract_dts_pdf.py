#!/usr/bin/env python3
"""提取 DTS 缺失通神论"""

import pdfplumber
from pathlib import Path

pdf_path = Path("D:/顺天系统资料/书籍典故资料/滴天髓_任铁樵.pdf")
output_path = Path("/d/shuntian/DTS_missing_chapters.md")

print(f"📖 打开 PDF: {pdf_path}")
print(f"文件大小: {pdf_path.stat().st_size / 1024:.1f} KB")
print()

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"总页数: {len(pdf.pages)}")
        
        missing_chapters = ["气血", "根蒂", "化元", "流运", "父丧", "母丧", "杂格局", "音律", "品貌", "进程", "关格", "玄关"]
        
        extracted = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            for chapter in missing_chapters:
                if chapter in text:
                    extracted.append({
                        "page": i+1,
                        "chapter": chapter,
                        "text": text[:800]
                    })
                    break
        
        print(f"找到 {len(extracted)} 页通神论内容")
        
        # 保存
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# DTS 缺失通神论提取结果\n\n")
            for item in extracted:
                f.write(f"## 第{item['chapter']}篇 (第{item['page']}页)\n\n")
                f.write(item['text'] + "\n\n---\n\n")
        
        print(f"✅ 已保存到: {output_path}")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
