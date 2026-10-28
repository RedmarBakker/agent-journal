from journal.features.sequences.states.following_sequence import FollowingSequence
from journal.features.tasks.states.ready import Ready
from journal.models.plan_state import PlanState
from tests.stories.fixtures.state_fixture import StateFixture
from tests.stories.fixtures.working_agent import WorkingAgent


class DraftPlan(StateFixture):
    """The agent drafted a plan, which starts the plan building sequence: start.plan, a draft with no phase."""

    stack = (Ready, FollowingSequence)

    parent = WorkingAgent

    def steps(self, story) -> None:
        self.plan = story.agent_creates_plan("the site", "the site is built")

    def expected(self, story) -> None:
        story.expect_plan(self.plan, state=PlanState.DRAFT)
        story.expect_stack(Ready, FollowingSequence)
