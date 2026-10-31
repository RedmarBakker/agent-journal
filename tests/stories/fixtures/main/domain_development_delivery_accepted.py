from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.domain_delivery_setup import merge_worker, production_record
from tests.stories.fixtures.main.domain_development_delivered import DomainDevelopmentDelivered
from tests.stories.fixtures.state_fixture import StateFixture


class DomainDevelopmentDeliveryAccepted(StateFixture):
    """The development worker's checked merge has accepted production evidence."""

    parent = DomainDevelopmentDelivered
    stack = (Ready,)

    def steps(self, story) -> None:
        merge_worker(story)
        story.time_travel(minutes=2 * 24 * 60)
        result = story.user_presses(
            f"/journal/plans/{self.plans.first}/delivery",
            production_record(self.tasks.first, "release-52", "sha256:revision-52"),
        )
        result.expect_viewer_passed()

    def expected(self, story) -> None:
        story.expect_worker(self.workers.first, state=WorkerState.MERGED)
        story.expect_task(self.tasks.first, state=TaskState.COMPLETED)
        story.expect_stack(story.agents.main, Ready)
