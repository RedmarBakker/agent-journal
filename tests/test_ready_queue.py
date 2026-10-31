from datetime import datetime, timedelta, timezone

from journal.features.tasks.support.ready_queue import ReadyQueue
from journal.models.task import Task
from journal.support.task_priority import LEVELS


def test_ready_queue_orders_deadline_risk_slack_priority_size_and_aging():
    now = datetime(2026, 10, 31, tzinfo=timezone.utc)
    rows = [
        Task(id=1, created_at=now, priority=LEVELS["critical"], size=1),
        Task(id=2, created_at=now, priority=LEVELS["normal"], size=8),
        Task(id=3, created_at=now, priority=LEVELS["critical"], size=8),
        Task(id=4, created_at=now, priority=LEVELS["normal"], size=3),
        Task(id=5, created_at=now, priority=LEVELS["critical"], size=1),
        Task(id=6, created_at=now, priority=LEVELS["critical"], size=1),
    ]
    forecasts = {
        1: {"sprint": {"ends_on": "2026-11-08"}, "probability_this_sprint": 25,
            "critical_path": {"tasks": [{"task_id": 1, "slack_days": 2}]}},
        2: {"sprint": {"ends_on": "2026-11-08"}, "probability_this_sprint": 25,
            "critical_path": {"tasks": [{"task_id": 2, "slack_days": 0}]}},
        3: {"sprint": {"ends_on": "2026-11-08"}, "probability_this_sprint": 25,
            "critical_path": {"tasks": [{"task_id": 3, "slack_days": 0}]}},
        4: {"sprint": {"ends_on": "2026-11-08"}, "probability_this_sprint": 25,
            "critical_path": {"tasks": [{"task_id": 4, "slack_days": 0}]}},
        5: {"sprint": {"ends_on": "2026-11-08"}, "probability_this_sprint": None,
            "critical_path": {"tasks": [{"task_id": 5, "slack_days": None}]}},
        6: {"sprint": {"ends_on": "2026-11-08"}, "probability_this_sprint": 85,
            "critical_path": {"tasks": [{"task_id": 6, "slack_days": 0}]}},
    }

    ordered = sorted(rows, key=lambda task: ReadyQueue.rank_key(task, forecasts[task.row_id], now, 70))

    assert [task.row_id for task in ordered] == [3, 4, 2, 1, 5, 6]

    aged_unknown = Task(id=7, created_at=now - timedelta(days=1), priority=LEVELS["normal"], size=None)
    new_urgent = Task(id=8, created_at=now, priority=LEVELS["critical"], size=1)
    unknown = {"sprint": {"ends_on": "2026-11-08"}, "probability_this_sprint": None,
               "critical_path": {"tasks": [{"task_id": 7, "slack_days": None}]}}
    urgent = {"sprint": {"ends_on": "2026-11-08"}, "probability_this_sprint": None,
              "critical_path": {"tasks": [{"task_id": 8, "slack_days": None}]}}

    aged = sorted((new_urgent, aged_unknown), key=lambda task: ReadyQueue.rank_key(
        task, {7: unknown, 8: urgent}[task.row_id], now, 70))

    assert [task.row_id for task in aged] == [7, 8]

    earlier = Task(id=9, created_at=now, priority=LEVELS["normal"], size=3)
    later = Task(id=10, created_at=now, priority=LEVELS["normal"], size=3)
    earlier_forecast = {"sprint": {"ends_on": "2026-11-08"}, "probability_this_sprint": 40,
                        "critical_path": {"tasks": [{"task_id": 9, "slack_days": 0}]}}
    later_forecast = {"sprint": {"ends_on": "2026-11-15"}, "probability_this_sprint": 40,
                      "critical_path": {"tasks": [{"task_id": 10, "slack_days": 0}]}}

    deadlines = sorted((later, earlier), key=lambda task: ReadyQueue.rank_key(
        task, {9: earlier_forecast, 10: later_forecast}[task.row_id], now, 70))

    assert [task.row_id for task in deadlines] == [9, 10]
