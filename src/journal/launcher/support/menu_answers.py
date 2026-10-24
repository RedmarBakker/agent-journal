from dataclasses import dataclass

from journal.launcher.support.answers import Answers
from journal.support.environment_row import EnvironmentRow


@dataclass
class MenuAnswers:
    """What a launch's menu knows as it asks its questions in turn: what the launch was given, the environments to choose from, the answers last time, and each answer as it is given."""

    agent: str
    environment: str
    new: bool
    stashed: bool
    omit: bool
    rows: list[EnvironmentRow]
    previous: Answers
    selection: str = ""
    session: str = ""
    resume: str = ""
    prompt_flags: bool = False
    stashed_hooks: bool = False
