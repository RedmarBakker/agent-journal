from journal.chat.process_cards import ProcessCards
from journal.engine.job import Job
from journal.features.shell.support.output_process_card import OutputProcessCard
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.scope import Scope


class RunMarkStart(Job):
    """Every second a watched run still going that has passed its 3 seconds and shows no card yet gets its card in the chat."""

    interval_seconds = 1.0

    def __init__(self, outputs: CommandOutputs, card: OutputProcessCard, cards: ProcessCards, scope: Scope) -> None:
        self.outputs, self.card, self.cards, self.scope = outputs, card, cards, scope

    def tick(self, time: float) -> None:
        for output in self.outputs.running_watched():
            with self.scope.environment(output.environment_id):
                if output.is_past_mark(time) and not self.card.is_shown(output):
                    self.cards.show(self.card.card_contents(output))
