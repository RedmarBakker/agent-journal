from sync_server.account import ADMIN, Account
from sync_server.db.account_rows import AccountRows
from sync_server.password import Password
from sync_server.password_strength import PasswordStrength
from sync_server.refusal import Refusal


class Accounts:
    """The team's people, each with a password kept only as a hash."""

    def __init__(self, rows: AccountRows) -> None:
        self.rows = rows

    def create(self, email: str, name: str, password: str, role: str, created_at: float) -> Account:
        PasswordStrength.check(password, email)
        if self.rows.with_email(email.lower()):
            raise Refusal(f"{email} already has an account")
        return self.find(self.rows.insert(email.lower(), name, role, Password.hashed(password), created_at))

    def first_admin(self, email: str, name: str, password: str, created_at: float) -> Account:
        if not self.is_empty():
            raise Refusal("this team server has its admin already: join it with the invitation URL an admin shares from the Team tab")
        return self.create(email, name, password, ADMIN, created_at)

    def password_changed(self, account: Account, old: str, new: str) -> Account:
        self.verified(account.email, old)
        return self.password_set(account, new)

    def password_set(self, account: Account, password: str) -> Account:
        PasswordStrength.check(password, account.email)
        self.rows.set_password(account.id, Password.hashed(password))
        return account

    def find(self, id: int) -> Account:
        row = self.rows.numbered(id)
        if row is None:
            raise Refusal(f"no account {id}")
        return Account(row["id"], row["email"], row["name"], row["role"])

    def verified(self, email: str, password: str) -> Account:
        row = self.rows.with_email(email.lower())
        if row is None or row["removed_at"] or not Password.matches(password, row["password_hash"]):
            raise Refusal("the email or the password is wrong")
        return self.find(row["id"])

    def active(self) -> list[Account]:
        return [Account(row["id"], row["email"], row["name"], row["role"]) for row in self.rows.active()]

    def is_empty(self) -> bool:
        return self.rows.count() == 0

    def remove(self, id: int, removed_at: float) -> Account:
        account = self.find(id)
        self.rows.remove(id, removed_at)
        return account

    def is_removed(self, id: int) -> bool:
        row = self.rows.numbered(id)
        return row is None or bool(row["removed_at"])

    def has_email(self, email: str) -> bool:
        return self.rows.with_email(email.lower()) is not None
