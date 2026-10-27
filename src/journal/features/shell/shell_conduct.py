import re

from journal.engine.base_state import BaseState
from journal.engine.conduct import Conduct
from journal.engine.support.settings import Settings
from journal.engine.nudge import Nudge
from journal.engine.support.transition import Transition
from journal.events.agent.agent_event import AgentEvent
from journal.events.agent.ticked import Ticked
from journal.events.agent.tool_finished import ToolFinished
from journal.events.agent.tool_starting import ToolStarting
from journal.features.shell.support.ended_output import EndedOutput
from journal.features.shell.support.folder_change import FolderChange
from journal.features.shell.support.project_paths import ProjectPaths
from journal.features.shell.support.piped_journal_command import PipedJournalCommand
from journal.features.shell.support.piped_test_run import PipedTestRun
from journal.models.alias import Alias
from journal.support.alias_call import AliasCall
from journal.support.tool_call import ToolCall
from journal.features.shell.support.reader import Reader
from journal.support.chain import Chain
from journal.support.foreground_option import FOREGROUND_OPTION
from journal.support.moment import Moment
from journal.support.timeout import Timeout
from journal.features.shell.shell_nudges import ShellNudges
from journal.features.shell.shell_options import ShellOptions
from journal.features.shell.shell_part import ShellPart
from journal.features.shell.support.shell_data import ShellData

# the output a journal output command names: journal output show 21620
OUTPUT_NUMBER = re.compile(r"\boutput\s+[a-z-]+\s+(\d+)")

SILENCE_SECONDS = 5.0
BACKGROUND_CHECK_DELAY_SECONDS = 300.0
ALIAS_RUNS = 3


class ShellConduct(Conduct):
    """The shell feature's conduct in every state: a file longer than the runner shows is read in parts, a shell loop that only polls journal commands is refused with the await that waits instead, a journal command runs alone while an alias may chain, a test run piped into a filter is refused, a cd that would leave the shell outside its environment's folder is refused, a read of an output by hand is pointed at the reader that reads it, a line an alias runs, typed by hand or through a wider alias, is refused with the alias, and a line run three times is asked to become one, the commands that ended in the background are named once the agent is quiet, with one reader offered for a run of them, or for a watched run at its end, one the agent waits on left to the wait, one running five minutes is looked at, and a watched output's view is sent after every tool use until its command ends; a watched card that has shown nothing for 30 seconds is named once, after a tool use or while the agent waits."""

    def on_tool_starting(self, event: ToolStarting, settings: Settings) -> Transition:
        return Transition.merged(self, [journal_poll_check(self, event, settings), journal_isolation_check(self, event, settings), piped_test_check(self, event, settings), piped_journal_check(self, event, settings), folder_change_check(self, event, settings), project_path_check(self, event, settings), partial_read_check(self, event, settings), readers_check(self, event, settings), reader_report_check(self, event, settings), alias_check(self, event, settings)])

    def on_tool_finished(self, event: ToolFinished, settings: Settings) -> Transition:
        watch = event.data.part(ShellPart).watch
        if not watch.is_watching():
            return unread_check(self, event, settings)
        if watch.ending:
            return self.none(ShellNudges.WATCH_ENDED.create(n=watch.output, command=watch.command, ending=watch.ending, lines=watch.text()), *reader_offer(event.data.part(ShellPart), {watch.output}))
        return self.none(ShellNudges.WATCH_VIEW.create(n=watch.output, command=watch.command, lines=watch.text()))

    def on_ticked(self, event: Ticked, settings: Settings) -> Transition:
        return Transition.merged(self, [background_check(self, event, settings), silent_run_check(self, event, settings), ended_check(self, event, settings), unread_check(self, event, settings)])


def outcome_text(ended: tuple[EndedOutput, ...]) -> str:
    outcomes: dict[str, list[int]] = {}
    for output in ended:
        if output.summary is None:
            outcomes.setdefault(output.ending, []).append(output.id)
    grouped = [f"output{'s' if len(ids) > 1 else ''} {', '.join(map(str, ids))} {outcome}" for outcome, ids in outcomes.items()]
    return "; ".join([*grouped, *(f"output {output.id} {output.ending}: {output.summary}" for output in ended if output.summary is not None)])


def partial_read_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    cap = settings.integer(ShellOptions.SHOWN)
    return state.refuse(ShellNudges.PARTIAL_FILE_READ.create(lines=event.call.file_lines, cap=cap)) if event.call.file_lines > 2 * cap else state.none()


def journal_poll_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    if not Chain.is_journal_poll([part.text for part in event.call.parts]):
        return state.none()
    polled = OUTPUT_NUMBER.search(event.call.command)
    return state.refuse(ShellNudges.JOURNAL_POLL.create(n=polled[1] if polled else "<n>"))


def journal_isolation_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    journal, parts = event.call.journal_parts()
    return state.refuse(ShellNudges.JOURNAL_COMMAND_ISOLATION.create()) if 0 < journal < parts else state.none()


def folder_change_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    changes = FolderChange.targets([part.text for part in event.call.parts])
    if not changes:
        return state.none()
    home = event.data.part(ShellPart).home
    targets = [target for target in changes if not FolderChange.is_home(target, home)]
    return state.refuse(ShellNudges.FOLDER_CHANGE_REFUSAL.create(target=targets[0], home=home)) if targets else state.none()


def project_path_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    if not event.call.parts:
        return state.none()
    relative = ProjectPaths.relative_line(event.call.command, event.data.part(ShellPart).home)
    return state.refuse(ShellNudges.PROJECT_PATH_REFUSAL.create(line=relative)) if relative != event.call.command else state.none()


def is_read(reader: Reader, call: ToolCall) -> bool:
    return any(reader.commands.reads(part.shape) for part in call.parts)


