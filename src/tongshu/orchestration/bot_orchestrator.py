"""
BOT Orchestration — 五引擎 BOT 调度框架

职责：
  1. 任务派发：解析用户意图，分配给合适的 BOT
  2. 状态追踪：监控各分支状态、测试通过率、提交历史
  3. 冲突检测：检测分支冲突、文件冲突
  4. 审核汇总：生成任务完成报告、周汇总报告

严禁：
  - 自行修改引擎代码（由对应 BOT 执行）
  - 跳过测试验证直接合并
  - 自行裁决架构问题
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class BOTRole(Enum):
    """BOT 角色枚举"""
    ZIPING = "ziping"           # 子平引擎
    MANGPAI = "mangpai"         # 盲派引擎
    ZIWEI = "ziwei"             # 紫微斗数
    HELUO = "heluo"             # 河洛理数
    YI = "yi"                   # 易经
    ZILIAO = "ziliao"           # 原典资料
    IT = "it"                   # 验证修复


class TaskType(Enum):
    """任务类型"""
    CALCULATION_AUDIT = "calculation_audit"      # 计算完整性审计
    EVIDENCE_VERIFY = "evidence_verify"          # 证据溯源验证
    BUG_FIX = "bug_fix"                          # Bug 修复
    TEST_EXPAND = "test_expand"                  # 测试扩展
    ARCHITECTURE_AUDIT = "architecture_audit"    # 架构审计
    CROSS_ENGINE = "cross_engine"               # 跨引擎协调


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW_PENDING = "review_pending"          # 等待用户审核
    COMPLETED = "completed"
    BLOCKED = "blocked"


@dataclass
class BOTState:
    """单个 BOT 的状态"""
    role: BOTRole
    branch: str
    ahead_of_main: int = 0
    commits: List[str] = field(default_factory=list)
    test_pass_rate: float = 1.0
    current_task: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING


@dataclass
class Task:
    """任务定义"""
    task_id: str
    title: str
    bot: BOTRole
    task_type: TaskType
    description: str = ""
    status: TaskStatus = TaskStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    report_path: Optional[str] = None


class BOTOrchestrator:
    """
    BOT 调度中心

    使用示例：
        orch = BOTOrchestrator(repo_path="/path/to/wisdom")
        orch.discover_bots()
        orch.show_status()

        # 派发任务
        task = orch.dispatch_task(
            title="Zǐpíng Calculation Integrity Audit",
            bot=BOTRole.ZIPING,
            task_type=TaskType.CALCULATION_AUDIT,
            description="验证16项计算面..."
        )

        # 生成报告
        orch.generate_report()
    """

    # BOT 角色与分支的映射
    BRANCH_MAP = {
        BOTRole.ZIPING: "ziping",
        BOTRole.MANGPAI: "mangpai",
        BOTRole.ZIWEI: "ziwei",
        BOTRole.HELUO: "heluo",
        BOTRole.YI: "yi",
        BOTRole.ZILIAO: "ziliao",
        BOTRole.IT: "it",
    }

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.bots: Dict[BOTRole, BOTState] = {}
        self.tasks: List[Task] = []

    def discover_bots(self) -> None:
        """发现所有 BOT 分支状态"""
        import subprocess

        # 先 fetch 最新远端状态
        subprocess.run(
            ["git", "fetch", "origin", "--prune"],
            capture_output=True
        )

        # Windows 路径需要转换为 forward slash
        repo_path = str(self.repo_path).replace('\\', '/')

        for role, branch in self.BRANCH_MAP.items():
            try:
                # 获取超前 origin/main 的提交数
                result = subprocess.run(
                    ["git", "-C", repo_path, "rev-list", "--count", f"origin/main..{branch}"],
                    capture_output=True, text=True, check=True
                )
                ahead = int(result.stdout.strip()) if result.stdout.strip() else 0

                # 获取最新提交
                result = subprocess.run(
                    ["git", "-C", repo_path, "log", "-1", "--oneline", branch],
                    capture_output=True, text=True, check=True
                )
                latest_commit = result.stdout.strip()

                self.bots[role] = BOTState(
                    role=role,
                    branch=branch,
                    ahead_of_main=ahead,
                    commits=[latest_commit] if latest_commit else [],
                )
            except subprocess.CalledProcessError:
                self.bots[role] = BOTState(role=role, branch=branch)

    def show_status(self) -> str:
        """生成 BOT 状态报告"""
        lines = ["=== BOT 调度状态 ===", ""]
        for role, state in self.bots.items():
            status = "🟢 同步" if state.ahead_of_main == 0 else f"🟡 超前 {state.ahead_of_main} commit"
            lines.append(f"{role.value:10} | {state.branch:15} | {status}")
        lines.append("")
        return "\n".join(lines)

    def dispatch_task(
        self,
        title: str,
        bot: BOTRole,
        task_type: TaskType,
        description: str = "",
    ) -> Task:
        """派发任务到指定 BOT"""
        task_id = f"T-{len(self.tasks) + 1:03d}"
        task = Task(
            task_id=task_id,
            title=title,
            bot=bot,
            task_type=task_type,
            description=description,
            status=TaskStatus.IN_PROGRESS,
        )
        self.tasks.append(task)

        # 更新 BOT 状态
        if bot in self.bots:
            self.bots[bot].current_task = task_id
            self.bots[bot].status = TaskStatus.IN_PROGRESS

        return task

    def complete_task(self, task_id: str, report_path: str) -> None:
        """标记任务完成"""
        for task in self.tasks:
            if task.task_id == task_id:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now()
                task.report_path = report_path
                break

        # 更新 BOT 状态
        for role, state in self.bots.items():
            if state.current_task == task_id:
                state.current_task = None
                state.status = TaskStatus.PENDING

    def detect_conflicts(self) -> List[str]:
        """检测分支冲突"""
        conflicts = []
        # 简化版：检查是否有多个 BOT 超前同一个 main commit
        ahead_bots = [
            (role, state) for role, state in self.bots.items()
            if state.ahead_of_main > 0
        ]
        if len(ahead_bots) > 1:
            conflicts.append(
                f"多个 BOT 超前 main: {', '.join(r.value for r, _ in ahead_bots)}"
            )
        return conflicts

    def generate_report(self) -> Dict[str, Any]:
        """生成调度报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "bots": {
                role.value: {
                    "branch": state.branch,
                    "ahead_of_main": state.ahead_of_main,
                    "current_task": state.current_task,
                    "status": state.status.value,
                }
                for role, state in self.bots.items()
            },
            "tasks": [
                {
                    "task_id": t.task_id,
                    "title": t.title,
                    "bot": t.bot.value,
                    "type": t.task_type.value,
                    "status": t.status.value,
                }
                for t in self.tasks
            ],
            "conflicts": self.detect_conflicts(),
        }
        return report


