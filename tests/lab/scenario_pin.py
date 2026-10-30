from dataclasses import dataclass
import re


@dataclass(frozen=True)
class ScenarioPin:
    name: str
    business_type: str
    version: str
    checksum: str
    simulated_minutes: int

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.business_type.strip() or not self.version.strip():
            raise ValueError("a scenario pin needs a name, business type and version")
        if not re.fullmatch(r"[0-9a-f]{64}", self.checksum):
            raise ValueError("a scenario pin needs its full SHA-256 checksum")
        if not isinstance(self.simulated_minutes, int) or isinstance(self.simulated_minutes, bool) or self.simulated_minutes <= 0:
            raise ValueError("scenario duration must be a positive simulated-minute count")
