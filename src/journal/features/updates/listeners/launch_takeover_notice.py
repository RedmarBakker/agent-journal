from journal.chat.moment_cards import MomentCards
from journal.events.listener import Listener
from journal.events.moments.server_replaced import ServerReplaced
from journal.repositories.agents import Agents
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.actor import Actor
from journal.support.card_type import CardType
from journal.supervisor_link import SupervisorLink

NOTICE = "The journal was updated to version {version}, replacing {previous}"


class LaunchTakeoverNotice(Listener[ServerReplaced]):
    """Each environment whose launch still runs when a newer journal server replaced the one it had is told so: a mark in its chat, and the moment on its agent's row, which the updates conduct says in one line at the agent's next hook."""

    def __init__(self, environments: Environments, supervisor: SupervisorLink, agents: Agents, scope: Scope, cards: MomentCards) -> None:
        self.environments, self.supervisor, self.agents, self.scope, self.cards = environments, supervisor, agents, scope, cards

    def handle(self, event: ServerReplaced) -> None:
        for environment in self.supervisor.running(self.environments.all()):
            with self.scope.environment(environment.row_id):
                agent = self.agents.current()
            label = NOTICE.format(version=event.version, previous=event.previous)
            self.cards.show(environment.row_id, agent.session if agent else None, label, shows=CardType.UPDATES)
            if agent is not None:
                self.agents.save(agent.upgraded(event.previous, event.version, event.time), Actor.system())
