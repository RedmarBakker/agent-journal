from journal.models.plan import Plan
from journal.repositories.delivery_forecasts import DeliveryForecasts
from journal.repositories.plan_outcome_history import PlanOutcomeHistory
from journal.features.plans.support.plan_owners import PlanOwners
from journal.support.actor import Actor


class EstimatesForecast:
    """Reads the plan owner's baseline forecast and outcome history without recording a snapshot."""

    def __init__(self, forecasts: DeliveryForecasts, history: PlanOutcomeHistory, owners: PlanOwners) -> None:
        self.forecasts, self.history, self.owners = forecasts, history, owners

    def forecast(self, plan: Plan) -> dict | None:
        return self.analysis(plan)[0]

    def outcome_history(self, plan: Plan) -> dict | None:
        return self.analysis(plan)[1]

    def composition_feedback(self, plan: Plan, task_id: int) -> str:
        evidence = self.composition_evidence(plan, task_id)
        lines = ["Ranges come from past delivered tasks; the learned ranges are advice only."]
        examples = evidence["examples"]
        if examples:
            lines.append(f"{len(examples)} similar finished {self.plural(len(examples), 'task')}:")
            lines.extend(self.example_line(row) for row in examples)
        else:
            lines.append("No similar finished tasks yet.")
        lines.extend(self.duration_lines(evidence["duration"]))
        lines.extend(self.bias_lines(evidence["calibration"]))
        return "\n".join(lines)

    def composition_evidence(self, plan: Plan, task_id: int) -> dict:
        owner = self.owner(plan)
        if owner is None:
            return {"examples": [], "duration": {"status": "not_enough_history", "stages": {}},
                    "calibration": {"sizing_bias": {}}}
        return self.forecasts.composition_evidence(plan.row_id, task_id, owner)

    @classmethod
    def example_line(cls, example: dict) -> str:
        return (f"Task {example['task_id']} · original estimate {example['original_size_points']} points · "
                f"final size {example['execution_size_points']} points · work took "
                f"{cls.duration(example['execution_seconds'])} · delivery took "
                f"{cls.duration(example['delivery_seconds'])} after work finished")

    @staticmethod
    def duration_lines(duration: dict) -> list[str]:
        stages = duration.get("stages", {})
        labels = {"execution_cycle": "work", "delivery_delay": "time from finishing work to delivery"}
        size = duration.get("size_points")
        return [f"For {size} points, {labels[name]} is estimated at {EstimatesForecast.duration(row['p50_seconds'])} "
                f"for a typical task and up to {EstimatesForecast.duration(row['p85_seconds'])} in the wider range."
                for name, row in stages.items() if row.get("status") == "forecast"]

    @staticmethod
    def bias_lines(calibration: dict) -> list[str]:
        minimum = calibration.get("minimum_calibration_samples")
        measured = [(name, row) for name, row in calibration.get("sizing_bias", {}).items()
                    if row.get("status") == "measured"]
        labels = {"execution_cycle": "work time", "delivery_delay": "delivery time"}
        if minimum is None and not measured:
            return ["There are no finished task times to compare with estimates yet."]
        stages = calibration.get("sizing_bias", {})
        lines = [f"Across {row['observed']} finished tasks, {labels.get(name, name)} took "
                 f"{row['actual_to_predicted_p50_ratio']:.2f} times as long as estimated."
                 for name, row in measured]
        if minimum is not None:
            lines.extend(f"Not enough finished tasks to compare {labels.get(name, name)} estimates "
                         f"({row.get('observed', 0)} of {minimum})."
                         for name, row in stages.items() if row.get("status") != "measured")
        if lines:
            return lines
        if not stages:
            return [f"Not enough finished tasks to measure how sizes compare (0 of {minimum})."]
        return ["There are no finished task times to compare with estimates yet."]

    @staticmethod
    def duration(seconds: float) -> str:
        if seconds >= 86400:
            return f"{seconds / 86400:.1f} days"
        if seconds >= 3600:
            return f"{seconds / 3600:.1f} hours"
        return f"{seconds / 60:.0f} minutes"

    @staticmethod
    def plural(count: int, word: str) -> str:
        return word if count == 1 else word + "s"

    def analysis(self, plan: Plan) -> tuple[dict | None, dict | None]:
        actor = self.owner(plan)
        if actor is None:
            return None, None
        history = self.history.read(plan.row_id, actor)
        return self.forecasts.estimate_from_history(plan, history, actor), history

    @staticmethod
    def basis(forecast: dict | None) -> str:
        if forecast is None:
            return "Not enough past delivery results; the plan has no owner, so no finish date or sprint chance can be estimated."
        if forecast["status"] != "forecast":
            missing = ", ".join(forecast["missing_evidence"])
            return f"Not enough past delivery results; missing {missing}; no finish date or sprint chance can be estimated."
        return (f"Past sprint results: {forecast['delivered_outcomes']} delivered plans and "
                f"{forecast['observed_capacity_days']} days with capacity information; typical finish {forecast['p50']}, "
                f"wider finish {forecast['p85']}, chance by this sprint's end {forecast['probability_this_sprint']}%.")

    def owner(self, plan: Plan) -> Actor | None:
        owner = self.owners.number(plan)
        return Actor.user(owner) if owner else None
