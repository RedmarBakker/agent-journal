import json
from collections.abc import Mapping
from pathlib import Path

from tests.lab.business_type import BusinessType


def is_tables(value: object) -> bool:
    return isinstance(value, (list, tuple)) and bool(value) and all(isinstance(item, Mapping) for item in value)


def toml_value(value: object) -> str:
    if isinstance(value, bool):
        return str(value).lower()
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        return f"[{', '.join(toml_value(item) for item in value)}]"
    raise TypeError(f"Cannot write {type(value).__name__} as a TOML value")


def toml_table(path: str, values: Mapping[str, object]) -> list[str]:
    header = f"[{path}]" if path else ""
    return toml_block(header, path, values)


def toml_array_table(path: str, values: Mapping[str, object]) -> list[str]:
    return toml_block(f"[[{path}]]", path, values)


def toml_block(header: str, path: str, values: Mapping[str, object]) -> list[str]:
    lines = [header] if header else []
    lines.extend(f"{key} = {toml_value(value)}" for key, value in values.items() if not isinstance(value, Mapping) and not is_tables(value))
    for key, value in values.items():
        child = f"{path}.{key}" if path else key
        if isinstance(value, Mapping):
            lines.extend(["", *toml_table(child, value)])
        elif is_tables(value):
            for table in value:
                lines.extend(["", *toml_array_table(child, table)])
    return lines


def listed(values: tuple[str, ...]) -> str:
    return "\n".join(f"- {value}" for value in values) or "No items listed."


class OrganizationBuilder:
    """Write business type contracts and guidance files into an organization folder."""

    def __init__(self) -> None:
        self.templates = Path(__file__).with_name("organization_template")

    def build(self, business_type: BusinessType, root: Path) -> Path:
        for domain in business_type.domains:
            self.domain(business_type, domain, root)
        return root

    def domain(self, business_type: BusinessType, domain: Mapping[str, object], root: Path) -> None:
        folder = root / "domains" / str(domain["id"])
        folder.mkdir(parents=True, exist_ok=True)
        roles = tuple(role for role in business_type.roles if role["domain"] == domain["id"])
        contract = {**domain, "roles": tuple(str(role["id"]) for role in roles)}
        (folder / "domain.toml").write_text("\n".join(toml_table("", contract)).strip() + "\n", encoding="utf-8")
        (folder / "AGENTS.md").write_text(self.domain_guidance(business_type, domain), encoding="utf-8")
        for role in roles:
            self.role(business_type, domain, role, folder)

    def role(self, business_type: BusinessType, domain: Mapping[str, object], role: Mapping[str, object], domain_folder: Path) -> None:
        folder = domain_folder / "roles" / str(role["id"])
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "role.toml").write_text("\n".join(toml_table("", role)).strip() + "\n", encoding="utf-8")
        (folder / "AGENTS.md").write_text(self.role_guidance(business_type, domain, role), encoding="utf-8")

    def domain_guidance(self, business_type: BusinessType, domain: Mapping[str, object]) -> str:
        return self.template("domain.md").format(
            company=business_type.title,
            title=domain["title"],
            outcome=domain["outcome"],
            responsible=listed(domain["responsible"]),
            not_responsible=listed(domain["not_responsible"]),
        )

    def role_guidance(self, business_type: BusinessType, domain: Mapping[str, object], role: Mapping[str, object]) -> str:
        return self.template("role.md").format(
            company=business_type.title,
            domain=domain["title"],
            title=role["title"],
            description=role["description"],
            responsible=listed(role["responsible"]),
            not_responsible=listed(role["not_responsible"]),
            inputs=listed(role["inputs"]),
            outputs=listed(role["outputs"]),
        )

    def template(self, name: str) -> str:
        return (self.templates / name).read_text(encoding="utf-8")
