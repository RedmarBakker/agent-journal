from journal.models.support.ref import Ref
from journal.repositories.scope import Scope
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.time_source import TimeSource
from tests.stories.fixtures.reviewer.reviewer_at_work import ReviewerAtWork


class ReviewerEndsAfterWorkerMerge(ReviewerAtWork):
    """A worker merges its task while its reviewer is still running."""

    parent = ReviewerAtWork

    def steps(self, story) -> None:
        with story.app.container.get(Scope).environment(1):
            tasks = story.app.container.get(Tasks)
            workers = story.app.container.get(Workers)
            task = tasks.find(self.tasks.briefed)
            worker = workers.find(self.workers.first)
            time = story.app.container.get(TimeSource).moment()
            actor = Actor.system()
            tasks.save(task.merge_completed(time, f"worker {worker.row_id} merged", worker.row_id), actor)
            tasks.release_task(Ref.build(worker), task.row_id, actor)
            workers.save(worker.merged(task.row_id, time.timestamp()), actor)

