from dataclasses import dataclass, field
from typing import ClassVar

from journal.models.model import Model
from journal.support.environment_key import EnvironmentKey


@dataclass(frozen=True)
class Environment(Model):
    """A place an agent works. Its key, made at random when it is made, never changes and is how this machine and the team server match it; its name is this machine's own and never changes when the journal joins a team; its team name, the owner's name before it, is the one the team server and every other machine know it by, and is absent until a team knows it."""

    local_fields: ClassVar[tuple[str, ...]] = ("name",)

    name: str = ""
    branch: str | None = None
    is_team_chat: bool = False
    team_name: str | None = None
    key: str = field(default_factory=EnvironmentKey.random)

    def local_ready(self) -> "Environment":
        return self.with_(name=self.team_name) if self.team_name is not None else self

    def team_ready(self, owner_prefix: str) -> "Environment":
        if self.team_name is not None:
            return self
        return self.with_(team_name=f"{owner_prefix}-{self.name}" if owner_prefix else self.name)
