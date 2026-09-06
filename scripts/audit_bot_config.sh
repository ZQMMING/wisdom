#!/bin/bash
# Bot配置深度审计脚本
# 用法: bash scripts/audit_bot_config.sh [bot-name]

BOT_NAME=${1:-all}
ERRORS=0
WARNINGS=0

echo "=== Bot配置深度审计 ==="
echo "目标Bot: $BOT_NAME"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 定义Bot配置映射
declare -A BOT_ENGINES=(
    ["bazi"]="src/tongshu/engines/bazi/"
    ["ziping"]="src/tongshu/engines/zi_ping_engine.py"
    ["blind"]="src/tongshu/engines/blind/"
    ["ziwei"]="src/tongshu/engines/ziwei/"
    ["heluo"]="src/tongshu/engines/heluo/"
    ["yi"]="src/tongshu/engines/yi/"
    ["corpus"]="data/classics/"
)

declare -A BOT_TESTS=(
    ["bazi"]="tests/test_bazi*.py tests/test_time*.py"
    ["ziping"]="tests/test_phase3*.py tests/test_yi/*.py"
    ["blind"]="tests/test_blind*.py"
    ["ziwei"]="tests/test_ziwei*.py"
    ["heluo"]="tests/test_heluo*.py"
    ["yi"]="tests/yi/"
    ["corpus"]="tests/test_corpus*.py tests/test_full_classification.py"
)

declare -A BOT_EVIDENCE=(
    ["bazi"]="data/evidence/di_tian_sui/ data/evidence/qiong_tong_bao_jian/ data/evidence/yuan_hai_zi_ping/ data/evidence/san_ming_tong_hui/ data/evidence/ziping_zhenquan/"
    ["ziping"]="data/evidence/di_tian_sui/ data/evidence/qiong_tong_bao_jian/ data/evidence/yuan_hai_zi_ping/ data/evidence/san_ming_tong_hui/ data/evidence/ziping_zhenquan/"
    ["blind"]="data/evidence/blind_seg/"
    ["ziwei"]="data/evidence/ziwei/"
    ["heluo"]="data/evidence/heluo/"
    ["yi"]="data/evidence/yi/"
    ["corpus"]="data/evidence/"
)

declare -A BOT_DOCS=(
    ["bazi"]="docs/bots/BOT-BAZI/"
    ["ziping"]="docs/bots/BOT-ZIPING/"
    ["blind"]="docs/bots/BOT-BLIND/"
    ["ziwei"]="docs/bots/BOT-ZIWEI/"
    ["heluo"]="docs/bots/BOT-HELUO/"
    ["yi"]="docs/bots/BOT-YI/"
    ["corpus"]="docs/bots/BOT-CORPUS/"
)

# 审计函数
audit_bot() {
    local bot=$1
    echo "--- 审计 $bot ---"
    
    # 1. 检查引擎文件
    local engine_path="${BOT_ENGINES[$bot]}"
    if [ -d "$engine_path" ]; then
        local file_count=$(find "$engine_path" -name "*.py" -type f | wc -l)
        echo "  ✅ 引擎目录存在: $engine_path ($file_count个Python文件)"
    elif [ -f "$engine_path" ]; then
        echo "  ✅ 引擎文件存在: $engine_path"
    else
        echo "  ❌ 引擎路径不存在: $engine_path"
        ((ERRORS++))
    fi
    
    # 2. 检查测试文件
    local test_pattern="${BOT_TESTS[$bot]}"
    local test_count=$(ls tests/$(echo $test_pattern | sed 's/tests\///') 2>/dev/null | wc -l)
    if [ $test_count -gt 0 ]; then
        echo "  ✅ 测试文件存在: $test_count个"
    else
        echo "  ⚠️  测试文件可能缺失: $test_pattern"
        ((WARNINGS++))
    fi
    
    # 3. 检查证据目录
    local evidence_paths="${BOT_EVIDENCE[$bot]}"
    for ev_path in $evidence_paths; do
        if [ -d "$ev_path" ]; then
            local file_count=$(find "$ev_path" -name "*.json" -type f | wc -l)
            echo "  ✅ 证据目录存在: $ev_path ($file_count个JSON文件)"
        else
            echo "  ⚠️  证据目录不存在: $ev_path"
            ((WARNINGS++))
        fi
    done
    
    # 4. 检查文档目录
    local doc_path="${BOT_DOCS[$bot]}"
    if [ -d "$doc_path" ]; then
        local doc_count=$(find "$doc_path" -name "*.md" -type f | wc -l)
        echo "  ✅ 文档目录存在: $doc_path ($doc_count个Markdown文件)"
    else
        echo "  ❌ 文档目录不存在: $doc_path"
        ((ERRORS++))
    fi
    
    # 5. 检查Git分支
    local branch_pattern="agent/$bot-*"
    local branch_count=$(git branch --list "$branch_pattern" | wc -l)
    echo "  📝 Agent分支: $branch_count个"
    
    echo ""
}

# 执行审计
if [ "$BOT_NAME" = "all" ]; then
    for bot in "${!BOT_ENGINES[@]}"; do
        audit_bot $bot
    done
else
    audit_bot $BOT_NAME
fi

echo "=== 审计结果 ==="
echo "错误数: $ERRORS"
echo "警告数: $WARNINGS"

if [ $ERRORS -gt 0 ]; then
    echo "❌ 审计失败: 存在$ERRORS个错误"
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo "⚠️  审计通过但有$WARNINGS个警告"
    exit 0
else
    echo "✅ 审计通过: 所有检查项正常"
    exit 0
fi
