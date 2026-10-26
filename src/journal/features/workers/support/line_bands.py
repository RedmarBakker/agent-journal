from journal.features.workers.support.handout_direction import HandoutDirection
from journal.features.workers.support.line_band import LineBand
from journal.features.workers.workers_nudges import WorkersNudges
from journal.models.support.pressure_band import PressureBand

LOW, NORMAL, HIGH = PressureBand.LOW, PressureBand.NORMAL, PressureBand.HIGH
INCREASE, DECREASE, NEUTRAL = HandoutDirection.INCREASE, HandoutDirection.DECREASE, HandoutDirection.NEUTRAL
CLEAR_OLDEST = WorkersNudges.CLEAR_OLDEST.key


class LineBands:
    """The one table of where each measure line speaks and which way it pushes, per mode: a line that asks for more handing out never shares a band with one that asks for less, and a line speaks only in its bands."""

    ROWS = (
        LineBand("builder", WorkersNudges.BUILDER_CODE_SHARE_LINE.key, (LOW, NORMAL), DECREASE),
        LineBand("builder", WorkersNudges.BUILDER_QUEUE_LINE.key, (HIGH,), DECREASE),
        LineBand("builder", WorkersNudges.BUILDER_WORKER_LINE.key, (LOW, NORMAL, HIGH), DECREASE),
        LineBand("orchestrator", CLEAR_OLDEST, (HIGH,), DECREASE),
        LineBand("orchestrator", "workers.orchestrator_check_worker", (NORMAL, HIGH), NEUTRAL),
        LineBand("orchestrator", "workers.orchestrator_hand_out", (LOW, NORMAL), INCREASE),
        LineBand("orchestrator", "workers.orchestrator_fill_place", (LOW, NORMAL), INCREASE),
        LineBand("orchestrator", "workers.orchestrator_queue_more", (LOW, NORMAL, HIGH), NEUTRAL),
        LineBand("orchestrator", "workers.orchestrator_clear_before_dispatch", (HIGH,), DECREASE),
        LineBand("solo", "workers.solo_answer", (PressureBand.NONE,), NEUTRAL),
    )

    @classmethod
    def is_allowed(cls, mode: str, nudge_key: str, band: PressureBand) -> bool:
        return any(row.mode == mode and row.nudge_key == nudge_key and band in row.bands for row in cls.ROWS)

    @classmethod
    def opposed_pairs(cls) -> tuple[tuple[str, str], ...]:
        return tuple((increase_row.nudge_key, decrease_row.nudge_key) for increase_row in cls.ROWS if increase_row.direction == INCREASE for decrease_row in cls.ROWS if decrease_row.direction == DECREASE and decrease_row.mode == increase_row.mode)
