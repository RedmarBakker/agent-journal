import hashlib
import socket
import ssl

from journal.db.schema import Schema
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_connection import LibraryConnection
from journal.features.library.support.library_link import LibraryLink
from journal.support.rejection import Rejection
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_url import TeamUrl
from sync_server.library_answer import LibraryAnswer
from sync_server.login_answer import LoginAnswer
from sync_server.login_request import LoginRequest


class LibraryConnect:
    """Connecting this journal to its team's library by the URL a person pastes: a server with no admin yet makes this person its admin, an invitation URL makes them a member, and a bare URL logs an account in; a server that signs its own certificate is trusted through its certificate authority, checked against the fingerprint an invitation carries."""

    def __init__(self, account: LibraryAccount, schema: Schema) -> None:
        self.account, self.link = account, LibraryLink(account, schema)

    def connected(self, url: TeamUrl, email: str, name: str, password: str) -> LibraryConnection:
        if self.account.is_connected():
            raise Rejection(f"this journal is connected to the library at {self.account.address()}: journal library disconnect first")
        self.trusted(url)
        summary = self.link.summary(url.address)
        login = self.login(url, summary, email, name, password)
        connection = LibraryConnection(summary.key, url.address, login.token, login.device_id, login.account_id, login.name, login.role)
        self.account.write(connection)
        return connection

    def renewed_connection(self, email: str, password: str) -> LibraryConnection:
        connection = self.account.connection()
        login = self.account_login(TeamUrl.parse(connection.address), email, password)
        renewed = LibraryConnection(connection.key, connection.address, login.token, login.device_id, login.account_id, login.name, login.role)
        self.account.write(renewed)
        return renewed

    def login(self, url: TeamUrl, summary: LibraryAnswer, email: str, name: str, password: str) -> LoginAnswer:
        if not summary.has_admin:
            return self.link.install(url.address, email, name, password, socket.gethostname())
        if url.is_invitation():
            return self.link.accept(url.address, url.code, email, name, password, socket.gethostname())
        return self.account_login(url, email, password)

    def account_login(self, url: TeamUrl, email: str, password: str) -> LoginAnswer:
        try:
            return self.link.login(url.address, LoginRequest(email, password, socket.gethostname()))
        except TeamRefusal as refused:
            raise Rejection(f"{url.address} did not take this email and password ({refused}): connect with an invitation URL an admin shares") from refused

    def trusted(self, url: TeamUrl) -> None:
        if not url.fingerprint and not url.has_self_signed_certificate():
            return
        certificate = self.link.root_certificate(url.address)
        if url.fingerprint and hashlib.sha256(ssl.PEM_cert_to_DER_cert(certificate)).hexdigest() != url.fingerprint.lower():
            raise Rejection(f"the certificate of {url.address} does not match the fingerprint in the invitation URL: check the URL or the address")
        self.account.folder().mkdir(parents=True, exist_ok=True)
        self.account.root_path().write_text(certificate)
