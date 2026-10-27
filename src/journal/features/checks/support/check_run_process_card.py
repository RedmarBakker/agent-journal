from journal.chat.auto_dock import AutoDock
from journal.chat.process_card import ProcessCard
from journal.chat.process_card_contents import ProcessCardContents
from journal.chat.process_cards import FINAL
from journal.features.checks.support.check_output import CheckOutput
from journal.features.checks.support.check_run_view import CheckRunView
from journal.models.agent import Agent
from journal.models.check import Check
from journal.models.message import Message
from journal.repositories.checks import Checks
from journal.repositories.messages import Messages
from journal.support.actor import Actor
from journal.support.card_type import CardType


class CheckRunProcessCard(ProcessCard):
    """The card of a check's run in the chat of a live main agent: docked at the bottom of the chat while it runs, with the progress the Checks page reads, and then the mark of whether it passed, failed or was stopped, with the end of what it printed."""

    name = "check_run"

    def __init__(self, checks: Checks, messages: Messages, auto_dock: AutoDock) -> None:
        self.checks, self.messages, self.auto_dock = checks, messages, auto_dock

    def card_contents(self, check: Check, run_start: float, agent: Agent) -> ProcessCardContents:
        active = check.has_run_start(run_start)
        key = f"check-run:{check.id}:{run_start}"
        data = {"kind": "card", "check": check.id, "row": f"{Check.table()}:{check.id}", "began_at": run_start, **self.run_view(check, run_start, active).fields(), **self.dock_state(key, run_start, active), FINAL: not active}
        detail = "" if active else CheckOutput.tail(check.last_output)
        return ProcessCardContents(self.name, agent.environment_id, key, self.label(check, active), data, Actor.system(), CardType.CHECKS, active, detail, agent.session)

    def refresh(self, message: Message) -> dict:
        check = self.checks.find(message.data["check"])
        run_start = message.data["began_at"]
        active = check.has_run_start(run_start)
        return {**self.run_view(check, run_start, active).fields(), "active": active}

    def dock_state(self, key: str, run_start: float, active: bool) -> dict:
        cards = self.messages.keyed(key, Actor.system())
        if not cards:
            return self.auto_dock.dock_fields(run_start) if active else {}
        return {} if active else self.auto_dock.undock_fields(cards[0])

    @staticmethod
    def label(check: Check, active: bool) -> str:
        return f"{check.title}: {'running' if active else check.verdict()}"

    @staticmethod
    def run_view(check: Check, run_start: float, active: bool) -> CheckRunView:
        if active and check.progress is not None:
            return CheckRunView.running(check.progress)
        return CheckRunView.ended(check, run_start)
