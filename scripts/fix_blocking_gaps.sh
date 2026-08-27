#!/bin/bash
# B-1 ~ B-8 blocking gap fixes via bash

set -e

DATA_DIR="/d/today/backend/data"
RULES_DIR="$DATA_DIR/rules"
EVDIR="$DATA_DIR/evidence"
NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "=== 开始修复 B-1 ~ B-8 ==="

# B-1: ZW-405..408 加 execution_enabled=false
echo ""
echo "[B-1] ZW-405..408 execution_enabled=false"
for n in 5 6 7 8; do
    path="$RULES_DIR/ZW-40$n.json"
    if [ -f "$path" ]; then
        # 使用python3添加字段
        /c/Users/ming/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "
import json, sys
path = '$path'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
data['execution_enabled'] = False
data['_fix_note'] = 'M2B1 B-1 fix $NOW: daily_sihua_roles never filled; rule is inert despite status=active'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(f'  ✓ $(basename $path)')
"
    else
        echo "  ✗ $path NOT FOUND"
    fi
done

# B-2: ZPZ-001..005 status=pending, evidence source_layer=engineering_seed
echo ""
echo "[B-2] ZPZ-001..005 → status=pending"
for n in 1 2 3 4 5; do
    # Fix rule
    rpath="$RULES_DIR/ZPZ-$n.json"
    if [ -f "$rpath" ]; then
        /c/Users/ming/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "
import json
path = '$rpath'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
data['status'] = 'pending'
data['_fix_note'] = 'M2B1 B-2 fix $NOW: 工程种子非经典原文直引，status降为pending'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(f'  ✓ $(basename $rpath)')
"
    fi
    
    # Fix evidence
    epath="$EVDIR/E-ZPZ-$n-001.json"
    if [ -f "$epath" ]; then
        /c/Users/ming/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "
import json
path = '$epath'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
if data.get('source_layer') == 'classical_original':
    data['source_layer'] = 'engineering_seed'
    data['_fix_note'] = 'M2B1 B-2 fix $NOW: source_layer修正为engineering_seed'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(f'  ✓ E-ZPZ-$n-001.json')
fi
done

# B-3: QTB-014 自述矛盾固化
echo ""
echo "[B-3] QTB-014 自述矛盾 → engineering_seed"
qtb_path="$RULES_DIR/QTB-014.json"
if [ -f "$qtb_path" ]; then
    /c/Users/ming/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "
import json
path = '$qtb_path'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
data['book_id'] = None
data['concept_id'] = None
data['_fix_note'] = 'M2B1 B-3 fix $NOW: 移除虚假book_id/concept_id；规则为工程种子'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(f'  ✓ QTB-014.json')
"
fi

# B-4: E-ZIWEI-001 虚拟规则显式声明
echo ""
echo "[B-4] E-ZIWEI-001 虚拟规则显式声明"
eziwei_path="$EVDIR/E-ZIWEI-001.json"
if [ -f "$eziwei_path" ]; then
    /c/Users/ming/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "
import json
path = '$eziwei_path'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
data['is_virtual_rule_ref'] = True
data['_fix_note'] = 'M2B1 B-4 fix $NOW: 显式声明rule_refs指向虚拟规则ZIWEI-MAIN-STAR-MAP'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(f'  ✓ E-ZIWEI-001.json')
"
fi

# B-8: 填充10_LEGACY_DEPRECATED
echo ""
echo "[B-8] 填充10_LEGACY_DEPRECATED"
LEGACY_DIR="/c/Users/ming/Documents/kimi/workspace/词库V4.0/10_LEGACY — 遗留资产层"
mkdir -p "$LEGACY_DIR"
legacy_index="$LEGACY_DIR/10_LEGACY_DEPRECATED.json"

