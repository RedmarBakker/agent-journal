from dataclasses import asdict

from journal.support.card_kind import CardKind
from journal.support.card_family import CardFamily
from journal.support.mark_group import MarkGroup
from journal.support.mark_kind import MarkKind

AGENT, REMINDERS, WORK, JOURNAL = "agent", "reminders", "work", "journal"


class MarkKinds:
    """The groups chat marks are listed in, and the families and kinds of marks no feature owns: the agent's thoughts, the journal's own faults and visitors' comments; every feature declares its own families and kinds, collected at boot."""

    GROUPS = (
        MarkGroup(AGENT, "Agent", "bot"),
        MarkGroup(REMINDERS, "Reminders", "reminders"),
        MarkGroup(WORK, "Work", "task"),
        MarkGroup(JOURNAL, "The journal", "bolt"),
    )
    FAMILIES = (
        CardFamily("thoughts", "The agent's words", "bot", AGENT),
        CardFamily("faults", "The journal's own faults", "warn", JOURNAL),
        CardFamily("visitors", "Visitors", "chat", JOURNAL),
    )
    KINDS = (
        MarkKind("thoughts", "Summaries of the agent's words", "thoughts", turns=("thought",)),
        MarkKind(CardKind.FAULTS, "The journal's own faults", "faults"),
        MarkKind("visitors", "Visitor comments", "visitors", turns=("visitor",)),
    )

    @staticmethod
    def served(families: list[CardFamily], kinds: list[MarkKind]) -> dict:
        family_index = {family.key: family for family in families}
        return {"groups": [asdict(group) for group in MarkKinds.GROUPS], "families": [{**asdict(family), "colouring": str(family.colouring)} for family in families],
                "kinds": [MarkKinds.served_kind(kind, family_index[kind.family]) for kind in kinds]}

    @staticmethod
    def served_kind(kind: MarkKind, family: CardFamily) -> dict:
        return {**asdict(kind), "key": str(kind.key), "icon": family.icon, "group": family.group, "colouring": str(family.colouring), "turns": list(kind.turns), "messages": list(kind.messages), "covers": [str(key) for key in kind.covers]}
