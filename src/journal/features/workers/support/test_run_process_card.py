from journal.chat.process_card import ProcessCard
from journal.chat.process_card_contents import ProcessCardContents
from journal.models.message import Message
from journal.models.test_outcome import TestOutcome
from journal.models.test_turn import TestTurn
from journal.models.test_turn_state import TestTurnState
from journal.models.support.ref import Ref
from journal.models.worker import Worker
from journal.repositories.tasks import Tasks
from journal.repositories.workers import Workers
from journal.support.actor import Actor
from journal.support.card_type import CardType


class TestRunProcessCard(ProcessCard):
    """The card of a worker's test run in the chat of the agent that sent it: a run going, then whether its tests passed or how many failed, marked with the worker after its icon, with the command it ran, the output it opens to and the worker's task whose proofs it shows; written again at each save of its turn, so it refreshes from itself."""

    name = "test_run"

    __test__ = False

    def __init__(self, workers: Workers, tasks: Tasks) -> None:
        self.workers, self.tasks = workers, tasks

    def card_contents(self, turn: TestTurn) -> ProcessCardContents:
        worker = self.workers.find(turn.worker)
        active = turn.state != TestTurnState.ENDED
        task_ids = self.tasks.holder_task_ids(Ref(Worker.table(), worker.id))
        card_fields = {"kind": "card", "turn": turn.id, "worker": f"Worker {worker.id}, {worker.name}", "output": turn.output, "line": turn.command, "summary": self.summary(turn, active), "proof_task": task_ids[0] if task_ids else 0}
        return ProcessCardContents(self.name, turn.environment_id, f"test-run:{turn.id}", self.label(turn, active), card_fields, Actor.system(), CardType.WORKER_TESTS, active, turn.command, worker.dispatcher)

    @staticmethod
    def label(turn: TestTurn, active: bool) -> str:
        if active:
            return "Running its tests"
        if turn.outcome == TestOutcome.PASSED:
            return "Its tests passed"
        return f"{turn.failed} of its tests failed" if turn.failed else "Its test run failed"

    @staticmethod
    def summary(turn: TestTurn, active: bool) -> str:
        if active:
            return "running"
        if turn.outcome == TestOutcome.PASSED:
            return "passed"
        return f"{turn.failed} failed" if turn.failed else "failed"

    def refresh(self, message: Message) -> dict:
        return {"active": message.data["active"]}
