from dataclasses import replace

from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent_listener import AgentListener
from journal.features.workers.support.load_items import LoadItems
from journal.features.workers.support.load_series import HALF_LIVES, LoadSeries
from journal.features.workers.support.place_scaling import PlaceScaling
from journal.features.workers.workers_options import WorkersOptions
from journal.models.agent import Agent
from journal.models.agent_role import AgentRole
from journal.repositories.agents import Agents
from journal.repositories.setting_rows import SettingRows
from journal.repositories.tasks import Tasks
from journal.support.actor import Actor


class LoadRecord(AgentListener[ToolFinished]):
    """After each tool use of the main agent, its load is measured from what waited on it and kept on its row for the work mode it is in, each mode keeping its own figure; in the orchestrator's, the workers out at once, with the subagents beside them, move by one place when the load has held over or under its level long enough, within the user's floor and ceiling; with no floor or ceiling set, the load measures and changes no place."""

    def __init__(self, agents: Agents, items: LoadItems, settings: SettingRows, tasks: Tasks) -> None:
        self.agents, self.items, self.settings, self.tasks = agents, items, settings, tasks

    def handle(self, event: ToolFinished) -> None:
        if event.subagent:
            return
        rows = self.agents.session_rows(event.session)
        if not rows or rows[0].role != AgentRole.MAIN:
            return
        window, half_life = self.settings.decimal(WorkersOptions.LOAD_WINDOW), self.settings.decimal(WorkersOptions.LOAD_HALF_LIFE)
        series = LoadSeries(window, half_life, self.settings.decimal(WorkersOptions.SCALE_UP_AT), self.settings.decimal(WorkersOptions.SCALE_DOWN_AT))
        items, dispatches = self.items.read(event.time - (window + HALF_LIVES * half_life) * 60)
        ratios = replace(series.measured(items, dispatches, event.time), over_full_minutes=self.settings.decimal(WorkersOptions.RECOVERY_FULL), over_zero_minutes=self.settings.decimal(WorkersOptions.RECOVERY_ZERO))
        orchestrating = self.settings.option(WorkersOptions.MODE) == "orchestrator"
        self.agents.rewritten(rows[0], Actor.system(), lambda current: self.scaled(current.load_measured(ratios), event.time) if orchestrating else current.load_measured(ratios))

    def scaled(self, agent: Agent, now: float) -> Agent:
        floor, ceiling = (str(self.settings.option(option)).strip() for option in (WorkersOptions.PLACE_FLOOR, WorkersOptions.PLACE_CEILING))
        if not floor.isdigit() or not ceiling.isdigit():
            return agent
        scaling = PlaceScaling(self.settings.decimal(WorkersOptions.SCALE_UP_DWELL), self.settings.decimal(WorkersOptions.SCALE_DOWN_DWELL), int(floor), int(ceiling))
        places = self.settings.integer(WorkersOptions.WORKER_LIMIT)
        if scaling.opens(agent.load, places, now):
            self.placed(1)
            return agent.place_opened(places + 1, now)
        if scaling.closes(agent.load, places, bool(self.tasks.worker_holdings()), now):
            self.placed(-1)
            return agent.place_closed(places - 1, now)
        return agent

    def placed(self, step: int) -> None:
        for option in (WorkersOptions.WORKER_LIMIT, WorkersOptions.SUBAGENT_LIMIT):
            self.settings.set(option.key, max(self.settings.integer(option) + step, 1), Actor.system())
