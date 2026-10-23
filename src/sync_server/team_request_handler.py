import json
from typing import Callable
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl, urlsplit

from sync_server.accept_request import AcceptRequest
from sync_server.account import Account
from sync_server.install_request import InstallRequest
from sync_server.host_ask_request import HostAskRequest
from sync_server.host_receipt import HostReceipt
from sync_server.password_request import PasswordRequest
from sync_server.signin_answer import SigninAnswer
from sync_server.signin_request import SigninRequest
from sync_server.admin_request import AdminRequest
from sync_server.blocks_request import BlocksRequest
from sync_server.file_answer import FileAnswer
from sync_server.file_place import FilePlace
from sync_server.lease_request import LeaseRequest
from sync_server.leases import UPGRADE_LEASE
from sync_server.login_request import LoginRequest
from sync_server.protocol import MIGRATION_HEADER, PROTOCOL, PROTOCOL_HEADER, UNVERSIONED, VERSION_HEADER
from sync_server.push_request import PushRequest
from sync_server.pull_query import PullQuery
from sync_server.pool_ask_request import PoolAskRequest
from sync_server.device_ask_request import DeviceAskRequest
from sync_server.host_decline import HostDecline
from sync_server.sync_answer import SyncAnswer
from sync_server.refusal import Refusal
from sync_server.upgrade_request import UpgradeRequest
from sync_server.upload_request import UploadRequest

BEARER = "Bearer "
FILES_PATH = "/files/"
FORWARDED_HEADER = "X-Forwarded-For"


