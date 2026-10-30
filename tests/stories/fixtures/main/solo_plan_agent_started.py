from journal.features.plans.plans_options import PlansOptions
from journal.features.plans.states.coordinating_plans import CoordinatingPlans
from journal.features.plans.support.agent_environments import AgentEnvironments
from journal.features.tasks.states.ready import Ready
from journal.features.workers.states.orchestrating_plan import OrchestratingPlan
from journal.models.plan_state import PlanState
from journal.repositories.environments import Environments
from journal.support.workspace_worktree import WorkspaceWorktree
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.state_fixture import StateFixture


PLAN_AGENT_SESSION = "plan-agent-write-session"


class SoloPlanAgentStarted(StateFixture):
    """The user started a solo plan with its Plan agent ready to work in the plan worktree."""

    stack = (Ready,)
    parent = NewSession
    settings = ((PlansOptions.PLAN_AGENTS, True),)

    def steps(self, story) -> None:
        root = story.app.config.root
        story.project_is_a_git_repository()
        story.git_in(root, "config", "user.name", "Story")
        story.git_in(root, "config", "user.email", "story@example.com")
        self.plans.first = story.user_creates_plan("A plan", "Write one file")
        self.tasks.first = story.user_adds_plan_task(self.plans.first, "Write the file")
        story.user_did(f"/journal/plans/{self.plans.first}/mode", {"mode": "solo"}, "user sets the plan to solo mode")
        story.user_approves_plan(self.plans.first)
        story.monkeypatch.setattr(
            AgentEnvironments,
            "launched",
            lambda places, environment, agent, repositories=None: WorkspaceWorktree.chosen(root, environment.name, repositories).created(),
        )
        result = story.agent_runs(story.agents.main, f"plan start {self.plans.first}")
        result.expect_command_passed()
        environment = story.app.container.get(Environments).existing(f"plan-{self.plans.first}")
        story.session_starts_in(environment.name, PLAN_AGENT_SESSION)
        result = story.agent_in_runs(story.agents.main, environment.name, PLAN_AGENT_SESSION, "environment overview")
        result.expect_command_passed()

    def expected(self, story) -> None:
        story.expect_plan(story.plans.first, state=PlanState.STARTED)
        story.expect_task(story.tasks.first)
        story.expect_stack(story.agents.main, CoordinatingPlans, OrchestratingPlan)
