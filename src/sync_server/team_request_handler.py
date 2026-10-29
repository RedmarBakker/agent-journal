import json
from typing import Callable
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlsplit

from sync_server.accept_request import AcceptRequest
from sync_server.account import Account
from sync_server.install_request import InstallRequest
from sync_server.password_request import PasswordRequest
from sync_server.signin_answer import SigninAnswer
from sync_server.admin_request import AdminRequest
from sync_server.file_store import LIMIT_BYTES
from sync_server.json_reply import JsonReply
from sync_server.login_request import LoginRequest
from sync_server.protocol import PROTOCOL, PROTOCOL_HEADER, UNVERSIONED, VERSION_HEADER
from sync_server.refusal import Refusal
from sync_server.missing_item import MissingItem
from sync_server.library_path import LIBRARY_PATH, LibraryPath
from sync_server.publish_request import PublishRequest
from sync_server.item_query import ItemQuery

BEARER = "Bearer "
# the most a JSON request body may hold; a file is held to the file store's own limit
JSON_LIMIT_BYTES = 4 * 1024 * 1024
FORWARDED_HEADER = "X-Forwarded-For"


class TeamRequestHandler(BaseHTTPRequestHandler):
    """One request to the team server, answered in JSON: POST /login, /accept, /install (the first connection to a server with no account, which makes its admin), /invite, /devices/revoke, /people/remove, /people/password (an admin resetting a person's password), /password (a person changing their own) and /backups (an admin asking for a backup of the team's database), GET /devices and /people, and the library's /library and /items routes; a refusal is a 403 with its line, an unknown path a 404. Every request names the protocol its journal speaks and every answer the server's: a journal on an older protocol is answered 426 with the line to upgrade it."""

    def do_GET(self) -> None:
        if self.is_outdated_client():
            return
        url = urlsplit(self.path)
        if LibraryPath.is_library(url.path):
            return self.library_read(url.path, ItemQuery.parsed(url.query))
        team = self.server.team
        routes = {"/devices": lambda: team.admins.listed(self.token()), "/people": lambda: team.people.answer(self.token())}
        self.answered(routes.get(url.path))

    def do_POST(self) -> None:
        if self.is_outdated_client():
            return
        team = self.server.team
        if LibraryPath.is_library(urlsplit(self.path).path):
            return self.answered(lambda: self.library_write(LibraryPath.parsed(urlsplit(self.path).path)))
        routes = {
            "/login": lambda: self.login(self.login_request()),
            "/accept": lambda: team.logins.accepted(self.typed(AcceptRequest), self.address()),
            "/install": lambda: team.logins.installed(self.typed(InstallRequest), self.address()),
            "/backups": lambda: team.backup_requests.answer(self.token()),
            "/invite": lambda: team.admins.invite(self.token(), self.typed(AdminRequest).email),
            "/devices/revoke": lambda: team.admins.revoke(self.token(), self.typed(AdminRequest).device_id),
            "/people/remove": lambda: team.admins.remove(self.token(), self.typed(AdminRequest).account_id),
            "/people/password": lambda: team.admins.password_reset(self.token(), self.typed(AdminRequest).account_id),
            "/password": lambda: self.password_changed(self.typed(PasswordRequest)),
        }
        self.answered(routes.get(urlsplit(self.path).path))

    def do_PUT(self) -> None:
        if self.is_outdated_client():
            return
        path = urlsplit(self.path).path
        if not LibraryPath.is_library(path):
            return self.answered(None)
        self.answered(lambda: self.server.team.library_routes.file_received(self.token(), self.file_path(path), self.raw_body()))

    def library_read(self, path: str, query: ItemQuery) -> None:
        routes = self.server.team.library_routes
        if path == LIBRARY_PATH:
            return self.answered(lambda: routes.member_summary(self.token()) if self.headers.get("Authorization") else routes.summary())
        parsed = LibraryPath.parsed(path)
        if parsed.file_name:
            return self.file_answer(lambda: routes.file(self.token(), parsed))
        if parsed.number:
            return self.answered(lambda: routes.version(self.token(), parsed))
        if parsed.name:
            return self.answered(lambda: routes.item(self.token(), parsed))
        self.answered(lambda: routes.listed(self.token(), query))

    def library_write(self, path: LibraryPath):
        routes = self.server.team.library_routes
        if path.is_withdrawal:
            return routes.withdrawn(self.token(), path)
        if path.is_deletion:
            return routes.deleted(self.token(), path)
        return routes.published(self.token(), path, self.typed(PublishRequest), self.headers.get(VERSION_HEADER, ""))

    @staticmethod
    def file_path(path: str) -> LibraryPath:
        parsed = LibraryPath.parsed(path)
        if not parsed.file_name:
            raise Refusal(f"a file is put at /items/<type>/<name>/<version>/files/<file>, not {path}")
        return parsed

    def is_outdated_client(self) -> bool:
        client_protocol = int(self.headers.get(PROTOCOL_HEADER, UNVERSIONED))
        if client_protocol >= PROTOCOL:
            return False
        JsonReply.send(self, 426, {"error": f"this journal speaks protocol {client_protocol} and the team server {PROTOCOL}: upgrade the journal with journal update apply"})
        return True

    def end_headers(self) -> None:
        self.send_header(PROTOCOL_HEADER, str(PROTOCOL))
        super().end_headers()

    def login(self, request: LoginRequest):
        return self.server.team.logins.answer(request, self.address())

    def password_changed(self, request: PasswordRequest) -> SigninAnswer:
        team = self.server.team
        return self.signin_answer(team.accounts.password_changed(team.devices.person(self.token()), request.old, request.new))

    @staticmethod
    def signin_answer(account: Account) -> SigninAnswer:
        return SigninAnswer(account_id=account.id, name=account.name)

    def answered(self, route) -> None:
        if route is None:
            JsonReply.send(self, 404, {"error": f"no such path: {self.path}"})
            return
        try:
            JsonReply.send(self, 200, asdict(route()))
        except MissingItem as missing:
            JsonReply.send(self, 404, {"error": str(missing)})
        except Refusal as refusal:
            JsonReply.send(self, 403, {"error": str(refusal)})

    def file_answer(self, read) -> None:
        try:
            data = read()
        except MissingItem as missing:
            JsonReply.send(self, 404, {"error": str(missing)})
            return
        except Refusal as refusal:
            JsonReply.send(self, 403, {"error": str(refusal)})
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def login_request(self) -> LoginRequest:
        return self.typed(LoginRequest)

    def typed(self, kind: Callable):
        try:
            return kind(**json.loads(self.raw_body(JSON_LIMIT_BYTES) or b"{}"))
        except (TypeError, ValueError) as wrong:
            raise Refusal(f"the body of this request is not what {urlsplit(self.path).path} takes: {wrong}") from wrong

    def raw_body(self, limit_bytes: int = LIMIT_BYTES) -> bytes:
        length = int(self.headers.get("Content-Length", "0"))
        if length > limit_bytes:
            raise Refusal(f"a body of {length} bytes is over this route's limit of {limit_bytes}")
        return self.rfile.read(length)

    def token(self) -> str:
        header = self.headers.get("Authorization", "")
        if not header.startswith(BEARER):
            raise Refusal("this request carries no device token: log in with journal team login")
        return header[len(BEARER):]

    def address(self) -> str:
        return self.headers.get(FORWARDED_HEADER, "").split(",")[0].strip() or self.client_address[0]

    def log_message(self, format: str, *values) -> None:
        return None
