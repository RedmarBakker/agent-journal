from journal.chat.process_cards import LAST_PROGRESS_KEY
from journal.events.agent.line_delivered import LineDelivered
from journal.events.agent_listener import AgentListener
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.support.output_view import OutputView
from journal.repositories.messages import Messages
from journal.repositories.scope import Scope
from journal.support.actor import Actor


class WatchProgressRecord(AgentListener[LineDelivered]):
    """A watched output's progress line, once sent to the agent, is kept on the output's card as the progress the agent last saw, so the next line waits until the run has moved on from it."""

    def __init__(self, messages: Messages, scope: Scope) -> None:
        self.messages, self.scope = messages, scope

    def handle(self, event: LineDelivered) -> None:
        if event.nudge != ShellNudges.WATCH_VIEW.key:
            return
        with self.scope.environment(event.environment_id):
            for card in self.messages.with_key(OutputView.key(int(event.values["n"]))):
                self.messages.save(card.with_(data={**card.data, LAST_PROGRESS_KEY: float(event.values.get("fraction", 0.0))}), Actor.system())
