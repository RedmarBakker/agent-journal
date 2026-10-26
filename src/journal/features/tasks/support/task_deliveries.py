from journal.features.tasks.support.one_plan_delivery import OnePlanDelivery
from journal.features.tasks.support.round_robin_delivery import RoundRobinDelivery
from journal.features.tasks.support.task_delivery import TaskDelivery
from journal.features.workers.workers_options import WorkersOptions
from journal.repositories.setting_rows import SettingRows


class TaskDeliveries:
    """The delivery of the work mode the user set: the orchestrator's round robin, the one-plan delivery of every other mode."""

    def __init__(self, settings: SettingRows, single: OnePlanDelivery, round_robin: RoundRobinDelivery) -> None:
        self.settings, self.single, self.round_robin = settings, single, round_robin

    def current(self) -> TaskDelivery:
        return {"orchestrator": self.round_robin}.get(self.settings.option(WorkersOptions.MODE), self.single)
