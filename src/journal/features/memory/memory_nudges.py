from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout


YEAR_SECONDS = 365 * 86400.0


class MemoryNudges:
    CONTEXT_DECISION = Nudge("memory", "decide_at_the_mark", "context {{percent}}% full: weigh your {{count}} memories (journal memory list shows them)", "`journal memory weigh <numbers> <weights>`, `journal memory add \"<what to keep in mind>\" --weight <1 to 10>` or `journal memory skip \"<why>\"`; writes wait until you do", repeat=Timeout.seconds(0))
    DECISION_EDIT_BLOCK = Nudge("memory", "write_held_until_decided", "writes wait until you weigh your memories at the context mark", "`journal memory weigh`, `journal memory add` or `journal memory skip \"<why>\"`")
    UNDECIDED_STOP = Nudge("memory", "stopped_at_mark", "you stopped before weighing your memories at the context mark, {{percent}}% full", "`journal memory weigh`, `journal memory add` or `journal memory skip \"<why>\"` first", repeat=Timeout.seconds(0))
    CHECK_STALE_MEMORY = Nudge("memory", "check_stale_memory", "{{stale_after}} days old or more, check they still hold: {{stale}}", "strike what no longer holds and reword what drifted", repeat=Timeout.seconds(86400))
    RULE_SCOPE_QUESTION = Nudge("memory", "does_the_rule_apply_project_wide", "does rule {{n}} apply to the whole project?", "if not, delete it and record a fact or a reminder")
    REMINDER_REPEATED = Nudge("memory", "reminder_repeated", "reminder {{n}}, again: {{text}}", repeat=Timeout.seconds(0))
    REMINDER_DUE = Nudge("memory", "reminder_due", "reminder {{n}} is due: {{text}}", repeat=Timeout.seconds(YEAR_SECONDS))
    MEMORY_TRIGGERED = Nudge("memory", "memory_for_this_moment", "{{noun}} {{n}} is for this moment: journal {{noun}} read {{n}}", repeat=Timeout.seconds(0))
    WORKER_MEMORIES = Nudge("memory", "memories_shown_at_clock_in", "your memories from your earlier jobs, heaviest first: {{memories}}", "keep one where it was or raise it with `journal memory weigh <numbers> <weights>`, and take out what is no longer true with `journal memory remove <numbers>`", repeat=Timeout.seconds(0))
    MEMORY_READ_REQUEST = Nudge("memory", "memory_whispered_back", "{{noun}} {{n}} is about this and not in your context: journal {{noun}} read {{n}}", repeat=Timeout.seconds(YEAR_SECONDS))
