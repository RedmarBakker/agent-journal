from journal.engine.clock import Clock
from journal.models.browser_session import BrowserSession
from journal.http.support.session_cookie import SessionCookie
from journal.repositories.browser_sessions import BrowserSessions
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_server_link import TeamServerLink

CHECK_SECONDS = 30.0


class MemberSessions:
    """The browser sessions of a hosted journal that belong to someone still on the team: the team server's people are read at most every half minute, and the session of a person no longer among them is closed and refused; when they cannot be read the members last read stand, and with none read yet every session does, until the next half minute."""

    def __init__(self, sessions: BrowserSessions, link: TeamServerLink, clock: Clock) -> None:
        self.sessions, self.link, self.clock = sessions, link, clock
        self.members: set[int] | None = None
        self.read_at = float("-inf")

    def session(self, cookie: str) -> BrowserSession | None:
        key = SessionCookie.key(cookie)
        session = self.sessions.session(key)
        if session and self.removed(session):
            self.sessions.closed(key)
            return None
        return session

    def removed(self, session: BrowserSession) -> bool:
        members = self.current()
        return members is not None and session.person not in members

    def current(self) -> set[int] | None:
        if self.clock.time() - self.read_at > CHECK_SECONDS:
            self.read_at = self.clock.time()
            try:
                self.members = {person.id for person in self.link.people().people}
            except (OSError, TeamRefusal):
                pass
        return self.members
