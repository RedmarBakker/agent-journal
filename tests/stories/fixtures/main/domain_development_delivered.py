from journal.features.tasks.states.ready import Ready
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.domain_delivery_setup import add_domain_plan, prepare_domain, report_worker
from tests.stories.fixtures.main.recorded_domain_delivery_estimates import RecordedDomainDeliveryEstimates
from tests.stories.fixtures.state_fixture import StateFixture


class DomainDevelopmentDelivered(StateFixture):
    """The user composed a development task and its worker reported checked work, waiting for the user's merge: story.plans.first, story.tasks.first and story.agents.workers.first()."""

    stack = (Ready,)
    parent = RecordedDomainDeliveryEstimates

    def steps(self, story) -> None:
        prepare_domain(story, self, "r02-development", "development", {"criterion": "A successful production deployment of the committed revision.", "evidence": "production_deployment", "target": "production"})
        add_domain_plan(story, self, "development")
        story.user_approves_plan(self.plans.first)
        report_worker(story, self)

    def expected(self, story) -> None:
        story.expect_worker(self.workers.first, state=WorkerState.DELIVERED)
        story.expect_stack(story.agents.main, Ready)
