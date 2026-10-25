from journal.engine.nudge import Nudge
from journal.support.timeout import Timeout

YEAR_SECONDS = 365 * 86400.0


class TasksNudges:
    """The nudges of the tasks feature."""

    TASK_POINTS_CHANGED = Nudge("tasks", "task_points_changed", "task {{n}} changed: point {{points}} of its brief rewritten", "read it again with `journal task show {{n}}`, and prove a rewritten point again if you proved it", repeat=Timeout.seconds(0))
    TASK_CHANGED = Nudge("tasks", "task_changed", "task {{n}} changed", "read it again with `journal task show {{n}}`", repeat=Timeout.seconds(0))

    TASK_CONTINUATION = Nudge("tasks", "carry_on", "{{name}} is in hand, {{logged}}: carry on", repeat=Timeout.seconds(0))
    STOP_LOG_REQUEST = Nudge("tasks", "log_first_at_stop", "{{name}}, {{logged}}: log where it stands first", "{{log_command}} \"<where it stands>\"", repeat=Timeout.seconds(0))
    OPEN_TASK = Nudge("tasks", "task_still_open", "{{name}} is still open: log where it stands or finish it", repeat=Timeout.seconds(900))
    UNLOGGED_TASK = Nudge("tasks", "task_open_with_nothing_logged", "task {{n}} is open with nothing logged")
    IMPASSE_REFUSAL = Nudge("tasks", "not_stuck_with_work_left", "{{count}} tasks are open, in progress or paused, so you are not stuck", "go on with them, or wait on what you started with journal await", repeat=Timeout.seconds(0))
    NEXT_TASK = Nudge("tasks", "next_task_holds_the_stop", "tasks are open, and auto mode is on: task {{n}} next", "carry on with it", repeat=Timeout.seconds(0))
    POSTPONED_WORK = Nudge("tasks", "deferred_work_is_a_task", "work deferred in words, not filed: `journal task create` it")
    COMMIT_CLOSURE = Nudge("tasks", "closed_by_commit", "commit {{sha}} closed {{tasks}}")
    STOP_POLLING = Nudge("tasks", "stop_polling", "you ran the same check {{times}} times in a row: {{command}}", "wait for it instead of polling")
    LOG_REQUEST = Nudge("tasks", "log_where_it_stands", "{{edits}} edits since you logged {{name}}: say where it stands", "{{log}} \"<where it stands>\"", repeat=Timeout.seconds(0))
    LOG_EDIT_BLOCK = Nudge("tasks", "write_held_until_logged", "{{edits}} edits since you logged {{name}}", "{{log}} \"<what was decided or done>\" before any other write", repeat=Timeout.seconds(0))
    CURRENT_TASK_REMINDER = Nudge("tasks", "task_in_hand_repeated", "{{name}} in hand, {{edits}} edits", repeat=Timeout.seconds(0))
    BLOCKED_REVIEW = Nudge("tasks", "check_the_blocked_tasks", "tasks {{tasks}} are blocked", "unblock one whose wait has passed or that you can decide, and report what you decided; when every task left is truly blocked, journal stuck \"<why>\"", repeat=Timeout.seconds(0))
    TASK_QUEUE = Nudge("tasks", "work_left_holds_the_stop", "tasks are left: {{tasks}}", "take one or resume a paused one; journal stuck \"<why>\" when every task left is truly blocked", repeat=Timeout.seconds(0))
    PAUSED_TASKS = Nudge("tasks", "paused_tasks_still_open", "paused tasks: {{tasks}}", "resume one that can go on with `journal task resume <n>`", repeat=Timeout.seconds(0))
    PAUSED_TASK_REMINDER = Nudge("tasks", "paused_task_asked_about", "task {{n}} is paused: {{why}}", "`journal task resume {{n}}` if it can go on now", repeat=Timeout.seconds(900))
    PAUSED_TASK_CLOSURE_REMINDER = Nudge("tasks", "paused_task_named_at_close", "task {{n}} is paused: {{why}}", "`journal task resume {{n}}` if it can go on now", repeat=Timeout.seconds(0))
    WAIT_CHECK = Nudge("tasks", "check_the_wait", "you have waited {{minutes}} min on {{what}}: check it", "still going: `journal await` again; done or failed: log it and go on", repeat=Timeout.seconds(300), blocks_regardless=True)
    IDLE_CHECK = Nudge("tasks", "check_in_after_quiet", "nothing has happened for half an hour", "carry on, take the next task, or say so in one line", repeat=Timeout.seconds(1800))
    WAIT_END = Nudge("tasks", "wait_over", "wait over: {{outcome}}", repeat=Timeout.seconds(0))
    PRIORITIES_REMINDER = Nudge("tasks", "give_tasks_their_priority", "{{count}} open tasks you made sit at the default priority: {{tasks}}", "give each its priority with `journal task edit <n> --priority <level>`, or `journal task priorities confirm` if they are all normal", repeat=Timeout.seconds(YEAR_SECONDS), blocks_regardless=True)
    PRIORITIES_REFUSAL = Nudge("tasks", "tasks_wait_for_their_priority", "{{count}} open tasks you made sit at the default priority: {{tasks}}. your next write waits", "`journal task edit <n> --priority <level>` on them, or `journal task priorities confirm`", repeat=Timeout.seconds(0))
    WAIT_SHORT = Nudge("tasks", "wait_it_out", "{{what}} has about {{seconds}} seconds left", "wait it out: `journal await` ends when it does", repeat=Timeout.seconds(0))
    WAIT_LONG = Nudge("tasks", "park_the_wait", "{{what}} has about {{seconds}} seconds left, too long to wait", "park it and carry on with task {{n}}; you are told when it ends", repeat=Timeout.seconds(0))
    WAIT_NEXT_TASK = Nudge("tasks", "next_task_while_waiting", "while you wait for {{what}}, task {{n}} is next", "work on it meanwhile, or end your turn if you need what you wait for", repeat=Timeout.seconds(0))
    TASK_OPENED = Nudge("tasks", "task_opened", "task {{n}} is open", "`journal task start {{n}}` takes it up", repeat=Timeout.seconds(0))
    PAUSE_WAIT_END = Nudge("tasks", "paused_wait_ended", "what paused task {{n}} waited on came: {{reason}}", "`journal task resume {{n}}`", repeat=Timeout.seconds(0))
    TASK_REOPENED = Nudge("tasks", "task_reopened", "task {{n}} is open again: {{reason}}", "`journal task start {{n}}` takes it up", repeat=Timeout.seconds(0))
    BROKEN_WAIT = Nudge("tasks", "fix_the_broken_wait", "{{waits}}", "fix it with `journal task block <n> --until \"<command>\"`, or `journal task unblock <n>`", repeat=Timeout.seconds(0))
    BLOCKED_TASK_REMINDER = Nudge("tasks", "blocked_task_asked_about", "blocked, with nothing that opens it by itself: {{tasks}}", "`journal task unblock <n>` once what it waits on has come", repeat=Timeout.seconds(2700), blocks_regardless=True)
