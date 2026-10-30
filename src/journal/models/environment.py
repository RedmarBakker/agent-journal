from dataclasses import dataclass, field

from journal.models.model import Model
from journal.support.environment_key import EnvironmentKey


@dataclass(frozen=True)
class Environment(Model):
    """A named place where an agent works, with a stable key and its source environment."""

    name: str = ""
    branch: str | None = None
    key: str = field(default_factory=EnvironmentKey.random)
    generated_for: str = ""
    parent_key: str = ""
