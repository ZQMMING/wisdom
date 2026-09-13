#!/usr/bin/env python3
"""QTBJ 己日调候提取脚本"""
import pdfplumber
from pathlib import Path

pdf_path = Path("D:/顺天系统资料/书籍典故资料/穷通宝鉴_余春台.pdf")
output_path = Path("/d/shuntian/QTBJ_ji_day_extract.md")

print("📖 提取 QTBJ 己日调候内容...")

try:
    with pdfplumber.open(pdf_path) as pdf:
        extracted = []
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            if "己日" in text or "己土" in text:
                # 找到上下文
                idx = text.find("己日") if "己日" in text else text.find("己土")
                start = max(0, idx - 200)
                end = min(len(text), idx + 600)
                context = text[start:end]
                extracted.append({
                    "page": i+1,
                    "context": context
                })
                if len(extracted) >= 5:
                    break
        
        print(f"找到 {len(extracted)} 页相关内容")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            for item in extracted:
                f.write(f"## 第{item['page']}页\n\n")
                f.write(item['context'])
                f.write("\n\n---\n\n")
        
        print(f"✅ 已保存到: {output_path}")
        
except Exception as e:
    print(f"❌ 错误: {e}")
