from journal.chat.process_cards import ProcessCards
from journal.events.listener import Listener
from journal.events.moments.output_view_changed import OutputViewChanged
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.scope import Scope


class ChangedOutputCard(Listener[OutputViewChanged]):
    """An output whose view changed has its process card written again from its files."""

    def __init__(self, outputs: CommandOutputs, card: OutputProcessCard, cards: ProcessCards, scope: Scope) -> None:
        self.outputs, self.card, self.cards, self.scope = outputs, card, cards, scope

    def handle(self, event: OutputViewChanged) -> None:
        with self.scope.environment(event.environment_id):
            if contents := self.card.card_contents(self.outputs.find(event.output)):
                self.cards.show(contents)
