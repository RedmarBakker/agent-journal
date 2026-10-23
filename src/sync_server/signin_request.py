from dataclasses import dataclass


@dataclass(frozen=True)
class SigninRequest:
    """The hosted journal taking up a one-time sign-in link, by its code."""

    code: str
