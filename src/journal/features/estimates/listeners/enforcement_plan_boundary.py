from journal.events.listener import Listener
from journal.events.rows.setting_changed import SettingChanged
from journal.features.estimates.estimates_options import ENFORCEMENT_PLAN_BOUNDARY, EstimatesOptions
from journal.repositories.plans import Plans
from journal.repositories.setting_rows import SettingRows
from journal.support.actor import Actor


class EnforcementPlanBoundary(Listener[SettingChanged]):
    """Records which plans already existed when estimates enforcement was enabled."""

    def __init__(self, plans: Plans, settings: SettingRows) -> None:
        self.plans, self.settings = plans, settings

    def handle(self, event: SettingChanged) -> None:
        if event.setting != EstimatesOptions.MODE.key or self.settings.option(EstimatesOptions.MODE) != "enforce":
            return
        latest = self.plans.maximum_globally(self.plans.query(), "id", 0)
        self.settings.set(ENFORCEMENT_PLAN_BOUNDARY, latest, Actor.system())
