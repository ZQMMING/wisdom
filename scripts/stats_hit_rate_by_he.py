# -*- coding: utf-8 -*-
"""分层命中率统计: 带天干五合vs不带天干五合"""
import sys
sys.path.insert(0, '.')
sys.path.insert(0, 'scripts')

from scripts.dayun_align import cases, engine

# 统计: 带五合组 vs 不带五合组的命中率
stats = {
    'has_he': {'total': 0, 'agree': 0},
    'no_he': {'total': 0, 'agree': 0},
    'by_distance': {
        'adjacent': {'total': 0, 'agree': 0},
        'one_apart': {'total': 0, 'agree': 0},
        'remote': {'total': 0, 'agree': 0},
    },
}

# 从dayun_align的输出中提取对齐结果
# 直接遍历cases, 用engine()判断是否命中
# 对齐判断逻辑: 大运五行是否在fav/av中

for li, fp, dy, txt in cases:
    try:
        p, f, ye, tp0, wp, th = engine(fp)
        has_he = len(th.get('he_pairs', [])) > 0
        
        # 简化对齐判断: 用ye(用神引擎)的fav/av
        fav = set(ye.get('fav', []))
        av = set(ye.get('av', []))
        
        # 大运五行
        dy_wx = {'甲乙': '木', '丙丁': '火', '戊己': '土', '庚辛': '金', '壬癸': '水'}
        for gs, wx in dy_wx.items():
            if dy[0] in gs:
                dy_element = wx
                break
        
        # 判断: 命中=大运五行在fav或av中
        hit = (dy_element in fav) or (dy_element in av)
        
        if has_he:
            stats['has_he']['total'] += 1
            if hit:
                stats['has_he']['agree'] += 1
            # 按位置分层(取最远的合对)
            max_dist = 'adjacent'
            for pair in th['he_pairs']:
                d = pair.get('position_distance', 'adjacent')
                if d == 'remote':
                    max_dist = 'remote'
                elif d == 'one_apart' and max_dist != 'remote':
                    max_dist = 'one_apart'
            stats['by_distance'][max_dist]['total'] += 1
            if hit:
                stats['by_distance'][max_dist]['agree'] += 1
        else:
            stats['no_he']['total'] += 1
            if hit:
                stats['no_he']['agree'] += 1
    except Exception:
        pass

print('=== 分层命中率统计 ===')
print()
print('带天干五合组:')
print('  总数: {}, 命中: {} ({:.1f}%)'.format(
    stats['has_he']['total'], stats['has_he']['agree'],
    stats['has_he']['agree']/max(stats['has_he']['total'],1)*100))
print()
print('不带天干五合组:')
print('  总数: {}, 命中: {} ({:.1f}%)'.format(
    stats['no_he']['total'], stats['no_he']['agree'],
    stats['no_he']['agree']/max(stats['no_he']['total'],1)*100))
print()
print('差异: {:.1f}pp'.format(
    stats['has_he']['agree']/max(stats['has_he']['total'],1)*100 - 
    stats['no_he']['agree']/max(stats['no_he']['total'],1)*100))
print()
print('按位置距离分层:')
for dist in ['adjacent', 'one_apart', 'remote']:
    s = stats['by_distance'][dist]
    print('  {}: 总数{}, 命中{} ({:.1f}%)'.format(
        dist, s['total'], s['agree'],
        s['agree']/max(s['total'],1)*100))
