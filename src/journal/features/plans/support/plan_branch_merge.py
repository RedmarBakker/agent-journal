import json
import shlex
from pathlib import Path

from journal.config import Config
from journal.features.git.support.branch_merge import BranchMerge
from journal.features.plans.support.plan_agents import PlanAgents
from journal.models.plan import Plan
from journal.models.plan_mode import PlanMode
from journal.models.plan_state import PlanState
from journal.repositories.plans import Plans
from journal.support.rejection import Rejection
from journal.support.worktree import Worktree
from journal.support.workspace_worktree import WorkspaceWorktree


class PlanBranchMerge:
    """The checked merge of a finished solo Plan agent worktree into the project."""

    def __init__(self, config: Config, plans: Plans, agents: PlanAgents, branches: BranchMerge) -> None:
        self.config, self.plans, self.agents, self.branches = config, plans, agents, branches

    def merge(self, n: int) -> str:
        plan = self.plans.find(n)
        self.check_plan(plan)
        environment = self.agents.environment(plan)
        if environment is None:
            raise Rejection(f"plan {n} has no Plan agent environment to merge")
        if self.agents.is_running(environment):
            raise Rejection(f"plan {n}'s Plan agent is still running: wait for it to stop before merging")
        tree = WorkspaceWorktree.chosen(self.config.root, environment.name)
        if not tree.path.is_dir():
            raise Rejection(f"plan {n}'s worktree {tree.path} is missing")
        leftover = tree.uncommitted()
        generated = self.generated_settings(tree, leftover)
        if other := sorted(set(leftover) - set(generated)):
            raise Rejection(f"plan {n}'s worktree has uncommitted files: {', '.join(other[:10])}")
        repositories = self.repositories(tree)
        tips = [self.checked_tip(plan, tree, checkout, source, label, prefix) for checkout, source, label, prefix in repositories]
        merged = [self.merged(plan, checkout, tip, label) for (checkout, _, label, _), tip in zip(repositories, tips) if self.pending(checkout, tip)]
        tree.removed_after_merge(generated)
        work = f"merged as {', '.join(merged)}" if merged else "had no commits waiting to merge"
        settings = f"; left out its generated settings {', '.join(generated)}" if generated else ""
        return f"plan {n}'s work {work}{settings}; its worktree {tree.path} was removed"

    @staticmethod
    def generated_settings(tree: Worktree, names: list[str]) -> list[str]:
        generated = []
        for name in names:
            relative = Path(name)
            if isinstance(tree, WorkspaceWorktree):
                repository = next((name for name in sorted(tree.repositories(), key=len, reverse=True) if relative.is_relative_to(name)), "")
                if not repository:
                    continue
                relative = relative.relative_to(repository)
            path = tree.path / name
            if relative == Path(".claude/settings.json") and PlanBranchMerge.generated_claude_settings(path):
                generated.append(name)
            elif relative == Path(".codex/hooks.json") and PlanBranchMerge.generated_codex_settings(path):
                generated.append(name)
        return generated

    @staticmethod
    def generated_claude_settings(path: Path) -> bool:
        try:
            settings = json.loads(path.read_text())
        except (OSError, UnicodeError, json.JSONDecodeError):
            return False
        if not isinstance(settings, dict):
            return False
        status = settings.get("statusLine", {})
        if not isinstance(status, dict):
            return False
        line = status.get("command", "")
        if not isinstance(line, str):
            return False
        try:
            command = shlex.split(line)
        except ValueError:
            return False
        return (
            set(settings) == {"enableAllProjectMcpServers", "statusLine"}
            and settings.get("enableAllProjectMcpServers") is True
            and status.get("type") == "command"
            and len(command) == 2
            and command[0] == "sh"
            and command[1].endswith("/.journal/src/journal/hooks/status.sh")
        )

    @staticmethod
    def generated_codex_settings(path: Path) -> bool:
        try:
            return json.loads(path.read_text()) == {}
        except (OSError, UnicodeError, json.JSONDecodeError):
            return False

    @staticmethod
    def check_plan(plan: Plan) -> None:
        if plan.state != PlanState.FINISHED:
            raise Rejection(f"plan {plan.id} is {plan.state}: only a finished plan's work can be merged")
        if plan.mode != PlanMode.SOLO:
            raise Rejection(f"plan {plan.id} is in {plan.mode} mode: only a solo Plan agent has a branch to merge")

    def repositories(self, tree: Worktree) -> list[tuple[Path, Path, str, str]]:
        if isinstance(tree, WorkspaceWorktree):
            inner = [(self.config.root / name, tree.path / name, name, name) for name in tree.repositories()]
            if tree.project_repository:
                inner.insert(0, (self.config.root, tree.path, "the project", ""))
            return inner
        return [(self.config.root, tree.path, "the project", "")]

    def checked_tip(self, plan: Plan, tree: Worktree, checkout: Path, source: Path, label: str, prefix: str) -> str:
        branch = self.branches.git("rev-parse", "--abbrev-ref", "HEAD", cwd=source)
        if branch.returncode != 0 or branch.stdout.strip() != tree.branch:
            raise Rejection(f"plan {plan.id}'s worktree is not on its branch {tree.branch} in {label}")
        tip = self.branches.git("rev-parse", "HEAD", cwd=source)
        if tip.returncode != 0:
            raise Rejection(f"plan {plan.id}'s branch has no commit in {label}: {self.branches.reason(tip)}")
        refusal = self.branches.refusal(checkout, tip.stdout.strip(), label, prefix)
        if refusal:
            raise Rejection(f"plan {plan.id}'s work was not merged: {refusal}")
        return tip.stdout.strip()

    def pending(self, checkout: Path, tip: str) -> bool:
        commits = self.branches.git("rev-list", "--count", f"HEAD..{tip}", cwd=checkout)
        if commits.returncode != 0:
            raise Rejection(f"git could not list commits waiting to merge: {self.branches.reason(commits)}")
        return int(commits.stdout.strip()) > 0

    def merged(self, plan: Plan, checkout: Path, tip: str, label: str) -> str:
        clashing = self.branches.merged(checkout, tip)
        if clashing:
            raise Rejection(f"plan {plan.id}'s work was not merged: conflict in {clashing} in {label}")
        head = self.branches.git("rev-parse", "--short", "HEAD", cwd=checkout)
        if head.returncode != 0:
            raise Rejection(f"plan {plan.id}'s merge finished but git could not read the new commit: {self.branches.reason(head)}")
        return head.stdout.strip()
