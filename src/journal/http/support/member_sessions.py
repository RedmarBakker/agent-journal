from journal.engine.clock import Clock
from journal.models.browser_session import BrowserSession
from journal.http.support.session_cookie import SessionCookie
from journal.repositories.browser_sessions import BrowserSessions
from journal.sync.team_server_link import TeamServerLink

CHECK_SECONDS = 30.0


class MemberSessions:
    """The browser sessions of a hosted journal that belong to someone still on the team: the team server's people are read at most every half minute, and the session of a person no longer among them is closed and refused."""

    def __init__(self, sessions: BrowserSessions, link: TeamServerLink, clock: Clock) -> None:
        self.sessions, self.link, self.clock = sessions, link, clock
        self.members: set[int] = set()
        self.read_at = float("-inf")

    def session(self, cookie: str) -> BrowserSession | None:
        key = SessionCookie.key(cookie)
        session = self.sessions.session(key)
        if session and session.person not in self.current():
            self.sessions.closed(key)
            return None
        return session

    def current(self) -> set[int]:
        if self.clock.time() - self.read_at > CHECK_SECONDS:
            self.members = {person.id for person in self.link.people().people}
            self.read_at = self.clock.time()
        return self.members
