from dataclasses import asdict

from journal.support.card_kind import CardKind
from journal.support.mark_group import MarkGroup
from journal.support.mark_kind import MarkKind

AGENT, REMINDERS, WORK, JOURNAL = "agent", "reminders", "work", "journal"


class MarkKinds:
    """Every kind of chat mark, registered once with its group: each CardKind a card names, and the turn kinds only the viewer draws, the agent's thoughts, your receipts, visitors' comments, acknowledged reminders and the agents talking; served to the viewer, which builds Show in chat from it."""

    GROUPS = (
        MarkGroup(AGENT, "Agent", "bot"),
        MarkGroup(REMINDERS, "Reminders", "reminders"),
        MarkGroup(WORK, "Work", "todos"),
        MarkGroup(JOURNAL, "The journal", "bolt"),
    )
    KINDS = (
        MarkKind("thoughts", "Summaries of the agent's words", "bot", AGENT, turns=("thought",)),
        MarkKind(CardKind.SKILLS, "Skills the agent loads", "book", AGENT),
        MarkKind("agents", "Agents talking to each other", "agents", AGENT, covers=(CardKind.SUBAGENTS, CardKind.WORKERS)),
        MarkKind(CardKind.SUBAGENTS, "Subagents", "agents", AGENT),
        MarkKind(CardKind.WORKERS, "Workers", "agents", AGENT, messages=("report",)),
        MarkKind(CardKind.REVIEWERS, "Reviews of a worker's work", "verifier", AGENT),
        MarkKind(CardKind.COMPACTIONS, "Conversation compacted", "gauge", AGENT),
        MarkKind(CardKind.CREATED, "Documents the agent made", "docs", AGENT),
        MarkKind(CardKind.SEARCHES, "Searches the agent ran", "search", AGENT),
        MarkKind(CardKind.IMPASSE, "Agent stuck", "warn", AGENT),
        MarkKind("acknowledgements", "Acknowledged reminders", "check", AGENT, main=False, shown=False, messages=("acknowledgement",)),
        MarkKind(CardKind.RULES, "Rules", "rules", REMINDERS),
        MarkKind(CardKind.FACTS, "Facts", "pins", REMINDERS),
        MarkKind(CardKind.REMINDERS, "Reminders", "reminders", REMINDERS),
        MarkKind(CardKind.COMMANDS, "Long commands and outputs", "terminal", WORK),
        MarkKind(CardKind.COMMITS, "Commits", "branch", WORK),
        MarkKind(CardKind.WORKTREES, "Worktrees", "branch", WORK),
        MarkKind(CardKind.CHECKS, "Checks passing and failing", "check", WORK),
        MarkKind(CardKind.QUESTIONS, "Questions asked and answered", "questions", WORK),
        MarkKind(CardKind.FILED, "Filed from your messages", "inbox", WORK, turns=("receipt",)),
        MarkKind(CardKind.TASK_MOVES, "Tasks started, finished, paused and blocked", "task", WORK),
        MarkKind(CardKind.CONFLICTS, "Your edits a colleague's newer edit replaced", "warn", WORK, main=False, shown=False),
        MarkKind(CardKind.SEQUENCES, "Sequences starting and finishing", "list", JOURNAL),
        MarkKind(CardKind.SEQUENCE_STEPS, "Every step of a sequence", "list", JOURNAL, main=False, shown=False),
        MarkKind(CardKind.TRIGGERS, "Triggers", "bolt", JOURNAL),
        MarkKind(CardKind.MENUS, "Menus the journal answered", "bolt", JOURNAL),
        MarkKind(CardKind.SUGGESTIONS, "Suggestions", "bulb", JOURNAL),
        MarkKind(CardKind.VERIFIERS, "Dismissals a verifier checked", "verifier", JOURNAL, shown=False),
        MarkKind(CardKind.PLUGINS, "Plugin notes", "plug", JOURNAL),
        MarkKind(CardKind.PHONES, "Phones paired", "phone", JOURNAL),
        MarkKind(CardKind.REQUESTS, "Requests filed for you", "inbox", JOURNAL),
        MarkKind(CardKind.UPDATES, "The journal server replaced by a newer launch", "bolt", JOURNAL),
        MarkKind(CardKind.FAULTS, "The journal's own faults", "warn", JOURNAL),
        MarkKind("visitors", "Visitor comments", "chat", JOURNAL, turns=("visitor",)),
    )

    @classmethod
    def served(cls) -> dict:
        return {"groups": [asdict(group) for group in cls.GROUPS], "kinds": [cls.served_kind(kind) for kind in cls.KINDS]}

    @staticmethod
    def served_kind(kind: MarkKind) -> dict:
        return {**asdict(kind), "key": str(kind.key), "turns": list(kind.turns), "messages": list(kind.messages), "covers": [str(key) for key in kind.covers]}
