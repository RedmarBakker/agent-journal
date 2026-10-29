from pathlib import Path


class OrganizationFixture:
    """A small agentic organization written into a folder for the tests: domains alpha and beta, Roles alpha/scout, alpha/builder and beta/keeper, each with the guidance file the loader needs, an empty Role folder it must ignore and one skill."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def write(self) -> "OrganizationFixture":
        (self.root / "skills" / "ids").mkdir(parents=True, exist_ok=True)
        (self.root / "skills" / "ids" / "SKILL.md").write_text("---\nname: ids\n---\nA skill.\n")
        self.domain("alpha", roles=["scout", "builder"], edges=[{"kind": "escalates_to", "to": "beta", "about": "a blocker"}])
        self.domain("beta", roles=["keeper"])
        self.role("alpha", "scout", cardinality="journal", writes=False, tools=["read_files"], model=self.model("opus", False))
        self.role("alpha", "builder", cardinality="many", writes=True, tools=["read_files", "edit_files", "run_tests"], skills=["ids"], edges=[{"kind": "delegates_to", "to": "scout", "about": "what to look up"}])
        self.role("beta", "keeper", cardinality="plan", writes=False, tools=["read_files"], approval_required=["contract_change"], model=self.model("opus", False))
        (self.root / "domains" / "alpha" / "roles" / "ghost").mkdir(parents=True, exist_ok=True)
        return self

    @staticmethod
    def model(claude: str, writes: bool) -> dict:
        return {"claude": claude, "codex": {"model": "gpt-6-luna", "effort": "max"} if writes else {"model": "gpt-6.1-sol", "effort": "xhigh"}}

    def domain(self, domain: str, **changes) -> Path:
        folder = self.root / "domains" / domain
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "AGENTS.md").write_text(f"Guidance of {domain}.\n")
        values = {"id": domain, "title": domain.title(), "icon": "🧪", "description": f"The {domain} domain.", "outcome": f"{domain} is done", "responsible": [f"{domain} work"], "not_responsible": ["other domains"], "roles": [], "skills": [], "model": self.model("sonnet", False), **changes}
        (folder / "domain.toml").write_text(self.toml(values))
        return folder

    def role(self, domain: str, role: str, **changes) -> Path:
        folder = self.root / "domains" / domain / "roles" / role
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "AGENTS.md").write_text(f"Guidance of {role}.\n")
        writes = changes.get("writes", False)
        values = {"id": role, "title": role.title(), "domain": domain, "description": f"The {role}.", "cardinality": "many", "writes": False, "responsible": ["the job"], "not_responsible": ["the rest"], "inputs": ["a task"], "outputs": ["a report"],
                  "skills": [], "tools": ["read_files"], "approval_required": [], "model": self.model("sonnet", writes), **changes}
        (folder / "role.toml").write_text(self.toml(values))
        return folder

    @classmethod
    def toml(cls, values: dict) -> str:
        scalars = [f"{key} = {cls.value(value)}" for key, value in values.items() if not isinstance(value, dict) and not cls.is_tables(value)]
        tables = [cls.table(key, value) for key, value in values.items() if isinstance(value, dict)]
        arrays = [cls.table(f"[[{key}]]", table) for key, value in values.items() if cls.is_tables(value) for table in value]
        return "\n".join(scalars) + "\n" + "\n".join(tables + arrays)

    @staticmethod
    def is_tables(value: object) -> bool:
        return isinstance(value, list) and bool(value) and isinstance(value[0], dict)

    @classmethod
    def table(cls, name: str, values: dict) -> str:
        header = name if name.startswith("[") else f"[{name}]"
        plain = [f"{key} = {cls.value(value)}" for key, value in values.items() if not isinstance(value, dict)]
        nested = [cls.table(f"{name.strip('[]')}.{key}", value) for key, value in values.items() if isinstance(value, dict)]
        return "\n".join([header, *plain]) + "\n" + "\n".join(nested)

    @classmethod
    def value(cls, value: object) -> str:
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, list):
            return "[" + ", ".join(cls.value(item) for item in value) + "]"
        return '"' + str(value).replace('"', '\\"') + '"'
