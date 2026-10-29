from journal.events.listener import Listener
from journal.events.models.saved import Saved
from journal.features.organization.support.board_standings import BoardStandings
from journal.models.link import Link
from journal.models.support.ref import Ref
from journal.models.task import Task
from journal.models.worker import Worker
from journal.repositories.domain_rows import DOMAIN_LINK
from journal.repositories.tasks import PLAN_LINK, Tasks


class BoardStandingRecord(Listener[Saved]):
    """A saved task, a plan or domain link to or from a task, or a worker that moved, as by clocking out, moves the plans of the tasks it touches on their domains' boards."""

    def __init__(self, standings: BoardStandings, tasks: Tasks) -> None:
        self.standings, self.tasks = standings, tasks

    def handle(self, event: Saved) -> None:
        for task in self.touched(event.model):
            self.standings.task_moved(task, event.actor)

    def touched(self, model) -> list[Task]:
        if isinstance(model, Task):
            return [model]
        if isinstance(model, Link) and model.link_type in (DOMAIN_LINK, PLAN_LINK):
            return self.tasks.numbered(ref.id for ref in (model.source, model.target) if ref.type == Task.table())
        if isinstance(model, Worker):
            return self.tasks.numbered(self.tasks.holder_task_ids(Ref.build(model)))
        return []
