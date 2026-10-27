from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


YEAR_SECONDS = 365 * 86400.0


class MemoryNudges:
    CONTEXT_DECISION = Nudge("memory", "decide_at_the_mark", "at {{percent}}%, weigh {{count}} memories: `journal memory weigh <numbers> <weights>` or `journal memory skip \"<why>\"`", "", repeat=Timeout.seconds(0))
    DECISION_EDIT_BLOCK = Nudge("memory", "write_held_until_decided", "writes wait until you weigh your memories: `journal memory weigh <numbers> <weights>` or `journal memory skip \"<why>\"`", "")
    UNDECIDED_STOP = Nudge("memory", "stopped_at_mark", "before you stop at context {{percent}}%: `journal memory weigh <numbers> <weights>` or `journal memory skip \"<why>\"`", "", repeat=Timeout.seconds(0))
    CHECK_STALE_MEMORY = Nudge("memory", "check_stale_memory", "memories {{stale}} are {{stale_after}}+ days old", "remove what is no longer true: `journal memory remove <numbers>`", repeat=Timeout.seconds(86400))
    RULE_SCOPE_QUESTION = Nudge("memory", "does_the_rule_apply_project_wide", "if rule {{n}} does not apply to the whole project, delete it and record a fact or a reminder instead", "")
    REMINDER_REPEATED = Nudge("memory", "reminder_repeated", "reminder {{n}}, again: {{text}}", repeat=Timeout.seconds(0))
    REMINDER_DUE = Nudge("memory", "reminder_due", "reminder {{n}} is due: {{text}}", repeat=Timeout.seconds(YEAR_SECONDS))
    MEMORY_TRIGGERED = Nudge("memory", "memory_for_this_moment", "{{noun}} {{n}} applies now: `journal {{noun}} read {{n}}`", repeat=Timeout.seconds(0))
    WORKER_MEMORIES = Nudge("memory", "memories_shown_at_clock_in", "your memories: {{memories}}", "`journal memory weigh <numbers> <weights>` or `journal memory remove <numbers>`", repeat=Timeout.seconds(0))
    MEMORY_READ_REQUEST = Nudge("memory", "memory_whispered_back", "{{noun}} {{n}} is about this and not in your context: `journal {{noun}} read {{n}}`", repeat=Timeout.seconds(YEAR_SECONDS))
