from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.domain_delivery_setup import add_domain_plan, report_worker, setup_domain
from tests.stories.fixtures.main.working_agent import WorkingAgent
from tests.stories.fixtures.state_fixture import StateFixture


class DomainDeliveryTaskWithCheckedWork(StateFixture):
    """A delivery task has checked work and a configured published-output policy."""

    parent = WorkingAgent
    stack = (Ready,)

    def steps(self, story) -> None:
        setup_domain(story, self, "r02-delivery", "release", {
            "criterion": "The release notes are published.",
            "evidence": "published_output",
            "target": "public release notes",
        })
        story.user_opens("/journal/organization").expect_viewer_passed()
        add_domain_plan(story, self, "release")
        story.user_approves_plan(self.plans.first)
        report_worker(story, self)

    def expected(self, story) -> None:
        story.expect_worker(self.workers.first, state=WorkerState.DELIVERED)
        story.expect_stack(story.agents.main, Ready)
