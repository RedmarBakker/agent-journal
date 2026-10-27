from dataclasses import dataclass

from journal.events.rows.row_event import RowEvent


@dataclass(frozen=True, kw_only=True)
class ClientErrorLogged(RowEvent):
    """The viewer posted an error the store did not hold yet: told once to every agent, with how many are held."""

    feature_name = "client_errors"

    count: int
