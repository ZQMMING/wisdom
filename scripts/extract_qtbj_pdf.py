#!/usr/bin/env python3
"""提取 QTBJ 缺失日干调候"""

import pdfplumber
from pathlib import Path

pdf_path = Path("D:/顺天系统资料/书籍典故资料/穷通宝鉴_余春台.pdf")
output_path = Path("/d/shuntian/QTBJ_missing_days.md")

print(f"📖 打开 PDF: {pdf_path}")
print(f"文件大小: {pdf_path.stat().st_size / 1024:.1f} KB")
print()

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"总页数: {len(pdf.pages)}")
        
        missing_days = ["甲日", "乙日", "戊日", "己日", "庚日"]
        
        extracted = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            for day in missing_days:
                if day in text:
                    extracted.append({
                        "page": i+1,
                        "day": day,
                        "text": text[:800]
                    })
                    break
        
        print(f"找到 {len(extracted)} 页缺失日干内容")
        
        # 保存
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# QTBJ 缺失日干调候提取结果\n\n")
            for item in extracted:
                f.write(f"## {item['day']} (第{item['page']}页)\n\n")
                f.write(item['text'] + "\n\n---\n\n")
        
        print(f"✅ 已保存到: {output_path}")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
