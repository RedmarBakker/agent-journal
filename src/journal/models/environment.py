from dataclasses import dataclass, field
from typing import ClassVar

from journal.events.rows.environment_unshared import EnvironmentUnshared
from journal.models.environment_type import EnvironmentType
from journal.models.model import Model
from journal.support.rejection import Rejection
from journal.support.environment_key import EnvironmentKey

UNKNOWN_TEAM_KEY = "unknown"


@dataclass(frozen=True)
class Environment(Model):
    """A place an agent works. Its key, made at random when it is made, never changes and is how this machine and the team server match it; its name is this machine's own and never changes when the journal joins a team; its team name, the owner's name before it, is the one the team server and every other machine know it by, and is absent until a team knows it; one its owner shares with the team carries the team's key, and is in every member's sidebar and its chat open to all; one that works in a worktree names the machine that holds its folder; a team's hub and sessions name the team by its key, which a journal that has not learnt it yet holds as unknown."""

    column_renames: ClassVar[dict[str, str]] = {"kind": "environment_type"}

    local_fields: ClassVar[tuple[str, ...]] = ("name",)

    name: str = ""
    branch: str | None = None
    worktree_host: str = ""
    team_name: str | None = None
    key: str = field(default_factory=EnvironmentKey.random)
    environment_type: EnvironmentType = EnvironmentType.LOCAL
    team_key: str = ""

    @classmethod
    def hub(cls, team_key: str, team_name: str) -> "Environment":
        return cls(name=team_name, team_name=team_name, environment_type=EnvironmentType.HUB, team_key=team_key)

    @classmethod
    def session(cls, team_key: str, name: str) -> "Environment":
        return cls(name=name, team_name=name, environment_type=EnvironmentType.SESSION, team_key=team_key)

    def is_personal(self) -> bool:
        return self.environment_type == EnvironmentType.LOCAL

    def is_session(self) -> bool:
        return self.environment_type == EnvironmentType.SESSION

    def is_team_chat(self) -> bool:
        return self.is_session() and self.branch is None

    def is_shared(self) -> bool:
        return self.is_personal() and bool(self.team_key)

    def is_private(self) -> bool:
        return self.is_personal() and not self.is_shared()

    def local_ready(self) -> "Environment":
        return self.with_(name=self.team_name) if self.team_name is not None else self

    def shared_with_team(self, team_key: str) -> "Environment":
        if not self.is_personal():
            raise Rejection(f"the {'Team chat' if self.is_session() else 'hub'} is the whole team's already")
        return self.with_(team_key=team_key)

    def unshared(self) -> "Environment":
        if not self.is_shared():
            return self
        return self.with_(team_key="").with_event(EnvironmentUnshared(environment_id=self.row_id))

    def key_learnt(self, team_key: str) -> "Environment":
        return self.with_(team_key=team_key) if self.team_key == UNKNOWN_TEAM_KEY else self

    def team_ready(self, owner_prefix: str) -> "Environment":
        if self.team_name is not None:
            return self
        return self.with_(team_name=f"{owner_prefix}-{self.name}" if owner_prefix else self.name)
