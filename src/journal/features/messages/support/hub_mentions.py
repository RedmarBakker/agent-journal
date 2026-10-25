from journal.features.messages.support.mentions import Mentions
from journal.models.support.ref import Ref
from journal.repositories.environments import Environments
from journal.sync.team_account import TeamAccount


class HubMentions:
    """The rows a text names, with the joined team's name before a row naming the row of its hub environment."""

    def __init__(self, account: TeamAccount, environments: Environments) -> None:
        self.account, self.environments = account, environments

    def found(self, text: str) -> list[Ref]:
        hubs = self.environments.team_chats() if self.account.team_name() else []
        return Mentions.found(text, [self.account.team_name()], hubs[0].name) if hubs else Mentions.found(text)
