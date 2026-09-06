#!/bin/bash
# BOT 工作流统一入口
# 用法: ./bot-workflow.sh {BOT_NAME} {ACTION} [ARGS]
# 
# ACTIONS:
#   selfcheck   - 运行自检
#   commit      - 提交代码（自动同步）
#   audit       - 创建审计文档
#   arbitrate   - 申请裁决
#   status      - 查看状态

set -e

BOT_NAME=$1
ACTION=$2
TIMESTAMP=$(date '+%Y%m%d_%H%M%S')

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "╔════════════════════════════════════════╗"
echo "║     顺天项目 BOT 工作流 v2.0           ║"
echo "║     BOT: $BOT_NAME                    ║"
echo "║     时间: $(date '+%Y-%m-%d %H:%M:%S')        ║"
echo "╚════════════════════════════════════════╝"
echo ""

# 验证 BOT 名称
case $BOT_NAME in
    MASTER|BOT-MASTER)
        SCRIPT="scripts/bot-selfcheck/bot-master.sh"
        PREFIX="G:"
        ;;
    BAZI|BOT-BAZI)
        SCRIPT="scripts/bot-selfcheck/bot-bazi.sh"
        PREFIX="P:"
        ;;
    ZIPING|BOT-ZIPING)
        SCRIPT="scripts/bot-selfcheck/bot-ziping.sh"
        PREFIX="ZP:"
        ;;
    BLIND|BOT-BLIND)
        SCRIPT="scripts/bot-selfcheck/bot-blind.sh"
        PREFIX="BL:"
        ;;
    HELUO|BOT-HELUO)
        SCRIPT="scripts/bot-selfcheck/bot-heluo.sh"
        PREFIX="H:"
        ;;
    YI|BOT-YI)
        SCRIPT="scripts/bot-selfcheck/bot-yi.sh"
        PREFIX="Y:"
        ;;
    TIME|BOT-TIME)
        SCRIPT="scripts/bot-selfcheck/bot-time.sh"
        PREFIX="T:"
        ;;
    CORPUS|BOT-CORPUS)
        SCRIPT="scripts/bot-selfcheck/bot-corpus.sh"
        PREFIX="C:"
        ;;
    *)
        echo -e "${RED}❌ 错误: 未知的 BOT 名称 '$BOT_NAME'${NC}"
        echo ""
        echo "支持的 BOT:"
        echo "  BOT-MASTER (G:) - 总调度、治理、证据"
        echo "  BOT-BAZI (P:)   - 八字排盘引擎"
        echo "  BOT-ZIPING (ZP:)- 子平引擎"
        echo "  BOT-BLIND (BL:)- 盲派引擎"
        echo "  BOT-HELUO (H:)  - 河洛引擎"
        echo "  BOT-YI (Y:)     - 易经引擎"
        echo "  BOT-TIME (T:)   - 时间计算引擎"
        echo "  BOT-CORPUS (C:) - 语料库管理"
        exit 1
        ;;
esac

