from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.domain_delivery_setup import add_domain_plan, report_worker, setup_domain
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class DomainPublishedDelivered(StateFixture):
    """The user composed a publishing task and its worker reported checked work, waiting for the user's merge: story.plans.first, story.tasks.first and story.agents.workers.first()."""

    stack = (Ready,)
    parent = WorkingAgent

    def steps(self, story) -> None:
        setup_domain(story, self, "r02-published", "publishing", {"criterion": "The release notes are published.", "evidence": "published_output", "target": "public release notes"})
        add_domain_plan(story, self, "publishing")
        story.user_approves_plan(self.plans.first)
        report_worker(story, self)

    def expected(self, story) -> None:
        story.expect_worker(self.workers.first, state=WorkerState.DELIVERED)
        story.expect_stack(story.agents.main, Ready)
