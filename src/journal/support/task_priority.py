from journal.support.rejection import Rejection

LEVELS = {"low": 50, "normal": 100, "high": 150, "critical": 200}
NORMAL = LEVELS["normal"]


class TaskPriority:
    """How urgent a task is: a number, with the named levels low 50, normal 100, high 150 and critical 200; a number that is a level reads by its name."""

    @staticmethod
    def parsed(text: str) -> int:
        word = text.strip().lower()
        if word in LEVELS:
            return LEVELS[word]
        if word.lstrip("-").isdigit():
            return int(word)
        raise Rejection(f"no such priority: {text}; give low, normal, high, critical or a number")

    @staticmethod
    def label(priority: int) -> str:
        return next((name for name, value in LEVELS.items() if value == priority), str(priority))
