from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.main.plan_approved import PlanApproved
from tests.stories.fixtures.state_fixture import StateFixture


class PlanWorker(StateFixture):
    """The agent sent one worker on the whole approved plan and it clocked in on the first task, the second queued behind it: story.agents.workers.first()."""

    stack = (Ready, ExternalWait)

    parent = PlanApproved

    def steps(self, story) -> None:
        self.workers.first = story.agent_dispatches_worker_on_plan(story.agents.main, "Lady Lovelace", self.plans.first)
        story.agent_starts_a_session(story.agents.workers.first())
        story.agent_clocks_in(story.agents.workers.first())

    def expected(self, story) -> None:
        story.expect_plan(self.plans.first, state=PlanState.DELEGATED)
        story.expect_task(self.tasks.first, delegated=True)
        story.expect_task(self.tasks.second, delegated=True)
