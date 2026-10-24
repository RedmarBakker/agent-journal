import html
from urllib.parse import parse_qsl

from sync_server.accounts import Accounts
from sync_server.refusal import Refusal
from sync_server.server_clock import ServerClock
from sync_server.setup_code import SetupCode

FORBIDDEN = "Forbidden: open the team's journal from your own journal, Settings, Team."
STYLE = (
    "body{font:15px/1.5 system-ui,sans-serif;background:#141518;color:#e6e6e9;display:flex;justify-content:center;padding:48px 16px}"
    "main{max-width:420px;width:100%}h1{font-size:20px;margin:0 0 8px}p{color:#a7a9b2;margin:0 0 20px}label{display:block;font-size:13px;margin:14px 0 4px}"
    "input{width:100%;box-sizing:border-box;padding:9px 10px;border-radius:8px;border:1px solid #33353d;background:#1c1d22;color:inherit;font:inherit}"
    "button{margin-top:20px;padding:10px 16px;border-radius:8px;border:0;background:#7c6cf2;color:white;font:inherit;cursor:pointer}"
    ".error{color:#ff8a8a}code{background:#1c1d22;padding:2px 6px;border-radius:6px}"
)


class SetupPage:
    """The page a browser sees at a team server's address while it has no admin: a form asking for the setup code its installer printed, a name, an email and a password, which claims the server and makes the admin, then says how to connect a journal. Once the admin exists the page is gone and the address forbidden, as before."""

    def __init__(self, accounts: Accounts, setup: SetupCode, clock: ServerClock) -> None:
        self.accounts, self.setup, self.clock = accounts, setup, clock

    def shown(self, address: str) -> tuple[int, str]:
        return (200, self.form("", {})) if self.accounts.is_empty() else (403, FORBIDDEN)

    def posted(self, body: bytes, address: str) -> tuple[int, str]:
        if not self.accounts.is_empty():
            return 403, FORBIDDEN
        fields = dict(parse_qsl(body.decode()))
        if not self.setup.matches(fields.get("code", "")):
            return 200, self.form("That setup code is not this server's: give the one its installer printed.", fields)
        try:
            account = self.accounts.first_admin(fields.get("email", ""), fields.get("name", ""), fields.get("password", ""), self.clock.time())
        except Refusal as refusal:
            return 200, self.form(str(refusal), fields)
        self.setup.discard()
        return 200, self.claimed(account.name, account.email, address)

    def form(self, error: str, fields: dict) -> str:
        value = lambda name: html.escape(fields.get(name, ""), quote=True)
        notice = f'<p class="error">{html.escape(error)}</p>' if error else ""
        return self.page(
            "Claim this team server",
            '<p>Give the setup code its installer printed. Whoever claims it becomes the team\'s admin.</p>'
            f'{notice}<form method="post">'
            f'<label for="code">Setup code</label><input id="code" name="code" value="{value("code")}" placeholder="ABCD-EFGH" autocomplete="off" required>'
            f'<label for="name">Your name</label><input id="name" name="name" value="{value("name")}" required>'
            f'<label for="email">Email</label><input id="email" name="email" type="email" value="{value("email")}" required>'
            '<label for="password">Password</label><input id="password" name="password" type="password" autocomplete="new-password" required>'
            '<button type="submit">Claim it</button></form>',
        )

    def claimed(self, name: str, email: str, address: str) -> str:
        return self.page(
            f"The team server is yours, {html.escape(name)}",
            "<p>Now connect your journal: in its Settings, Team tab, give this address, your email and your password; or run</p>"
            f"<p><code>journal team join {html.escape(address)} --email {html.escape(email)}</code></p>"
            "<p>Invite colleagues from the Team tab afterwards.</p>",
        )

    @staticmethod
    def page(title: str, body: str) -> str:
        return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title><style>{STYLE}</style></head><body><main><h1>{title}</h1>{body}</main></body></html>'
