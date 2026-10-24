import queue
import threading
import time
from dataclasses import replace
from typing import Iterator

from journal.engine.support.session_agents import SessionAgents
from journal.engine.nudger import Nudger
from journal.engine.nudge import Nudge
from journal.repositories.entries import Entries
from journal.supervisor_link import SupervisorLink
from journal.support.command_shape import CommandShape
from journal.features.shell.support.reader import Reader
from journal.features.shell.support.reader_guess import ReaderGuess
from journal.features.shell.support.readers import Readers
from journal.config import Config
from journal.features.aliases.support.alias_lines import AliasLines
from journal.features.shell.support.watch_suggestions import WatchSuggestions
from journal.features.shell.support.time_limit_wrapper import TimeLimitWrapper
from journal.models.alias import Alias
from journal.repositories.command_outputs import CommandOutputs
from journal.features.shell.support.activity_label import LONG_RUNS, ActivityLabel
from journal.features.shell.support.cap import Cap
from journal.features.shell.support.chain_worker import ChainWorker
from journal.features.shell.support.foreground_limit import ForegroundLimit
from journal.features.shell.support.output_cap import OutputCap
from journal.features.shell.support.output_files import OutputFiles
from journal.features.shell.support.output_show import OutputShow
from journal.features.shell.support.shell_record import ShellRecord
from journal.features.shell.support.shell_request import ShellRequest
from journal.support.chain import Chain
from journal.repositories.scope import Scope
from journal.support.caller import Caller
from journal.support.stage_times import StageTimes
from journal.features.faults.support.slow_requests import SlowRequests
from journal.features.shell.shell_nudges import ShellNudges
from journal.models.command_output import CommandOutput
from journal.features.shell.support.output_process_card import OutputProcessCard

EXIT = "__journal_exit"
SHELL = "SHELL"
SETUP_ROUTE = "/shell/setup"
TICK_SECONDS = 0.2
LIMIT_READ_TICKS = 10
VARIED_RUNS = 3


