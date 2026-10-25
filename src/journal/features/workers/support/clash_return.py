import time

from journal.features.workers.support.worker_actions import WorkerActions
from journal.features.workers.workers_options import WorkersOptions
from journal.models.worker import Worker
from journal.repositories.setting_rows import SettingRows
from journal.repositories.workers import Workers
from journal.support.actor import Actor

RETURN_JOB = "the project's branch moved under your finished work and it no longer merges cleanly; once it is rebased, clock out again, and the journal runs your tests again"


class ClashReturn:
    """A worker's branch that clashes with the branch it merges into goes back to its worker to rebase, with the files it clashes in, by itself and without a word to the agent that sent it; its proofs stay checked, and a branch sent back as often in a row as the setting allows is named to that agent."""

    def __init__(self, workers: Workers, actions: WorkerActions, settings: SettingRows) -> None:
        self.workers, self.actions, self.settings = workers, actions, settings

    def send(self, worker: Worker, clashing: str) -> None:
        self.workers.save(worker.clashed(clashing, self.settings.integer(WorkersOptions.CLASH_LIMIT), time.time()), Actor.system())
        self.actions.send(worker.id, RETURN_JOB, worker.dispatcher, Actor.system())
