from journal.features.workers.support.load_item import LoadItem
from journal.features.workers.support.load_items import LoadItems
from journal.models.support.agent_load import AgentLoad
from journal.features.workers.support.load_series import HALF_LIVES, LoadSeries
from journal.features.workers.support.place_scaling import PlaceScaling
from journal.features.plans.support.plan_agent_coordinator import PlanAgentCoordinator
from journal.features.workers.workers_options import WorkersOptions
from journal.models.agent import Agent
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks

WORKER_REF = "workers:"


class LoadMeter:
    """Measures the main agent's worker and message queues, and adjusts worker and subagent limits while it coordinates Plan agents."""

    def __init__(self, agents: Agents, items: LoadItems, settings: SettingRows, tasks: Tasks, coordinator: PlanAgentCoordinator) -> None:
        self.agents, self.items, self.settings, self.tasks, self.coordinator = agents, items, settings, tasks, coordinator

    def series(self) -> LoadSeries:
        window, half_life = self.settings.decimal(WorkersOptions.WORKLOAD_WINDOW_MINUTES), self.settings.decimal(WorkersOptions.WORKLOAD_SMOOTHING_MINUTES)
        return LoadSeries(window, half_life, self.settings.decimal(WorkersOptions.PLACE_OPENING_RATIO), self.settings.decimal(WorkersOptions.PLACE_CLOSING_RATIO))

    def queues(self, items: list[LoadItem], time: float) -> tuple[AgentLoad, AgentLoad]:
        work_series, message_series = self.series(), self.series()
        work_items, message_items = [item for item in items if item.ref.startswith(WORKER_REF)], [item for item in items if not item.ref.startswith(WORKER_REF)]
        return work_series.measured(work_items, time), message_series.measured(message_items, time)

    def measure(self, agent: Agent, time: float) -> None:
        work_series = self.series()
        items = self.items.read(time - (work_series.window_minutes + HALF_LIVES * work_series.half_life_minutes) * 60)
        work_queue, message_queue = self.queues(items, time)
        self.agents.rewritten(agent, Actor.system(), lambda current: self.measured(current, work_queue, message_queue, time))

    def measured(self, agent: Agent, work_queue: AgentLoad, message_queue: AgentLoad, time: float) -> Agent:
        measured = agent.queue_loads_measured(work_queue, message_queue)
        return self.scaled(measured, time) if self.coordinator.is_coordinator() else measured

    def scaled(self, agent: Agent, moment: float) -> Agent:
        fewest, ceiling = (str(self.settings.option(option)).strip() for option in (WorkersOptions.MIN_PLACES, WorkersOptions.MAX_PLACES))
        if not fewest.isdigit() or not ceiling.isdigit():
            return agent
        scaling = PlaceScaling(self.settings.decimal(WorkersOptions.PLACE_OPENING_MINUTES), self.settings.decimal(WorkersOptions.PLACE_CLOSING_MINUTES), int(fewest), int(ceiling))
        places = self.settings.integer(WorkersOptions.WORKER_LIMIT)
        if scaling.opens(agent.work_queue, places, moment):
            self.placed(1)
            return agent.place_opened(places + 1, moment)
        if scaling.closes(agent.work_queue, places, bool(self.tasks.worker_holdings()), moment):
            self.placed(-1)
            return agent.place_closed(places - 1, moment)
        return agent

    def placed(self, step: int) -> None:
        for option in (WorkersOptions.WORKER_LIMIT, WorkersOptions.SUBAGENT_LIMIT):
            self.settings.set(option.key, max(self.settings.integer(option) + step, 1), Actor.system())
