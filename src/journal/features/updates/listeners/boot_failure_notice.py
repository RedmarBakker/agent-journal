from journal.support.card_outcome import CardOutcome
from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.boot_failed import BootFailed
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.card_type import CardType
from journal.supervisor_link import SupervisorLink


class BootFailureNotice(Listener[BootFailed]):
    """Each environment whose launch runs is told in its chat what failed at boot and what the journal did about it."""

    def __init__(self, environments: Environments, supervisor: SupervisorLink, agents: Agents, scope: Scope, cards: MomentCards) -> None:
        self.environments, self.supervisor, self.agents, self.scope, self.cards = environments, supervisor, agents, scope, cards

    def handle(self, event: BootFailed) -> None:
        for environment in self.supervisor.running(self.environments.all()):
            with self.scope.environment(environment.row_id):
                agent = self.agents.current()
            self.cards.show(environment.row_id, agent.session if agent else None, "The journal took too long to start and was restarted", event.text, shows=CardType.UPDATES, outcome=CardOutcome.WARNED)
