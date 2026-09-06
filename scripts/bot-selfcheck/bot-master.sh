#!/bin/bash
# BOT-MASTER 自检脚本
# 职责: 治理、证据系统、总调度

BOT_NAME="BOT-MASTER"
BOT_PREFIX="G:"
BOT_PATHS=(
    "src/tongshu/governance/"
    "src/tongshu/assertion/"
    "backend/data/evidence/"
    "docs/bots/BOT-MASTER/"
    "docs/bots/BOT-ZIPING/"
    "docs/bots/BOT-BLIND/"
    "docs/bots/BOT-HELUO/"
    "docs/bots/BOT-YI/"
    "docs/bots/BOT-CORPUS/"
)

echo "=== ${BOT_NAME} 自检 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 检查是否在主分支
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    echo "❌ 错误: 当前不在 main 分支 ($BRANCH)"
    echo "   请切换到 main 分支: git checkout main"
    exit 1
fi
echo "✅ 分支检查通过: $BRANCH"

# 2. 检查未提交的更改
UNCOMMITTED=$(git diff --name-only 2>/dev/null)
if [ -n "$UNCOMMITTED" ]; then
    echo "⚠️  检测到未提交的更改:"
    echo "$UNCOMMITTED"
    echo ""
    echo "   请先完成所有更改或 stash"
fi

# 3. 检查测试
echo ""
echo "🧪 运行 BOT-MASTER 测试..."
pytest tests/test_*governance*.py tests/test_*evidence*.py tests/test_*audit*.py -v --tb=short 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 测试通过"
else
    echo "⚠️  部分测试失败，请检查"
fi

# 4. 检查引擎隔离
echo ""
echo "🔍 检查引擎隔离..."
STAGED=$(git diff --cached --name-only 2>/dev/null)
ENGINES=("ziwei_engine" "heluo/" "blind/" "bazi_engine" "meihua.py" "yi/")
FOUND_ENGINE=0

for engine in "${ENGINES[@]}"; do
    if echo "$STAGED" | grep -q "$engine"; then
        echo "❌ 检测到引擎文件: $engine"
        FOUND_ENGINE=1
    fi
done

if [ $FOUND_ENGINE -eq 1 ]; then
    echo ""
    echo "⚠️  BOT-MASTER 不应直接修改引擎代码"
    echo "   请让相应 BOT 自行提交引擎变更"
fi

# 5. 检查裁决文档
echo ""
echo "📋 检查裁决文档..."
ARBITRATION_DOCS=$(find docs/bots -name "*ARBITRATION*" -o -name "*裁决*" 2>/dev/null | wc -l)
if [ $ARBITRATION_DOCS -gt 0 ]; then
    echo "⚠️  发现 $ARBITRATION_DOCS 个裁决文档"
    echo "   请确保已通知 GPT 和用户等待裁决"
fi

echo ""
echo "=== 自检完成 ==="
echo "建议操作:"
echo "  1. git add {本BOT相关文件}"
echo "  2. git commit -m \"G: {内容}\""
echo "  3. git push origin main"
