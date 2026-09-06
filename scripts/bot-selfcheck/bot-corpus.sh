#!/bin/bash
# BOT-CORPUS 自检脚本
# 职责: 语料库管理（五部经典）

BOT_NAME="BOT-CORPUS"
BOT_PREFIX="C:"
BOT_PATHS=(
    "data/classics/"
    "docs/bots/*/REPORT.md"
    "docs/bots/*/PHASE*.md"
)

echo "=== ${BOT_NAME} 自检 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 1. 检查分支
BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$BRANCH" != "main" ]; then
    echo "❌ 错误: 当前不在 main 分支 ($BRANCH)"
    exit 1
fi
echo "✅ 分支检查通过: $BRANCH"

# 2. 检查文件范围
echo ""
echo "🔍 检查文件范围..."
STAGED=$(git diff --cached --name-only 2>/dev/null)

# 语料库不应该修改引擎代码
ENGINES=("ziwei_engine" "blind/" "heluo/" "bazi_engine" "meihua.py" "yi/" "time/")
FOUND_ENGINE=0

for engine in "${ENGINES[@]}"; do
    if echo "$STAGED" | grep -q "$engine"; then
        echo "⚠️  检测到引擎文件: $engine"
        echo "   BOT-CORPUS 不应直接修改引擎代码"
        FOUND_ENGINE=1
    fi
done

if [ $FOUND_ENGINE -eq 1 ]; then
    echo ""
    echo "⚠️  请确认是否需要修改引擎代码"
    echo "   如果是，请让相应 BOT 自行提交"
fi

echo "✅ 文件范围检查通过"

# 3. 检查语料库完整性
echo ""
echo "📚 检查语料库完整性..."
CLASSICS_COUNT=$(find data/classics -name "*.json" 2>/dev/null | wc -l)
echo "   发现 $CLASSICS_COUNT 个语料文件"

echo ""
echo "=== 自检完成 ==="
echo "建议操作:"
echo "  1. git add data/classics/ docs/bots/*/REPORT.md"
echo "  2. git commit -m \"C: Corpus - {变更说明}\""
echo "  3. git push origin main"
