from journal.chat.docking import Docking
from journal.chat.process_cards import ProcessCards
from journal.engine.base_state import BaseState
from journal.engine.stack_moved import StackMoved
from journal.events.listener import Listener
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.features.shell.support.output_view import OutputView
from journal.features.tasks.support.wait_targets import WaitTargets
from journal.repositories.agents import Agents
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.messages import Messages
from journal.support.actor import Actor


class WaitingRunDocks(Listener[StackMoved]):
    """The card of a run an agent starts waiting for is docked at once and cannot be taken down; once no agent of the environment waits for it any more, it can be again."""

    def __init__(self, agents: Agents, outputs: CommandOutputs, messages: Messages, card: OutputProcessCard, cards: ProcessCards, docking: Docking) -> None:
        self.agents, self.outputs, self.messages, self.card, self.cards, self.docking = agents, outputs, messages, card, cards, docking

    def handle(self, event: StackMoved) -> None:
        for number in self.output_ids(event.added_states):
            self.locked(number)
        for number in self.released_ids(event):
            for message in self.messages.keyed(OutputView.key(number), Actor.system()):
                self.docking.wait_release(message, Actor.system())

    def locked(self, number: int) -> None:
        output = self.outputs.find(number)
        if not output.ended:
            self.docking.wait_lock(self.cards.show(self.card.card_contents(output)), Actor.system())

    def released_ids(self, event: StackMoved) -> set[int]:
        ended = self.output_ids(event.removed_states)
        return ended - self.waiting_output_ids(event.agent.environment_id) if ended else set()

    def waiting_output_ids(self, environment_id: int) -> set[int]:
        return {number for agent in self.agents.unended_scoped(environment_id) for number in WaitTargets.wait_output_ids(agent.stack)}

    @staticmethod
    def output_ids(states: tuple[BaseState, ...]) -> set[int]:
        return {number for state in states for number in state.wait_output_ids()}