class TeamRequestHandler(BaseHTTPRequestHandler):
    """One request to the team server, answered in JSON: POST /login, /accept, /install (the first connection to a server with no account, which makes its admin), /signin-links (a member's journal asking for a one-time link to open the hosted journal signed in) and /signin-links/redeem (the hosted journal taking one up), /host-requests and /host-requests/done (a write asked of an environment's host, and the host saying it is made), /pool-requests (a job asked of any machine of the pool), /device-requests (a write asked of one machine), /host-requests/claim and /host-requests/decline (a machine taking a pool request up, or turning it down), /push, answered with the pull it carries, /blocks, /invite, /devices/revoke, /people/remove, /people/password (an admin resetting a person's password), /password (a person changing their own), /team/version, /team/versions, /upload and /upgrade, GET /pull?after=<sequence>&wait=<seconds>&keys=<environment keys, comma separated>&slots=<pool slots offered>&free=<free ones>&version=<journal version>, which brings the writes waiting for those environments' host, for the device and for the pool too, /copy, /devices, /people and /team, which alone needs no token; /files/<table>/<row>/<name>, read with GET and written with POST of its bytes, and /leases?name=<name>, which POST /leases/take and /leases/release change; a refusal is a 403 with its line, an unknown path a 404. Every request names the protocol its journal speaks and every answer the server's: a journal on an older protocol is answered 426 with the line to upgrade it, and a push or pull from a journal on an older migration than the team's, or on another version than the pinned one while the team requires it, is refused with it; the device holding the upgrade lease is let through on its old version to send and pull before it upgrades."""

    def do_GET(self) -> None:
        if self.is_outdated_client():
            return
        url = urlsplit(self.path)
        if url.path.startswith(FILES_PATH):
            self.file_answer(lambda: self.server.team.files.get(self.file_place(url.path)))
            return
        query = dict(parse_qsl(url.query))
        team = self.server.team
        routes = {"/pull": lambda: self.current(lambda: team.pulls.answer(self.token(), PullQuery.parsed(query))), "/copy": lambda: team.copies.answer(self.token()), "/devices": lambda: team.admins.listed(self.token()), "/team": lambda: team.details.answer(), "/people": lambda: team.people.answer(self.token()), "/leases": lambda: self.lease_state(query.get("name", ""))}
        self.answered(routes.get(url.path))

    def do_POST(self) -> None:
        if self.is_outdated_client():
            return
        team = self.server.team
        if urlsplit(self.path).path.startswith(FILES_PATH):
            self.answered(lambda: FileAnswer(team.files.put(self.file_place(urlsplit(self.path).path), self.raw_body())))
            return
        routes = {
            "/login": lambda: self.login(self.login_request()),
            "/accept": lambda: team.logins.accepted(self.typed(AcceptRequest), self.address()),
            "/install": lambda: team.logins.installed(self.typed(InstallRequest), self.address()),
            "/signin-links": lambda: SigninAnswer(code=team.signins.issue(self.token(), team.clock.time())),
            "/host-requests": lambda: team.host_requests.created(self.token(), self.typed(HostAskRequest), team.clock.time()),
            "/host-requests/done": lambda: team.host_requests.finished(self.token(), self.typed(HostReceipt).id, team.clock.time()),
            "/host-requests/claim": lambda: team.host_requests.claimed(self.token(), self.typed(HostReceipt).id),
            "/host-requests/decline": lambda: team.host_requests.declined(self.token(), self.typed(HostDecline).id),
            "/pool-requests": lambda: team.host_requests.pooled(self.token(), self.typed(PoolAskRequest), team.clock.time()),
            "/device-requests": lambda: team.host_requests.addressed(self.token(), self.typed(DeviceAskRequest), team.clock.time()),
            "/signin-links/redeem": lambda: self.signin_answer(team.signins.redeemed(self.token(), self.typed(SigninRequest).code, team.clock.time())),
            "/push": lambda: self.current(lambda: self.push_reply(team)),
            "/upgrade": lambda: team.upgrades.answer(self.token(), self.typed(UpgradeRequest.parsed)),
            "/blocks": lambda: team.blocks.answer(self.token(), self.typed(BlocksRequest).tables),
            "/invite": lambda: team.admins.invite(self.token(), self.typed(AdminRequest).email),
            "/devices/revoke": lambda: team.admins.revoke(self.token(), self.typed(AdminRequest).device_id),
            "/people/remove": lambda: team.admins.remove(self.token(), self.typed(AdminRequest).account_id),
            "/people/password": lambda: team.admins.password_reset(self.token(), self.typed(AdminRequest).account_id),
            "/password": lambda: self.password_changed(self.typed(PasswordRequest)),
            "/team/version": lambda: team.admins.pin(self.token(), self.typed(AdminRequest).version),
            "/team/versions": lambda: team.admins.allow(self.token(), self.typed(AdminRequest).versions),
            "/upload": lambda: self.uploaded(self.typed(UploadRequest.parsed)),
            "/leases/take": lambda: team.leases.acquire(self.typed(LeaseRequest).name, team.devices.device(self.token()), team.devices.person(self.token()), team.clock.time()),
            "/leases/release": lambda: team.leases.release(self.typed(LeaseRequest).name, team.devices.device(self.token()), team.clock.time()),
        }
        self.answered(routes.get(urlsplit(self.path).path))

    def is_outdated_client(self) -> bool:
        client_protocol = int(self.headers.get(PROTOCOL_HEADER, UNVERSIONED))
        if client_protocol >= PROTOCOL:
            return False
        self.sent(426, {"error": f"this journal speaks protocol {client_protocol} and the team server {PROTOCOL}: upgrade the journal with journal update apply"})
        return True

    def push_reply(self, team) -> SyncAnswer:
        team.leases.require_free(UPGRADE_LEASE, team.devices.device(self.token()), team.clock.time())
        request = self.push_request()
        pushed = team.pushes.answer(self.token(), request, team.clock.time())
        return SyncAnswer(pushed, team.pulls.answer(self.token(), request.pull_query()))

    def current(self, route):
        team = self.server.team
        team.details.require_migration(int(self.headers.get(MIGRATION_HEADER, UNVERSIONED)))
        if not team.leases.is_holder(UPGRADE_LEASE, team.devices.device(self.token()), team.clock.time()):
            team.details.require_version(self.headers.get(VERSION_HEADER, ""))
        return route()

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
            self.sent(404, {"error": f"no such path: {self.path}"})
            return
        try:
            self.sent(200, asdict(route()))
        except Refusal as refusal:
            self.sent(403, {"error": str(refusal)})

    def file_place(self, path: str) -> FilePlace:
        self.server.team.devices.device(self.token())
        return FilePlace.parsed(path.removeprefix(FILES_PATH))

    def file_answer(self, read) -> None:
        try:
            data = read()
        except Refusal as refusal:
            self.sent(404, {"error": str(refusal)})
            return
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def sent(self, status: int, body: dict) -> None:
        text = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(text)))
        self.end_headers()
        self.wfile.write(text)

    def lease_state(self, name: str):
        self.server.team.devices.device(self.token())
        return self.server.team.leases.state(name, self.server.team.clock.time())

    def uploaded(self, request: UploadRequest):
        return self.server.team.uploads.answer(self.token(), request)

    def login_request(self) -> LoginRequest:
        return self.typed(LoginRequest)

    def push_request(self) -> PushRequest:
        return self.typed(PushRequest.parsed)

    def typed(self, kind: Callable):
        try:
            return kind(**json.loads(self.raw_body() or b"{}"))
        except (TypeError, ValueError) as wrong:
            raise Refusal(f"the body of this request is not what {urlsplit(self.path).path} takes: {wrong}") from wrong

    def raw_body(self) -> bytes:
        return self.rfile.read(int(self.headers.get("Content-Length", "0")))

    def token(self) -> str:
        header = self.headers.get("Authorization", "")
        if not header.startswith(BEARER):
            raise Refusal("this request carries no device token: log in with journal team login")
        return header[len(BEARER):]

    def address(self) -> str:
        return self.headers.get(FORWARDED_HEADER, "").split(",")[0].strip() or self.client_address[0]

    def log_message(self, format: str, *values) -> None:
        return None
