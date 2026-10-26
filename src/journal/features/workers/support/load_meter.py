from dataclasses import asdict, replace

from journal.features.workers.support.load_items import LoadItems
from journal.features.workers.support.load_series import HALF_LIVES, LoadSeries
from journal.features.workers.support.place_scaling import PlaceScaling
from journal.features.workers.workers_options import WorkersOptions
from journal.models.agent import Agent
from journal.models.entry import Entry
from journal.repositories.agents import Agents
from journal.repositories.entries import Entries
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor

LOAD_INPUTS = "load_inputs"
LOAD_INPUT_ITEM_COUNT = 400


class LoadMeter:
    """Measures the main agent's load from what waited on it and keeps it on its row for the work mode it is in, and keeps the inputs of each measure as an entry, the newest items at most, so the load can be measured again from them; in the orchestrator's mode the workers out at once, with the subagents beside them, move by one place when the load has held over or under its level long enough, within the user's floor and ceiling."""

    def __init__(self, agents: Agents, items: LoadItems, settings: SettingRows, tasks: Tasks, entries: Entries) -> None:
        self.agents, self.items, self.settings, self.tasks, self.entries = agents, items, settings, tasks, entries

    def series(self) -> LoadSeries:
        window, half_life = self.settings.decimal(WorkersOptions.WORKLOAD_WINDOW_MINUTES), self.settings.decimal(WorkersOptions.WORKLOAD_SMOOTHING_MINUTES)
        return LoadSeries(window, half_life, self.settings.decimal(WorkersOptions.PLACE_OPENING_RATIO), self.settings.decimal(WorkersOptions.PLACE_CLOSING_RATIO))

    def measure(self, agent: Agent, time: float) -> None:
        series = self.series()
        items, dispatches = self.items.read(time - (series.window_minutes + HALF_LIVES * series.half_life_minutes) * 60)
        ratios = replace(series.measured(items, dispatches, time), over_full_minutes=self.settings.decimal(WorkersOptions.RECOVERY_FULL), over_zero_minutes=self.settings.decimal(WorkersOptions.RECOVERY_ZERO))
        self.entries.save(Entry(environment_id=agent.environment_id, kind=LOAD_INPUTS, actor=Actor.agent(agent.session), data={"time": time, "dispatches": dispatches, "items": [asdict(item) for item in items[-LOAD_INPUT_ITEM_COUNT:]]}), Actor.system())
        is_orchestrator = self.settings.option(WorkersOptions.MODE) == "orchestrator"
        self.agents.rewritten(agent, Actor.system(), lambda current: self.scaled(current.load_measured(ratios), time) if is_orchestrator else current.load_measured(ratios))

    def scaled(self, agent: Agent, moment: float) -> Agent:
        fewest, ceiling = (str(self.settings.option(option)).strip() for option in (WorkersOptions.MIN_PLACES, WorkersOptions.MAX_PLACES))
        if not fewest.isdigit() or not ceiling.isdigit():
            return agent
        scaling = PlaceScaling(self.settings.decimal(WorkersOptions.PLACE_OPENING_MINUTES), self.settings.decimal(WorkersOptions.PLACE_CLOSING_MINUTES), int(fewest), int(ceiling))
        places = self.settings.integer(WorkersOptions.WORKER_LIMIT)
        if scaling.opens(agent.load, places, moment):
            self.placed(1)
            return agent.place_opened(places + 1, moment)
        if scaling.closes(agent.load, places, bool(self.tasks.worker_holdings()), moment):
            self.placed(-1)
            return agent.place_closed(places - 1, moment)
        return agent

    def placed(self, step: int) -> None:
        for option in (WorkersOptions.WORKER_LIMIT, WorkersOptions.SUBAGENT_LIMIT):
            self.settings.set(option.key, max(self.settings.integer(option) + step, 1), Actor.system())
