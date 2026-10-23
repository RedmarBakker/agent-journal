from dataclasses import dataclass


@dataclass(frozen=True)
class HostAskRequest:
    """A write a journal asks of an environment's host: the environment's key, the kind of write, what it carries, and the account it is asked for, which only the hosted journal may name for another person."""

    environment_key: str
    kind: str
    body: dict
    account_id: int
