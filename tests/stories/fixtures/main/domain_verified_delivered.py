from journal.features.tasks.states.ready import Ready
from journal.models.task_state import TaskState
from journal.models.worker_state import WorkerState
from tests.stories.fixtures.main.domain_delivery_setup import merge_worker, replace_domain_definition
from tests.stories.fixtures.main.domain_delivery_task_with_checked_work import DomainDeliveryTaskWithCheckedWork


class DomainVerifiedDelivered(DomainDeliveryTaskWithCheckedWork):
    """A checked merge satisfies the task's verified-output policy."""

    parent = DomainDeliveryTaskWithCheckedWork

    def steps(self, story) -> None:
        replace_domain_definition(story, "r02-verified-delivery", "release", {
            "criterion": "The output is verified by the checked worker merge.",
            "evidence": "verified_output",
            "target": "checked worker merge",
        })
        merge_worker(story)

    def expected(self, story) -> None:
        story.expect_worker(self.workers.first, state=WorkerState.MERGED)
        story.expect_task(self.tasks.first, state=TaskState.COMPLETED)
        story.expect_stack(story.agents.main, Ready)