# 执行动作
case $ACTION in
    selfcheck)
        echo -e "${GREEN}🧪 运行自检...${NC}"
        bash "$SCRIPT"
        ;;
    
    commit)
        echo ""
        echo -e "${YELLOW}📝 开始提交流程...${NC}"
        echo ""
        
        # 1. 自检
        echo "步骤 1/4: 运行自检..."
        bash "$SCRIPT"
        
        # 2. 检查未提交更改
        echo ""
        echo "步骤 2/4: 检查更改..."
        if [ -z "$(git diff --name-only)" ]; then
            echo -e "${RED}❌ 没有检测到更改${NC}"
            exit 1
        fi
        
        UNCOMMITTED=$(git diff --name-only)
        echo "待提交文件:"
        echo "$UNCOMMITTED" | head -20
        if [ $(echo "$UNCOMMITTED" | wc -l) -gt 20 ]; then
            echo "   ... 还有 $(echo "$UNCOMMITTED" | wc -l | tr -d ' ') 个文件"
        fi
        
        # 3. 询问用户确认
        echo ""
        read -p "确认提交? (y/N): " CONFIRM
        if [ "$CONFIRM" != "y" ] && [ "$CONFIRM" != "Y" ]; then
            echo "❌ 用户取消提交"
            exit 0
        fi
        
        # 4. 执行提交
        echo ""
        echo "步骤 3/4: 创建 commit..."
        read -p "请输入 commit message: " MESSAGE
        git add -A
        git commit -m "$PREFIX $MESSAGE"
        
        # 5. 推送到 GitHub
        echo ""
        echo "步骤 4/4: 推送到 GitHub..."
        git push origin main
        
        echo ""
        echo -e "${GREEN}✅ 提交完成！${NC}"
        echo "   Commit: $(git log -1 --oneline)"
        echo "   GitHub: https://github.com/ZQMMING/wisdom/commit/$(git rev-parse HEAD)"
        ;;
    
    audit)
        PHASE=$3
        if [ -z "$PHASE" ]; then
            PHASE="phase1"
        fi
        
        REPORT_DIR="docs/bots/$BOT_NAME"
        REPORT_FILE="$REPORT_DIR/AUDIT_${PHASE^^}_${TIMESTAMP}.md"
        
        echo ""
        echo -e "${YELLOW}📊 创建审计报告...${NC}"
        mkdir -p "$REPORT_DIR"
        
        cat > "$REPORT_FILE" << EOF
# ${BOT_NAME} - ${PHASE^^} 审计报告

**生成时间**: $(date '+%Y-%m-%d %H:%M:%S')
**BOT**: $BOT_NAME
**阶段**: ${PHASE^^}
**状态**: ⏳ 等待裁决

---

## 一、审计范围
- 代码路径: [待填写]
- 测试覆盖: [待填写]
- 证据引用: [待填写]

## 二、审计发现
[待填写]

## 三、建议操作
- [ ] 执行变更
- [ ] 拒绝变更
- [ ] 要求修改后重新提交

---

## 裁决区

**GPT 裁决**: 待填写
**用户裁决**: 待填写
**裁决时间**: 待填写
**执行状态**: 待执行
EOF
        
        echo ""
        echo -e "${GREEN}✅ 审计报告已创建: $REPORT_FILE${NC}"
        echo ""
        echo "下一步:"
        echo "  1. 填写审计报告内容"
        echo "  2. commit 到 GitHub: git add $REPORT_FILE && git commit -m \"$PREFIX: $BOT_NAME - $PHASE 审计报告\""
        echo "  3. push 到 GitHub: git push origin main"
        echo "  4. 通知 GPT 和用户等待裁决"
        ;;
    
    arbitrate)
        TYPE=$3
        if [ -z "$TYPE" ]; then
            TYPE="technical"
        fi
        
        ARB_DIR="docs/bots/$BOT_NAME"
        ARB_FILE="$ARB_DIR/ARBITRATION_${TYPE^^}_${TIMESTAMP}.md"
        
        echo ""
        echo -e "${YELLOW}⚖️  创建裁决申请...${NC}"
        mkdir -p "$ARB_DIR"
        
        cat > "$ARB_FILE" << EOF
# ${BOT_NAME} - ${TYPE^^} 裁决申请

**申请人**: $BOT_NAME
**时间**: $(date '+%Y-%m-%d %H:%M:%S')
**类型**: $TYPE
**状态**: ⏳ 等待裁决

---

## 一、问题摘要
[待填写问题描述]

## 二、涉及文件
- [待填写]

## 三、可选方案

### 方案 A: [名称]
- 优势: [待填写]
- 劣势: [待填写]
- 推荐指数: ⭐⭐⭐

### 方案 B: [名称]
- 优势: [待填写]
- 劣势: [待填写]
- 推荐指数: ⭐⭐

## 四、建议方案
**推荐**: 方案 A
**理由**: [待填写]

---

## 裁决区

### GPT 裁决
- 选择方案: [待填写]
- 理由: [待填写]
- 裁决时间: [待填写]

