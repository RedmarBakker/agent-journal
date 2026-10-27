from journal.chat.process_cards import ProcessCards
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.repositories.command_outputs import CommandOutputs


class WatchUpdate(AgentListener[ToolFinished]):
    """After every tool use the card of the agent's watched output is read again from its files; the watch ends at its command's end, with the line that reports it."""

    def __init__(self, outputs: CommandOutputs, card: OutputProcessCard, cards: ProcessCards) -> None:
        self.outputs, self.card, self.cards = outputs, card, cards

    def handle(self, event: ToolFinished) -> None:
        for output in self.outputs.watched(event.session):
            if contents := self.card.card_contents(output):
                self.cards.show(contents)
