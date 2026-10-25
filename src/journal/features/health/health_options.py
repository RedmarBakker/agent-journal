from journal.support.option import Option
from journal.support.option_scope import OptionScope


class HealthOptions:
    """The options of the health feature: how the supervisor checks the journal and starts it again, and how the journal copies its database."""

    CHECK_SECONDS = Option("health.check_seconds", "Health check every", "How often the supervisor asks the journal whether it is well; read at the next launch", 10, unit="seconds", scope=OptionScope.MACHINE)
    ANSWER_SECONDS = Option("health.answer_seconds", "Health answer may take", "How long the supervisor waits for the journal's health answer before it counts a miss; read at the next launch", 5, unit="seconds", scope=OptionScope.MACHINE)
    MISSES = Option("health.misses", "Restart after misses in a row", "How many health checks in a row the journal may miss before the supervisor starts it again; read at the next launch", 3, unit="misses", scope=OptionScope.MACHINE)
    BOOT_SECONDS = Option("health.boot_seconds", "Leave a fresh boot alone for", "How long after the journal starts the supervisor waits before its first health check; read at the next launch", 60, unit="seconds", scope=OptionScope.MACHINE)
    BACKUP_MINUTES = Option("health.backup_minutes", "Copy the database every", "How often the journal writes an online copy of its database to .journal/backups-watch; 0 writes none", 15, unit="minutes", scope=OptionScope.MACHINE)
    BACKUP_COUNT = Option("health.backup_count", "Database copies kept", "How many of the newest database copies stay in .journal/backups-watch", 2, unit="copies", scope=OptionScope.MACHINE)