### 用户裁决
- 选择方案: [待填写]
- 理由: [待填写]
- 裁决时间: [待填写]

### 执行状态
- [ ] 等待裁决
- [ ] 已批准，待执行
- [ ] 已执行
- [ ] 已拒绝
EOF
        
        echo ""
        echo -e "${GREEN}✅ 裁决申请已创建: $ARB_FILE${NC}"
        echo ""
        echo "⚠️  重要提醒："
        echo "   1. 必须填写完整的裁决申请文档"
        echo "   2. 必须 commit 到 GitHub"
        echo "   3. 必须通知 GPT 和用户"
        echo "   4. 必须等待明确裁决后才能执行"
        echo ""
        echo "下一步:"
        echo "  1. 填写裁决申请内容"
        echo "  2. git add $ARB_FILE"
        echo "  3. git commit -m \"$PREFIX: $BOT_NAME - $TYPE 裁决申请\""
        echo "  4. git push origin main"
        echo "  5. 通知 GPT 和用户等待裁决"
        ;;
    
    status)
        echo ""
        echo "=== 仓库状态 ==="
        echo ""
        echo "当前分支: $(git rev-parse --abbrev-ref HEAD)"
        echo "最新提交: $(git log -1 --oneline)"
        echo "远程状态: $(git status -sb | head -1)"
        echo ""
        echo "=== BOT 状态 ==="
        echo ""
        
        # 检查各 BOT 的最新提交
        for BOT in "BOT-MASTER" "BOT-BAZI" "BOT-ZIPING" "BOT-BLIND" "BOT-HELUO" "BOT-YI" "BOT-TIME" "BOT-CORPUS"; do
            case $BOT in
                BOT-MASTER) PREFIX="G:" ;;
                BOT-BAZI) PREFIX="P:" ;;
                BOT-ZIPING) PREFIX="ZP:" ;;
                BOT-BLIND) PREFIX="BL:" ;;
                BOT-HELUO) PREFIX="H:" ;;
                BOT-YI) PREFIX="Y:" ;;
                BOT-TIME) PREFIX="T:" ;;
                BOT-CORPUS) PREFIX="C:" ;;
            esac
            
            LAST_COMMIT=$(git log --oneline --grep="$PREFIX" -1 2>/dev/null || echo "无提交")
            echo "$BOT ($PREFIX): $LAST_COMMIT"
        done
        ;;
    
    help|--help|-h)
        echo ""
        echo "用法: $0 {BOT_NAME} {ACTION} [ARGS]"
        echo ""
        echo "BOT 名称:"
        echo "  BOT-MASTER   - 总调度、治理、证据系统"
        echo "  BOT-BAZI     - 八字排盘引擎"
        echo "  BOT-ZIPING   - 子平引擎"
        echo "  BOT-BLIND    - 盲派引擎"
        echo "  BOT-HELUO    - 河洛引擎"
        echo "  BOT-YI       - 易经引擎"
        echo "  BOT-TIME     - 时间计算引擎"
        echo "  BOT-CORPUS   - 语料库管理"
        echo ""
        echo "Actions:"
        echo "  selfcheck    - 运行 BOT 自检"
        echo "  commit       - 提交代码并同步到 GitHub"
        echo "  audit        - 创建审计报告 (phase1|phase2|phase3|final)"
        echo "  arbitrate    - 创建裁决申请 (technical|architectural|business)"
        echo "  status       - 查看仓库和 BOT 状态"
        echo "  help         - 显示此帮助信息"
        echo ""
        echo "示例:"
        echo "  $0 BOT-BAZI selfcheck"
        echo "  $0 BOT-HELUO commit"
        echo "  $0 BOT-ZIPING audit phase2"
        echo "  $0 BOT-MASTER arbitrate technical"
        ;;
    
    *)
        echo -e "${RED}❌ 错误: 未知动作 '$ACTION'${NC}"
        echo ""
        echo "运行 '$0 help' 查看帮助信息"
        exit 1
        ;;
esac
