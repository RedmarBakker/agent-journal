from journal.http.support.request_head import RequestHead
from journal.http.support.supervisor_access import SupervisorAccess
from journal.support.actor import Actor
from journal.support.caller import LOCAL_USER
from journal.support.response import Response
from journal.supervisor_authority import SupervisorAuthority
from journal.supervisor_failure import SupervisorFailure
from journal.supervisor_principal import SupervisorPrincipal

TOKEN_HEADER = "x-journal-supervisor-token"
AUTHORIZATION_HEADER = "authorization"
OWNER_PATHS = frozenset({"/_supervisor/v1/enrollment", "/_supervisor/v1/enrollment/change"})
SERVICE_PATHS = frozenset({
    "/_supervisor/v1/admit",
    "/_supervisor/v1/observe",
    "/_supervisor/v1/usage",
    "/_supervisor/v1/apply",
    "/_supervisor/v1/receipt",
})
PRIVATE_PREFIX = "/_supervisor/"


class SupervisorRequestAuth:
    """Resolve private supervisor requests before ordinary local/browser identity can run."""

    def __init__(self, authority: SupervisorAuthority) -> None:
        self.authority = authority

    def before_identity(self, head: RequestHead, path: str) -> SupervisorAccess:
        has_token, token, token_error = self._service_credential(head.headers)
        if path in OWNER_PATHS:
            if has_token:
                return self._refused(403, "the supervisor service credential cannot use owner management routes")
            if head.method != "POST":
                return self._refused(403, "supervisor owner management routes accept POST only")
            return SupervisorAccess(actor=Actor.user(LOCAL_USER))

        if path in SERVICE_PATHS:
            if token_error:
                return self._refused(403, "the supervisor service credential headers disagree")
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
    def _service_credential(headers: dict[str, str]) -> tuple[bool, str, bool]:
        token_header = TOKEN_HEADER in headers
        token = headers.get(TOKEN_HEADER, "")
        authorization = headers.get(AUTHORIZATION_HEADER)
        if authorization is None:
            return token_header, token, False
        scheme, separator, bearer = authorization.partition(" ")
        if scheme.lower() != "bearer":
            return token_header, token, False
        if not separator or not bearer or bearer.strip() != bearer or " " in bearer:
            return True, "", False
        if token_header and token != bearer:
            return True, "", True
        return True, bearer, False

    @staticmethod
    def _refused(status: int, message: str) -> SupervisorAccess:
        return SupervisorAccess(error=Response(status, {"error": message}))
