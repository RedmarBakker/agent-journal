from datetime import datetime, timezone
from journal.features.environment_seed import EnvironmentSeed
from journal.support.actor import Actor
from journal.repositories.environments import Environments
from journal.repositories.plans import Plans
from journal.repositories.scope import Scope
from journal.support.time_source import TimeSource


class ClosedPlans(EnvironmentSeed):
    """At boot, a started plan whose every task is closed is done: its tasks are the truth of it, whoever closed them; a paused or a blocked task is still open."""

    def __init__(self, plans: Plans, environments: Environments, scope: Scope, time_source: TimeSource) -> None:
        self.time_source = time_source
        super().__init__(environments, scope)
        self.plans = plans

    def run_scoped(self) -> None:
        for plan in self.plans.complete_plans():
            self.plans.save(plan.finished(self.time_source.moment().timestamp()), Actor.system())
