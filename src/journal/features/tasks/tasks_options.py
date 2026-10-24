from journal.support.option import USER, Option


class TasksOptions:
    """The options of the tasks feature."""

    AUTO = Option("tasks.auto", "Work the list on its own", "At a stop with tasks open, the next one holds the stop until it is taken up; off, the agent stops and waits for you", True, kind="switch", setter=USER)
    FIRST_DELAY = Option("tasks.first_nudge_after", "Ask for a log after", "Edits without a log line before the agent is asked where its task stands", 25, unit="edits")
    TASK_REMINDER_INTERVAL = Option("tasks.name_every", "Name the task back every", "Edits between reminders of the task in hand, so drift is visible", 25, unit="edits")
    LOG_LIMIT = Option("tasks.log_after", "Hold the next write after", "Edits without a log line before the agent's next write waits for one", 50, unit="edits")
    LOG_AGE_LIMIT = Option("tasks.log_old_after_minutes", "Ask for a log at a stop after", "Minutes since the task's last log line before a stop asks for one before carrying on", 10, unit="min")
    BLOCK_BATCH = Option("tasks.block_batch_seconds", "Refuse a third block within", "A third task blocked within this many seconds of two others is refused: blocking a batch is clearing the list, not tasks that cannot move", 300, unit="seconds")
