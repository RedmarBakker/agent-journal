import time

from journal.models.environment import Environment
from journal.repositories.environments import Environments
from journal.support.actor import Actor
from journal.support.rejection import Rejection
from journal.sync.team_account import TeamAccount
from journal.sync.team_chat_branch import TEAM_CHAT
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_requests import TeamRequests
from journal.sync.team_server_link import TeamServerLink

SESSION_BRANCH = "journal/session-"
RENEW_SECONDS = 30


class SessionLeases:
    """The sessions this machine holds: journal session start takes the team server's lease named for the session, refused while another machine holds it and, with the server unreachable, refused saying so before anything is written; then makes the session on the team's hub, with a branch of its own, or finds it, and records it held here, so this machine is its host. A held lease is renewed with the sync, and one another machine has taken since is let go here."""

    def __init__(self, account: TeamAccount, link: TeamServerLink, environments: Environments) -> None:
        self.account, self.link, self.environments = account, link, environments
        self.renewed_at = 0.0

    def start(self, name: str, actor: Actor) -> Environment:
        if not self.account.is_joined():
            raise Rejection("a session is a team's, held by one machine at a time: join a team first with journal team join")
        if name == TEAM_CHAT:
            raise Rejection("the Team chat is the team's own session: journal team claim holds it")
        TeamRequests.reached(lambda: self.link.acquire_lease(self.lease_name(name)))
        session = self.session(name, actor)
        self.account.record_held_sessions([*self.account.held_sessions(), name])
        return session

    def session(self, name: str, actor: Actor) -> Environment:
        sessions = self.environments.session_rows([name])
        return sessions[0] if sessions else self.environments.save(Environment.session(self.account.team_key(), name).with_(branch=SESSION_BRANCH + name), actor)

    def hosted(self) -> list[Environment]:
        return self.environments.session_rows(self.account.held_sessions())

    def renew(self) -> None:
        if time.monotonic() - self.renewed_at < RENEW_SECONDS:
            return
        self.renewed_at = time.monotonic()
        for name in self.account.held_sessions():
            self.renewed(name)

    def renewed(self, name: str) -> None:
        try:
            self.link.acquire_lease(self.lease_name(name))
        except TeamRefusal:
            self.account.record_held_sessions([session_name for session_name in self.account.held_sessions() if session_name != name])

    @staticmethod
    def lease_name(name: str) -> str:
        return f"session:{name}"
