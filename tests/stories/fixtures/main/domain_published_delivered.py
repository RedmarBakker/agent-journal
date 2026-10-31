from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.domain_delivery_setup import merge_worker, production_record
from tests.stories.fixtures.main.domain_delivery_task_with_checked_work import DomainDeliveryTaskWithCheckedWork


class DomainPublishedDelivered(DomainDeliveryTaskWithCheckedWork):
    """The checked task is merged, but publication evidence is still required."""

    parent = DomainDeliveryTaskWithCheckedWork

    def steps(self, story) -> None:
        merge_worker(story)
        delivery = f"/journal/plans/{self.plans.first}/delivery"
        result = story.user_opens(delivery)
        result.expect_viewer_shows("status", "awaiting_evidence")
        wrong = production_record(self.tasks.first, "release-42", "sha256:revision-42")
        result = story.user_presses(delivery, wrong)
        result.expect_viewer_refused("does not match release's published output requirement")

    def expected(self, story) -> None:
        story.expect_worker(self.workers.first, state=WorkerState.MERGED)
        story.expect_task(self.tasks.first, state=TaskState.COMPLETED)
        story.expect_stack(story.agents.main, Ready)
