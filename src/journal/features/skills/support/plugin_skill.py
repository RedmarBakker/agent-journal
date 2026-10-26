from dataclasses import dataclass

from journal.support.skill import Skill


@dataclass(frozen=True, kw_only=True)
class PluginSkill(Skill):
    """A skill a plugin publishes: its folder is its name and its text the published file, so a read of that file counts as reading it."""

    plugin: str
    published: str

    @property
    def folder(self) -> str:
        return self.name

    def text(self) -> str:
        return self.published
