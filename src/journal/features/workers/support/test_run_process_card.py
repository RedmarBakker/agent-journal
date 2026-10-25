from journal.chat.process_card import ProcessCard
from journal.chat.process_card_contents import ProcessCardContents
from journal.models.message import Message
from journal.models.test_outcome import TestOutcome
from journal.models.test_turn import TestTurn
from journal.models.test_turn_state import TestTurnState
from journal.models.worker import Worker
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class TestRunProcessCard(ProcessCard):
    """The card of a worker's test run in the chat of the agent that sent it: the worker active its tests, then whether they passed or how many failed, with the command it ran; written again at each save of its turn, so it refreshes from itself."""

    name = "test_run"

    __test__ = False

    def __init__(self, workers: Workers) -> None:
        self.workers = workers

    def card_contents(self, turn: TestTurn) -> ProcessCardContents:
        worker = self.workers.find(turn.worker)
        active = turn.state != TestTurnState.ENDED
        return ProcessCardContents(self.name, turn.environment_id, f"test-run:{turn.id}", self.label(turn, worker, active), {"kind": "card", "turn": turn.id}, Actor.system(), CardKind.COMMANDS, active, turn.command, worker.dispatcher)

    @staticmethod
    def label(turn: TestTurn, worker: Worker, active: bool) -> str:
        worker_label = f"Worker {worker.id}, {worker.name}"
        if active:
            return f"{worker_label} runs its tests"
        if turn.outcome == TestOutcome.PASSED:
            return f"{worker_label}: its tests passed"
        return f"{worker_label}: {turn.failed} of its tests failed" if turn.failed else f"{worker_label}: its test run failed"

    def refresh(self, message: Message) -> dict:
        return {"active": message.data["active"]}
