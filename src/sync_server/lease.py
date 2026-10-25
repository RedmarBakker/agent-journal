from dataclasses import dataclass


@dataclass(frozen=True)
class Lease:
    """Who holds a named lease: its name, the device and the person holding it, when it was last renewed, whether it has lapsed for want of renewal, and the device's name; an empty holder when nobody holds it."""

    name: str
    device_id: int = 0
    holder: str = ""
    renewed_at: float = 0.0
    is_lapsed: bool = False
    device_name: str = ""

    def excludes(self, device_id: int) -> bool:
        return self.has_other_holder(device_id) and not self.is_lapsed

    def has_other_holder(self, device_id: int) -> bool:
        return bool(self.holder) and self.device_id != device_id

    def refusal(self, request_at: float) -> str:
        line = f"{self.name} is held by {self.holder} on {self.device_name}, last seen {request_at - self.renewed_at:.0f} seconds ago"
        return f"{line}; it has lapsed, so only a takeover has it" if self.is_lapsed else line
