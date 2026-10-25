from enum import StrEnum


class EnvironmentKind(StrEnum):
    """What an environment is to the team: a person's own, a team's hub, or a team's session, a chat the whole team reads and writes, the Team chat the first."""

    LOCAL = "local"
    HUB = "hub"
    SESSION = "session"
