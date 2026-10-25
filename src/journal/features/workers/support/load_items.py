from datetime import datetime, timezone

from journal.features.workers.support.load_item import LoadItem
from journal.features.workers.workers_options import WorkersOptions
from journal.models.author import Author
from journal.models.support.ref import Ref
from journal.models.worker import CLOCKED_OUT, MERGED, SENT_BACK, Worker
from journal.repositories.messages import Messages
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers

# a worker's moves that bring it to the orchestrator, and those that clear what it brought
UNFINISHED, IDLE = "ended without clocking out", "reported"
CLEARING = (SENT_BACK, MERGED, "released", "retired", "stopped", "sent a job")
DISPATCHES = ("dispatched", "sent a job")


class LoadItems:
    """What has waited on the orchestrator since `start`, read from the rows it is about: a worker's clock-out, weighted more when it comes back after a send-back, its end without clocking out, and its idle place while a task is open, each cleared by its next send-back, merge, release, retirement, stop or job; a user's message, cleared by the agent's first reply to it; with the times the orchestrator dispatched or sent a job."""

    def __init__(self, workers: Workers, messages: Messages, tasks: Tasks, settings: SettingRows) -> None:
        self.workers, self.messages, self.tasks, self.settings = workers, messages, tasks, settings

    def read(self, start: float) -> tuple[list[LoadItem], list[float]]:
        since = datetime.fromtimestamp(start, timezone.utc)
        workers = self.workers.selected(self.workers.query().filter_greater_equal("updated_at", since).order("id"))
        idle_weight = self.settings.decimal(WorkersOptions.WEIGHT_IDLE_PLACE) if self.tasks.open_count() else 0.0
        items = [item for worker in workers for item in self.worker_items(worker, idle_weight) if item.cleared_at == 0.0 or item.cleared_at >= start]
        dispatches = [time for worker in workers for word, time in worker.moves.steps if word in DISPATCHES and time >= start]
        return [*items, *self.message_items(since)], dispatches

    def worker_items(self, worker: Worker, idle_weight: float) -> list[LoadItem]:
        ref, repeat, pending, items = str(Ref.build(worker)), False, None, []
        weights = {CLOCKED_OUT: 1.0, UNFINISHED: 1.0, IDLE: idle_weight}
        for word, time in worker.moves.steps:
            if word in weights and pending is None and weights[word]:
                pending = LoadItem(ref, time, self.settings.decimal(WorkersOptions.WEIGHT_REPEAT_SEND_BACK) if word == CLOCKED_OUT and repeat else weights[word])
            elif word in CLEARING:
                items += [pending.cleared(time)] if pending is not None else []
                pending, repeat = None, word == SENT_BACK
        return [*items, *([pending] if pending is not None else [])]

    def message_items(self, since: datetime) -> list[LoadItem]:
        weight = self.settings.decimal(WorkersOptions.WEIGHT_USER_MESSAGE)
        asked = self.messages.selected(self.messages.main_chat().filter(author=Author.USER).filter_greater_equal("created_at", since).order("id"))
        replied: dict[int, float] = {}
        for reply in self.messages.recent_replies(since):
            replied.setdefault(reply.reply_target, reply.creation_time.timestamp())
        return [LoadItem(str(Ref.build(message)), message.creation_time.timestamp(), weight, replied.get(message.row_id, 0.0)) for message in asked]
