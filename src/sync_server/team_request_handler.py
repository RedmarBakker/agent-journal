import json
from typing import Callable
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qsl, urlsplit

from sync_server.accept_request import AcceptRequest
from sync_server.agent_view_post import AgentViewPost
from sync_server.account import Account
from sync_server.departure_answer import DepartureAnswer
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
from sync_server.file_store import LIMIT_BYTES
from sync_server.lease_request import LeaseRequest
from sync_server.json_reply import JsonReply
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
from sync_server.missing_item import MissingItem
from sync_server.library_path import LIBRARY_PATH, LibraryPath
from sync_server.publish_request import PublishRequest
from sync_server.item_query import ItemQuery
from sync_server.upgrade_request import UpgradeRequest
from sync_server.upload_request import UploadRequest

BEARER = "Bearer "
# the most a JSON request body may hold; a file is held to the file store's own limit
JSON_LIMIT_BYTES = 4 * 1024 * 1024
FILES_PATH = "/files/"
FORWARDED_HEADER = "X-Forwarded-For"
# where a browser that is no member is sent: the page claiming a server with no admin yet, else a refusal
SETUP_PATH = "/setup"


class TeamRequestHandler(BaseHTTPRequestHandler):
    """One request to the team server, answered in JSON: POST /login, /accept, /install (the first connection to a server with no account, which makes its admin), /signin-links (a member's journal asking for a one-time link to open the hosted journal signed in) and /signin-links/redeem (the hosted journal taking one up), /host-requests and /host-requests/done (a write asked of an environment's host, and the host saying it is made), /pool-requests (a job asked of any machine of the pool), /device-requests (a write asked of one machine), /host-requests/claim and /host-requests/decline (a machine taking a pool request up, or turning it down), /push, answered with the pull it carries, /blocks, /invite, /devices/revoke, /people/remove, /people/leave (a member's own journal leaving the team, its leases freed and its shared environments withdrawn), /people/password (an admin resetting a person's password), /password (a person changing their own), /team/version, /team/versions, /team/repository (an admin tying the team to its repository or untying it), /team/hub (an admin's migration marking the team on the hub), /upload, /upgrade and /backups (an admin asking for a backup of the team's database before the move to the hub), GET /pull?after=<sequence>&wait=<seconds>&keys=<environment keys, comma separated>&slots=<pool slots offered>&free=<free ones>&version=<journal version>, which brings the writes waiting for those environments' host, for the device and for the pool too, /copy, /devices, /people and /team, which alone needs no token; /files/<table>/<row>/<name>, read with GET and written with POST of its bytes, and /leases?name=<name>, which POST /leases/take, /leases/take-free (refused while another device holds it, lapsed or not) and /leases/release change, a lease newly taken waking every held pull so its new holder pulls at once for what it now hosts; a refusal is a 403 with its line, an unknown path a 404. Every request names the protocol its journal speaks and every answer the server's: a journal on an older protocol is answered 426 with the line to upgrade it, and a push or pull from a journal on an older migration than the team's, or on another version than the pinned one while the team requires it, is refused with it; the device holding the upgrade lease is let through on its old version to send and pull before it upgrades."""

    def do_GET(self) -> None:
        if urlsplit(self.path).path == SETUP_PATH:
            return self.page(self.server.team.setup_page.shown(self.public_address()))
        if self.is_outdated_client():
            return
        url = urlsplit(self.path)
        if url.path.startswith(FILES_PATH):
            self.file_answer(lambda: self.server.team.files.get(self.file_place(url.path)))
            return
        if LibraryPath.is_library(url.path):
            return self.library_read(url.path, ItemQuery.parsed(url.query))
        query = dict(parse_qsl(url.query))
        team = self.server.team
        routes = {"/pull": lambda: self.current(lambda: team.pulls.answer(self.token(), PullQuery.parsed(query))), "/copy": lambda: team.copies.answer(self.token()), "/devices": lambda: team.admins.listed(self.token()), "/team": lambda: team.details.answer(), "/people": lambda: team.people.answer(self.token()), "/leases": lambda: self.lease_state(query.get("name", "")), "/agent-views": lambda: team.agent_views.listed(self.token(), [key for key in query.get("keys", "").split(",") if key], team.clock.time())}
        self.answered(routes.get(url.path))

    def do_POST(self) -> None:
        if urlsplit(self.path).path == SETUP_PATH:
            return self.page(self.server.team.setup_page.posted(self.raw_body(), self.public_address()))
        if self.is_outdated_client():
            return
        team = self.server.team
        if urlsplit(self.path).path.startswith(FILES_PATH):
            self.answered(lambda: FileAnswer(team.files.put(self.file_place(urlsplit(self.path).path), self.raw_body())))
            return
        if LibraryPath.is_library(urlsplit(self.path).path):
            return self.answered(lambda: self.library_write(LibraryPath.parsed(urlsplit(self.path).path)))
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
            "/agent-views": lambda: team.agent_views.posted(self.token(), self.typed(AgentViewPost), team.clock.time()),
            "/upgrade": lambda: team.upgrades.answer(self.token(), self.typed(UpgradeRequest.parsed)),
            "/backups": lambda: team.backup_requests.answer(self.token()),
            "/blocks": lambda: team.blocks.answer(self.token(), self.typed(BlocksRequest).tables),
            "/invite": lambda: team.admins.invite(self.token(), self.typed(AdminRequest).email),
            "/devices/revoke": lambda: team.admins.revoke(self.token(), self.typed(AdminRequest).device_id),
            "/people/remove": lambda: team.admins.remove(self.token(), self.typed(AdminRequest).account_id),
            "/people/leave": lambda: self.departed(team),
            "/people/password": lambda: team.admins.password_reset(self.token(), self.typed(AdminRequest).account_id),
            "/password": lambda: self.password_changed(self.typed(PasswordRequest)),
            "/team/version": lambda: team.admins.pin(self.token(), self.typed(AdminRequest).version),
            "/team/versions": lambda: team.admins.allow(self.token(), self.typed(AdminRequest).versions),
            "/team/repository": lambda: team.admins.tie(self.token(), self.typed(AdminRequest).tied),
            "/team/hub": lambda: team.admins.moved_to_hub(self.token()),
            "/upload": lambda: self.uploaded(self.typed(UploadRequest.parsed)),
            "/leases/take": lambda: self.lease_taken(team.leases.acquire),
            "/leases/take-free": lambda: self.lease_taken(team.leases.acquire_free),
            "/leases/release": lambda: team.leases.release(self.typed(LeaseRequest).name, team.devices.device(self.token()), team.clock.time()),
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
        return routes.published(self.token(), path, self.typed(PublishRequest), self.headers.get(VERSION_HEADER, ""))

    @staticmethod
    def file_path(path: str) -> LibraryPath:
        parsed = LibraryPath.parsed(path)
        if not parsed.file_name:
            raise Refusal(f"a file is put at /items/<type>/<name>/<version>/files/<file>, not {path}")
        return parsed

    def departed(self, team) -> DepartureAnswer:
        person = team.devices.person(self.token())
        return DepartureAnswer(team.departure.left(person.id, f"user:{person.id}"))

    def page(self, answer: tuple[int, str]) -> None:
        status, text = answer
        body = text.encode()
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8" if status == 200 else "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def public_address(self) -> str:
        return f"https://{self.headers.get('Host', '')}"

    def is_outdated_client(self) -> bool:
        client_protocol = int(self.headers.get(PROTOCOL_HEADER, UNVERSIONED))
        if client_protocol >= PROTOCOL:
            return False
        JsonReply.send(self, 426, {"error": f"this journal speaks protocol {client_protocol} and the team server {PROTOCOL}: upgrade the journal with journal update apply"})
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
            JsonReply.send(self, 404, {"error": f"no such path: {self.path}"})
            return
        try:
            JsonReply.send(self, 200, asdict(route()))
        except MissingItem as missing:
            JsonReply.send(self, 404, {"error": str(missing)})
        except Refusal as refusal:
            JsonReply.send(self, 403, {"error": str(refusal)})

    def file_place(self, path: str) -> FilePlace:
        self.server.team.devices.device(self.token())
        return FilePlace.parsed(path.removeprefix(FILES_PATH))

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

    def lease_taken(self, take: Callable):
        request, team = self.typed(LeaseRequest), self.server.team
        device = team.devices.device(self.token())
        former = team.leases.state(request.name, team.clock.time())
        lease = take(request.name, device, team.devices.person(self.token()), team.clock.time(), request.lapse_seconds)
        if former.device_id != device.id:
            team.log.wake()
        return lease

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