# ── 预定义调度规则 ───────────────────────────────────────────────

TASK_ROUTING = {
    "四柱计算": BOTRole.ZIPING,
    "时柱计算": BOTRole.ZIPING,
    "节气边界": BOTRole.ZIPING,
    "大运推导": BOTRole.ZIPING,
    "做功体系": BOTRole.MANGPAI,
    "宾主体用": BOTRole.MANGPAI,
    "格局验证": BOTRole.MANGPAI,
    "星曜四化": BOTRole.ZIWEI,
    "大限验证": BOTRole.ZIWEI,
    "宫位排布": BOTRole.ZIWEI,
    "元堂后天": BOTRole.HELUO,
    "应期链": BOTRole.HELUO,
    "卦辞爻辞": BOTRole.YI,
    "原典溯源": BOTRole.ZILIAO,
    "VERIFIED标记": BOTRole.ZILIAO,
    "测试修复": BOTRole.IT,
    "Bug修复": BOTRole.IT,
    "回归测试": BOTRole.IT,
}


def route_task(description: str) -> Optional[BOTRole]:
    """根据任务描述路由到合适的 BOT"""
    for keyword, bot in TASK_ROUTING.items():
        if keyword in description:
            return bot
    return None


if __name__ == "__main__":
    orch = BOTOrchestrator(repo_path="/c/Users/wisdom/wisdom")
    orch.discover_bots()
    print(orch.show_status())

    # 示例：派发任务
    task = orch.dispatch_task(
        title="Zǐpíng Calculation Integrity Audit",
        bot=BOTRole.ZIPING,
        task_type=TaskType.CALCULATION_AUDIT,
        description="验证子平引擎 16 项计算面，包括四柱、节气、时柱、大运等",
    )
    print(f"任务已派发：{task.task_id} → {task.bot.value}")
