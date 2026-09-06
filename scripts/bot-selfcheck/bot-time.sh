#!/bin/bash
# BOT-TIME 自检脚本
# 职责: 时间计算引擎（节气、真太阳时）

BOT_NAME="BOT-TIME"
BOT_PREFIX="T:"
BOT_PATHS=(
    "src/tongshu/engines/time/"
    "tests/test_time*.py"
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

# 2. 检查测试
echo ""
echo "🧪 运行 BOT-TIME 测试..."
pytest tests/test_time*.py tests/test_*boundary*.py -v --tb=short 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ 测试通过"
else
    echo "❌ 测试失败，禁止提交"
    exit 1
fi

# 3. 检查文件范围
echo ""
echo "🔍 检查文件范围..."
STAGED=$(git diff --cached --name-only 2>/dev/null)

OTHER_BOTS=("ziwei_engine" "blind/" "heluo/" "bazi_engine" "meihua.py" "yi/")
FOUND_OTHER=0

for bot in "${OTHER_BOTS[@]}"; do
    if echo "$STAGED" | grep -q "$bot"; then
        echo "❌ 检测到其他 BOT 的文件: $bot"
        FOUND_OTHER=1
    fi
done

if [ $FOUND_OTHER -eq 1 ]; then
    echo ""
    echo "⚠️  禁止混合提交！"
    echo "   请拆分提交，只包含 time 相关文件"
    exit 1
fi

echo "✅ 文件范围检查通过"

echo ""
echo "=== 自检完成 ==="
echo "建议操作:"
echo "  1. git add src/tongshu/engines/time/ tests/test_time*.py"
echo "  2. git commit -m \"T: TimeEngine - {变更说明}\""
echo "  3. git push origin main"
