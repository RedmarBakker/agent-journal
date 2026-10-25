from journal.db.connection import Connection
from journal.events.bus import Bus
from journal.models.agent import Agent
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.models.worker_state import WorkerState
from journal.repositories.links import Links
from journal.repositories.rows import Rows
from journal.repositories.scope import Scope
from journal.repositories.scoped_repository import ScopedRepository
from journal.repositories.tasks import Tasks




class Workers(ScopedRepository[Worker]):
    model = Worker

    def __init__(self, connection: Connection, bus: Bus, scope: Scope, links: Links, rows: Rows, tasks: Tasks) -> None:
        super().__init__(connection, bus, scope)
        self.links, self.rows, self.tasks = links, rows, tasks

    def open_workers(self) -> list[Worker]:
        return self.selected(self.query().filter_listed("state", [WorkerState.DISPATCHED, WorkerState.READY, WorkerState.DELIVERED, WorkerState.UNFINISHED]).order("id"))

    def running_workers(self) -> list[Worker]:
        return self.selected(self.query().filter_listed("state", [WorkerState.DISPATCHED, WorkerState.READY]).order("id"))

    def idle_workers(self) -> list[Worker]:
        return self.selected(self.query().filter(state=WorkerState.REPORTED, adopted=False).order("id"))

    def queued_reviews(self) -> list[Worker]:
        return self.selected(self.query().filter(state=WorkerState.DELIVERED, review_pending=True).filter_greater("review_queued_at", 0).order("review_queued_at"))

    def merged_since(self, time: float) -> list[Worker]:
        return self.selected(self.query().filter_greater("merged_at", time).order("merged_at"))

    def checkable_workers(self) -> list[Worker]:
        return self.selected(self.query().filter(state=WorkerState.DELIVERED).filter_unequal("review_pending", True).order("id"))

    def has_idle(self) -> bool:
        return any(worker.is_idle() for worker in self.scoped())

    def has_unanswered(self, time: float, seconds: float) -> bool:
        return any(worker.is_unanswered(time, seconds) for worker in self.scoped())

    def running_pool_workers(self) -> list[Worker]:
        return [worker for worker in self.running_workers() if worker.pool_request]

    def running_locally(self) -> list[Worker]:
        return [worker for worker in self.running_workers() if not worker.pool_request]

    def peers(self, sender: Worker) -> list[Worker]:
        return [worker for worker in self.scoped() if worker.dispatcher == sender.dispatcher and worker.id != sender.id and (worker.is_running() or worker.is_idle())]

    def active(self) -> list[Worker]:
        return self.matching(state=WorkerState.DISPATCHED)

    def containing(self, task_ids: set[int]) -> dict[int, Worker]:
        holdings = self.tasks.task_worker_holdings(task_ids)
        rows = {worker.id: worker for worker in self.selected_globally(self.query().filter_listed("id", sorted(set(holdings.values()))))} if holdings else {}
        return {task: rows[worker] for task, worker in holdings.items() if worker in rows}

    def agent_holder(self, agent: Agent) -> Ref:
        rows = self.session_worker(agent.session) if agent.role.is_sent() else []
        return Ref.build(rows[0]) if rows else Ref.build(agent)

    def session_worker(self, session: str) -> list[Worker]:
        if not session:
            return []
        rows = {w.id: w for query in (self.query().filter(session=session), self.query().filter(resume=session)) for w in self.selected(query)}
        return [rows[n] for n in sorted(rows)]
