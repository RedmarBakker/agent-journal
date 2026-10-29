from dataclasses import dataclass
from pathlib import Path

from journal.features.skills.support.skill_files import HOMES, SKILL_FILE
from journal.support.tool_call import ToolCall


@dataclass(frozen=True)
class SkillCard:
    """One skill, the journal's or a plugin's, as the feature data carries it: its name, where its file is from the project's root, the hash of its text, the words that call for it, the states that require it and the journal command nouns it must be read before; a read of its file from any agent's skill folder, or its load by name, reads it."""

    name: str
    path: str
    digest: str
    keywords: tuple[str, ...]
    required_states: tuple[str, ...]
    commands: tuple[str, ...] = ()

    def matches_read(self, call: ToolCall) -> bool:
        paths = tuple(f"{home}/{Path(self.path).parent.name}/{SKILL_FILE}" for home in HOMES)
        return self.name == call.skill_loaded or any(path.endswith(candidate) for path in call.read_paths for candidate in paths)
