from functools import partial

from journal.events.listener import Listener
from journal.support.listener_queue import ListenerQueue
from journal.events.rows.worker_merged import WorkerMerged
from journal.features.verification.support.model_fit_evidence import ModelFitEvidence
from journal.features.verification.support.verifier_dispatch import VerifierDispatch
from journal.features.workers.support.work_mode import WorkMode
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.setting_rows import SettingRows
from journal.repositories.statistics import Statistics
from journal.repositories.workers import Workers
from journal.support.actor import Actor

MERGES = "verification.merges"


class ModelFitSample(Listener[WorkerMerged]):
    """In orchestrator mode one merge in every workers.model_fit_sample is sampled: a verifier on the fast model, sent by the journal, judges from the task's brief, the diff and the report whether the worker's model was too strong, right or too weak; nought samples none; on the deferred worker after the merge has answered, so nothing it does touches the merge."""

    def __init__(self, deferred: ListenerQueue, settings: SettingRows, statistics: Statistics, workers: Workers, evidence: ModelFitEvidence, dispatch: VerifierDispatch, work_mode: WorkMode) -> None:
        self.deferred, self.settings, self.statistics, self.workers, self.evidence, self.dispatch, self.work_mode = deferred, settings, statistics, workers, evidence, dispatch, work_mode

    def handle(self, event: WorkerMerged) -> None:
        self.deferred.add(partial(self.sampled, event))

    def sampled(self, event: WorkerMerged) -> None:
        every = self.settings.integer(WorkersOptions.MODEL_FIT_SAMPLE)
        if every <= 0 or not self.work_mode.delegates_work():
            return
        if self.statistics.incremented(f"{MERGES}.{event.environment_id}", Actor.system()).value % every:
            return
        worker = self.workers.find(event.worker.id)
        self.dispatch.sent(worker, self.evidence.brief(worker), lambda: True)
