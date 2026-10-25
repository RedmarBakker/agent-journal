from enum import StrEnum


class EnvironmentKind(StrEnum):
    """What an environment is to the team: a person's own, or a team's hub."""

    LOCAL = "local"
    HUB = "hub"
