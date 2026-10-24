from collections.abc import Callable
from dataclasses import dataclass, replace

from journal.launcher.support.answers import Answers
from journal.launcher.support.menu_stage import MenuStage
from journal.support.environment_row import EnvironmentRow


@dataclass(frozen=True)
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

    def with_environment(self, environment_picker: Callable[[str, list[EnvironmentRow]], str]) -> "MenuStage":
        return MenuStage(replace(self, selection=self.environment or environment_picker(self.agent, self.rows)), not self.environment)

    def with_session(self, free: Callable[[str], list], session_picker: Callable[[str, list], str]) -> "MenuStage":
        if self.new or self.selection in {row.name for row in self.rows}:
            return MenuStage(replace(self, session=""), False)
        sessions = free(self.agent)
        return MenuStage(replace(self, session=session_picker(self.selection, sessions) if sessions else ""), bool(sessions))

    def with_resume(self, environment_lister: Callable[[str, list[EnvironmentRow]], list[EnvironmentRow]], resume_picker: Callable[[str, str, str], str]) -> "MenuStage":
        last = next((row.last_session(self.agent) for row in environment_lister(self.selection, self.rows) if row.name == self.selection), "")
        if self.session or self.new or not last:
            return MenuStage(replace(self, resume=self.session), False)
        return MenuStage(replace(self, resume=resume_picker(self.agent, self.selection, last)), True)

    def with_prompts(self, prompts_picker: Callable[[str], bool]) -> "MenuStage":
        return MenuStage(replace(self, prompt_flags=self.omit or prompts_picker(self.agent)), not self.omit)

    def with_hooks(self, hooks_picker: Callable[[str, bool], bool]) -> "MenuStage":
        stashed_choice = self.stashed or self.previous.stashed_hooks
        if self.stashed or self.resume:
            return MenuStage(replace(self, stashed_hooks=stashed_choice), False)
        return MenuStage(replace(self, stashed_hooks=hooks_picker(self.agent, self.previous.stashed_hooks)), True)
