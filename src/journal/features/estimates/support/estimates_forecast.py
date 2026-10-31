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
        lines = ["Empirical baseline remains selected; learned duration ranges are advisory."]
        examples = evidence["examples"]
        if examples:
            lines.append(f"{len(examples)} comparable delivered {self.plural(len(examples), 'example')} in the same authorized cohort:")
            lines.extend(self.example_line(row) for row in examples)
        else:
            lines.append("No comparable delivered examples for this authorized cohort.")
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
        return (f"task {example['task_id']} · original size {example['original_size_points']} story points · "
                f"execution size {example['execution_size_points']} story points · "
                f"actual execution {cls.duration(example['execution_seconds'])} · "
                f"actual delivery delay {cls.duration(example['delivery_seconds'])}")

    @staticmethod
    def duration_lines(duration: dict) -> list[str]:
        stages = duration.get("stages", {})
        labels = {"execution_cycle": "execution", "delivery_delay": "delivery"}
        size = duration.get("size_points")
        return [f"Learned {labels[name]} range for {size} story points: P50 {EstimatesForecast.duration(row['p50_seconds'])}, "
                f"P85 {EstimatesForecast.duration(row['p85_seconds'])}."
                for name, row in stages.items() if row.get("status") == "forecast"]

    @staticmethod
    def bias_lines(calibration: dict) -> list[str]:
        minimum = calibration.get("minimum_calibration_samples")
        measured = [(name, row) for name, row in calibration.get("sizing_bias", {}).items()
                    if row.get("status") == "measured"]
        if measured:
            return [f"Aggregate sizing-bias summary for {name.replace('_', ' ')}: actual durations were "
                    f"{row['actual_to_predicted_p50_ratio']:.2f}× predicted P50 across {row['observed']} held-out actuals."
                    for name, row in measured]
        if minimum is None:
            return ["No aggregate sizing-bias score; there is no owner-scoped outcome history."]
        observed = max((row.get("observed", 0) for row in calibration.get("sizing_bias", {}).values()), default=0)
        return [f"No aggregate sizing-bias score: {observed} held-out actuals; need {minimum} for a score."]

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
            return "not enough history; the plan has no recorded owner, so no finish date or sprint probability can be estimated"
        if forecast["status"] != "forecast":
            missing = ", ".join(forecast["missing_evidence"])
            return f"not enough history; missing {missing}; no finish date or sprint probability can be estimated"
        return (f"baseline {forecast['method_version']} from {forecast['delivered_outcomes']} comparable accepted deliveries "
                f"and {forecast['observed_capacity_days']} observed capacity days; P50 {forecast['p50']}, "
                f"P85 {forecast['p85']}, this sprint {forecast['probability_this_sprint']}%")

    def owner(self, plan: Plan) -> Actor | None:
        owner = self.owners.number(plan)
        return Actor.user(owner) if owner else None
