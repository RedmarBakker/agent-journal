from dataclasses import dataclass
import hashlib
import json
import math


@dataclass(frozen=True)
class Design:
    name: str
    settings: tuple[tuple[str, str | int | float | bool | None], ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("a design needs a name")
        names = tuple(name for name, _ in self.settings)
        if any(not name.strip() for name in names) or len(set(names)) != len(names):
            raise ValueError("design setting names must be non-empty and unique")
        if any(not isinstance(value, (str, int, float, bool, type(None))) for _, value in self.settings):
            raise ValueError("design settings must be JSON scalar values")
        if any(isinstance(value, float) and not math.isfinite(value) for _, value in self.settings):
            raise ValueError("design setting values must be finite")
        if any(any(word in name.lower() for word in ("secret", "token", "credential", "password", "api_key", "private_key")) for name in names):
            raise ValueError("design settings cannot contain credentials")

    @classmethod
    def from_mapping(cls, name: str, settings: dict[str, object]) -> "Design":
        values = tuple(sorted(settings.items()))
        if any(not isinstance(value, (str, int, float, bool, type(None))) for _, value in values):
            raise ValueError("design settings must be JSON scalar values")
        return cls(name, values)

    @property
    def settings_digest(self) -> str:
        encoded = json.dumps(dict(self.settings), sort_keys=True, separators=(",", ":"), allow_nan=False)
        return hashlib.sha256(encoded.encode()).hexdigest()

    @property
    def digest(self) -> str:
        encoded = json.dumps({"name": self.name, "settings_digest": self.settings_digest}, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(encoded.encode()).hexdigest()

    def manifest(self) -> dict[str, object]:
        return {"name": self.name, "settings": dict(self.settings), "digest": self.digest, "settings_digest": self.settings_digest}
