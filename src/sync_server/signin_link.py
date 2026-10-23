from dataclasses import dataclass


@dataclass(frozen=True)
class SigninLink:
    """A one-time sign-in link waiting to be taken up: the account it signs in and when it expires."""

    account_id: int
    expires_at: float
