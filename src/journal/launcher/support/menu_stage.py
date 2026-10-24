from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from journal.launcher.support.menu_answers import MenuAnswers


@dataclass(frozen=True)
class MenuStage:
    """The answers after one question of the menu, and whether the question was shown."""

    answers: "MenuAnswers"
    is_shown: bool
