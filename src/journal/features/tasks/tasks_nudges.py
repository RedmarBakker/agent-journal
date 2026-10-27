from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout

YEAR_SECONDS = 365 * 86400.0


class TasksNudges:
    """The nudges of the tasks feature."""

    TASK_POINTS_CHANGED = Nudge("tasks", "task_points_changed", "task {{n}}: brief point {{points|cap=15}} rewritten", "reread it with `journal task show {{n}}` and prove it again if you had", repeat=Timeout.seconds(0))
    TASK_CHANGED = Nudge("tasks", "task_changed", "task {{n}} changed", "read it again with `journal task show {{n}}`", repeat=Timeout.seconds(0))

    TASK_CONTINUATION = Nudge("tasks", "carry_on", "{{name}} is in hand, {{logged}}: carry on", repeat=Timeout.seconds(0))
    STOP_LOG_REQUEST = Nudge("tasks", "log_first_at_stop", "{{name}}, {{logged}}", "log it first: {{log_command}} \"<status>\"", repeat=Timeout.seconds(0))
    OPEN_TASK = Nudge("tasks", "task_still_open", "{{name}} is still open: log where it stands or finish it", repeat=Timeout.seconds(900))
    UNLOGGED_TASK = Nudge("tasks", "task_open_with_nothing_logged", "task {{n}} has nothing logged. log where it stands with `journal task log {{n}} \"<where it stands>\"`")
    IMPASSE_REFUSAL = Nudge("tasks", "not_stuck_with_work_left", "{{count}} tasks are open: you are not stuck", "work on them, or `journal await \"<what you wait for>\" --output <n>`", repeat=Timeout.seconds(0))
    NEXT_TASK_STARTED = Nudge("tasks", "next_task_started", "task {{n}} started", "carry on with it", repeat=Timeout.seconds(0))
    POSTPONED_WORK = Nudge("tasks", "deferred_work_is_a_task", "you deferred work in words. file it with `journal task create \"<title>\" --brief \"<what and where to start>\"`")
    COMMIT_CLOSURE = Nudge("tasks", "closed_by_commit", "commit {{sha}} closed {{tasks|cap=89}}")
    STOP_POLLING = Nudge("tasks", "stop_polling", "you ran {{command|cap=50}} {{times}} times in a row", "stop polling; wait for it")
    LOG_REQUEST = Nudge("tasks", "log_where_it_stands", "{{edits}} edits since you logged {{name|cap=33}}", "log where it stands: {{log}} \"<where it stands>\"", repeat=Timeout.seconds(0))
    LOG_EDIT_BLOCK = Nudge("tasks", "write_held_until_logged", "{{edits}} edits since you logged {{name}}", "writes wait for {{log}} \"<what was done>\"", repeat=Timeout.seconds(0))
    CURRENT_TASK_REMINDER = Nudge("tasks", "task_in_hand_repeated", "{{name}} in hand, {{edits}} edits", repeat=Timeout.seconds(0))
    BLOCKED_REVIEW = Nudge("tasks", "check_the_blocked_tasks", "tasks {{tasks|cap=30}} are blocked", "`journal task unblock <n>` what you can, else `journal stuck \"<why>\"`", repeat=Timeout.seconds(0))
    PAUSED_CHOICE = Nudge("tasks", "paused_work_to_choose", "paused: {{tasks|cap=15}}{{blocked}}", "`journal task resume <n>`, or `journal task skip-paused` to take the open task", repeat=Timeout.seconds(0))
    PAUSED_TASKS = Nudge("tasks", "paused_tasks_still_open", "paused tasks: {{tasks|cap=51}}", "resume one that can go on: `journal task resume <n>`", repeat=Timeout.seconds(0))
    PAUSED_TASK_REMINDER = Nudge("tasks", "paused_task_asked_about", "task {{n}} is paused: {{why|cap=50}}", "`journal task resume {{n}}` if it can go on now", repeat=Timeout.seconds(900))
    PAUSED_TASK_CLOSURE_REMINDER = Nudge("tasks", "paused_task_named_at_close", "task {{n}} is paused: {{why|cap=50}}", "`journal task resume {{n}}` if it can go on now", repeat=Timeout.seconds(0))
    WAIT_CHECK = Nudge("tasks", "check_the_wait", "you have waited {{minutes}} minutes on {{what|cap=31}}", "read its latest lines and check it does what you expect", repeat=Timeout.seconds(300), blocks_regardless=True)
    IDLE_CHECK = Nudge("tasks", "check_in_after_quiet", "nothing has happened for half an hour", "carry on, take the next task, or say in one line why not", repeat=Timeout.seconds(1800))
    WAIT_LIFTED = Nudge("tasks", "wait_lifted", "your wait on {{what|cap=19}} was lifted; check {{n}} still runs. remove it if not needed: `journal check remove {{n}}`", repeat=Timeout.seconds(0))
    WAIT_CHECK_PASSED = Nudge("tasks", "wait_check_passed", "{{what|cap=30}} is done: {{lines|cap=78}}", repeat=Timeout.seconds(0))
    WAIT_END = Nudge("tasks", "wait_over", "wait over: {{outcome|cap=100}}", repeat=Timeout.seconds(0))
    PRIORITIES_REMINDER = Nudge("tasks", "give_tasks_their_priority", "tasks {{tasks|cap=13}} need a priority: `journal task edit <n> --priority <level>`, or `journal task priorities confirm`", "", repeat=Timeout.seconds(YEAR_SECONDS), blocks_regardless=True)
    PRIORITIES_REFUSAL = Nudge("tasks", "tasks_wait_for_their_priority", "writes wait: tasks {{tasks|cap=20}} need a priority, `journal task edit <n> --priority <level>` or `journal task priorities confirm`", "", repeat=Timeout.seconds(0), longest_characters=140, longest_reason="a hold that must name both ways out of it")
    WAIT_SHORT = Nudge("tasks", "wait_it_out", "{{what|cap=19}} has about {{seconds}} seconds left and you already wait on it", "end your turn; you are informed when it ends", repeat=Timeout.seconds(0))
    WAIT_LONG = Nudge("tasks", "park_the_wait", "{{what|cap=18}} has about {{seconds}} seconds left, too long to wait", "carry on with task {{n}}; you are informed when it ends", repeat=Timeout.seconds(0))
    WAIT_PAUSED_TASK = Nudge("tasks", "paused_task_while_waiting", "while you wait for {{what}}, resume paused task {{n}}: `journal task resume {{n}}`", "", repeat=Timeout.seconds(0))
    WAIT_NEXT_TASK = Nudge("tasks", "next_task_while_waiting", "while you wait for {{what}}, work on task {{n}}; you are informed when the wait ends", "", repeat=Timeout.seconds(0))
    WAIT_STOP = Nudge("tasks", "no_stop_while_waiting", "{{what|cap=24}} still runs ({{left|cap=16}})", "do not stop; carry on with task {{n}} until it ends", repeat=Timeout.seconds(0))
    WAIT_SWITCH_REFUSAL = Nudge("tasks", "await_switches_task", "{{what|cap=24}} runs {{left}}, too long to wait", "work on task {{n}} meanwhile: `journal task start {{n}}`", repeat=Timeout.seconds(0))
    WAIT_REFUSAL = Nudge("tasks", "await_only_what_ends_soon", "{{what|cap=24}} runs {{left}}, too long to wait", "carry on with task {{n}}; you are informed when it ends", repeat=Timeout.seconds(0))
    WAIT_REASON_REQUEST = Nudge("tasks", "await_needs_its_reason", "{{what|cap=24}} runs {{left}}; to wait anyway, say why", "add --why \"<why it must wait now>\" to the await", repeat=Timeout.seconds(0))
    WAIT_REASON_LINE = Nudge("tasks", "await_with_its_reason", "waiting because {{why|cap=48}}", "do any open work that does not depend on it meanwhile", repeat=Timeout.seconds(0))
    OUTPUT_POLL_REFUSAL = Nudge("tasks", "output_polled", "do not poll output {{n}}", "wait for it: `journal await \"<what>\" --output {{n}}`", repeat=Timeout.seconds(0))
    TASK_OPENED = Nudge("tasks", "task_opened", "task {{n}} is open", "take it up with `journal task start {{n}}`", repeat=Timeout.seconds(0))
    PAUSE_WAIT_END = Nudge("tasks", "paused_wait_ended", "task {{n}}'s wait is over: {{reason|cap=61}}", "run `journal task resume {{n}}`", repeat=Timeout.seconds(0))
    TASK_REOPENED = Nudge("tasks", "task_reopened", "task {{n}} is open again: {{reason|cap=51}}", "take it up with `journal task start {{n}}`", repeat=Timeout.seconds(0))
    BROKEN_WAIT = Nudge("tasks", "fix_the_broken_wait", "{{waits}}", "fix it with `journal task block <n> --until \"<command>\"`, or `journal task unblock <n>`", repeat=Timeout.seconds(0))
    BLOCKED_TASK_REMINDER = Nudge("tasks", "blocked_task_asked_about", "blocked with nothing to open them: {{tasks|cap=18}}", "run `journal task unblock <n>` once what it waits on has arrived", repeat=Timeout.seconds(2700), blocks_regardless=True)
