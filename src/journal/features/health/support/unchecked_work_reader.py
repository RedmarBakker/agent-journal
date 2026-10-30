from journal.features.health.support.bypass_log import BypassLog
from journal.features.health.support.journal_repository import JournalRepository
from journal.features.health.support.unchecked_work import UncheckedWork
from journal.models.agent import Agent


class UncheckedWorkReader:
    """The hooks and shell lines still waiting in the bypass log, read without taking them, so the agent is told before the chat's mark takes them off the log."""

    def __init__(self, log: BypassLog, repository: JournalRepository) -> None:
        self.log, self.repository = log, repository

    def read(self, agent: Agent) -> UncheckedWork:
        return UncheckedWork.read(self.log.waiting(), self.repository.is_open())
