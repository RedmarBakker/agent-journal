from types import MappingProxyType

from journal.features.messages.support.mentions import Mentions
from journal.models.support.ref import Ref
from journal.repositories.environments import Environments


class HubMentions:
    """The rows a text names, with a team's name before a row naming the row of that team's hub environment."""

    def __init__(self, environments: Environments) -> None:
        self.environments = environments

    def found(self, text: str) -> list[Ref]:
        return Mentions.found(text, MappingProxyType({hub.team_name: hub.name for hub in self.environments.hubs()}))
