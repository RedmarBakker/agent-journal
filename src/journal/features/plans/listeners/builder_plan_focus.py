from journal.events.listener import Listener
from journal.events.rows.setting_changed import SettingChanged
from journal.features.plans.support.plan_focus import PlanFocus
from journal.features.workers.workers_options import MODE_SETTINGS
from journal.repositories.environments import Environments
from journal.repositories.scope import Scope
from journal.support.actor import Actor


class BuilderPlanFocus(Listener[SettingChanged]):
    """A switch of the work mode, or of Plan agents instead of work modes, out of the orchestrator keeps one started plan in each environment, the one furthest along, and pauses the rest; the mode is the project's, so every environment is looked at."""

    def __init__(self, focus: PlanFocus, environments: Environments, scope: Scope) -> None:
        self.focus, self.environments, self.scope = focus, environments, scope

    def handle(self, event: SettingChanged) -> None:
        if event.setting not in MODE_SETTINGS:
            return
        for environment in self.environments.all():
            with self.scope.environment(environment.row_id):
                self.focus.keep_furthest(Actor.system())
