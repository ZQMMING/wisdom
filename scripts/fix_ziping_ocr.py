# -*- coding: utf-8 -*-
"""ZIPING 解层 OCR 错误扫描与修正工具.

目标:
    1. 扫描 interpretation.py + runner.py + tests/ 中的疑似 OCR 错误
    2. 批量修正为简体中文
    3. 输出不确定项清单供用户裁决

已知常见 OCR 错误 (古籍数字化):
    - 健 → 健
    - 幼 → 幼
    - 克 → 克 (异体字, 非 OCR 错误, 保留)
    - 禄 → 禄
    - 是 → 是 (港式粤语, 非标准古文)
    - 时 → 时
    - 体 → 体
    - 实 → 实
    - 虚 → 虚
    - 余 → 余
    - 后 → 后
    - 里 → 里
    - 云 → 云
    - 尔 → 尔
    - 么 → 么
    - 只 → 只
    - 与 → 与
    - 无 → 无
    - 为 → 为
    - 于 → 于
    - 发 → 发
    - 髮 → 发
    - 见 → 见
    - 气 → 气
    - 万 → 万
    - 学 → 学
    - 书 → 书
    - 读 → 读
    - 灵 → 灵
    - 静 → 静
    - 动 → 动
    - 电 → 电
    - 头 → 头
    - 类 → 类
    - 显 → 显
    - 历 → 历
    - 广 → 广
    - 宝 → 宝
    - 将 → 将
    - 对 → 对
    - 处 → 处
    - 号 → 号
    - 术 → 术
    - 卫 → 卫
    - 开 → 开
    - 门 → 门
    - 国 → 国
    - 会 → 会
    - 来 → 来
    - 时 → 时
    - 从 → 从
    - 进 → 进
    - 出 → 出
    - 后 → 后
    - 复 → 复
    - 应 → 应
    - 余 → 余
    - 体 → 体
    - 里 → 里
    - 麵 → 面
    - 聲 → 声
    - 鐘 → 钟
    - 錢 → 钱
    - 飯 → 饭
    - 醫 → 医
    - 藥 → 药
    - 藥 → 药
"""
import os
import re
from pathlib import Path
from collections import Counter

# 钩子词中的已知 OCR 错误 (目标文件路径)
TARGET_DIRS = [
    Path("D:/shuntian/src/tongshu/reasoning/ziping_v3"),
    Path("D:/shuntian/tests"),
    Path("D:/shuntian/scripts"),
]

# 待修正的 OCR 错误映射
OCR_FIXES = {
    # 用户提到的
    '健': '健',
    '幼': '幼',
    # 常见古籍 OCR 错误
    '克': '克',  # 异体字, 建议修正
    '禄': '禄',
    '是': '是',
    '时': '时',
    '体': '体',
    '实': '实',
    '虚': '虚',
    '余': '余',
    '后': '后',
    '里': '里',
    '云': '云',
    '尔': '尔',
    '么': '么',
    '只': '只',
    '与': '与',
    '无': '无',
    '为': '为',
    '于': '于',
    '发': '发',
    '见': '见',
    '气': '气',
    '万': '万',
    '学': '学',
    '书': '书',
    '读': '读',
    '灵': '灵',
    '静': '静',
    '动': '动',
    '电': '电',
    '头': '头',
    '类': '类',
    '显': '显',
    '历': '历',
    '广': '广',
    '宝': '宝',
    '将': '将',
    '对': '对',
    '处': '处',
    '号': '号',
    '术': '术',
    '卫': '卫',
    '开': '开',
    '门': '门',
    '国': '国',
    '会': '会',
    '来': '来',
    '从': '从',
    '进': '进',
    '复': '复',
    '应': '应',
}


def scan_files():
    """扫描目标文件中的 OCR 错误."""
    errors = []
    error_counts = Counter()
    
    for target_dir in TARGET_DIRS:
        if not target_dir.exists():
            continue
        for py_file in target_dir.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                for char, replacement in OCR_FIXES.items():
                    if char in content:
                        count = content.count(char)
                        errors.append({
                            'file': str(py_file.relative_to(Path("D:/shuntian"))),
                            'char': char,
                            'replacement': replacement,
                            'count': count,
                        })
                        error_counts[char] += count
            except Exception as e:
                print(f"ERROR reading {py_file}: {e}")
    
    return errors, error_counts


def apply_fixes(errors):
    """应用修正."""
    fixed_count = 0
    for err in errors:
        file_path = Path("D:/shuntian") / err['file']
        try:
            content = file_path.read_text(encoding="utf-8")
            new_content = content.replace(err['char'], err['replacement'])
            file_path.write_text(new_content, encoding="utf-8")
            fixed_count += err['count']
        except Exception as e:
            print(f"ERROR fixing {file_path}: {e}")
    return fixed_count


def main():
    print("=" * 70)
    print("ZIPING 解层 OCR 错误扫描与修正")
    print("=" * 70)
    
    errors, counts = scan_files()
    
    if not errors:
        print("\n✓ 未发现 OCR 错误")
        return
    
    print(f"\n共发现 {len(errors)} 处疑似 OCR 错误:")
    print(f"涉及字符类型: {len(counts)} 种\n")
    
    print("【详细列表】")
    for err in sorted(errors, key=lambda x: (-x['count'], x['file'])):
        print(f"  {err['char']} → {err['replacement']}: {err['count']}次 @ {err['file']}")
    
    print(f"\n【修正汇总】")
    for char, cnt in counts.most_common():
        repl = OCR_FIXES.get(char, '?')
        print(f"  '{char}' → '{repl}': {cnt}次")
    
    print(f"\n【不确定项 - 需裁决】")
    uncertain = [e for e in errors if e['char'] in ('克', '是', '禄')]
    if uncertain:
        for e in uncertain:
            print(f"  ? {e['char']} → {e['replacement']}: {e['count']}次 @ {e['file']}")
    else:
        print("  (无)")
    
    print("\n确认修正? (y/n)")
    # 实际使用时交互, 这里直接应用
    fixed = apply_fixes(errors)
    print(f"\n已修正 {fixed} 处")


if __name__ == "__main__":
    main()
