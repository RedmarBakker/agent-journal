from journal.features.tasks.states.external_wait import ExternalWait
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.plan_approved import PlanApproved
from tests.stories.fixtures.state_fixture import StateFixture


class PlanWorker(StateFixture):
    """The agent sent one worker on the whole approved plan and it clocked in on the first task, the second queued behind it: start.worker."""

    stack = (Ready, ExternalWait)

    parent = PlanApproved

    def steps(self, story) -> None:
        self.worker = story.agent_dispatches_worker_on_plan("Lady Lovelace", self.plan)
        story.worker_clocks_in(self.worker)

    def expected(self, story) -> None:
        story.expect_plan(self.plan, state=PlanState.DELEGATED)
        story.expect_task(self.first_task, delegated=True)
        story.expect_task(self.second_task, delegated=True)
