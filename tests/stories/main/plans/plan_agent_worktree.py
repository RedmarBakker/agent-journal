from journal.engine.agent_launcher import AgentLauncher
from journal.features.git.support.branch_holders import BranchHolders
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.team.support.start_rule import StartRule
from journal.models.plan_state import PlanState
from journal.models.task_state import TaskState
from journal.repositories.environments import Environments
from journal.support.agent_role import AgentRole
from journal.support.worktree import Worktree
from journal.support.workspace_worktree import WorkspaceWorktree
from journal.supervisor_link import SupervisorLink
from tests.stories.builder.story_marks import BUILDER_MODE, setting, story
from tests.stories.fixtures.main.plan_approved import PlanApproved


@story(PlanApproved, mode=BUILDER_MODE, subject=AgentRole.MAIN)
@setting(PlansOptions.PLAN_AGENTS, True)
def test_a_plan_agent_launches_in_its_own_worktree_while_main_runs(story, monkeypatch):
    app = story.app
    environments = app.container.get(Environments)
    main = environments.existing("main")

    monkeypatch.setattr(WorkspaceWorktree, "chosen", classmethod(lambda cls, root, name: Worktree(root, name)))

    def created(tree):
        tree.path.mkdir(parents=True, exist_ok=True)
        (tree.path / "branch").write_text(tree.branch)
        return tree.path

    def checkout_branch(branches, environment):
        branch = Worktree(branches.root, environment.name).path / "branch"
        return branch.read_text() if branch.is_file() else "main"

    def launched(launcher, environment, arguments):
        target = environments.existing(environment)
        branches = app.container.get(BranchHolders)
        running = app.container.get(SupervisorLink).runs(main.row_id)
        refusal = app.container.get(StartRule).refusal(target, 1)
        (launcher.config.root / ".plan-agent-start-check").write_text("|".join((str(running), branches.checkout_branch(main), branches.checkout_branch(target), refusal)))
        (launcher.config.root / ".plan-agent-launch-arguments").write_text(" ".join(arguments))
        return 1

    monkeypatch.setattr(Worktree, "created", created)
    monkeypatch.setattr(BranchHolders, "checkout_branch", checkout_branch)
    monkeypatch.setattr(SupervisorLink, "runs", lambda supervisor, environment_id: environment_id == main.row_id)
    monkeypatch.setattr(AgentLauncher, "launched", launched)

    plan, environment = story.plans.first, f"plan-{story.plans.first}"
    story.user_opens(f"/journal/plans/{plan}")
    story.user_presses(f"/journal/plans/{plan}/start", {})
    story.expect_viewer_passed()
    story.expect_viewer_shows("state", "started")
    story.expect_plan(plan, state=PlanState.STARTED)
    story.expect_task(story.tasks.first, state=TaskState.STARTED)
    story.expect_task(story.tasks.second, state=TaskState.OPEN)
    story.expect_project_file_is(f".claude/worktrees/{environment}/branch", f"worktree-{environment}")
    story.expect_project_file_is(".plan-agent-start-check", f"True|main|worktree-{environment}|")
    story.expect_project_file(".plan-agent-launch-arguments", "--worktree", environment)
    story.expect_stack(story.agents.subject, CoordinatingPlans)
