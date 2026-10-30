from journal.http.support.member_sessions import MemberSessions
from journal.http.support.request_head import RequestHead
from journal.http.support.supervisor_access import SupervisorAccess
from journal.support.actor import Actor
from journal.support.response import Response
from journal.supervisor_authority import SupervisorAuthority
from journal.supervisor_failure import SupervisorFailure
from journal.supervisor_principal import SupervisorPrincipal

TOKEN_HEADER = "x-journal-supervisor-token"
OWNER_PATHS = frozenset({"/_supervisor/v1/enrollment", "/_supervisor/v1/enrollment/change"})
SERVICE_PATHS = frozenset({
    "/_supervisor/v1/admit",
    "/_supervisor/v1/observe",
    "/_supervisor/v1/apply",
    "/_supervisor/v1/receipt",
})
PRIVATE_PREFIX = "/_supervisor/"


class SupervisorRequestAuth:
    """Resolve private supervisor requests before ordinary local/browser identity can run."""

    def __init__(self, authority: SupervisorAuthority, sessions: MemberSessions) -> None:
        self.authority, self.sessions = authority, sessions

    def before_identity(self, head: RequestHead, path: str) -> SupervisorAccess:
        has_token = TOKEN_HEADER in head.headers
        token = head.headers.get(TOKEN_HEADER, "")
        if path in OWNER_PATHS:
            if has_token:
                return self._refused(403, "the supervisor service credential cannot use owner management routes")
            if head.method != "POST":
                return self._refused(403, "supervisor owner management routes accept POST only")
            session = self.sessions.session(head.cookie)
            if session is None:
                return self._refused(401, "an authenticated owner browser session is required")
            return SupervisorAccess(actor=Actor.user(session.person))

        if path in SERVICE_PATHS:
            try:
                principal = self.authority.authenticate(token)
            except SupervisorFailure as denied:
                return self._refused(denied.status, str(denied))
            if head.method != "POST":
                return self._refused(403, "supervisor service credentials cannot use this method")
            return SupervisorAccess(principal.actor, principal)

        if path.startswith(PRIVATE_PREFIX):
            return self._refused(403, "the supervisor route is not available")
        if has_token:
            return self._refused(403, "the supervisor service credential cannot use generic journal routes")
        return SupervisorAccess()

    @staticmethod
    def _refused(status: int, message: str) -> SupervisorAccess:
        return SupervisorAccess(error=Response(status, {"error": message}))
