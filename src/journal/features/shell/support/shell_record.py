import shutil
from dataclasses import asdict
from pathlib import Path

from journal.engine.command_events import CommandEvents
from journal.events.announcer import Announcer
from journal.features.git.support.git_facts import GitFacts
from journal.features.shell.support.changed_file import ChangedFile
from journal.features.shell.support.activity_label import ActivityLabel
from journal.features.shell.support.output_log import OutputLog
from journal.features.shell.support.output_views import OutputViews
from journal.models.entry import Entry
from journal.repositories.agents import Agents
from journal.models.agent import Agent
from journal.repositories.command_outputs import CommandOutputs
from journal.repositories.entries import Entries
from journal.repositories.setting_rows import SettingRows
from journal.repositories.scope import Scope
from journal.support.caller import Caller
from journal.support.part import Part
from journal.engine.states_catalogue import StatesCatalogue
from journal.models.command_output import CommandOutput
from journal.features.shell.shell_options import ShellOptions
from journal.support.time_source import TimeSource

TAIL_CHARACTERS = 2000
PART_START, PART_END, MOVED, ENDED = "running", "ran", "background", "ended"


class ShellRecord:
    """What the runner records as a chain runs: each of the agent's own parts as it starts and ends with its status, time, output tail and the files it changed (the edits feature stores the changed lines from the tool's end), the move to the background with its card and event, the end of a moved chain, and whether an ended output is stored under its number or discarded."""

    def __init__(self, entries: Entries, log: OutputLog, outputs: CommandOutputs, views: OutputViews, events: CommandEvents, agents: Agents, settings: SettingRows, scope: Scope, states: StatesCatalogue, announcer: Announcer, time_source: TimeSource, labels: ActivityLabel) -> None:
        self.labels = labels
        self.time_source = time_source
        self.announcer = announcer
        self.entries, self.log, self.outputs, self.views = entries, log, outputs, views
        self.events, self.agents, self.settings, self.scope, self.states = events, agents, settings, scope, states

    def start(self, chain: str, command: str, folder: Path, caller: Caller, ran_in: str = "") -> int:
        return self.log.start(chain, command, folder, caller, ran_in).row_id

    def started(self, chain: str, part: str, caller: Caller) -> None:
        self.record(caller, PART_START, {"chain": chain, "part": part, "doing": self.labels.build(part)})

    def finish_part(self, chain: str, part: str, status: int, seconds: float, output: str, changed: list[ChangedFile], caller: Caller) -> None:
        self.record(caller, PART_END, {"chain": chain, "part": part, "doing": self.labels.build(part), "status": status, "seconds": seconds, "output": output[-TAIL_CHARACTERS:], "changed": [asdict(c) for c in changed]})
        if status == 0 and part.startswith("git "):
            self.git_event(chain, part, caller)

    def git_event(self, chain: str, part: str, caller: Caller) -> None:
        rows = self.outputs.matching(chain=chain)
        event = GitFacts.event(part, Path(rows[0].ran_in), self.scope.id, caller.session) if rows and rows[0].ran_in else None
        if event is not None:
            self.announcer.announce(event)

    def moved(self, chain: str, part: str, folder: Path, caller: Caller) -> int:
        self.record(caller, MOVED, {"chain": chain, "part": part, "doing": self.labels.build(part), "file": str(folder)})
        output = self.outputs.save(self.outputs.chain_output(chain).backgrounded(), caller.actor)
        if caller.session is not None:
            self.events.moved(output, caller.session)
        return output.row_id

    def ended(self, chain: str, status: int, folder: Path, last: str, caller: Caller) -> None:
        self.record(caller, ENDED, {"chain": chain, "status": status, "file": str(folder), "last": last})
        agent = self.agents.current()
        output, moment = self.outputs.chain_output(chain), self.time_source.moment().timestamp()
        summary = self.views.ended_summary(output.with_(ended=True, status=status))
        finish = output.wait_end(status, moment, summary) if agent is not None and self.wait_covers(output, agent) else output.ended_with(status, moment, summary)
        saved = self.outputs.save(finish, caller.actor)
        if agent is not None:
            self.events.ended(saved, agent)

    def foreground_end(self, chain: str, status: int, caller: Caller) -> None:
        output = self.outputs.chain_output(chain)
        self.outputs.save(output.ended_with(status, self.time_source.moment().timestamp()).unwatched(), caller.actor)

    def wait_covers(self, output: CommandOutput, agent: Agent) -> bool:
        top = self.states.stack(agent).top() if agent.session == output.session else None
        return top is not None and f"{output.table()}:{output.id}" in top.wait_description()[1].split(",")

    def is_stored(self, chain: str, line: str, size: int, cut: bool) -> bool:
        return size >= self.settings.integer(ShellOptions.SHORT) or bool(Part(line).pipe_positions(0)) or cut

    def delete_output(self, chain: str, caller: Caller) -> None:
        output = self.outputs.chain_output(chain)
        self.outputs.delete(output, caller.actor)
        shutil.rmtree(output.folder, ignore_errors=True)

    def record(self, caller: Caller, type_name: str, data: dict) -> None:
        self.entries.save(Entry(environment_id=self.scope.id, entry_type=type_name, actor=caller.actor, data={**data, "session": caller.session, "time": self.time_source.moment().timestamp()}), caller.actor)
