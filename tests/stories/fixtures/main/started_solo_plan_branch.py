from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.models.plan_state import PlanState
from journal.repositories.environments import Environments
from journal.support.workspace_worktree import WorkspaceWorktree
from tests.stories.fixtures.main.coordinating_plan_agent import CoordinatingPlanAgent
from tests.stories.fixtures.state_fixture import StateFixture


PLAN_AGENT_SESSION = "plan-agent-session"


class StartedSoloPlanBranch(StateFixture):
    """A solo Plan agent has committed work on its branch while its tasks remain open."""

    parent = CoordinatingPlanAgent
    stack = (CoordinatingPlans,)

    def steps(self, story) -> None:
        story.project_is_a_git_repository()
        root, plan = story.app.config.root, self.plans.first
        story.git_in(root, "config", "user.name", "Story")
        story.git_in(root, "config", "user.email", "story@example.com")
        installed = (
            (".agents/skills/journal-plan/SKILL.md", "old journal skill\n"),
            (".claude/skills/journal-plan/SKILL.md", "old Claude journal skill\n"),
            (".codex/agents/journal-plan.toml", "old journal profile\n"),
            (".claude/agents/journal-plan.md", "old Claude agent profile\n"),
            (".codex/hooks.json", '{"hooks": {"journal": false}}\n'),
            ("AGENTS.md", "old journal instructions\n"),
            ("CLAUDE.md", "old Claude instructions\n"),
        )
        for name, text in installed:
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            story.git_in(root, "add", "-f", name)
        story.git_in(root, "commit", "-q", "-m", "install journal files")
        story.monkeypatch.setattr(AgentEnvironments, "launched", lambda places, environment, agent, repositories=None: WorkspaceWorktree.chosen(root, environment.name, repositories).created())
        story.agent_runs(story.agents.main, f"plan start {plan}")
        environment = story.app.container.get(Environments).existing(f"plan-{plan}")
        story.session_starts_in(environment.name, PLAN_AGENT_SESSION)
        tree = WorkspaceWorktree.chosen(root, environment.name)
        tree.created()
        story.agent_in_runs(story.agents.main, environment.name, PLAN_AGENT_SESSION, f"plan start {plan}")
        change = tree.path / "PLAN-AGENT-SMOKE.md"
        change.write_text("completed solo plan change\n")
        story.git_in(change.parent, "add", change.name)
        story.git_in(change.parent, "-c", "user.email=story@example.com", "-c", "user.name=Story", "commit", "-q", "-m", "finish plan change")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.STARTED)
        story.expect_stack(story.agents.main, CoordinatingPlans)
