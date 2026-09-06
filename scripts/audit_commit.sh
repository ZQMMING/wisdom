#!/bin/bash
# 边界审计脚本
# 用法: ./scripts/audit_commit.sh [commit] [base]

COMMIT=${1:-HEAD}
BASE=${2:-main}

echo "=== 边界审计 ==="
echo "Commit: $COMMIT"
echo "Base: $BASE"
echo ""

# 获取变更文件列表
CHANGED_FILES=$(git diff $BASE...$COMMIT --name-only 2>/dev/null || git diff $BASE...$COMMIT --name-only)

if [ -z "$CHANGED_FILES" ]; then
    echo "⚠️  无变更文件或无法比较"
    exit 1
fi

echo "变更文件 ($(echo "$CHANGED_FILES" | wc -l) 个):"
echo "$CHANGED_FILES"
echo ""

# 检查是否包含其他引擎代码
BLOCKED=false
BLOCKED_FILES=""

while IFS= read -r file; do
    # BAZI引擎保护（八字排盘）
    if [[ "$file" == src/tongshu/engines/bazi/* ]] && ! [[ "$file" == src/tongshu/engines/bazi_engine* ]]; then
        BLOCKED=true
        BLOCKED_FILES="$BLOCKED_FILES\n  ❌ $file (八字排盘保护)"
    fi
    
    # ZIWEI引擎保护（紫微斗数）
    if [[ "$file" == src/tongshu/engines/ziwei/* ]] || [[ "$file" == *ziwei* ]]; then
        BLOCKED=true
        BLOCKED_FILES="$BLOCKED_FILES\n  ❌ $file (紫微斗数保护)"
    fi
    
    # ZIPING引擎保护（子平辨层）
    if [[ "$file" == src/tongshu/engines/zi_ping* ]] || [[ "$file" == *zi_ping* ]] || [[ "$file" == src/tongshu/reasoning/* ]]; then
        BLOCKED=true
        BLOCKED_FILES="$BLOCKED_FILES\n  ❌ $file (子平辨层保护)"
    fi
    
    # HELUO引擎保护（河洛理数）
    if [[ "$file" == src/tongshu/engines/heluo/* ]]; then
        BLOCKED=true
        BLOCKED_FILES="$BLOCKED_FILES\n  ❌ $file (河洛理数保护)"
    fi
    
    # YI引擎保护（易经卦象）
    if [[ "$file" == src/tongshu/engines/yi/* ]]; then
        BLOCKED=true
        BLOCKED_FILES="$BLOCKED_FILES\n  ❌ $file (易经卦象保护)"
    fi
    
    # BLIND引擎保护（盲派）
    if [[ "$file" == src/tongshu/engines/blind* ]] || [[ "$file" == *blind* ]]; then
        BLOCKED=true
        BLOCKED_FILES="$BLOCKED_FILES\n  ❌ $file (盲派保护)"
    fi
    
    # Golden Dataset保护
    if [[ "$file" == cases/golden/* ]]; then
        BLOCKED=true
        BLOCKED_FILES="$BLOCKED_FILES\n  ❌ $file (Golden Dataset保护)"
    fi
    
    # Evidence数据保护（除非是CORPUS引擎）
    if [[ "$file" == data/evidence/* ]] && ! [[ "$file" == data/evidence/di_tian_sui/* ]] && ! [[ "$file" == data/evidence/qiong_tong_bao_jian/* ]] && ! [[ "$file" == data/evidence/yuan_hai_zi_ping/* ]] && ! [[ "$file" == data/evidence/san_ming_tong_hui/* ]] && ! [[ "$file" == data/evidence/ziping_zhenquan/* ]]; then
        BLOCKED=true
        BLOCKED_FILES="$BLOCKED_FILES\n  ❌ $file (Evidence保护)"
    fi
    
done <<< "$CHANGED_FILES"

echo "=== 审计结果 ==="

if [ "$BLOCKED" = true ]; then
    echo ""
    echo "🚫 COMMIT BLOCKED: 发现越界文件"
    echo -e "$BLOCKED_FILES"
    echo ""
    echo "请检查commit内容，确保只修改本引擎代码"
    exit 1
else
    echo "✅ 边界审计通过"
    echo "变更文件均在本引擎允许范围内"
    exit 0
fi
