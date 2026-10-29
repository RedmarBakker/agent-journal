from dataclasses import dataclass, field

from journal.models.model import Model
from journal.support.environment_key import EnvironmentKey


@dataclass(frozen=True)
class Environment(Model):
    """A place an agent works: its name, the branch it works on, and a key made at random when it is made that never changes."""

    name: str = ""
    branch: str | None = None
    key: str = field(default_factory=EnvironmentKey.random)
