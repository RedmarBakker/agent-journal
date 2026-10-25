from journal.features.messages.support.mentions import Mentions
from journal.models.support.ref import Ref
from journal.repositories.environments import Environments


class HubMentions:
    """The rows a text names, with a team's name before a row naming the row of that team's hub environment."""

    def __init__(self, environments: Environments) -> None:
        self.environments = environments

    def found(self, text: str) -> list[Ref]:
        hubs = self.environments.hubs()
        return Mentions.found(text, [hub.team_name for hub in hubs], hubs[0].name) if hubs else Mentions.found(text)
