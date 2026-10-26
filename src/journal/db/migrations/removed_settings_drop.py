from typing import ClassVar

from journal.db.connection import Connection
from journal.db.migration import Migration

REMOVED_KEYS = ("workers.fitness_level_step", "workers.own_share_full_score", "workers.own_share_zero_score", "workers.own_share_weight", "workers.builder_lines_per_handover", "workers.builder_handovers",
                "workers.orchestrator_lines", "workers.fitness_threshold", "workers.solo_dispatches", "workers.check_reminder_uses", "workers.load_told_from", "workers.load_told_step", "workers.load_drain_tool_uses",
                "workers.weight_idle_place", "workers.interruption_window_minutes", "workers.interruptions_full_score_per_hour", "workers.interruptions_zero_score_per_hour", "workers.plenty_open_tasks",
                "workers.quick_report_minutes", "workers.quick_report_drop_points", "workers.tiny_job_drop_points", "workers.drop_recovery_minutes", "workers.report_misfit_drop_points", "workers.queue_window_minutes",
                "workers.queue_drain_hours")


class RemovedSettingsDrop(Migration):
    """The settings rows of the options the fitness measures replaced are deleted, so the Settings page and the settings reader never meet a key no option names."""

    number: ClassVar[int] = 63

    def apply(self, connection: Connection) -> None:
        connection.execute(f"DELETE FROM settings WHERE key IN ({', '.join('?' for _ in REMOVED_KEYS)})", REMOVED_KEYS)