def alias_refusals(text: str, aliases: tuple[Alias, ...]) -> list[Nudge]:
    call = AliasCall.parsed(text)
    called = [alias for alias in aliases if alias.name == call.name]
    if called:
        line = called[0].expanded(call.args)
        return [ShellNudges.MORE_SPECIFIC_ALIAS.create(name=alias.name, called=called[0].name, line=line) for alias in covering_aliases(line, aliases, called[0].head_size())]
    if Chain.is_journal(text):
        return []
    return [ShellNudges.ALIASED_LINE.create(name=alias.name, line=text) for alias in covering_aliases(text, aliases, -1)]


def covering_aliases(line: str, aliases: tuple[Alias, ...], head_size: int) -> list[Alias]:
    return sorted((alias for alias in aliases if alias.starts(line) and alias.head_size() > head_size), key=lambda alias: -alias.head_size())


def piped_test_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    program = PipedTestRun.piped_filter(event.call.parts, {alias.name: alias for alias in event.data.part(ShellPart).aliases})
    return state.refuse(ShellNudges.PIPED_TEST_RUN.create(filter=program)) if program else state.none()


def piped_journal_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    cut = PipedJournalCommand.piped(event.call.command, event.data.part(ShellPart).uncut_verbs)
    return state.refuse(ShellNudges.PIPED_JOURNAL_COMMAND.create(command=cut[0], filter=cut[1])) if cut else state.none()


def alias_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    shell = event.data.part(ShellPart)
    refusals = [refusal for part in event.call.parts for refusal in alias_refusals(part.text, shell.aliases)]
    if refusals:
        return state.refuse(refusals[0])
    command, shape = event.call.command, event.call.recorded().shape
    if not Timeout.tool_uses(ALIAS_RUNS).is_elapsed(event.shape_runs) or bool(event.call.parts) and Chain.is_journal(event.call.parts[0].text) or event.call.is_read() or " " not in shape:
        return state.none()
    reader = next((r.name for r in shell.readers if is_read(r, event.call)), "<the reader that reads its output>")
    tip = ShellNudges.ALIAS_SUGGESTION.create(shape=shape, reader=f" --reader {reader}")
    return state.none() if tip.rendered() in shell.tipped else state.none(tip)


def readers_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    reads = [part for part in event.call.parts if part.reads_output]
    if not reads:
        return state.none()
    shell = event.data.part(ShellPart)
    tips = [ShellNudges.READER_HINT.create(reader=r.name, about=r.subject) for r in shell.readers if r.matches(reads[0].text)]
    new_tips = [tip for tip in tips if tip.rendered() not in shell.tipped]
    return state.none(new_tips[0]) if new_tips else state.none()


def ended_check(state: BaseState, event: Ticked, settings: Settings) -> Transition:
    ended = event.data.part(ShellPart).unannounced
    if not Timeout.seconds(SILENCE_SECONDS).is_elapsed(event.silence_seconds) or not ended:
        return state.none()
    return state.none(ShellNudges.OUTPUTS_ENDED.create(outputs=outcome_text(ended), n=ended[0].id), *reader_offer(event.data.part(ShellPart), {output.id for output in ended}))


def reader_offer(shell: ShellData, outputs: set[int]) -> list[Nudge]:
    offer = next((offer for offer in shell.reader_offers if offer.output in outputs), None)
    return [ShellNudges.READER_OFFER.create(part=offer.part, command=offer.command)] if offer is not None else []


def unread_check(state: BaseState, event: AgentEvent, settings: Settings) -> Transition:
    shell = event.data.part(ShellPart)
    if event.subagent or not shell.unread or shell.unannounced:
        return state.none()
    interval = Timeout.tool_uses(settings.integer(ShellOptions.UNREAD_OUTPUT_INTERVAL)).combined(Timeout.seconds(settings.integer(FOREGROUND_OPTION)))
    if not interval.reset(shell.last_ending_line).has_passed(Moment(seconds=event.time, tool_uses=shell.tool_uses)):
        return state.none()
    return state.none(ShellNudges.UNREAD_OUTPUT.create(outputs=outcome_text(shell.unread), n=shell.unread[0].id))


def reader_report_check(state: BaseState, event: ToolStarting, settings: Settings) -> Transition:
    shell = event.data.part(ShellPart)
    return state.none(*(line for line in reader_lines(shell) if line.rendered() not in shell.tipped))


def reader_lines(shell: ShellData) -> list[Nudge]:
    raised = [ShellNudges.REPORT_RAISED.create(n=n) for n in sorted({*shell.unread_reports, *shell.unfixed_reports})]
    refuted = [ShellNudges.REPORT_REFUTED.create(verdicts=ShellNudges.report_refutations(reports)) for reports in (shell.refuted_reports,) if reports]
    return [*raised, *refuted]


def silent_run_check(state: BaseState, event: AgentEvent, settings: Settings) -> Transition:
    shell = event.data.part(ShellPart)
    unhinted = [run for run in shell.silent_runs if not any(f"output {run.output} has printed nothing" in line for line in shell.tipped)]
    return state.none(ShellNudges.SILENT_RUN_HINT.create(n=unhinted[0].output, seconds=unhinted[0].quiet_seconds)) if unhinted else state.none()


def background_check(state: BaseState, event: Ticked, settings: Settings) -> Transition:
    shell = event.data.part(ShellPart)
    if not shell.background or not Timeout.seconds(BACKGROUND_CHECK_DELAY_SECONDS).started(shell.backgrounded_at).is_elapsed(event.time):
        return state.none()
    return state.none(ShellNudges.BACKGROUND_CHECK.create(background_outputs=", ".join(str(n) for n in shell.background)))
