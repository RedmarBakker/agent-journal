from datetime import datetime, timezone

from journal.features.workers.support.load_item import LoadItem
from journal.features.workers.workers_options import WorkersOptions
from journal.models.author import Author
from journal.models.support.ref import Ref
from journal.models.worker import DELIVERY_MOVE, MERGED, REJECTION_MOVE, Worker
from journal.repositories.messages import Messages
from journal.repositories.proofs import Proofs
from journal.models.proof_state import ProofState
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers

# a worker's moves that bring it to the orchestrator, and those that end what it brought without clearing it
UNFINISHED = "ended without clocking out"
ENDING = (REJECTION_MOVE, "released", "retired", "stopped", "sent a job")
DISPATCHES = ("dispatched", "sent a job")


class LoadItems:
    """What has waited on the orchestrator since `start`, read from the rows it is about: a worker's clock-out, weighted more when it comes back after a send-back, its end without clocking out, each cleared by its merge or a checked proof and ended without a clearing by a send-back, a release, a retirement, a stop or a new job; a user's message, cleared by the agent's first reply naming it, never by a reaction or a read; with the times the orchestrator dispatched or sent a job."""

    def __init__(self, workers: Workers, messages: Messages, tasks: Tasks, settings: SettingRows, proofs: Proofs) -> None:
        self.workers, self.messages, self.tasks, self.settings, self.proofs = workers, messages, tasks, settings, proofs

    def read(self, start: float) -> tuple[list[LoadItem], list[float]]:
        window_start = datetime.fromtimestamp(start, timezone.utc)
        workers = self.workers.selected(self.workers.query().filter_greater_equal("updated_at", window_start).order("id"))
        items = [item for worker in workers for item in self.worker_items(worker) if item.cleared_at == 0.0 or item.cleared_at >= start]
        dispatches = [time for worker in workers for word, time in worker.moves.steps if word in DISPATCHES and time >= start]
        return [*items, *self.message_items(window_start)], dispatches

    def worker_items(self, worker: Worker) -> list[LoadItem]:
        ref, repeat, pending, items, checks = str(Ref.build(worker)), False, None, [], self.check_times(worker)
        weights = {DELIVERY_MOVE: 1.0, UNFINISHED: 1.0}
        for word, time in worker.moves.steps:
            pending = self.checked(pending, checks, time, items)
            if word in weights and pending is None and weights[word]:
                is_return = word == DELIVERY_MOVE and repeat
                pending = LoadItem(ref, time, self.settings.decimal(WorkersOptions.RESEND_WEIGHT) if is_return else weights[word], is_repeat=is_return)
            elif word == MERGED or word in ENDING:
                items += self.closed(pending, word, time)
                pending, repeat = None, word == REJECTION_MOVE
        pending = self.checked(pending, checks, float("inf"), items)
        if pending is not None:
            items.append(pending)
        return items

    @staticmethod
    def closed(pending: LoadItem | None, word: str, time: float) -> list[LoadItem]:
        if pending is None:
            return []
        return [pending.cleared(time) if word == MERGED else pending.ended(time)]

    @staticmethod
    def checked(pending: LoadItem | None, checks: list[float], cutoff: float, items: list[LoadItem]) -> LoadItem | None:
        check_time = next((time for time in checks if pending is not None and pending.arrived_at <= time < cutoff), None)
        if pending is None or check_time is None:
            return pending
        items.append(pending.cleared(check_time))
        return None

    def check_times(self, worker: Worker) -> list[float]:
        task_ids = self.tasks.holder_task_ids(Ref.build(worker))
        proofs = self.proofs.task_proofs(self.tasks.find(task_ids[0])) if task_ids else []
        return sorted(proof.update_time.timestamp() for proof in proofs if proof.state == ProofState.CHECKED)

    def message_items(self, begin: datetime) -> list[LoadItem]:
        weight = self.settings.decimal(WorkersOptions.WEIGHT_USER_MESSAGE)
        user_messages = self.messages.selected(self.messages.main_chat().filter(author=Author.USER).filter_greater_equal("created_at", begin).order("created_at").order("id"))
        replied: dict[int, float] = {}
        for reply in self.messages.recent_replies(begin):
            replied[reply.reply_target] = min(replied.get(reply.reply_target, reply.creation_time.timestamp()), reply.creation_time.timestamp())
        return [LoadItem(str(Ref.build(message)), message.creation_time.timestamp(), weight, replied.get(message.row_id, 0.0)) for message in user_messages]
