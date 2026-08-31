"""
飞书消息 → HERMES-DISPATCH 自动桥接器

触发条件（飞书消息包含以下关键词时自动派发）:
- "调度" / "dispatch" / "派发" → 创建HERMES-DISPATCH任务单
- "审计" / "audit" → 触发STEP1全审流程
- "修复" / "fix" / "B-" → 创建修复任务单
- "P0" / "阻塞" → 标记为P0紧急任务

工作流程:
1. 接收飞书消息
2. 解析意图（通过LLM分析或关键词匹配）
3. 生成HERMES-DISPATCH模板
4. 写入 docs/audit/ 目录
5. 通知用户（飞书消息回复）
6. 自动派发至Claude/OpenCode（根据任务类型）
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# ============ 路径配置 ============
BASE_DIR = Path("D:/shuntian/backend")
DOCS_AUDIT_DIR = BASE_DIR / "docs" / "audit"
DISPATCH_TEMPLATE = """\
# 📨 HERMES-DISPATCH: {task_id}

---

## 基本信息

**Task ID**: {task_id}
**Step**: {step}
**Priority**: {priority}
**Owner**: {owner}
**Auditor**: Claude (Independent)
**Requester**: Hermes (总调度)
**来源**: 飞书消息自动派发
**触发消息**: {source_message}

---

## WHY

{why}

---

## WHAT

{what}

---

## CURRENT STATE

{current_state}

---

## CANONICAL

{canonical}

---

## SCOPE

允许修改:
{scope}

---

## BOUNDARY

禁止修改:
- Golden Dataset 期望值
- Canonical Rule / DB Schema
- 五经原典 Evidence
- 测试断言语义
- 冻结区资产（见 AGENTS.md §3）

---

## INPUT

{input}

---

## OUTPUT

{output}

---

## ACCEPTANCE CRITERIA

{acceptance}

---

## TEST

{test}

---

## REGRESSION

{regression}

---

## ROLLBACK

{rollback}

---

