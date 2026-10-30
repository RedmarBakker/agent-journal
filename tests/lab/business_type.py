import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType


def freeze(value: object) -> object:
    if isinstance(value, dict):
        return MappingProxyType({key: freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return tuple(freeze(item) for item in value)
    return value


@dataclass(frozen=True)
class BusinessType:
    """A business type's organization spec, with its domains and Roles read from TOML."""

    id: str
    title: str
    domains: tuple[Mapping[str, object], ...]
    roles: tuple[Mapping[str, object], ...]

    @classmethod
    def read(cls, path: Path) -> "BusinessType":
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        return cls(data["id"], data["title"], tuple(freeze(domain) for domain in data["domains"]), tuple(freeze(role) for role in data["roles"]))
