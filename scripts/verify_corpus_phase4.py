#!/usr/bin/env python3
"""Phase 4: BOT-CORPUS 五部经典全面验证 - 快速验证脚本"""
import json
from pathlib import Path

def main():
    classics_path = Path('data/classics/original')
    evidence_path = Path('data/evidence')
    
    print("=" * 60)
    print("BOT-CORPUS Phase 4 全面验证报告")
    print("=" * 60)
    
    # 1. 原始数据统计
    print("\n[1] 原始数据统计")
    classics_data = {}
    for f in classics_path.glob('*段落数据.json'):
        if '_merged' in f.name or f.name.startswith('_'):
            continue
        data = json.load(open(f, encoding='utf-8'))
        name = f.stem.replace('_段落数据', '')
        count = len(data.get('passages', data) if isinstance(data, dict) else data)
        classics_data[name] = count
        print(f"  {name}: {count} 条")
    
    total_original = sum(classics_data.values())
    print(f"  总计: {total_original} 条")
    
    # 2. 证据文件统计
    print("\n[2] 证据文件统计")
    evidence_stats = {}
    for d in ['di_tian_sui', 'ziping_zhenquan', 'qiong_tong_bao_jian', 'san_ming_tong_hui', 'yuan_hai_zi_ping']:
        path = evidence_path / d
        if path.exists():
            files = list(path.glob('E-*.json'))
            evidence_stats[d] = len(files)
            print(f"  {d}: {len(files)} 个文件")
    
    total_evidence = sum(evidence_stats.values())
    print(f"  总计: {total_evidence} 个证据文件")
    
    # 3. 覆盖度分析
    print("\n[3] 覆盖度分析")
    coverage_map = {
        'DTS_滴天髓': 'di_tian_sui',
        'PZZQ_子平真诠': 'ziping_zhenquan',
        'QTBJ_穷通宝鉴': 'qiong_tong_bao_jian',
        'SMTH_三命通会': 'san_ming_tong_hui',
        'YHZP_渊海子平': 'yuan_hai_zi_ping'
    }
    
    print(f"  {'经典':<12} {'原始':>8} {'证据':>8} {'覆盖率':>10}")
    print("  " + "-" * 42)
    
    for orig_name, evid_key in coverage_map.items():
        orig_count = classics_data.get(orig_name.replace('_', ''), 0)
        # 修正映射
        if '滴天髓' in orig_name:
            orig_count = classics_data.get('滴天髓', 0)
        elif '子平真诠' in orig_name:
            orig_count = classics_data.get('子平真诠', 0)
        elif '穷通宝鉴' in orig_name:
            orig_count = classics_data.get('穷通宝鉴', 0)
        elif '三命通会' in orig_name:
            orig_count = classics_data.get('三命通会', 0)
        elif '渊海子平' in orig_name:
            orig_count = classics_data.get('渊海子平', 0)
        
        evid_count = evidence_stats.get(evid_key, 0)
        coverage = f"{evid_count/orig_count*100:.1f}%" if orig_count > 0 else "N/A"
        print(f"  {orig_name:<12} {orig_count:>8} {evid_count:>8} {coverage:>10}")
    
    # 4. 证据质量抽样
    print("\n[4] 证据质量抽样验证")
    sample_files = list(evidence_path.rglob('E-*.json'))[:5]
    for f in sample_files:
        data = json.load(open(f, encoding='utf-8'))
        status = data.get('verification_status', 'UNKNOWN')
        strength = data.get('evidence_strength', 'UNKNOWN')
        print(f"  {f.name}: status={status}, strength={strength}")
    
    print("\n" + "=" * 60)
    print("验证完成！")
    print("=" * 60)

if __name__ == '__main__':
    main()
