from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.domain_delivery_setup import add_domain_plan, prepare_domain, report_worker
from tests.stories.fixtures.main.recorded_domain_delivery_estimates import RecordedDomainDeliveryEstimates
from tests.stories.fixtures.state_fixture import StateFixture


class DomainDeliveryTaskWithCheckedWork(StateFixture):
    """A delivery task has checked work and a configured published-output policy."""

    parent = RecordedDomainDeliveryEstimates
    stack = (Ready,)

    def steps(self, story) -> None:
        prepare_domain(story, self, "r02-delivery", "release", {
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
