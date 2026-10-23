from dataclasses import dataclass


@dataclass(frozen=True)
class PoolAskRequest:
    """A job a journal asks of the team's pool: the asking environment's key, the kind of job, what it carries, the account it is asked for, and the journal version a machine must run to take it."""

    environment_key: str
    kind: str
    body: dict
    account_id: int
    version: str
