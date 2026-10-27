import json
import ssl
import urllib.error
import urllib.request
from urllib.parse import quote, urlencode
from dataclasses import asdict

from journal.db.schema import Schema
from journal.sync.team_account import TeamAccount
from journal.sync.team_refusal import TeamRefusal
from journal.support.rejection import Rejection
from journal.version import VERSION
from sync_server.protocol import MIGRATION_HEADER, PROTOCOL, PROTOCOL_HEADER, UNVERSIONED, VERSION_HEADER
from sync_server.publish_request import PublishRequest
from sync_server.item import Item
from sync_server.item_list_answer import ItemListAnswer
from sync_server.item_query import ItemQuery
from sync_server.item_version import ItemVersion
from sync_server.item_versions_answer import ItemVersionsAnswer
from sync_server.library_answer import LibraryAnswer
from sync_server.login_answer import LoginAnswer
from sync_server.device import Device
from sync_server.device_list import DeviceList
from sync_server.invitation_answer import InvitationAnswer
from sync_server.password_answer import PasswordAnswer
from sync_server.people_answer import PeopleAnswer
from sync_server.login_request import LoginRequest
from journal.features.library.support.library_account import LibraryAccount
from sync_service.team_link import TeamLink

REQUEST_SECONDS = 10
FILE_SECONDS = 120
ROOT_CERTIFICATE = "/root.crt"


