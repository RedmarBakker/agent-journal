from journal.models.support.ref import Ref
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from tests.stories.fixtures.reviewer.reviewer_at_work import ReviewerAtWork


class ReviewerEndsAfterWorkerMerge(ReviewerAtWork):
    """A worker merges its task while its reviewer is still running."""

    parent = ReviewerAtWork

    def steps(self, story) -> None:
        task = story.app.container.get(Tasks).find(self.tasks.briefed)
        worker = story.app.container.get(Workers).find(self.workers.first)
        time = story.app.container.get(TimeSource).moment()
        actor = Actor.system()
        story.app.container.get(Tasks).save(
            task.merge_completed(time, f"worker {worker.row_id} merged", worker.row_id), actor,
        )
        story.app.container.get(Tasks).release_task(Ref.build(worker), task.row_id, actor)
        story.app.container.get(Workers).save(worker.merged(task.row_id, time.timestamp()), actor)

