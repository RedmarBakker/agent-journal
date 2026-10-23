from journal.events.listener import Listener
from journal.events.models.created import Created
from journal.features.plans.support.plan_testing import NONE_TITLE, PlanTesting
from journal.models.plan import Plan
from journal.repositories.setting_rows import SettingRows


class PlanTestingDefault(Listener[Created]):
    """A new plan follows the testing template the settings name for new plans, unless they name none."""

    def __init__(self, testing: PlanTesting, settings: SettingRows) -> None:
        self.testing, self.settings = testing, settings

    def handle(self, event: Created) -> None:
        from journal.features.plans.feature import Plans
        title = str(self.settings.option(Plans.TESTING))
        if not isinstance(event.model, Plan) or title == NONE_TITLE:
            return
        self.testing.choose(event.model, title, event.actor)
