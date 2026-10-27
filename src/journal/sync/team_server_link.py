from dataclasses import asdict
import json

from journal.db.schema import Schema
from journal.sync.team_account import TeamAccount
from journal.features.library.support.library_link import LibraryLink, REQUEST_SECONDS
from sync_server.backup_answer import BackupAnswer
from sync_server.agent_view_list import AgentViewList
from sync_server.blocks_answer import BlocksAnswer
from sync_server.copied_row import CopiedRow
from sync_server.device import Device
from sync_server.device_list import DeviceList
from sync_server.file_place import FilePlace
from sync_server.full_copy import FullCopy
from sync_server.invitation_answer import InvitationAnswer
from sync_server.login_answer import LoginAnswer
from sync_server.login_request import LoginRequest
from sync_server.people_answer import PeopleAnswer
from sync_server.pull_query import PullQuery
from sync_server.pool_ask_request import PoolAskRequest
from sync_server.device_ask_request import DeviceAskRequest
from sync_server.password_answer import PasswordAnswer
from sync_server.signin_answer import SigninAnswer
from sync_server.team_summary import TeamSummary
from sync_server.upload_answer import UploadAnswer
from sync_server.lease import Lease

COPY_SECONDS = 120


class TeamServerLink:
    """The one way the journal reaches its team server, each request with the device's token, and the headers, push body and pull path the sync service sends it with: a push and a pull each name the environments this journal hosts so the writes asked of it come back with them; a write asked of another environment's host and the word that one asked of this journal is made, a request for blocks of row numbers, the full copy, and the joining and admin requests. Its requests go through the LibraryLink, which holds the transport, until the row sync is removed."""

    def __init__(self, account: TeamAccount, schema: Schema) -> None:
        self.account, self.schema = account, schema
        self.transport = LibraryLink(account, schema)

    def bound(self, account: TeamAccount) -> "TeamServerLink":
        return TeamServerLink(account, self.schema)

    @staticmethod
    def push_body(changes: list[dict], clock_offset: float, query: PullQuery) -> dict:
        # a team server from before the pool refuses a push with fields it does not know
        pool_fields = {"pool_slots": query.pool.slots, "pool_free": query.pool.free, "version": query.version} if query.pool.slots else {}
        return {"changes": changes, "clock_offset": clock_offset, "sequence": query.sequence, "environment_keys": list(query.environment_keys), **pool_fields}

    @staticmethod
    def pull_path(query: PullQuery) -> str:
        return f"/pull?after={query.sequence}&wait={query.wait_seconds}&keys={','.join(query.environment_keys)}&slots={query.pool.slots}&free={query.pool.free}&version={query.version}"

    def send_agent_views(self, views: dict[str, list[dict]]) -> None:
        self.posted("/agent-views", {"views": views})

    def agent_views(self, keys: list[str]) -> dict[str, list[dict]]:
        return AgentViewList(**json.loads(self.sent(self.account.address(), f"/agent-views?keys={','.join(keys)}", None, REQUEST_SECONDS))).views

    def ask_host(self, environment_key: str, type_name: str, body: dict, account_id: int) -> None:
        self.posted("/host-requests", {"environment_key": environment_key, "kind": type_name, "body": body, "account_id": account_id})

    def ask_pool(self, request: PoolAskRequest) -> int:
        answer = json.loads(self.posted("/pool-requests", asdict(request)))
        return int(answer["requests"][0]["id"])

    def ask_device(self, request: DeviceAskRequest) -> None:
        self.posted("/device-requests", asdict(request))

    def claim_request(self, id: int) -> None:
        self.posted("/host-requests/claim", {"id": id})

    def decline_request(self, id: int, reason: str) -> None:
        self.posted("/host-requests/decline", {"id": id, "reason": reason})

    def finish_host_request(self, id: int) -> None:
        self.posted("/host-requests/done", {"id": id})

    def fetch_blocks(self, tables: list[str]) -> BlocksAnswer:
        return BlocksAnswer.parsed(**json.loads(self.posted("/blocks", {"tables": tables})))

    def full_copy(self) -> FullCopy:
        return FullCopy.parsed(**json.loads(self.sent(self.account.address(), "/copy", None, COPY_SECONDS)))

    def upload(self, rows: list[CopiedRow], highest: dict, repository: str, version: str, team_name: str) -> UploadAnswer:
        body = json.dumps({"rows": [row.__dict__ for row in rows], "highest": highest, "repository": repository, "version": version, "migration": self.schema.version(), "team_name": team_name}).encode()
        return UploadAnswer(**json.loads(self.sent(self.account.address(), "/upload", body, COPY_SECONDS)))

    def upgrade(self, rows: list[CopiedRow], highest: dict, base_sequence: int) -> UploadAnswer:
        body = json.dumps({"rows": [row.__dict__ for row in rows], "highest": highest, "migration": self.schema.version(), "base_sequence": base_sequence}).encode()
        return UploadAnswer(**json.loads(self.sent(self.account.address(), "/upgrade", body, COPY_SECONDS)))

    def backup(self) -> BackupAnswer:
        return BackupAnswer(**json.loads(self.sent(self.account.address(), "/backups", b"{}", COPY_SECONDS)))

    def invite(self, email: str) -> InvitationAnswer:
        return InvitationAnswer(**json.loads(self.posted("/invite", {"email": email})))

    def devices(self) -> DeviceList:
        return DeviceList.parsed(**json.loads(self.sent(self.account.address(), "/devices", None, REQUEST_SECONDS)))

    def pin_version(self, version: str) -> TeamSummary:
        return TeamSummary(**json.loads(self.posted("/team/version", {"version": version})))

    def leave_team(self) -> int:
        return int(json.loads(self.posted("/people/leave", {})).get("withdrawn", 0))

    def remove_person(self, account_id: int) -> str:
        return str(json.loads(self.posted("/people/remove", {"account_id": account_id})).get("name", ""))

    def move_to_hub(self) -> TeamSummary:
        return TeamSummary(**json.loads(self.posted("/team/hub", {})))

    def tie_repository(self, tied: bool) -> TeamSummary:
        return TeamSummary(**json.loads(self.posted("/team/repository", {"tied": tied})))

    def allow_versions(self, rule: str) -> TeamSummary:
        return TeamSummary(**json.loads(self.posted("/team/versions", {"versions": rule})))

    def people(self) -> PeopleAnswer:
        return PeopleAnswer.parsed(**json.loads(self.sent(self.account.address(), "/people", None, REQUEST_SECONDS)))

    def revoke(self, device_id: int) -> Device:
        return Device(**json.loads(self.posted("/devices/revoke", {"device_id": device_id})))

    def summary(self, address: str) -> TeamSummary:
        return TeamSummary(**json.loads(self.sent(address, "/team", None, REQUEST_SECONDS)))

    def accept(self, address: str, code: str, email: str, name: str, password: str, device_name: str) -> LoginAnswer:
        return self.transport.accept(address, code, email, name, password, device_name)

    def install(self, address: str, email: str, name: str, password: str, device_name: str) -> LoginAnswer:
        return self.transport.install(address, email, name, password, device_name)

    def change_password(self, old: str, new: str) -> None:
        self.posted("/password", {"old": old, "new": new})

    def reset_password(self, account_id: int) -> str:
        return PasswordAnswer(**json.loads(self.posted("/people/password", {"account_id": account_id}))).password

    def signin_code(self) -> str:
        return SigninAnswer(**json.loads(self.posted("/signin-links", {}))).code

    def signin_account(self, code: str) -> SigninAnswer:
        return SigninAnswer(**json.loads(self.posted("/signin-links/redeem", {"code": code})))

    def login(self, address: str, request: LoginRequest) -> LoginAnswer:
        return self.transport.login(address, request)

    def root_certificate(self, address: str) -> str:
        return self.transport.root_certificate(address)

    def posted(self, path: str, body: dict) -> bytes:
        return self.sent(self.account.address(), path, json.dumps(body).encode(), REQUEST_SECONDS)

    def acquire_lease(self, name: str) -> Lease:
        return Lease(**json.loads(self.posted("/leases/take", {"name": name})))

    def acquire_free_lease(self, name: str, lapse_seconds: float) -> Lease:
        return Lease(**json.loads(self.posted("/leases/take-free", {"name": name, "lapse_seconds": lapse_seconds})))

    def takeover_lease(self, name: str, lapse_seconds: float) -> Lease:
        return Lease(**json.loads(self.posted("/leases/take", {"name": name, "lapse_seconds": lapse_seconds})))

    def release_lease(self, name: str) -> Lease:
        return Lease(**json.loads(self.posted("/leases/release", {"name": name})))

    def lease_state(self, name: str) -> Lease:
        return Lease(**json.loads(self.sent(self.account.address(), f"/leases?name={name}", None, REQUEST_SECONDS)))

    def upload_file(self, place: FilePlace, data: bytes) -> None:
        self.sent(self.account.address(), f"/files/{place.address()}", data, COPY_SECONDS)

    def fetch_file(self, place: FilePlace) -> bytes:
        return self.sent(self.account.address(), f"/files/{place.address()}", None, COPY_SECONDS)

    def sent(self, address: str, path: str, body: bytes | None, seconds: float) -> bytes:
        return self.transport.sent(address, path, body, seconds)

    def headers(self) -> dict[str, str]:
        return self.transport.headers()
