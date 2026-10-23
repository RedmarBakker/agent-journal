from dataclasses import dataclass


@dataclass(frozen=True)
class SigninAnswer:
    """A sign-in link issued, by its code, or taken up, by the account it signs in."""

    code: str = ""
    account_id: int = 0
    name: str = ""
