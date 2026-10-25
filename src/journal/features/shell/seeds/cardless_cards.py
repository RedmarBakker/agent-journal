from journal.features.seed import Seed
from journal.features.shell.support.cardless_runs import CardlessRuns
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.messages import Messages
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.card_kind import CardKind


class CardlessCards(Seed):
    """At boot, the cards a command wrote before it was judged cardless go: a line that only read, searched or listed, or did only everyday git, whose commit and push marks say it, and did not fail."""

    def __init__(self, messages: Messages, outputs: CommandOutputs, cardless: CardlessRuns, environments: Environments, scope: Scope) -> None:
        self.messages, self.outputs, self.cardless, self.environments, self.scope = messages, outputs, cardless, environments, scope

    def run(self) -> None:
        for environment in self.environments.all():
            with self.scope.environment(environment.row_id):
                self.cleared()

    def cleared(self) -> None:
        for card in self.messages.newest_shown(CardKind.COMMANDS):
            outputs = self.outputs.matching(id=card.data.get("output", 0))
            if outputs and self.cardless.is_cardless(outputs[0]):
                self.messages.delete(card, Actor.system())
