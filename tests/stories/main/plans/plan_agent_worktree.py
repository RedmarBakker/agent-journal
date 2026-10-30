from pathlib import Path

from journal.engine.agent_launcher import AgentLauncher
from journal.features.git.support.branch_holders import BranchHolders
from journal.features.git.support.start_rule import StartRule
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.launcher.launch import Launch
from journal.launcher.menu import Menu
from journal.launcher.support.foreign_hooks import ForeignHooks
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.providers.claude import Claude
from journal.providers.codex import Codex
from journal.providers.support.status_line import StatusLine
from journal.repositories.environments import Environments
from journal.support.agent_role import AgentRole
from journal.support.environment_row import EnvironmentRow
from journal.support.project_command import ProjectCommand
from journal.support.worktree import Worktree
from journal.support.workspace_worktree import WorkspaceWorktree
from journal.supervisor_link import SupervisorLink
from tests.stories.builder.story_marks import BUILDER_MODE, setting, story
from tests.stories.fixtures.main.plan_approved import PlanApproved


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
def test_a_plan_agent_creates_its_worktree_before_the_branch_guard_checks_it(story, monkeypatch):
    app = story.app
    environments = app.container.get(Environments)
    main = environments.existing("main")
    root = app.config.root
    plan, environment = story.plans.first, f"plan-{story.plans.first}"
    (root / ".plan-agent-branch").write_text("main")
    target_branch = Worktree(root, environment).folder / ".plan-agent-branch"
    branch_before_launch = target_branch.read_text() if target_branch.is_file() else "main"
    (root / ".plan-agent-branches-before-launch").write_text(f"{(root / '.plan-agent-branch').read_text()}|{branch_before_launch}")

    monkeypatch.setattr(WorkspaceWorktree, "chosen", classmethod(lambda cls, root, name: cls(root, name)))

    creations = 0

    def created(tree):
        nonlocal creations
        creations += 1
        if creations == 1:
            return tree.path
        tree.path.mkdir(parents=True, exist_ok=True)
        (tree.path / ".plan-agent-branch").write_text(tree.branch)
        return tree.path

    def checkout_branch(branches, environment):
        folder = Worktree(branches.root, environment.name).folder
        branch = folder / ".plan-agent-branch"
        value = branch.read_text() if branch.is_file() else "main"
        if environment.name == f"plan-{plan}" and not (root / ".plan-agent-guard-branch").is_file():
            (root / ".plan-agent-guard-branch").write_text(f"{folder.relative_to(root)}|{value}")
        return value

    def environment_rows(menu):
        rules, supervisor = app.container.get(StartRule), app.container.get(SupervisorLink)
        return [
            EnvironmentRow(environment.name, working=supervisor.runs(environment.row_id), refusal=rules.refusal(environment))
            for environment in environments.working()
        ]

    def running_environments(supervisor, candidates):
        return [candidate for candidate in candidates if candidate.row_id in running]

    def supervise(launch, choice):
        folder = Path(launch.launch_file(choice, StatusLine(root))["front"]["folder"])
        branch = folder / ".plan-agent-branch"
        (root / ".plan-agent-start-check").write_text("|".join((choice.environment, launch.worktree, str(folder.relative_to(root)), branch.read_text())))
        return 0

    def launched(launcher, environment, arguments):
        (root / ".plan-agent-launch-arguments").write_text(" ".join(arguments))
        running.add(environments.existing(environment).row_id)
        result = Launch.parse(arguments, launcher.config.root).run()
        (root / ".plan-agent-launch-status").write_text(str(result))
        return result

    running = {main.row_id}
    monkeypatch.setattr(Worktree, "created", created)
    monkeypatch.setattr(WorkspaceWorktree, "created", created)
    monkeypatch.setattr(BranchHolders, "checkout_branch", checkout_branch)
    monkeypatch.setattr(SupervisorLink, "runs", lambda supervisor, environment_id: environment_id in running)
    monkeypatch.setattr(SupervisorLink, "running", running_environments)
    monkeypatch.setattr(Menu, "environments", environment_rows)
    monkeypatch.setattr(Menu, "journal", lambda menu, *arguments: "")
    monkeypatch.setattr(Launch, "supervise", supervise)
    monkeypatch.setattr(ProjectCommand, "write", lambda command: None)
    monkeypatch.setattr(ForeignHooks, "restore", lambda hooks: None)
    monkeypatch.setattr(Claude, "worktree_hooks", lambda provider, root, folder, script, command: None)
    monkeypatch.setattr(Claude, "folder_trusted", lambda provider, root, folder: None)
    monkeypatch.setattr(Codex, "worktree_hooks", lambda provider, root, folder, script, command: None)
    monkeypatch.setattr(Codex, "folder_trusted", lambda provider, root, folder: None)
    monkeypatch.setattr(AgentLauncher, "launched", launched)

    story.user_opens(f"/journal/plans/{plan}")
    result = story.user_presses(f"/journal/plans/{plan}/start", {})
    result.expect_viewer_passed()
    result.expect_viewer_shows("state", "started")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_project_file_is(".plan-agent-branches-before-launch", "main|main")
    story.expect_project_file_is(".plan-agent-guard-branch", f".claude/worktrees/{environment}|worktree-{environment}")
    story.expect_project_file_is(".plan-agent-start-check", f"{environment}|{environment}|.claude/worktrees/{environment}|worktree-{environment}")
    story.expect_project_file_is(".plan-agent-launch-status", "0")
    story.expect_project_file(".plan-agent-launch-arguments", "--worktree", environment)
    story.expect_stack(story.agents.subject, CoordinatingPlans, OrchestratingPlan)
