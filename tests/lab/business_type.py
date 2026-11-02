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
    organization_domain_map: Mapping[str, str]

    @classmethod
    def read(cls, path: Path) -> "BusinessType":
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        domains = tuple(freeze(domain) for domain in data["domains"])
        mapping = data.get("organization_domain_map", {})
        domain_ids = {domain["id"] for domain in data["domains"]}
        if not isinstance(mapping, dict) or any(source not in domain_ids or not isinstance(target, str) or not target.strip()
                                                for source, target in mapping.items()):
            raise ValueError("organization_domain_map must map business type domains to named organization domains")
        return cls(data["id"], data["title"], domains, tuple(freeze(role) for role in data["roles"]),
                   MappingProxyType(dict(mapping)))
