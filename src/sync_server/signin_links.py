import secrets
import threading

from sync_server.account import Account
from sync_server.accounts import Accounts
from sync_server.devices import Devices
from sync_server.refusal import Refusal
from sync_server.signin_link import SigninLink

VALID_SECONDS = 120


class SigninLinks:
    """One-time links a member's own journal asks for, with its device token, to open the team's hosted journal signed in as that member: each works once, within two minutes, and only the hosted journal's relay account may take one up. They are kept in memory, so a server that restarts forgets the ones not taken up yet."""

    def __init__(self, devices: Devices, accounts: Accounts) -> None:
        self.devices, self.accounts = devices, accounts
        self.waiting: dict[str, SigninLink] = {}
        self.guard = threading.Lock()

    def issue(self, token: str, issued_at: float) -> str:
        person = self.devices.person(token)
        code = secrets.token_urlsafe(24)
        with self.guard:
            self.waiting[code] = SigninLink(person.id, issued_at + VALID_SECONDS)
        return code

    def redeemed(self, token: str, code: str, redeemed_at: float) -> Account:
        if not self.devices.person(token).is_relay():
            raise Refusal("only the team's hosted journal takes up a sign-in link")
        with self.guard:
            link = self.waiting.pop(code, None)
        if link is None or link.expires_at < redeemed_at:
            raise Refusal("this sign-in link was used already or has expired: open the shared journal again from your own journal's Team tab")
        return self.accounts.find(link.account_id)
