from dataclasses import dataclass


@dataclass(frozen=True)
class RoleModels:
    """The model a Role runs on under each provider, and the reasoning effort it is given on Codex."""

    claude: str
    codex: str
    effort: str

    def for_provider(self, name: str) -> str:
        return self.claude if name == "claude" else self.codex
