import json

from journal.db.schema import Schema
from journal.sync.team_account import TeamAccount
from journal.features.library.support.library_link import LibraryLink, REQUEST_SECONDS
from sync_server.backup_answer import BackupAnswer
from sync_server.device import Device
from sync_server.device_list import DeviceList
from sync_server.invitation_answer import InvitationAnswer
from sync_server.login_answer import LoginAnswer
from sync_server.login_request import LoginRequest
from sync_server.people_answer import PeopleAnswer
from sync_server.password_answer import PasswordAnswer
from sync_server.signin_answer import SigninAnswer
from sync_server.team_summary import TeamSummary

COPY_SECONDS = 120


class TeamServerLink:
    """The one way the journal reaches its team server, each request with the device's token: the backup, the joining and the admin requests, sent through the LibraryLink, which holds the transport."""

    def __init__(self, account: TeamAccount, schema: Schema) -> None:
        self.account, self.schema = account, schema
        self.transport = LibraryLink(account, schema)

    def bound(self, account: TeamAccount) -> "TeamServerLink":
        return TeamServerLink(account, self.schema)

    def backup(self) -> BackupAnswer:
        return BackupAnswer(**json.loads(self.sent(self.account.address(), "/backups", b"{}", COPY_SECONDS)))

    def invite(self, email: str) -> InvitationAnswer:
        return self.transport.invite(email)

    def devices(self) -> DeviceList:
        return self.transport.devices()

    def pin_version(self, version: str) -> TeamSummary:
        return TeamSummary(**json.loads(self.posted("/team/version", {"version": version})))

    def leave_team(self) -> int:
        return int(json.loads(self.posted("/people/leave", {})).get("withdrawn", 0))

    def remove_person(self, account_id: int) -> str:
        return self.transport.remove_person(account_id)

    def allow_versions(self, rule: str) -> TeamSummary:
        return TeamSummary(**json.loads(self.posted("/team/versions", {"versions": rule})))

    def people(self) -> PeopleAnswer:
        return self.transport.people()

    def revoke(self, device_id: int) -> Device:
        return self.transport.revoke(device_id)

    def summary(self, address: str) -> TeamSummary:
        return TeamSummary(**json.loads(self.sent(address, "/team", None, REQUEST_SECONDS)))

    def accept(self, address: str, code: str, email: str, name: str, password: str, device_name: str) -> LoginAnswer:
        return self.transport.accept(address, code, email, name, password, device_name)

    def install(self, address: str, email: str, name: str, password: str, device_name: str) -> LoginAnswer:
        return self.transport.install(address, email, name, password, device_name)

    def change_password(self, old: str, new: str) -> None:
        self.transport.change_password(old, new)

    def reset_password(self, account_id: int) -> str:
        return self.transport.reset_password(account_id)

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

    def sent(self, address: str, path: str, body: bytes | None, seconds: float) -> bytes:
        return self.transport.sent(address, path, body, seconds)

    def headers(self) -> dict[str, str]:
        return self.transport.headers()
