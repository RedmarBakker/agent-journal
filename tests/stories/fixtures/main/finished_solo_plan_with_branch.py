from journal.features.plans.plans_nudges import PlansNudges
from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.models.plan_state import PlanState
from journal.repositories.environments import Environments
from journal.support.workspace_worktree import WorkspaceWorktree
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.state_fixture import StateFixture


class FinishedSoloPlanWithBranch(StateFixture):
    """A finished solo plan has a committed change on the Plan agent's worktree branch."""

    parent = PlanApproved
    stack = (CoordinatingPlans,)
    settings = ((PlansOptions.PLAN_AGENTS, True),)

    def steps(self, story) -> None:
        story.project_is_a_git_repository()
        root, plan = story.app.config.root, self.plans.first
        story.git_in(root, "config", "user.name", "Story")
        story.git_in(root, "config", "user.email", "story@example.com")
        story.monkeypatch.setattr(AgentEnvironments, "launched", lambda places, environment, agent: WorkspaceWorktree.chosen(root, environment.name).created())
        story.agent_runs(story.agents.main, f"plan start {plan}")
        environment = story.app.container.get(Environments).existing(f"plan-{plan}")
        session = "plan-agent-session"
        story.session_starts_in(environment.name, session)
        tree = WorkspaceWorktree.chosen(root, environment.name)
        tree.created()
        story.agent_in_runs(story.agents.main, environment.name, session, f"plan start {plan}")
        change = tree.path / "PLAN-AGENT-SMOKE.md"
        change.write_text("completed solo plan change\n")
        story.git_in(change.parent, "add", change.name)
        story.git_in(change.parent, "-c", "user.email=story@example.com", "-c", "user.name=Story", "commit", "-q", "-m", "finish plan change")
        story.agent_in_runs(story.agents.main, environment.name, session, f"task complete {self.tasks.first} --how done")
        story.agent_in_runs(story.agents.main, environment.name, session, f"task complete {self.tasks.second} --how done")

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.FINISHED)
        story.last_step.expect_agent_told(story.agents.main, PlansNudges.PLAN_MERGE_READY, n=self.plans.first)
        story.expect_stack(story.agents.main, CoordinatingPlans)
