from dataclasses import asdict

from journal.features.workers.support.band_rules import BandRules
from journal.features.workers.support.load_item import LoadItem
from journal.features.workers.support.load_items import LoadItems
from journal.models.support.agent_load import AgentLoad
from journal.features.workers.support.load_series import HALF_LIVES, LoadSeries
from journal.features.workers.support.mode_measures import ModeMeasures
from journal.features.workers.support.place_scaling import PlaceScaling
from journal.features.workers.support.work_mode import WorkMode
from journal.features.workers.workers_options import WorkersOptions
from journal.models.agent import Agent
from journal.models.entry import Entry
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor

LOAD_INPUTS = "load_inputs"
WORKER_REF = "workers:"
LARGEST_ITEM_COUNT = 400


class LoadMeter:
    """Measures the main agent's two queues from what waited on it, the workers' items against the mode's line (the builder's ceiling, else the scale-up level) and the user's messages against the scale-up level, and keeps both on its row for the work mode it is in, with the band the worker queue stands in for that mode and the state of each of the mode's measures, and keeps the inputs of each measure as an entry, the newest items at most, so the load can be measured again from them; in the orchestrator's mode the workers out at once, with the subagents beside them, move by one place when the load has held over or under its level long enough, within the user's floor and ceiling."""

    def __init__(self, agents: Agents, items: LoadItems, settings: SettingRows, tasks: Tasks, entries: Entries, bands: BandRules, measures: ModeMeasures, work_mode: WorkMode) -> None:
        self.agents, self.items, self.settings, self.tasks, self.entries, self.bands, self.measures, self.work_mode = agents, items, settings, tasks, entries, bands, measures, work_mode

    def series(self, busy_at: float) -> LoadSeries:
        window, half_life = self.settings.decimal(WorkersOptions.WORKLOAD_WINDOW_MINUTES), self.settings.decimal(WorkersOptions.WORKLOAD_SMOOTHING_MINUTES)
        return LoadSeries(window, half_life, busy_at, self.settings.decimal(WorkersOptions.PLACE_CLOSING_RATIO))

    def work_level(self) -> float:
        option = WorkersOptions.PLACE_OPENING_RATIO if self.work_mode.delegates_work() else WorkersOptions.BUILDER_CEILING
        return self.settings.decimal(option)

    def queues(self, items: list[LoadItem], dispatches: list[float], time: float) -> tuple[AgentLoad, AgentLoad]:
        work_series, message_series = self.series(self.work_level()), self.series(self.settings.decimal(WorkersOptions.PLACE_OPENING_RATIO))
        work_items, message_items = [item for item in items if item.ref.startswith(WORKER_REF)], [item for item in items if not item.ref.startswith(WORKER_REF)]
        return work_series.measured(work_items, dispatches, time), message_series.measured(message_items, [], time)

    def measure(self, agent: Agent, time: float) -> None:
        work_series = self.series(self.work_level())
        items, dispatches = self.items.read(time - (work_series.window_minutes + HALF_LIVES * work_series.half_life_minutes) * 60)
        work_queue, message_queue = self.queues(items, dispatches, time)
        self.entries.save(Entry(environment_id=agent.environment_id, entry_type=LOAD_INPUTS, actor=Actor.agent(agent.session), data={"time": time, "dispatches": dispatches, "items": [asdict(item) for item in items[-LARGEST_ITEM_COUNT:]]}), Actor.system())
        self.agents.rewritten(agent, Actor.system(), lambda current: self.measured(current, work_queue, message_queue, items, time))

    def measured(self, agent: Agent, work_queue: AgentLoad, message_queue: AgentLoad, items: list[LoadItem], time: float) -> Agent:
        mode = str(self.settings.option(WorkersOptions.MODE))
        band = self.bands.band(agent, mode, work_queue, [item for item in items if item.ref.startswith(WORKER_REF)], time)
        queued = agent.queues_measured(work_queue, message_queue).band_moved(band, time)
        measured = queued.measures_worked(self.measures.worked(queued, mode, time))
        return self.scaled(measured, time) if self.work_mode.delegates_work() else measured

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