class ShellRunner:
    """Runs one shell line for the shim and streams back what the agent sees: the line is split into its parts, the journal's own setup of the line timed and reported like a slow request when it runs past its budget, run in the user's shell by the worker, each part shown as its status lands and the cap says, the chain moved to the background past the foreground limit with a line naming its output, and an ended output stored under its number or forgotten. A read or write of the project's code streams straight through, nothing stored. The stream is read after the request has left its scope, so the environment comes along and is named again for every read and write; the exit line starts on a line of its own."""

    def __init__(self, config: Config, caps: OutputCap, limits: ForegroundLimit, worker: ChainWorker, record: ShellRecord, scope: Scope, suggestions: WatchSuggestions, guess: ReaderGuess, aliases: AliasLines, outputs: CommandOutputs, readers: Readers, supervisor: SupervisorLink, entries: Entries, stages: StageTimes, slow: SlowRequests, nudger: Nudger, sessions: SessionAgents, card: OutputProcessCard) -> None:
        self.nudger, self.sessions = nudger, sessions
        self.config, self.caps, self.limits, self.worker, self.record, self.scope, self.suggestions = config, caps, limits, worker, record, scope, suggestions
        self.aliases, self.outputs, self.readers, self.supervisor, self.entries = aliases, outputs, readers, supervisor, entries
        self.stages, self.slow, self.guess, self.card = stages, slow, guess, card
        self.wrappers_told: set[str] = set()

    def run(self, posted: ShellRequest, caller: Caller, environment: int) -> Iterator[bytes]:
        began = time.perf_counter()
        request = replace(posted, line=self.aliases.expanded(posted.line))
        with self.scope.environment(environment), self.stages.timed("shell setup"):
            cap = self.caps.build(request.line)
            folder = OutputFiles(self.config.home / "runtime" / "outputs" / f"{time.time_ns()}-{threading.get_ident()}")
            folder.split(request.line, Chain.parts(request.line))
            if not cap.is_whole() and not cap.is_direct():
                folder.numbered(self.record.start(folder.folder.name, "\n".join(Chain.self_parts(posted.line)), folder.folder, caller))
        self.slow.measured(SHELL, SETUP_ROUTE, (time.perf_counter() - began) * 1000)
        output_text: queue.Queue = queue.Queue()
        ended: list[int] = []
        faults: list[Exception] = []
        thread = threading.Thread(target=lambda: self.worked(folder, request, caller, cap.is_direct(), output_text, ended, faults, environment), name="shell-chain", daemon=True)
        thread.start()
        last = b"\n"
        with self.scope.environment(environment):
            for block in (self.direct(output_text, thread, faults) if cap.is_direct() else self.foreground(folder, request, caller, cap, environment, faults)):
                last = block[-1:] or last
                yield block
        if cap.is_direct() or folder.is_finished():
            self.closed(folder, request, caller, cap)
            yield f"{'' if last == b'\n' else chr(10)}{EXIT} {ended[0] if ended else 0}\n".encode()

    def worked(self, folder: OutputFiles, request: ShellRequest, caller: Caller, direct: bool, output_text: queue.Queue, ended: list[int], faults: list[Exception], environment: int) -> None:
        with self.scope.environment(environment):
            try:
                ended.append(self.worker.run(folder, request, caller, direct, output_text.put))
            except Exception as fault:
                faults.append(fault)
        output_text.put(None)

    @staticmethod
    def direct(output_text: queue.Queue, thread: threading.Thread, faults: list[Exception]) -> Iterator[bytes]:
        while True:
            block = output_text.get()
            if block is None:
                thread.join()
                raise_first(faults)
                return
            yield block

    def foreground(self, folder: OutputFiles, request: ShellRequest, caller: Caller, cap: Cap, environment: int, faults: list[Exception]) -> Iterator[bytes]:
        display = OutputShow(folder, cap)
        limit = self.limits.build(request.line, caller.environment, caller.session)
        reader = self.readers.reading(request.line) if limit > 0 else None
        background = self.aliases.background_part(request.line)
        immediate = bool(background) or (reader is not None and self.is_long_run(reader.commands.read_part(request.line), limit))
        if limit > 0 and not immediate and not cap.is_whole():
            self.start_card(folder, request.line, reader, caller)
        shown, tick, began = 0, 0, time.monotonic()
        while True:
            raise_first(faults)
            while folder.has_ended(shown):
                yield display.build(shown).encode()
                shown += 1
            if folder.is_finished():
                yield self.send_notes(caller, environment, display.notes).encode()
                return
            if limit > 0 and (immediate or time.monotonic() - began >= limit):
                folder.moved()
                part = reader.commands.read_part(request.line) if reader is not None else background or folder.part_text(shown)
                number = self.record.moved(folder.folder.name, part, folder.folder, caller)
                alias = self.aliases.running(part)
                notes = self.send_notes(caller, environment, [*display.notes, ShellNudges.BACKGROUND_MOVE.create(n=number, file=str(folder.folder)), *self.watch_lines(number, part, alias, reader, caller)])
                yield f"{notes}{EXIT} 0\n".encode()
                return
            time.sleep(TICK_SECONDS)
            tick += 1
            if tick % LIMIT_READ_TICKS == 0:
                limit = self.limits.build(request.line, caller.environment, caller.session)

    # a run whose reader is known shows its card in the chat as it starts, before any move to the background
    def start_card(self, folder: OutputFiles, line: str, reader: Reader | None, caller: Caller) -> None:
        reader_name = self.known_reader(self.aliases.line_alias(line), reader)
        if reader_name:
            self.outputs.watch(self.outputs.chain_output(folder.folder.name), reader_name, "", caller.actor)

    @staticmethod
    def known_reader(alias: Alias | None, reader: Reader | None) -> str:
        if alias is not None:
            return alias.reader
        return reader.name if reader is not None else ""

    # a run known to take long moves to the background at once: a test run or a build, or a command whose last run went past the limit;
    # any other runs in the foreground until it passes the limit
    def is_long_run(self, part: str, limit: int) -> bool:
        last = self.outputs.last_run(part)
        return ActivityLabel.build(part) in LONG_RUNS or (last is not None and last.run_seconds() >= limit)

    def send_notes(self, caller: Caller, environment: int, notes: list[Nudge]) -> str:
        if caller.session is None:
            return ""
        agent = self.sessions.agent(caller.session, environment)
        lines = [line for note in notes if (line := self.nudger.deliver(agent, note))]
        if caller.worker_number is not None or caller.subagent:
            return "".join(f"[journal] {line}\n" for line in lines)
        for line in lines:
            self.supervisor.remark(environment, line)
        return ""

    def watch_lines(self, number: int, part: str, alias: Alias | None, reader: Reader | None, caller: Caller) -> list[Nudge]:
        if alias is not None:
            return [*self.watched(number, alias, caller), *self.alias_wrapper_lines(alias)]
        wrapper = self.line_wrapper_lines(part)
        if reader is not None:
            return [*self.reader_watched(number, part, reader, caller), *wrapper]
        guessed = self.guess.guessed(self.outputs.find(number), part)
        if guessed is not None:
            return [ShellNudges.READER_GUESSED.create(reader=guessed.name, about=guessed.subject, command=CommandShape.command_name(part)), *self.reader_watched(number, part, guessed, caller), *wrapper]
        return [*self.suggestions.lines(number, part), *wrapper]

    def alias_wrapper_lines(self, alias: Alias) -> list[Nudge]:
        unwrapped = TimeLimitWrapper.unwrapped(alias.line)
        if unwrapped == alias.line or alias.name in self.wrappers_told:
            return []
        self.wrappers_told.add(alias.name)
        return [ShellNudges.ALIAS_TIME_LIMIT.create(name=alias.name, line=unwrapped)]

    def line_wrapper_lines(self, part: str) -> list[Nudge]:
        unwrapped = TimeLimitWrapper.unwrapped(part)
        shape = CommandShape.build(unwrapped)
        if unwrapped == part or shape in self.wrappers_told:
            return []
        self.wrappers_told.add(shape)
        return [ShellNudges.LINE_TIME_LIMIT.create(command=shape)]

    def reader_watched(self, number: int, part: str, reader: Reader, caller: Caller) -> list[Nudge]:
        self.outputs.watch(self.outputs.find(number), reader.name, "", caller.actor)
        shape = CommandShape.build(part)
        watched = [ShellNudges.READER_WATCH.create(n=number, command=shape, reader=reader.name)]
        varied = self.entries.shape_commands(caller.session, shape) if caller.session and not reader.topic_pattern else set()
        return [*watched, ShellNudges.READER_TOPIC.create(command=shape, count=len(varied), reader=reader.name)] if len(varied) >= VARIED_RUNS else watched

    def watched(self, number: int, alias: Alias, caller: Caller) -> list[Nudge]:
        self.outputs.watch(self.outputs.find(number), alias.reader, "", caller.actor)
        return [ShellNudges.ALIAS_WATCH.create(n=number, name=alias.name, reader=f" through the reader {alias.reader}" if alias.reader else "")]

    # a run whose card shows, or will, keeps its output for the card to open
    def is_carded(self, output: CommandOutput) -> bool:
        if not (output.watch_reader or output.is_watched):
            return False
        with self.scope.environment(output.environment_id):
            return output.is_past_mark(time.time()) or self.card.is_shown(output)

    def closed(self, folder: OutputFiles, request: ShellRequest, caller: Caller, cap: Cap) -> None:
        if cap.is_direct() or cap.is_whole():
            folder.remove()
            return
        if not self.record.is_stored(folder.folder.name, request.line, folder.size(), folder.has_cut()) and not self.is_carded(self.outputs.chain_output(folder.folder.name)):
            self.record.delete_output(folder.folder.name, caller)


def raise_first(faults: list[Exception]) -> None:
    if faults:
        raise faults[0]
