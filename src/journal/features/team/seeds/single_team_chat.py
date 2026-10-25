from journal.features.seed import Seed
from journal.repositories.environment_owners import OWNER
from journal.repositories.environments import Environments
from journal.repositories.links import Links
from journal.support.actor import Actor
from journal.sync.team_chat_branch import TEAM_CHAT


class SingleTeamChat(Seed):
    """At boot, the Team chat is one environment, known to the team as team and owned by no one; a journal that holds more, as a join once made them, keeps the first and drops the others, which that join made empty. A session of its own, which has its own branch, is no Team chat and is left alone."""

    def __init__(self, environments: Environments, links: Links) -> None:
        self.environments, self.links = environments, links

    def run(self) -> None:
        chats = self.environments.team_chats()
        if not chats:
            return
        team_chat, *duplicates = chats
        for link in self.links.model_links("target", [team_chat], OWNER):
            self.links.delete(link, Actor.system())
        if team_chat.team_name != TEAM_CHAT:
            self.environments.save(team_chat.with_(team_name=TEAM_CHAT), Actor.system())
        for chat in duplicates:
            self.environments.wipe(chat, Actor.system())
