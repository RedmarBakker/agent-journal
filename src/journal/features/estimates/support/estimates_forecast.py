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
