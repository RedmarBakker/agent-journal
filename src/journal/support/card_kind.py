from enum import StrEnum


class CardKind(StrEnum):
    """What a mark in the chat is, by the switch in Show in chat that hides it: every card names one. A kind whose marks come in a burst, as the edits a colleague's kept over yours do, folds the marks of one burst into one."""

    SKILLS = "skills"
    SUBAGENTS = "subagents"
    WORKERS = "workers"
    COMPACTIONS = "compactions"
    CREATED = "made"
    IMPASSE = "stuck"
    RULES = "rules"
    FACTS = "facts"
    REMINDERS = "reminders"
    COMMANDS = "commands"
    COMMITS = "commits"
    WORKTREES = "worktrees"
    CHECKS = "checks"
    QUESTIONS = "questions"
    SEQUENCES = "sequences"
    SEQUENCE_STEPS = "sequence_steps"
    TRIGGERS = "triggers"
    MENUS = "menus"
    SEARCHES = "searches"
    SUGGESTIONS = "suggestions"
    PLUGINS = "plugins"
    PHONES = "phones"
    FILED = "filed"
    TASK_MOVES = "task_moves"
    FAULTS = "faults"
    CONFLICTS = "conflicts"

    def folds(self) -> bool:
        return self in (CardKind.CONFLICTS,)
