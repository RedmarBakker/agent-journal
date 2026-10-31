from datetime import datetime, timezone


class ReadyOrder:
    """Ranks ready work by forecast risk, critical slack, age, priority and size."""

    @staticmethod
    def rank_key(task, forecast: dict | None, now: datetime, threshold: int) -> tuple:
        created = ReadyOrder.value(task, "created_at") or datetime.min.replace(tzinfo=timezone.utc)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        local_now = now if now.tzinfo else now.replace(tzinfo=timezone.utc)
        age_days = max(0, (local_now.date() - created.astimezone(local_now.tzinfo).date()).days)
        task_id = ReadyOrder.value(task, "row_id", ReadyOrder.value(task, "task_id"))
        priority = ReadyOrder.value(task, "priority", 0)
        size = ReadyOrder.value(task, "size", ReadyOrder.value(task, "size_points"))
        risk = ReadyOrder.risk_group(ReadyOrder.probability(forecast), forecast, threshold)
        slack = ReadyOrder.slack(task_id, forecast)
        return (*risk, slack is None, slack if slack is not None else 0, -age_days,
                -priority, size is None, size if size is not None else 0, created.timestamp(), task_id)

    @staticmethod
    def probability(forecast: dict | None) -> int | None:
        probability = forecast.get("probability_this_sprint") if forecast else None
        return probability if isinstance(probability, int) and not isinstance(probability, bool) else None

    @staticmethod
    def risk_group(probability: int | None, forecast: dict | None, threshold: int) -> tuple[int, int, str]:
        sprint = forecast.get("sprint") if forecast else None
        ends_on = sprint.get("ends_on", "") if isinstance(sprint, dict) else ""
        if not ends_on or probability is None:
            return 1, 0, ends_on or "9999-12-31"
        return (0 if probability < threshold else 2), probability, ends_on

    @staticmethod
    def slack(task_id: int, forecast: dict | None) -> int | None:
        path = forecast.get("critical_path", {}) if forecast else {}
        task = next((row for row in path.get("tasks", ()) if row.get("task_id") == task_id), None)
        slack = task.get("slack_days") if task else None
        return slack if isinstance(slack, int) and not isinstance(slack, bool) else None

    @staticmethod
    def value(task, name: str, default=None):
        if isinstance(task, dict):
            return task.get(name, default)
        return getattr(task, name, default)
