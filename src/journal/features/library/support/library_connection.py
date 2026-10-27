from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class LibraryConnection:
    """What connecting to a library keeps: the library's key and address, this device's token and number, and the person's account number, name and role there."""

    key: str
    address: str
    token: str
    device_id: int
    account_id: int
    name: str
    role: str

    @classmethod
    def read(cls, fields: dict) -> "LibraryConnection":
        return cls(**{name: fields[name] for name in cls.__dataclass_fields__})

    def fields(self) -> dict:
        return asdict(self)