**生成时间**: {timestamp}
**调度方**: Hermes Agent (飞书自动桥接)
"""


class FeishuDispatchBridge:
    """飞书消息 → HERMES-DISPATCH 自动桥接"""

    # 飞书消息关键词 → 意图映射
    INTENT_PATTERNS = {
        "audit_step1": {
            "keywords": ["审计", "audit", "全审", "STEP1", "step1"],
            "step": "STEP 1",
            "owner": "Claude",
            "priority": "P0",
        },
        "fix_blocker": {
            "keywords": ["修复", "fix", "B-", "blocker", "阻塞"],
            "step": "STEP 3-6",
            "owner": "OpenCode",
            "priority": "P0/P1",
        },
        "dispatch_task": {
            "keywords": ["调度", "dispatch", "派发", "任务"],
            "step": "自定义",
            "owner": "OpenCode/Claude",
            "priority": "P1",
        },
        "p0_emergency": {
            "keywords": ["P0", "紧急", "emergency", "阻塞项"],
            "step": "即时",
            "owner": "OpenCode",
            "priority": "P0",
        },
    }

    def __init__(self):
        self.audit_dir = DOCS_AUDIT_DIR
        self.task_counter = self._load_task_counter()

    def _load_task_counter(self) -> int:
        """加载任务计数器（从文件恢复，避免重启后重置）"""
        counter_file = self.audit_dir / ".dispatch_counter.json"
        if counter_file.exists():
            try:
                data = json.loads(counter_file.read_text())
                return data.get("counter", 0)
            except:
                pass
        return 100  # 从100开始，避免与现有TASK-005/006冲突

    def _save_task_counter(self, count: int):
        """保存任务计数器"""
        counter_file = self.audit_dir / ".dispatch_counter.json"
        counter_file.write_text(json.dumps({"counter": count}, indent=2))

    def analyze_message(self, message: str) -> dict:
        """分析飞书消息，返回意图和调度建议"""
        message_lower = message.lower()

        # 关键词匹配
        matched_intents = []
        for intent, config in self.INTENT_PATTERNS.items():
            if any(kw in message_lower for kw in config["keywords"]):
                matched_intents.append(intent)

        # 提取关键信息
        priority = "P1"
        if "P0" in message or "紧急" in message or "blocker" in message_lower:
            priority = "P0"

        # 判断是否需要Claude审计
        needs_claude_audit = any(
            kw in message_lower for kw in ["审计", "audit", "验证", "verify"]
        )

        # 判断是否需要OpenCode执行
        needs_opencode = any(
            kw in message_lower
            for kw in ["修复", "fix", "改代码", "实现", "代码"]
        )

        return {
            "matched_intents": matched_intents,
            "priority": priority,
            "needs_claude_audit": needs_claude_audit,
            "needs_opencode": needs_opencode,
            "raw_message": message,
            "owner": config["owner"] if matched_intents else "OpenCode",
        }

    def generate_dispatch(self, analysis: dict, task_name: str) -> str:
        """生成HERMES-DISPATCH模板"""
        self.task_counter += 1
        task_id = f"TASK-{self.task_counter:03d}"
        self._save_task_counter(self.task_counter)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 根据意图填充模板
        intent = analysis["matched_intents"][0] if analysis["matched_intents"] else "dispatch_task"
        config = self.INTENT_PATTERNS.get(intent, self.INTENT_PATTERNS["dispatch_task"])

        why_map = {
            "audit_step1": "用户通过飞书请求全量审计，触发STEP 1流程",
            "fix_blocker": f"用户通过飞书请求修复阻塞项，触发STEP 3-6修复流程",
            "dispatch_task": "用户通过飞书派发新任务",
            "p0_emergency": "P0紧急阻塞项，需立即处理",
        }

        what_map = {
            "audit_step1": "执行12域全审，产出五件套报告",
            "fix_blocker": "按任务单修复指定问题，原子commit",
            "dispatch_task": task_name,
            "p0_emergency": f"紧急修复: {task_name}",
        }

        canonical_map = {
            "audit_step1": "shuntian-governance-dispatch skill §四（12域审计清单）",
            "fix_blocker": "AGENTS.md 权限矩阵 + BLOCKER_REGISTRY.md",
            "dispatch_task": "根据具体任务确定",
            "p0_emergency": "BLOCKER_REGISTRY.md P0项",
        }

        dispatch_content = DISPATCH_TEMPLATE.format(
            task_id=task_id,
            step=config["step"],
            priority=analysis["priority"],
            owner=config["owner"],
            source_message=analysis["raw_message"][:200],
            why=why_map.get(intent, why_map["dispatch_task"]),
            what=what_map.get(intent, what_map["dispatch_task"]),
            current_state="待分析...",
            canonical=canonical_map.get(intent, canonical_map["dispatch_task"]),
            scope="- 任务相关代码文件\n- 测试文件（按任务要求）\n- 文档（更新状态）",
            input=f"飞书消息: {analysis['raw_message']}",
            output=f"HERMES-DISPATCH文档 + 执行结果报告",
            acceptance="验收标准根据具体任务确定",
            test="pytest相关测试必须通过",
            regression="不得破坏现有测试基线",
            rollback="git revert commit_hash",
            timestamp=timestamp,
        )

        return dispatch_content, task_id

    def save_dispatch(self, content: str, task_id: str) -> Path:
        """保存dispatch文档"""
        filename = f"HERMES_DISPATCH_{task_id}.md"
        filepath = self.audit_dir / filename
        filepath.write_text(content, encoding="utf-8")
        return filepath

    def process_feishu_message(self, message: str) -> dict:
        """处理飞书消息，返回调度结果"""
        analysis = self.analyze_message(message)

        # 生成任务名（简化消息前50字）
        task_name = message[:50].strip()

        # 生成dispatch
        dispatch_content, task_id = self.generate_dispatch(analysis, task_name)

        # 保存
        filepath = self.save_dispatch(dispatch_content, task_id)

        # 构建回复
        reply = f"""📨 **HERMES-DISPATCH 已生成**

**Task ID**: {task_id}
**优先级**: {analysis['priority']}
**Owner**: {analysis['owner']}
**文档**: {filepath.name}

**意图识别**:
- 关键词匹配: {', '.join(analysis['matched_intents']) if analysis['matched_intents'] else '通用任务'}
- 需要Claude审计: {'是' if analysis['needs_claude_audit'] else '否'}
- 需要OpenCode执行: {'是' if analysis['needs_opencode'] else '否'}

下一步:
1. Hermes核验dispatch内容
2. User终裁批准
3. 派发至对应Agent执行
"""

        return {
            "task_id": task_id,
            "filepath": filepath,
            "analysis": analysis,
            "reply": reply,
        }


# ============ 飞书Webhook处理器 ============

def handle_feishu_webhook(event: dict) -> Optional[str]:
    """
    飞书Webhook入口处理器
    
    调用方式:
    - 飞书机器人收到消息时触发
    - 或作为独立脚本运行
    
    参数:
        event: 飞书事件对象（已解析）
    
    返回:
        回复消息文本，或None（静默处理）
    """
    bridge = FeishuDispatchBridge()

    # 提取消息内容
    message = event.get("message", {})
    text = message.get("text", "")

    if not text:
        return None

    # 处理消息
    result = bridge.process_feishu_message(text)

    return result["reply"]


# ============ 独立运行模式 ============

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法: python feishu_dispatch_bridge.py <消息内容>")
        print("示例: python feishu_dispatch_bridge.py \"修复B-01 wang_score阈值问题\"")
        sys.exit(1)

    message = " ".join(sys.argv[1:])
    bridge = FeishuDispatchBridge()
    result = bridge.process_feishu_message(message)

    print(f"\n✅ Dispatch已生成: {result['filepath']}")
    print(f"\n📋 任务ID: {result['task_id']}")
    print(f"\n💬 飞书回复:\n{result['reply']}")
