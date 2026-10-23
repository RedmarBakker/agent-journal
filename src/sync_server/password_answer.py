import secrets
import string
from dataclasses import dataclass

LETTERS = string.ascii_letters + string.digits + "-_!"
PASSWORD_CHARACTERS = 22


@dataclass(frozen=True)
class PasswordAnswer:
    """A password an admin's reset made for a member, to pass on to them."""

    password: str

    @classmethod
    def generated(cls) -> "PasswordAnswer":
        return cls("".join(secrets.choice(LETTERS) for _ in range(PASSWORD_CHARACTERS)))
