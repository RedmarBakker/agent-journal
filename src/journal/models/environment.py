from dataclasses import dataclass, field
from typing import ClassVar

from journal.events.rows.environment_unshared import EnvironmentUnshared
from journal.models.environment_kind import EnvironmentKind
from journal.models.model import Model
from journal.support.rejection import Rejection
from journal.support.environment_key import EnvironmentKey


@dataclass(frozen=True)
class Environment(Model):
    """A place an agent works. Its key, made at random when it is made, never changes and is how this machine and the team server match it; its name is this machine's own and never changes when the journal joins a team; its team name, the owner's name before it, is the one the team server and every other machine know it by, and is absent until a team knows it; one its owner shares with the team is in every member's sidebar and its chat open to all; one that works in a worktree names the machine that holds its folder; a team's hub names the team by its key."""

    local_fields: ClassVar[tuple[str, ...]] = ("name",)

    name: str = ""
    branch: str | None = None
    worktree_host: str = ""
    is_team_chat: bool = False
    team_name: str | None = None
    is_shared_with_team: bool = False
    key: str = field(default_factory=EnvironmentKey.random)
    kind: EnvironmentKind = EnvironmentKind.LOCAL
    team_key: str = ""

    @classmethod
    def hub(cls, team_key: str, team_name: str) -> "Environment":
        return cls(name=team_name, team_name=team_name, kind=EnvironmentKind.HUB, team_key=team_key)

    def is_personal(self) -> bool:
        return self.kind == EnvironmentKind.LOCAL and not self.is_team_chat

    def local_ready(self) -> "Environment":
        return self.with_(name=self.team_name) if self.team_name is not None else self

    def shared_with_team(self) -> "Environment":
        if self.is_team_chat:
            raise Rejection("the Team chat is the whole team's already")
        return self.with_(is_shared_with_team=True)

    def unshared(self) -> "Environment":
        if not self.is_shared_with_team:
            return self
        return self.with_(is_shared_with_team=False).with_event(EnvironmentUnshared(environment_id=self.row_id))

    def team_ready(self, owner_prefix: str) -> "Environment":
        if self.team_name is not None:
            return self
        return self.with_(team_name=f"{owner_prefix}-{self.name}" if owner_prefix else self.name)
