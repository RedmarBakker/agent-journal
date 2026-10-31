import socket

from journal.db.schema import Schema
from journal.features.library.support.library_account import LibraryAccount
from journal.features.library.support.library_accounts import LibraryAccounts
from journal.features.library.support.library_connection import LibraryConnection
from journal.features.library.support.library_link import LibraryLink
from journal.support.rejection import Rejection
from journal.sync.certificate_fingerprint import CertificateFingerprint
from journal.sync.team_refusal import TeamRefusal
from journal.sync.team_url import TeamUrl
from sync_server.library_answer import LibraryAnswer
from sync_server.login_answer import LoginAnswer
from sync_server.login_request import LoginRequest


class LibraryConnect:
    """Connecting this journal to one more team by the URL a person pastes, beside the teams it has: a server with no admin yet makes this person its admin, an invitation URL makes them a member, and a bare URL logs an account in; until the server names its key the account is kept by its address, so no other team's token or certificate goes to it; a server that signs its own certificate is trusted through its certificate authority, checked against the fingerprint an invitation carries; a team already connected, or a name another team has, is refused."""

    def __init__(self, account: LibraryAccount, accounts: LibraryAccounts, schema: Schema) -> None:
        self.account, self.accounts, self.link = account, accounts, LibraryLink(account, schema)

    def connected(self, url: TeamUrl, email: str, name: str, password: str, team: str) -> LibraryConnection:
        team_name = team or url.host()
        if team_name in self.accounts.names():
            raise Rejection(f"a team called {team_name} is connected here already: give this one another name with --team")
        self.account.move_shared_root()
        joining = self.accounts.keyed(url.file_name())
        link = self.link.bound(joining)
        self.trusted(url, joining, link)
        summary = link.summary(url.address)
        joined = self.accounts.keyed(summary.key)
        if joined.is_connected():
            raise Rejection(f"this journal is connected to {url.address} already, as the team {joined.connection().team}")
        login = self.login(url, summary, email, name, password, link)
        connection = LibraryConnection(summary.key, url.address, login.token, login.device_id, login.account_id, login.name, login.role, team_name)
        joined.write(connection)
        joining.move_root(joined)
        return connection

    def renewed_connection(self, account: LibraryAccount, email: str, password: str) -> LibraryConnection:
        connection = account.connection()
        login = self.account_login(TeamUrl.parse(connection.address), email, password, self.link.bound(account))
        renewed = LibraryConnection(connection.key, connection.address, login.token, login.device_id, login.account_id, login.name, login.role, connection.team)
        account.write(renewed)
        return renewed

    def login(self, url: TeamUrl, summary: LibraryAnswer, email: str, name: str, password: str, link: LibraryLink) -> LoginAnswer:
        if not summary.has_admin:
            if not url.setup_code:
                raise Rejection(f"{url.address} is new: claim it with journal team connect {url.address}/setup?code=<code> from its log")
            return link.install(url.address, url.setup_code, email, name, password, socket.gethostname())
        if url.is_invitation():
            return link.accept(url.address, url.code, email, name, password, socket.gethostname())
        return self.account_login(url, email, password, link)

    @staticmethod
    def account_login(url: TeamUrl, email: str, password: str, link: LibraryLink) -> LoginAnswer:
        try:
            return link.login(url.address, LoginRequest(email, password, socket.gethostname()))
        except TeamRefusal as refused:
            raise Rejection(f"{url.address} did not take this email and password ({refused}): connect with an invitation URL an admin shares") from refused

    @staticmethod
    def trusted(url: TeamUrl, joining: LibraryAccount, link: LibraryLink) -> None:
        if not url.fingerprint and not url.has_self_signed_certificate():
            return
        certificate = link.root_certificate(url.address)
        if url.fingerprint and not CertificateFingerprint.matches(certificate, url.fingerprint):
            raise Rejection(f"the certificate of {url.address} does not match the fingerprint in the invitation URL: check the URL or the address")
        joining.folder().mkdir(parents=True, exist_ok=True)
        joining.team_root_path().write_text(certificate)
