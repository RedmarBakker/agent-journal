import json
import ssl
import urllib.error
import urllib.request

from sync_service.team_address import TeamAddress
from sync_service.team_refusal import TeamRefusal

REQUEST_SECONDS = 10
COPY_SECONDS = 120


class TeamLink:
    """The team server as the sync service reaches it, with what the journal server says of it: its address, the headers each request carries, the certificate authority to trust and the least protocol an answer may be in; an answer comes back as the bytes the team sent, which the service hands the journal server unread. A network fault is raised as the OSError it is, a refusal as a TeamRefusal."""

    def __init__(self, team: TeamAddress) -> None:
        self.team = team

    def push(self, body: dict) -> bytes:
        return self.sent("/push", json.dumps(body).encode(), REQUEST_SECONDS)

    def pull(self, path: str, wait_seconds: float) -> bytes:
        return self.sent(path, None, wait_seconds + REQUEST_SECONDS)

    def full_copy(self) -> bytes:
        return self.sent("/copy", None, COPY_SECONDS)

    def upload(self, address: str, data: bytes) -> None:
        self.sent(f"/files/{address}", data, COPY_SECONDS)

    def sent(self, path: str, body: bytes | None, seconds: float) -> bytes:
        request = urllib.request.Request(self.team.address + path, data=body, headers=self.team.headers)
        try:
            with urllib.request.urlopen(request, timeout=seconds, context=self.trust()) as answer:
                self.checked(answer.headers)
                return answer.read()
        except urllib.error.HTTPError as refused:
            raise TeamRefusal(self.refusal_line(refused)) from refused

    def checked(self, headers) -> None:
        server_protocol = int(headers.get(self.team.protocol_header, 0))
        if server_protocol < self.team.least_protocol:
            raise TeamRefusal(f"the team server speaks protocol {server_protocol}, older than this journal's {self.team.least_protocol}: upgrade the team server's image")

    @staticmethod
    def refusal_line(refused: urllib.error.HTTPError) -> str:
        body = refused.read()
        if refused.headers.get_content_type() != "application/json":
            return f"the team server answered {refused.code}: {body.decode(errors='replace').strip()}"
        return json.loads(body or b"{}").get("error", f"the team server answered {refused.code}")

    def trust(self) -> ssl.SSLContext:
        return ssl.create_default_context(cafile=self.team.authority) if self.team.authority else ssl.create_default_context()
