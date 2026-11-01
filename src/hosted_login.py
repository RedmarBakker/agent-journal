import hashlib
import hmac
import html
import http.client
import ipaddress
import os
import secrets
import sys
import time
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlencode, urlsplit

from login_throttle import LoginThrottle


SESSION_SECONDS = 43200
MAX_LOGIN_BYTES = 8192
PASSWORD_COST = 2**14
HOP_HEADERS = frozenset(
    (
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailer",
        "transfer-encoding",
        "upgrade",
    )
)


def password_digest(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode(), salt=salt, n=PASSWORD_COST, r=8, p=1, dklen=32)


def create_login_state(password: str) -> dict:
    if not password:
        raise ValueError("the hosted login password cannot be empty")
    salt = secrets.token_bytes(16)
    return {
        "salt": salt,
        "digest": password_digest(password, salt),
        "sessions": {},
        "clock": time.monotonic,
        "throttle": LoginThrottle(),
    }


def escape_login_message(message: str) -> str:
    return html.escape(message, quote=True)


def prune_expired_sessions(sessions: dict[str, float], now: float) -> None:
    for token, expiration in tuple(sessions.items()):
        if expiration <= now:
            del sessions[token]


class HostedLoginHandler(BaseHTTPRequestHandler):
    """The password gate and reverse proxy for a hosted journal."""

    protocol_version = "HTTP/1.1"

    def __init__(self, state: dict, upstream: tuple[str, int], *args, **kwargs) -> None:
        self.state, self.upstream = state, upstream
        super().__init__(*args, **kwargs)

    def do_GET(self) -> None:
        self.answer()

    def do_HEAD(self) -> None:
        self.answer()

    def do_POST(self) -> None:
        self.answer()

    def do_PUT(self) -> None:
        self.answer()

    def do_PATCH(self) -> None:
        self.answer()

    def do_DELETE(self) -> None:
        self.answer()

    def do_OPTIONS(self) -> None:
        self.answer()

    def answer(self) -> None:
        path = urlsplit(self.path)
        if path.path == "/login" and self.command == "GET":
            self.login_form(parse_qs(path.query).get("next", ["/"])[0])
        elif path.path == "/login" and self.command == "POST":
            self.login()
        elif path.path == "/logout" and self.command == "POST":
            self.logout()
        elif path.path == "/logout":
            self.write(405, b"Log out with POST", headers={"Allow": "POST"})
        elif not self.authenticated():
            self.login_required()
        else:
            self.proxy()

    def login_form(self, next_path: str, message: str = "", status: int = 200, retry_after: int = 0) -> None:
        target = self.safe_next(next_path)
        body = (
            "<!doctype html><html><head><meta charset=\"utf-8\"><title>Journal login</title></head><body>"
            "<main><h1>Journal login</h1>"
            f"<p>{escape_login_message(message)}</p>"
            "<form method=\"post\" action=\"/login\">"
            f"<input type=\"hidden\" name=\"next\" value=\"{html.escape(target, quote=True)}\">"
            "<label>Password <input type=\"password\" name=\"password\" autocomplete=\"current-password\" required></label>"
            "<button type=\"submit\">Log in</button></form></main></body></html>"
        ).encode()
        headers = {"Retry-After": str(retry_after)} if retry_after else None
        self.write(status, body, "text/html; charset=utf-8", headers)

    def login(self) -> None:
        now = self.state["clock"]()
        prune_expired_sessions(self.state["sessions"], now)
        source = self.client_source()
        if retry_after := self.state["throttle"].retry_after(source, now):
            self.write(429, b"Too many login attempts. Wait before trying again.", headers={"Retry-After": str(retry_after)})
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self.write(400, b"Invalid login request")
            return
        if length < 0:
            self.write(400, b"Invalid login request")
            return
        if length > MAX_LOGIN_BYTES:
            self.write(413, b"Login request is too large")
            return
        fields = parse_qs(self.rfile.read(length).decode("utf-8", errors="replace"), keep_blank_values=True)
        password = fields.get("password", [""])[0]
        if not hmac.compare_digest(password_digest(password, self.state["salt"]), self.state["digest"]):
            retry_after = self.state["throttle"].failed(source, now)
            self.login_form(fields.get("next", ["/"])[0], "The password was not accepted.", 401, retry_after)
            return
        self.state["throttle"].succeeded(source)
        token = secrets.token_urlsafe(32)
        self.state["sessions"][token] = now + SESSION_SECONDS
        self.send_response(303)
        self.send_header("Location", self.safe_next(fields.get("next", ["/"])[0]))
        cookie = f"journal_hosted_session={token}; Path=/; Max-Age={SESSION_SECONDS}; HttpOnly; Secure; SameSite=Lax"
        self.send_header("Set-Cookie", cookie)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True

    def authenticated(self) -> bool:
        token = self.session_token()
        expiration = self.state["sessions"].get(token, 0)
        if expiration > self.state["clock"]():
            return True
        self.state["sessions"].pop(token, None)
        return False

    def logout(self) -> None:
        if not self.authenticated():
            return self.login_required()
        self.state["sessions"].pop(self.session_token(), None)
        self.send_response(303)
        self.send_header("Location", "/login")
        self.send_header("Set-Cookie", "journal_hosted_session=; Path=/; Max-Age=0; HttpOnly; Secure; SameSite=Lax")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True

    def session_token(self) -> str:
        for part in self.headers.get("Cookie", "").split(";"):
            name, _, value = part.strip().partition("=")
            if name == "journal_hosted_session":
                return value
        return ""

    def client_source(self) -> str:
        forwarded = self.headers.get("X-Forwarded-For", "")
        candidate = forwarded.split(",")[-1].strip() if forwarded else ""
        try:
            return str(ipaddress.ip_address(candidate))
        except ValueError:
            return str(ipaddress.ip_address(self.client_address[0]))

    def login_required(self) -> None:
        target = self.safe_next(self.path)
        self.send_response(303)
        self.send_header("Location", "/login?" + urlencode({"next": target}))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", "0")
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True

    def proxy(self) -> None:
        connection = http.client.HTTPConnection(*self.upstream, timeout=30)
        content_length = self.headers.get("Content-Length")
        try:
            length = int(content_length) if content_length else 0
        except ValueError:
            self.write(400, b"Invalid request length")
            return
        if length < 0:
            self.write(400, b"Invalid request length")
            return
        body = self.rfile.read(length) if length else None
        connection_headers = {
            token.strip().lower()
            for value in self.headers.get_all("Connection", [])
            for token in value.split(",")
        }
        headers = {}
        for name, value in self.headers.items():
            lowered = name.lower()
            if lowered in HOP_HEADERS | connection_headers | {"host", "content-length"}:
                continue
            if lowered == "cookie":
                value = "; ".join(
                    cookie.strip()
                    for cookie in value.split(";")
                    if cookie.strip().partition("=")[0] != "journal_hosted_session"
                )
                if not value:
                    continue
            headers[name] = value
        headers["Host"] = self.headers.get("Host", f"{self.upstream[0]}:{self.upstream[1]}")
        try:
            connection.request(self.command, self.path, body=body, headers=headers)
            response = connection.getresponse()
        except (OSError, http.client.HTTPException):
            connection.close()
            self.write(503, b"The journal is unavailable")
            return
        self.send_response(response.status, response.reason)
        for name, value in response.getheaders():
            if name.lower() not in HOP_HEADERS:
                self.send_header(name, value)
        self.send_header("Connection", "close")
        self.end_headers()
        while chunk := response.read1(65536):
            self.wfile.write(chunk)
            self.wfile.flush()
        self.close_connection = True
        connection.close()

    def write(
        self,
        status: int,
        body: bytes,
        content_type: str = "text/plain; charset=utf-8",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        for name, value in (headers or {}).items():
            self.send_header(name, value)
        self.send_header("Connection", "close")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)
        self.close_connection = True

    @staticmethod
    def safe_next(path: str) -> str:
        unsafe = ("//", "\\", "\r", "\n")
        if not path.startswith("/") or any(part in path for part in unsafe):
            return "/"
        return path


def main() -> int:
    password = os.environ.pop("JOURNAL_HOSTED_PASSWORD", "")
    if len(password) < 16:
        print(
            "JOURNAL_HOSTED_PASSWORD must contain at least 16 characters before the hosted login can start",
            file=sys.stderr,
        )
        return 2
    upstream = urlsplit(os.environ.get("JOURNAL_HOSTED_UPSTREAM", "http://127.0.0.1:8421"))
    allowed_hosts = {"journal", "localhost", "127.0.0.1"}
    if upstream.scheme != "http" or upstream.hostname not in allowed_hosts:
        print("JOURNAL_HOSTED_UPSTREAM must name the local journal HTTP service", file=sys.stderr)
        return 2
    port = int(os.environ.get("JOURNAL_HOSTED_PORT", "8440"))
    state = create_login_state(password)
    handler = partial(HostedLoginHandler, state, (upstream.hostname, upstream.port or 80))
    ThreadingHTTPServer(("0.0.0.0", port), handler).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
