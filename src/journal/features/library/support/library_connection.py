from dataclasses import asdict, dataclass

from journal.sync.team_url import TeamUrl


@dataclass(frozen=True)
class LibraryConnection:
    """What connecting to a team keeps: the team's key, plain name and address, this device's token and number, and the person's account number, name and role there; a file from before teams had names is named by its server's host."""

    key: str
    address: str
    token: str
    device_id: int
    account_id: int
    name: str
    role: str
    team: str

    @classmethod
    def read(cls, fields: dict) -> "LibraryConnection":
        named = {"team": TeamUrl(fields["address"]).host(), **fields}
        return cls(**{name: named[name] for name in cls.__dataclass_fields__})

    def fields(self) -> dict:
        return asdict(self)
