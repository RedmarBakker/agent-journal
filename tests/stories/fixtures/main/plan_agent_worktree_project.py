from journal.features.tasks.states.ready import Ready
from tests.stories.builder.plan_agent_worktree import prepare_plan_agent_worktrees
from tests.stories.fixtures.main.new_session import NewSession
from tests.stories.fixtures.state_fixture import StateFixture


class PlanAgentWorktreeProject(StateFixture):
    """The project has the Git setup used by Plan agent worktree stories."""

    parent = NewSession

    def steps(self, story) -> None:
        prepare_plan_agent_worktrees(story, story.monkeypatch)

    def expected(self, story) -> None:
        story.expect_stack(story.agents.main, Ready)