class LibraryLink:
    """The one way the journal reaches its team's server, a library request that finds no server answering refused with the line to connect again: each request with the device's token, this journal's protocol, version and the migration its database is at, a server on a bare address trusted through the certificate authority the join stored, and an answer from a server on an older protocol refused with the line to upgrade it; one method per library route. A network fault is raised as the OSError it is; a refusal as a TeamRefusal."""

    def __init__(self, account: TeamAccount | LibraryAccount, schema: Schema) -> None:
        self.account, self.schema = account, schema

    def bound(self, account: TeamAccount | LibraryAccount) -> "LibraryLink":
        return LibraryLink(account, self.schema)

    def summary(self, address: str) -> LibraryAnswer:
        return LibraryAnswer(**json.loads(self.reached(address, "/library", None, REQUEST_SECONDS)))

    def items(self, query: ItemQuery) -> ItemListAnswer:
        return ItemListAnswer.parsed(json.loads(self.read(f"/items?{urlencode({key: value for key, value in (('type', query.item_type), ('search', query.search)) if value is not None})}")))

    def item(self, item_type: str, name: str) -> ItemVersionsAnswer:
        return ItemVersionsAnswer.parsed(json.loads(self.read(f"/items/{quote(item_type)}/{quote(name)}")))

    def version(self, item_type: str, name: str, number: int) -> ItemVersion:
        return ItemVersion.read(json.loads(self.read(f"/items/{quote(item_type)}/{quote(name)}/{number}")))

    def publish(self, item_type: str, name: str, request: PublishRequest) -> ItemVersion:
        return ItemVersion.read(json.loads(self.reached(self.account.address(), f"/items/{quote(item_type)}/{quote(name)}", json.dumps(asdict(request)).encode(), REQUEST_SECONDS)))

    def withdraw(self, item_type: str, name: str) -> Item:
        return Item.read(json.loads(self.reached(self.account.address(), f"/items/{quote(item_type)}/{quote(name)}/withdraw", b"{}", REQUEST_SECONDS)))

    def put_file(self, item_type: str, name: str, number: int, file_name: str, data: bytes) -> ItemVersion:
        return ItemVersion.read(json.loads(self.reached(self.account.address(), f"/items/{quote(item_type)}/{quote(name)}/{number}/files/{quote(file_name)}", data, FILE_SECONDS, "PUT")))

    def file(self, item_type: str, name: str, number: int, file_name: str) -> bytes:
        return self.reached(self.account.address(), f"/items/{quote(item_type)}/{quote(name)}/{number}/files/{quote(file_name)}", None, FILE_SECONDS)

    def install(self, address: str, email: str, name: str, password: str, device_name: str) -> LoginAnswer:
        body = json.dumps({"email": email, "name": name, "password": password, "device_name": device_name}).encode()
        return LoginAnswer(**json.loads(self.reached(address, "/install", body, REQUEST_SECONDS)))

    def accept(self, address: str, code: str, email: str, name: str, password: str, device_name: str) -> LoginAnswer:
        body = json.dumps({"code": code, "email": email, "name": name, "password": password, "password_repeat": password, "device_name": device_name}).encode()
        return LoginAnswer(**json.loads(self.reached(address, "/accept", body, REQUEST_SECONDS)))

    def login(self, address: str, request: LoginRequest) -> LoginAnswer:
        return LoginAnswer(**json.loads(self.reached(address, "/login", json.dumps(request.__dict__).encode(), REQUEST_SECONDS)))

    def delete_version(self, item_type: str, name: str, number: int) -> ItemVersion:
        return ItemVersion.read(json.loads(self.posted(f"/items/{quote(item_type)}/{quote(name)}/{number}/delete", {})))

    def invite(self, email: str) -> InvitationAnswer:
        return InvitationAnswer(**json.loads(self.posted("/invite", {"email": email})))

    def devices(self) -> DeviceList:
        return DeviceList.parsed(**json.loads(self.read("/devices")))

    def revoke(self, device_id: int) -> Device:
        return Device(**json.loads(self.posted("/devices/revoke", {"device_id": device_id})))

    def people(self) -> PeopleAnswer:
        return PeopleAnswer.parsed(**json.loads(self.read("/people")))

    def remove_person(self, account_id: int) -> str:
        return str(json.loads(self.posted("/people/remove", {"account_id": account_id})).get("name", ""))

    def change_password(self, old: str, new: str) -> None:
        self.posted("/password", {"old": old, "new": new})

    def reset_password(self, account_id: int) -> str:
        return PasswordAnswer(**json.loads(self.posted("/people/password", {"account_id": account_id}))).password

    def posted(self, path: str, body: dict) -> bytes:
        return self.reached(self.account.address(), path, json.dumps(body).encode(), REQUEST_SECONDS)

    def read(self, path: str) -> bytes:
        return self.reached(self.account.address(), path, None, REQUEST_SECONDS)

    def root_certificate(self, address: str) -> str:
        unchecked = ssl.create_default_context()
        unchecked.check_hostname, unchecked.verify_mode = False, ssl.CERT_NONE
        with urllib.request.urlopen(address + ROOT_CERTIFICATE, timeout=REQUEST_SECONDS, context=unchecked) as answer:
            return answer.read().decode()

    def reached(self, address: str, path: str, body: bytes | None, seconds: float, method: str | None = None) -> bytes:
        try:
            return self.sent(address, path, body, seconds, method)
        except TeamRefusal as refused:
            raise Rejection(str(refused)) from refused
        except urllib.error.URLError as unreached:
            raise Rejection(f"the library at {address} did not answer ({unreached.reason}): check the connection, or connect again with journal library connect") from unreached

    def sent(self, address: str, path: str, body: bytes | None, seconds: float, method: str | None = None) -> bytes:
        request = urllib.request.Request(address + path, data=body, headers=self.headers(), method=method)
        try:
            with urllib.request.urlopen(request, timeout=seconds, context=self.trust()) as answer:
                self.checked(answer.headers)
                return answer.read()
        except urllib.error.HTTPError as refused:
            raise TeamRefusal(TeamLink.refusal_line(refused)) from refused


    def headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", PROTOCOL_HEADER: str(PROTOCOL), MIGRATION_HEADER: str(self.schema.version()), VERSION_HEADER: VERSION}
        if self.account.is_connected():
            headers["Authorization"] = f"Bearer {self.account.token()}"
        return headers

    @staticmethod
    def checked(headers) -> None:
        server_protocol = int(headers.get(PROTOCOL_HEADER, UNVERSIONED))
        if server_protocol < PROTOCOL:
            raise TeamRefusal(f"the team server speaks protocol {server_protocol}, older than this journal's {PROTOCOL}: upgrade the team server's image")

    def trust(self) -> ssl.SSLContext:
        root = self.account.root_path()
        return ssl.create_default_context(cafile=str(root)) if root.is_file() else ssl.create_default_context()