if [ ! -f "$legacy_index" ]; then
    cat > "$legacy_index" << 'LEGACY_EOF'
{
  "generated": "TIMESTAMP",
  "total": 4,
  "items": [
    {
      "legacy_id": "LEG-001",
      "type": "orphan_semantic",
      "description": "07_PRODUCT_THEMES中7个零引用SEM标签",
      "recommendation": "裁定删除或接入",
      "audit_ref": "M2B1 L-4"
    },
    {
      "legacy_id": "LEG-002",
      "type": "empty_registry",
      "description": "10_LEGACY_DEPRECATED空占位",
      "recommendation": "本条目即为填充结果",
      "audit_ref": "M2B1 B-8"
    },
    {
      "legacy_id": "LEG-003",
      "type": "unmapped_expression",
      "description": "09_EXPRESSION_LIBRARY中49条无semantic_refs表达式",
      "recommendation": "逐条裁定：回填semantic_refs或降级为纯文案",
      "audit_ref": "M2B1 L-5"
    },
    {
      "legacy_id": "LEG-004",
      "type": "field_mismatch",
      "description": "08_ACTION_REGISTRY中6个THEME_*值与theme词表不一致",
      "recommendation": "统一为THEME_XING/THEME_SHI等六主题ASCII",
      "audit_ref": "M2B1 L-2"
    }
  ]
}
LEGACY_EOF
    # 替换时间戳
    sed -i "s/TIMESTAMP/$NOW/" "$legacy_index"
    echo "  ✓ 填充 4 条遗留资产"
else
    echo "  - 已存在，无需新增"
fi

# 桥接: 运行时MAP添加词库anchor
echo ""
echo "[BRIDGE] 运行时MAP添加词库anchor字段"
mappings_dir="$DATA_DIR/mappings"
bridge_map=(
    "MAP-1001:BAZI_SEM_POSHENG"
    "MAP-1002:BAZI_SEM_PIANZHENG"
    "MAP-1003:BAZI_SEM_ZHENGCAI"
    "MAP-1004:BAZI_SEM_PIANCAI"
    "MAP-1005:BAZI_SEM_SHISHEN"
    "MAP-1006:BAZI_SEM_SHANGGUAN"
    "MAP-1007:BAZI_SEM_ZHIGUAN"
    "MAP-1008:BAZI_SEM_QISHA"
    "MAP-1009:BAZI_SEM_XIONGDI"
    "MAP-1010:BAZI_SEM_JIECAI"
)

for entry in "${bridge_map[@]}"; do
    mid="${entry%%:*}"
    anchor="${entry##*:}"
    path="$mappings_dir/$mid.json"
    if [ -f "$path" ]; then
        /c/Users/ming/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "
import json
path = '$path'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
data['lexicon_anchor'] = '$anchor'
data['_bridge_note'] = 'M2B1 BRIDGE fix $NOW: 桥接词库DELIVERABLES 04_MAPPING_REGISTRY命名空间'
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(f'  ✓ $mid.json')
"
    else
        echo "  ✗ $mid.json NOT FOUND"
    fi
done

# 创建词表统一映射表
echo ""
echo "[UNIFY] 创建词表统一映射表"
unify_path="$DATA_DIR/knowledge/theme_context_tone_unified.json"
mkdir -p "$(dirname "$unify_path")"

/c/Users/ming/AppData/Local/hermes/hermes-agent/venv/Scripts/python.exe -c "
import json
path = '$unify_path'
data = {
    'generated': '$NOW',
    'purpose': '统一三套theme/context/tone词表',
    'theme_mapping': {
        'WORK': 'THEME_SHI',
        'RELATION': 'THEME_REN',
        'EMOTION': 'THEME_YANG',
        'LEARNING': 'THEME_SHI',
        'FAMILY_SOCIAL': 'THEME_REN',
        'ACTION_LIFE': 'THEME_XING'
    },
    'tone_recommendation': '运行时取warm/restrained/neutral/scholarly；词库calm_modern对齐restrained'
}
with open(path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
    f.write('\n')
print(f'  ✓ $(basename $unify_path)')
"

echo ""
echo "✅ 全部修复完成"
