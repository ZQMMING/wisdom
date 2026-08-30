# -*- coding: utf-8 -*-
"""修复p0_8_7扩展数据的min_truth格式"""

import json
import os

def fix_min_truth_format(filepath: str) -> int:
    """修复min_truth格式，移除'→ 成立（仅此结论）'后缀"""
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assertions = data.get('verified_assertions', [])
    fixed_count = 0
    
    for assertion in assertions:
        original_min_truth = assertion.get('min_truth', '')
        
        # 移除'→ 成立（仅此结论）'后缀
        if '→ 成立（仅此结论）' in original_min_truth:
            new_min_truth = original_min_truth.replace('→ 成立（仅此结论）', '')
            assertion['min_truth'] = new_min_truth
            fixed_count += 1
            print(f"  ✓ {assertion['passage_id']}: {original_min_truth} → {new_min_truth}")
        elif '→' in original_min_truth and '仅此结论' in original_min_truth:
            # 其他变体
            new_min_truth = original_min_truth.split('→')[0].strip()
            assertion['min_truth'] = new_min_truth
            fixed_count += 1
            print(f"  ✓ {assertion['passage_id']}: {original_min_truth} → {new_min_truth}")
    
    # 保存修复后的数据
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    return fixed_count


def main():
    print("="*70)
    print("修复p0_8_7扩展数据的min_truth格式")
    print("="*70)
    
    filepath = r'D:\shuntian\backend\data\p0_8_7_expansion.json'
    
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return
    
    print(f"\n▶ 修复前检查:")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assertions = data.get('verified_assertions', [])
    print(f"  总断言: {len(assertions)}条")
    
    count_with_suffix = sum(1 for a in assertions if '→ 成立' in a.get('min_truth', ''))
    print(f"  含'→ 成立'后缀: {count_with_suffix}条")
    
    print(f"\n▶ 开始修复...")
    fixed_count = fix_min_truth_format(filepath)
    
    print(f"\n▶ 修复完成:")
    print(f"  修复数量: {fixed_count}条")
    
    # 验证修复结果
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assertions = data.get('verified_assertions', [])
    count_after = sum(1 for a in assertions if '→ 成立' in a.get('min_truth', ''))
    
    print(f"\n▶ 修复后验证:")
    print(f"  仍含'→ 成立'后缀: {count_after}条")
    
    if count_after == 0:
        print(f"\n✅ 所有min_truth已精简为真正最小命题")
    else:
        print(f"\n⚠️ 仍有{count_after}条未修复")
    
    print("\n" + "="*70)
    print("核心结论")
    print("="*70)
    
    print(f"\n【修复统计】")
    print(f"  总断言: {len(assertions)}条")
    print(f"  已修复: {fixed_count}条")
    print(f"  剩余问题: {count_after}条")
    
    print(f"\n【下一步】")
    if count_after == 0:
        print(f"  ✓ 可以重新运行P0-8.9质量审计")
    else:
        print(f"  ⚠️ 需要进一步手动修复剩余{count_after}条")


if __name__ == '__main__':
    main()
