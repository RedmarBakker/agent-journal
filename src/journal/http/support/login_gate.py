from journal.http.support.request import Request
from journal.http.support.member_sessions import MemberSessions
from journal.support.response import Response
from journal.sync.hosting import Hosting
from journal.sync.sync_secret import SyncSecret

OPEN_PATHS = ("/sign-in", "/open", "/assets/", "/hooks/", "/cli", "/shell/")


class LoginGate:
    """A hosted journal's door: every request but the sign-in page, the one-time link a member's journal opens, the built files it loads, the hooks, the CLI and a service beside the journal that carries its secret, the sync service among them, needs a browser session, and one without is sent to /sign-in when it asks for a page and refused 401 when it asks the API; a journal that is not hosted has no door."""

    def __init__(self, hosting: Hosting, sessions: MemberSessions, secret: SyncSecret) -> None:
        self.hosting, self.sessions, self.secret = hosting, sessions, secret

    def refusal(self, request: Request) -> Response | None:
        if not self.hosting.is_hosted() or request.path.startswith(OPEN_PATHS) or self.secret.allows(request.headers) or self.sessions.session(request.cookie):
            return None
        if request.path.startswith("/journal/"):
            return Response(401, {"error": "sign in with your team account at /sign-in"})
        return Response(303, None, {"Location": "/sign-in"})
