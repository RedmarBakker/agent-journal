from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceAskRequest:
    """A write a journal asks of one machine by its device number, such as a word for a pool worker running there: the device, the asking environment's key, the kind, what it carries and the account it is asked for."""

    device_id: int
    environment_key: str
    kind: str
    body: dict
    account_id: int
