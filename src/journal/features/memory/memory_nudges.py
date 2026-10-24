from journal.engine.nudge import Nudge


YEAR_SECONDS = 365 * 86400.0


class MemoryNudges:
    CONTEXT_DECISION = Nudge("memory", "decide_at_the_mark", "context {{percent}}% full: decide what to keep", "`journal fact create \"<what is true here>\"`, `journal rule create \"<Always/Never ...>\"` or `journal memory skip \"<why>\"`; writes wait until you do", repeat_interval=0)
    DECISION_EDIT_BLOCK = Nudge("memory", "write_held_until_decided", "writes wait until you decide what to keep from the context", "`journal fact create`, `journal rule create`, or `journal memory skip \"<why>\"`")
    UNDECIDED_STOP = Nudge("memory", "stopped_at_mark", "you stopped with a decision due at the context mark, {{percent}}% full", "`journal fact create`, `journal rule create` or `journal memory skip \"<why>\"` first", repeat_interval=0)
    CHECK_STALE_MEMORY = Nudge("memory", "check_stale_memory", "{{stale_after}} days old or more, check they still hold: {{stale}}", "strike what no longer holds and reword what drifted", repeat_interval=86400)
    RULE_SCOPE_QUESTION = Nudge("memory", "does_the_rule_apply_project_wide", "does rule {{n}} apply to the whole project?", "if not, delete it and record a fact or a reminder")
    REMINDER_DUE = Nudge("memory", "reminder_due", "reminder {{n}} is due: {{text}}", repeat_interval=YEAR_SECONDS)
    MEMORY_TRIGGERED = Nudge("memory", "memory_for_this_moment", "{{noun}} {{n}} is for this moment: journal {{noun}} read {{n}}", repeat_interval=0)
    MEMORY_READ_REQUEST = Nudge("memory", "memory_whispered_back", "{{noun}} {{n}} is about this and not in your context: journal {{noun}} read {{n}}", repeat_interval=YEAR_SECONDS)
